# Make Skyblock Items: JSON to MCFunction
Have you ever wanted to make cool Hypixel Skyblock items, but found
MCStacker to be too annoying? Well, this is your answer! Using this
tool, you can write a JSON file and generate your item with ease.

## Installation & Usage
### Prerequisites
- A command prompt
- Git
- Python 3.8 or newer
- A text editor (that ideally supports JSON)

```sh
git clone https://github.com/IY314/make_skyblock_items.git
cd make_skyblock_items
```
`epic_sword.json`:
```json
{
    "skyblock_item": true,
    "name": "Epic Sword",
    "type": "SWORD",
    "item": "minecraft:iron_sword",
    "rarity": "rarity.epic",
    "reforges": ["reforges.Sharp"],
    "stats": {
        "stats.damage": "+120",
        "stats.strength": "+100"
    },
    "enchantments": {
        "Sharpness": ["enchantments.Sharpness", 5, "sharpness"],
        "Critical": ["enchantments.Critical", 5],
        "First Strike": ["enchantments.First Strike", 4]
    }
}
```
### Explanation:
#### **A Note about References:**
This example uses references such as `reforges.Sharp` and `stats.damage`. The program will look at a certain reference `abc.def.ghi` as "Look for `ghi` in the object `def` in the JSON file `abc` that resides in the directory `items`. Substitute `ghi` as the value instead of this reference."

References can be used to reuse JSON code when making your items. The files included within the `items` directly are updated periodically to include enchantments, reforges, stat names, and rarities from Skyblock.
1. Declare that, yes, this is a Skyblock item file. (`skyblock_item`)
2. Set the name, item type, Minecraft item ID, and rarity of the item.
(`name`, `type`, `item`, `rarity`) 
3. List reforges. Reforges **must** be listed as objects in reforge format or a reference to one.
4. Set stats of the item. The stat, unfortunately, **must** be a reference to a stat, due to the nature of JSON object keys.
5. Set enchantments. Enchantments are listed in the form `display_name: [enchantment_format_or_reference, level, <optional - minecraft_enchantment_id>]`.
