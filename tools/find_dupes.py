"""Find and remove near-duplicate images.

Compares every image as 16x16 RGBA (transparent pixels flattened onto grey).
Two images are "near duplicates" when at most --threshold of their 256 pixels differ
(a pixel differs when any channel, or opacity, differs by more than 24).

Only new images (repo root) are ever deleted; the named library in the category folders
is kept as is. Among new images, the one with the most similar neighbours is kept and its
neighbours are removed (greedy).

usage:
  python tools/find_dupes.py --stats                 # pair counts per difference level
  python tools/find_dupes.py --review out.png        # render sample pairs per level
  python tools/find_dupes.py --threshold 26          # dry run: how many would be removed
  python tools/find_dupes.py --threshold 26 --apply  # delete them
"""
import argparse
import os
import random
import sys
from collections import Counter, defaultdict

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import REPO, library_images, new_images  # noqa: E402

MAX_ND = 26  # largest threshold we search for; also the prefilter bound


def load(paths):
    n = len(paths)
    A = np.zeros((n, 16, 16, 4), np.uint8)
    for i, p in enumerate(paths):
        im = Image.open(os.path.join(REPO, p)).convert('RGBA')
        if im.size != (16, 16):
            im = im.resize((16, 16), Image.NEAREST)
        A[i] = np.asarray(im)
    a = A[..., 3:4].astype(np.float32) / 255
    P = (A[..., :3] * a + 128 * (1 - a)).astype(np.int16)
    mask = A[..., 3:4] > 127
    P = np.concatenate([P, mask.astype(np.int16) * 255], -1)
    return P, mask.reshape(n, -1).astype(np.float32)


def find_pairs(P, M, rows):
    """Pairs (i, j, nd) with nd <= MAX_ND, i in rows. Uses opacity-mask hamming distance and
    squared L2 as cheap prefilters (both are lower bounds on what a <=MAX_ND pair can have)."""
    n = len(P)
    F = P.reshape(n, -1).astype(np.float32)
    sq = (F ** 2).sum(1)
    ms = M.sum(1)
    d2_max = MAX_ND * 4 * 255 ** 2 + 256 * 4 * 24 ** 2
    pairs = []
    rows = np.asarray(rows)
    for s in range(0, len(rows), 1024):
        r = rows[s:s + 1024]
        ham = ms[r, None] + ms[None] - 2 * M[r] @ M.T
        d2 = sq[r, None] + sq[None] - 2 * F[r] @ F.T
        ii, jj = np.nonzero((ham <= MAX_ND) & (d2 < d2_max))
        ii = r[ii]
        keep = jj != ii
        ii, jj = ii[keep], jj[keep]
        for c in range(0, len(ii), 100000):
            a, b = ii[c:c + 100000], jj[c:c + 100000]
            nd = (np.abs(P[a] - P[b]).max(-1) > 24).sum((1, 2))
            k = nd <= MAX_ND
            pairs += list(zip(a[k].tolist(), b[k].tolist(), nd[k].tolist()))
    # dedupe symmetric pairs
    seen = {}
    for i, j, nd in pairs:
        seen[(min(i, j), max(i, j))] = nd
    return [(i, j, nd) for (i, j), nd in seen.items()]


def choose_removals(pairs, n_new, threshold):
    """Indices < n_new are new images, the rest are library images (never removed)."""
    nb = defaultdict(set)
    for i, j, nd in pairs:
        if nd <= threshold:
            nb[i].add(j)
            nb[j].add(i)
    removed = set()
    # anything new that matches the library goes first
    for i in list(nb):
        if i < n_new and any(j >= n_new for j in nb[i]):
            removed.add(i)
    kept = set()
    for i in sorted((x for x in nb if x < n_new), key=lambda x: (-len(nb[x]), x)):
        if i in removed:
            continue
        kept.add(i)
        removed |= {j for j in nb[i] if j < n_new and j not in kept}
    return removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--threshold', type=int, default=26)
    ap.add_argument('--stats', action='store_true')
    ap.add_argument('--review', metavar='PNG')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    assert args.threshold <= MAX_ND

    new, lib = new_images(), library_images()
    paths = new + lib
    print(f'new {len(new)}, library {len(lib)}')
    if not new:
        return
    P, M = load(paths)
    pairs = find_pairs(P, M, range(len(new)))
    print(f'similar pairs touching new images: {len(pairs)}')

    if args.stats:
        print(sorted(Counter(min(nd // 2 * 2, MAX_ND) for _, _, nd in pairs).items()))
        for t in (1, 8, 12, 17, 26):
            print(f'  threshold {t:2d}: remove {len(choose_removals(pairs, len(new), t))}')

    if args.review:
        bins = [(0, 1), (2, 4), (5, 8), (9, 12), (13, 17), (18, 22), (23, 26)]
        random.seed(1)
        W = Image.new('RGB', (6 * 150, len(bins) * 80), (215, 215, 215))
        d = ImageDraw.Draw(W)
        for r, (lo, hi) in enumerate(bins):
            c = [p for p in pairs if lo <= p[2] <= hi]
            for k, (i, j, nd) in enumerate(random.sample(c, min(6, len(c)))):
                for t, x in enumerate((i, j)):
                    im = Image.open(os.path.join(REPO, paths[x])).convert('RGBA').resize((64, 64), Image.NEAREST)
                    W.paste(im, (k * 150 + 4 + t * 68, r * 80 + 2), im)
                d.text((k * 150 + 4, r * 80 + 67), f'nd={nd}', fill=0)
        W.save(args.review)
        print('review sheet:', args.review)

    rm = sorted(choose_removals(pairs, len(new), args.threshold))
    print(f'threshold {args.threshold}: {len(rm)} new images would be removed')
    if args.apply:
        for i in rm:
            os.remove(os.path.join(REPO, paths[i]))
        print('removed', len(rm))


if __name__ == '__main__':
    main()
