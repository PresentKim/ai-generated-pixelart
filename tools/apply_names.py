"""Validate subagent naming output and move the new images into category folders.

usage:
  python tools/apply_names.py WORK_DIR          # validate only (coverage, per-sheet id range, stats)
  python tools/apply_names.py WORK_DIR --apply  # rename + move

Reads WORK_DIR/index.json and WORK_DIR/out/sheet_NNN.tsv ("id<TAB>category<TAB>name").
Names are normalised (lowercase, [a-z0-9_], category prefix, <=80 chars); unknown
categories fall back to the name's first word or "misc". Files land at
<category>/<name>-NNNN.png, numbering continuing after any existing file of that name.
"""
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CATEGORIES, REPO  # noqa: E402

CATS = set(CATEGORIES)


def normalise(cat, name):
    cat, name = cat.strip().lower(), name.strip().lower()
    name = re.sub(r'_+', '_', re.sub(r'[^a-z0-9_]+', '_', name)).strip('_')
    if cat not in CATS:
        first = name.split('_')[0]
        cat = first if first in CATS else 'misc'
    if not name.startswith(cat + '_'):
        name = f'{cat}_{name}'
    return cat, name[:80].rstrip('_')


def main():
    work = sys.argv[1]
    apply = '--apply' in sys.argv
    index = {int(k): v for k, v in json.load(open(os.path.join(work, 'index.json'), encoding='utf-8')).items()}
    got, bad, misplaced = {}, [], []
    for p in sorted(glob.glob(os.path.join(work, 'out', 'sheet_*.tsv'))):
        sheet = int(re.search(r'sheet_(\d+)', p).group(1))
        for ln in open(p, encoding='utf-8-sig'):
            parts = ln.rstrip('\r\n').split('\t')
            if len(parts) != 3 or not parts[0].strip().isdigit():
                if ln.strip():
                    bad.append((os.path.basename(p), ln.strip()))
                continue
            i = int(parts[0])
            if i // 100 != sheet:
                misplaced.append((os.path.basename(p), i))
            got[i] = normalise(parts[1], parts[2])
    missing = sorted(set(index) - set(got))
    print(f'named {len(got)} of {len(index)}, missing {len(missing)}, bad lines {len(bad)}, ids on wrong sheet {len(misplaced)}')
    if missing:
        print('sheets with missing ids:', sorted({m // 100 for m in missing}))
    for b in bad[:10]:
        print('  bad:', b)
    for m in misplaced[:10]:
        print('  wrong sheet:', m)
    print(Counter(c for c, _ in got.values()).most_common())
    long_ = sum(1 for _, n in got.values() if len(n.split('_')) > 9 or len(n) > 70)
    print('names over 9 words or 70 chars:', long_)
    if not apply:
        return
    assert not missing and not misplaced, 'fix missing / misplaced ids first'

    groups = defaultdict(list)
    for i in sorted(got):
        groups[got[i]].append(i)
    moved = 0
    for (cat, name), ids in groups.items():
        d = os.path.join(REPO, cat)
        os.makedirs(d, exist_ok=True)
        pat = re.compile(re.escape(name) + r'-(\d{4,})\.png$')
        start = max([int(m.group(1)) for f in os.listdir(d) if (m := pat.match(f))], default=0)
        for k, i in enumerate(ids, start + 1):
            dst = os.path.join(d, f'{name}-{k:04d}.png')
            assert not os.path.exists(dst), dst
            os.rename(os.path.join(REPO, index[i]), dst)
            moved += 1
    print('moved', moved)


if __name__ == '__main__':
    main()
