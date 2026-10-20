"""Build labelled contact sheets of the new (repo-root) images for naming by subagents.

usage: python tools/make_sheets.py WORK_DIR

Writes into WORK_DIR (keep it outside the repo, e.g. the session scratchpad):
  index.json              id -> original filename
  sheets/sheet_NNN.png    100 icons (10x10, upscaled 4x, id printed under each)
  lists/sheet_NNN.txt     "id<TAB>original name" for the same icons
  out/                    empty; subagents write sheet_NNN.tsv here
  GUIDE.md                copy of tools/NAMING_GUIDE.md
"""
import json
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import REPO, new_images  # noqa: E402

PER, COLS, IMG, CW, CH = 100, 10, 64, 80, 84


def main():
    work = sys.argv[1]
    for d in ('sheets', 'lists', 'out'):
        os.makedirs(os.path.join(work, d), exist_ok=True)
    shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'NAMING_GUIDE.md'), os.path.join(work, 'GUIDE.md'))
    files = new_images()
    json.dump({i: f for i, f in enumerate(files)}, open(os.path.join(work, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    font = ImageFont.load_default()
    for s in range(0, len(files), PER):
        n = s // PER
        sheet = Image.new('RGB', (COLS * CW, (PER // COLS) * CH), (215, 215, 215))
        d = ImageDraw.Draw(sheet)
        lines = []
        for k, f in enumerate(files[s:s + PER]):
            i = s + k
            im = Image.open(os.path.join(REPO, f)).convert('RGBA').resize((IMG, IMG), Image.NEAREST)
            x, y = (k % COLS) * CW, (k // COLS) * CH
            sheet.paste(im, (x + 8, y + 2), im)
            d.text((x + 8, y + 68), str(i), fill=(0, 0, 0), font=font)
            lines.append(f'{i}\t{f[:-4]}')
        sheet.save(os.path.join(work, 'sheets', f'sheet_{n:03d}.png'))
        open(os.path.join(work, 'lists', f'sheet_{n:03d}.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(f'{len(files)} images, {(len(files) + PER - 1) // PER} sheets in {work}')


if __name__ == '__main__':
    main()
