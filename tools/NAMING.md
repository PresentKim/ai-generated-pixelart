# Naming task

You name pixel-art sprite sheets so they are easy to search. Each page image `pages/pNNN.png` shows up to 20 sheets.
Each sheet has a black label `#ID` above it (shown on white, scaled up). The matching `pages/pNNN.txt` lists
`ID<TAB>grid<TAB>original filename`. The original filename is often the AI prompt or a rough tag list:
use it as a hint, but trust what you SEE (the prompt may be wrong, truncated, or meaningless like base64 / "drowersieve").
Every tile in a sheet will get this one base name plus a -0001.. suffix, so the name must describe the sheet as a whole
(if the tiles are a mixed set, name the shared theme and list the main colors across the set).

## Format
lowercase English words joined by `_`, only [a-z0-9_], 4 to 9 words, at most 80 characters. Order:

  {subject}_{category}_{shape/material/features}_{colors}

- subject: the concrete thing first, most specific noun (e.g. `fishing_rod`, `pineapple`, `treasure_chest`, `seedling`, `pigeon`).
- category: one or two broad search words from: food, drink, potion, dessert, fruit, vegetable, crop, plant, flower, tree,
  weapon, tool, armor, accessory, jewelry, block, terrain, ore, gem, mineral, ingot, material, container, chest, furniture,
  machine, tech, creature, animal, fish, monster, coin, currency, icon, rune, magic, relic, decoration, structure, misc.
- shape/material/features: 1-3 words of what makes it distinctive (e.g. `wooden`, `round`, `glowing`, `cracked`, `lattice_crust`, `horseshoe`).
- colors: the 2-4 dominant colors, most dominant first, from: red, crimson, orange, yellow, gold, green, lime, teal, cyan, blue,
  navy, purple, violet, pink, magenta, brown, beige, cream, white, gray, black, silver, bronze, copper.
  Do NOT count the white background.

Examples: `fishing_rod_tool_wooden_pole_float_brown_green`, `seedling_sprout_plant_crop_soil_green_brown`,
`cherry_pie_slice_dessert_food_lattice_crust_crimson_gold`, `horseshoe_magnet_tool_eye_magic_blue_red_gold`,
`floating_island_terrain_tree_waterfall_green_brown_blue`, `skull_coin_currency_round_cream_brown`.
Don't use "item", "game", "pixel", "icon set", "collection", "minecraft", "asset" unless it's literally the subject.

## Output
Write ONE JSON file per page: `names/pNNN.json` = {"<ID>": "<name>", ...} with an entry for EVERY ID in that page's txt.
Look at every page image yourself (Read tool). Do not write scripts that guess names from filenames alone.
