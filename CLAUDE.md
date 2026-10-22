# AI pixel-art preprocessing

This branch (`preproccess`) is a staging area for AI-generated pixel-art images. They get processed here before they
move to `main`. `main` holds only finished assets: flat 16x16 PNG tiles named `<name>-NNNN.png`, about 24.8k files.

## Input layout

- `2x2/ 3x3/ 4x4/ 6x6/ 7x7/ 8x8/ etc/`: source sheets (each folder keeps a `.gitkeep`).
- A sheet is a square grid of 16px tiles on a white background, usually variations of one subject:
  32px = 2x2, 48px = 3x3, 16px = a single tile. The folder name is only a hint; the pixel size decides the grid.
- The filename is often the AI prompt (sometimes cut off, or with " (1)" duplicates), sometimes a rough tag list,
  and sometimes meaningless (base64, typos). Use it as a naming hint only.
- Sizes that aren't a clean 16px grid (for example 256px or 384px AI upscales) are skipped by the tools. Report
  them to the user to handle manually.

## Output rules (what `main` expects)

- Every tile is exactly 16x16. Saved as palette PNG (mode P) with index 0 transparent, or RGBA if a tile has more
  than 255 colors.
- Background removal is conservative: the user touches up tiles anyway, and a leftover white pixel is easier to
  fix than a lost subject pixel.
  - The reference background is the most common near-white (every channel >= 235) border color of the tile.
    Pixels within 6 per channel of it, flood-filled from the tile border, become transparent. Light subject
    pixels (silver, pale fills, highlights) touching the background are kept.
  - A near-white pixel left with 3+ of its 4 sides open (transparent or off-tile) is removed as noise.
  - Enclosed white holes (ring, bow, donut interiors) stay white by default. `split.py --holes` clears them with
    the old rule (hole >= 3 px, >= 60% of its wall matches the outline colors and is dark), but that rule also
    erases dice pips, book pages, shoe whites and eye whites, so use it only for sheets of rings and the like.
  - Known leftovers: hole interiors and faint off-white noise along the tile edge. The user fixes those by hand.
- Fully transparent tiles are dropped. Tiles whose source had a colored background keep it.
- Names: one base name per sheet, `{subject}_{category}_{shape/material/features}_{colors}`. Lowercase English
  joined by `_`, 4–9 words, at most 80 characters. The full vocabulary is in `tools/NAMING.md`.
- Numbering: `-0001`, `-0002`, ... in row-major tile order. If a base name already exists on `main` (or earlier in
  the batch), numbering continues after its highest number, so names never collide with `main`.

## Workflow

Use a scratch work dir (`W` below) outside the repo. Run from the repo root.

1. `python tools/manifest.py W` builds `W/manifest.json` (id, path, grid, original name) and preview pages
   `W/pages/pNNN.png` + `.txt`, with 20 labeled sheets per page. Note any "skip" lines.
2. Optionally run `python tools/split.py W . W/testout test` and look at the tiles to check background removal.
3. Name the sheets with subagents, about 10 pages per agent, in parallel; the sonnet model is enough. Prompt:
   "Work dir: W. First Read NAMING.md (copy `tools/NAMING.md` into W) and follow it exactly. Your pages: pAAA
   through pBBB. Write names/pAAA.json ... Reply 'done' plus any page you could not finish."
   Agents must look at every page image, not guess from filenames.
4. Validate: every manifest id has a name, each name matches `[a-z0-9_]+`, and nothing over 80 characters. Drop
   filler tokens such as `item` and `game`.
5. `python tools/split.py W . processed` writes the tiles to `processed/` and a mapping
   `W/split_log.tsv` (source, tile index, output file). Spot-check a random sample visually, before and after.
6. Check that every file in `processed/` is 16x16.
7. `python tools/remove_originals.py W` deletes the processed source sheets. Skipped files stay.
8. Commit on `preproccess` in the usual style: `feat: Add N images` for new sources,
   `feat: Add N processed tiles ...`, `feat: Remove N files cause proccessed.`
   Moving `processed/` into `main` is a separate step the user asks for. The user usually compresses images
   afterwards (`chore: compress images`, oxipng).
