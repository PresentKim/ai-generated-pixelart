# Pixel-art icon naming guide (for naming subagents)

Each contact sheet `sheets/sheet_NNN.png` shows 100 icons (16x16, upscaled) on a light grey background, each labelled with its numeric ID.
`lists/sheet_NNN.txt` has `ID<TAB>original_filename` for the same icons. The original name is often the AI prompt or an older
auto-generated label: use it as a strong hint, but trust what you SEE (colours, shape) when they disagree. Some originals are
garbage (base64-like strings, "-recolored" variants with changed colours): name those purely from the image.

## Output
For each sheet write `out/sheet_NNN.tsv` (UTF-8), one line per ID, every ID of that sheet, no header:
`ID<TAB>category<TAB>name`

## category: exactly one of
weapon (swords, axes, bows, arrows, spears, staves used as weapons, maces, guns)
armor (helmets, chestplates, boots-as-armor, shields, gauntlets)
tool (pickaxes, hoes, shovels, fishing rods, hammers-as-tools, keys, wrenches, buckets, watering cans)
food (any edible: cakes, fruit, meat, bread, vegetables, sweets, dishes)
drink (cups, mugs, tea, juice, bottled beverages)
potion (magic/alchemy potion bottles and flasks with liquid)
plant (flowers, trees, saplings, leaves, mushrooms, crops not prepared as food, seeds)
gem (gemstones, crystals, jewels, diamonds, crystal clusters)
material (ingots, ores, nuggets, raw resources, wood logs/planks, cloth, leather, bones, dust)
block (cube/terrain/building blocks, tiles, bricks, textures)
creature (animals, monsters, slimes, characters, faces, mobs)
accessory (rings, amulets, necklaces, crowns, jewelry, charms)
clothing (shirts, hats, capes, shoes, non-armor wearables)
container (chests, boxes, bags, wallets, barrels, empty bottles/jars, bowls, cauldrons, pots)
furniture (tables, chairs, beds, lamps, shelves, workstations)
magic (orbs, scrolls, spell books, runes, wands-not-weapons, magic relics, totems)
tech (machines, gears, circuits, energy cells, robots, sci-fi modules, furnaces/industrial)
ui (hearts, stars, symbols, arrows-as-icons, buttons, abstract/geometric icons, badges, coins-as-currency icons)
decoration (statues, banners, ornaments, candles, trophies, flags)
misc (anything that fits nothing above)

## name: format `category_subject_colors_shape_details`
- lowercase English, only a-z 0-9 and `_`, 4 to 9 words, max 70 characters.
- 1st word = the category (same as column 2).
- then the specific subject (`sword`, `strawberry_cake`, `fishing_rod`, `amethyst_cluster`, `health_heart`).
- then the 1-3 dominant colours as seen, most dominant first (`purple_blue`, `white_red`). Use plain colour words:
  red orange yellow gold green lime teal cyan blue navy purple pink magenta brown beige black grey silver white.
- then 1-3 words of shape/material/feature/what it depicts (`round`, `curved_blade`, `glowing`, `wooden`, `cracked`,
  `with_fish`, `lattice_crust`, `spiked`, `empty`, `filled`, `cluster`).
- Do NOT add numbers or IDs; numbering is added later. Duplicate names across IDs are fine, but DO distinguish visibly
  different variants (different colour, filled vs empty, broken vs whole) in the name.
- Every word must describe what is actually visible in THAT icon. When icons look identical, give them the identical
  name. Never cycle or invent descriptor words just to make names differ.
- Examples:
  `weapon_sword_grey_red_flame_hilt`
  `ui_health_heart_silver_red_filled`
  `food_strawberry_cake_white_red_round_cream`
  `tool_fishing_rod_brown_red_wooden_with_fish`
  `gem_amethyst_cluster_purple_crystal_shards`
  `container_chest_grey_black_metal_closed`

## Working rules
- Work through every sheet assigned to you: Read the sheet PNG (to view it) AND its list, then write the TSV.
- Don't skip IDs and don't write IDs from another sheet.
- Other agents run in the same folder at the same time. Put any helper scripts or temp files ONLY in your own
  subfolder `work_<first sheet number>/`; never create or edit files in the folder root. Only write `out/` files for
  your own sheets.
- When done, reply with the sheet numbers you completed, plus any sheet where you named icons coarsely.
