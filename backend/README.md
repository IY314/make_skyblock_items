# Make Skyblock Items: JSON to MCFunction
Have you ever wanted to make cool Hypixel Skyblock items, but found
MCStacker to be too annoying? Well, this is your answer! Using this
tool, you can write a JSON file and generate your item with ease.

## Installation
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
    "reforges": ["reforges.Sharp"],
    "stats": {
        "stats.damage": "+120",
        "stats.strength": "+100"
    },
    "enchantments": {
        "Sharpness": ["enchantments.Sharpness", 5, "sharpness"],
        "Critical": ["enchantments.Critical", 5],
        "First Strike": ["enchantments.First Strike", 4]
    },
    "rarity": "rarity.epic"
}

