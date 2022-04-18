from argparse import ArgumentParser
import json
import random
import re


ROMAN_VALUES = [
    (1000, 'M'),
    (900, 'CM'),
    (500, 'D'),
    (400, 'CD'),
    (100, 'C'),
    (90, 'XC'),
    (50, 'L'),
    (40, 'XL'),
    (10, 'X'),
    (9, 'IX'),
    (5, 'V'),
    (4, 'IV'),
    (1, 'I')
]

COLOR_VALUES = {
    '0': 'black',
    '1': 'dark_blue',
    '2': 'dark_green',
    '3': 'dark_aqua',
    '4': 'dark_red',
    '5': 'dark_purple',
    '6': 'gold',
    '7': 'gray',
    '8': 'dark_gray',
    '9': 'blue',
    'a': 'green',
    'b': 'aqua',
    'c': 'red',
    'd': 'light_purple',
    'e': 'yellow',
    'f': 'white'
}


def int_to_roman(number):
    result = []
    for value, symbol in ROMAN_VALUES:
        quotient, number = divmod(number, value)
        result.append(symbol * quotient)
        if number == 0:
            break
    return ''.join(result)


class SkyblockItem:
    def __init__(self, **kwargs):
        self.enchantments = {}
        self.reforges = {}
        self.stats = {}
        self.modifiers = []
        self.nbt = {}

        for kw in kwargs:
            if kw == 'skyblock_item':
                continue
            elif kw in ('name', 'type', 'item'):
                setattr(self, kw, kwargs[kw])
            elif kw == 'rarity':
                setattr(self, kw, self.resolve_ref(kwargs[kw]))
            elif kw in ('enchantments', 'stats', 'reforges', 'modifiers'):
                getattr(self, f'get_{kw}')(kwargs[kw])
            elif kw == 'nbt':
                self.nbt = kwargs[kw]


        self.final_stats = self.calculate_stats()

    @classmethod
    def resolve_ref(cls, string: str):
        path = string.split('.')
        first = path[0].split(':')
        if len(first) == 1:
            first.insert(0, 'items')
        elif len(first) > 2:
            raise ValueError(f'Invalid reference {string!r}')

        try:
            with open(f'{"/".join(first)}.json') as f:
                data = json.load(f)
                for name in path[1:]:
                    data = data[name]
                return data
        except (FileNotFoundError, KeyError):
            return None

    def get_enchantments(self, dct):
        for k, v in dct.items():
            name = k
            if (description := self.resolve_ref(v[0])) is None:
                description = v[0]
            level = v[1]
            if len(v) == 2:
                vanilla = None
            else:
                vanilla = v[2]
            self.enchantments[name] = (description, level, vanilla)

    def get_stats(self, dct, method='assign'):
        stats = {self.resolve_ref(k)[0]: v for k, v in dct.items()}
        if method == 'assign':
            self.stats = stats
        elif method == 'return':
            return stats
        else:
            raise TypeError('Invalid result option')

    def get_reforges(self, lst):
        for e in lst:
            if isinstance(e, str):
                reforge = self.resolve_ref(e)
                if reforge is None:
                    raise NameError(e)
            else:
                reforge = e

            name = reforge['name']
            del reforge['name']
            stats = self.get_stats(reforge, 'return')
            self.reforges[name] = stats
    
    def get_modifiers(self, dct):
        for k in dct:
            self.modifiers.append({
                'AttributeName': k,
                'Name': k,
                **{k.title(): v for k, v in dct[k].items()},
                'UUID': [random.randint(0, 1000000) for _ in range(4)]
            })

    def calculate_stats(self):
        stats = {}
        for stat, quantifier in self.stats.items():
            if quantifier.endswith('%'):
                percent = True
                value = int(quantifier[:-1])
            else:
                percent = False
                value = int(quantifier)

            stats[stat] = [value, percent]

        for ref_stats in self.reforges.values():
            for stat, quantifier in ref_stats.items():
                if stat in stats:
                    if stats[stat][1] != quantifier.endswith('%'):
                        raise TypeError(
                            'Invalid reforge stat value '
                            f'{quantifier!r} for stat {stat!r}'
                        )
                    if stats[stat][1]:
                        stats[stat][0] += int(quantifier[:-1])
                    else:
                        stats[stat][0] += int(quantifier)
                else:
                    if quantifier.endswith('%'):
                        percent = True
                        value = int(quantifier[:-1])
                    else:
                        percent = False
                        value = int(quantifier)
                    stats[stat] = value, percent

        return stats
    
    def format_colors(self, string, default_color='gray'):
        result = []
        format_regex = re.compile(r'(:)([0-9a-f])\{(.*?)\}')
        splitted = format_regex.split(string)
        is_seq = False
        text = {'italic': False}
        for s in splitted:
            if s == ':' and not is_seq:
                is_seq = True
            elif re.compile(r'[0-9a-f]').fullmatch(s) and is_seq:
                text['color'] = COLOR_VALUES[s]
            else:
                text['text'] = s
                if not is_seq:
                    text['color'] = default_color
                result.append(text.copy())
                text.clear()
                is_seq = False
        return json.dumps(result)

    def give_cmd(self, args):
        result = '/give '
        if (target := args.target) is None:
            target = '@p'
        result += f'{target} {self.item}'
        enchantments = []
        display_enchantments = []
        name = {
            'text': f'{" ".join(self.reforges)} {self.name}',
            'color': COLOR_VALUES[self.rarity[1]],
            'italic': False
        }
        lore = []

        for stat in self.final_stats:
            quantifier = str(self.final_stats[stat][0])
            if not quantifier.startswith('-'):
                quantifier = f'+{quantifier}'
            if self.final_stats[stat][1]:
                quantifier += '%'
            line = [{'text': f'{stat}: ', 'color': 'gray', 'italic': False},
                    {'text': quantifier, 'color': 'red', 'italic': False}]
            for reforge, ref_stats in self.reforges.items():
                if stat in ref_stats:
                    line.append({
                        'text': f' ({reforge} {ref_stats[stat]})',
                        'color': 'dark_gray',
                        'italic': False
                    })
            lore.append(json.dumps(line))
        lore.append('[{"text": ""}]')

        for ench, (desc, lvl, vanilla) in self.enchantments.items():
            if vanilla is not None:
                enchantments.append({'id': vanilla, 'lvl': lvl})
            display_enchantments.append((ench, lvl, desc))

        if len(display_enchantments) > 4:
            line = ''
            for i, (ench, lvl, _) in enumerate(display_enchantments):
                line += f'{ench} {int_to_roman(lvl)}, '
                if len(line) > 42 or i == len(display_enchantments) - 1:
                    lore.append(json.dumps({
                        'text': line,
                        'color': 'blue',
                        'italic': False
                    }))
                    line = ''
            lore.append('[{"text": ""}]')
        else:
            for ench, lvl, desc in display_enchantments:
                lore.append(json.dumps({
                    'text': f'{ench} {int_to_roman(lvl)}',
                    'color': 'blue',
                    'italic': False
                }))
                lore.append(self.format_colors(desc))
                lore.append('[{"text": ""}]')
        
        lore.append(json.dumps({
            'text': f'{self.rarity[0]} {self.type}',
            'color': COLOR_VALUES[self.rarity[1]],
            'bold': True,
            'italic': False
        }))

        modifiers = []

        for modifier in self.modifiers:
            mod = []
            for k, v in modifier.items():
                if k == 'UUID':
                    mod.append(f'UUID:[I;{",".join((str(i) for i in v))}]')
                else:
                    mod.append(f'{k}:{json.dumps(v)}')

            modifiers.append(f'{{{",".join(mod)}}}')

        result += f'{{display:{{Name:{json.dumps(name)!r},'
        result += f'Lore:{lore}}},Unbreakable:true,HideFlags:63,'
        result += f'Enchantments:{json.dumps(enchantments)},AttributeModifiers:[{",".join(modifiers)}],'
        result += ','.join((f'{k}:{v!r}' for k, v in self.nbt.items())) + '}'
        return result


def decode_skyblock(dct):
    if 'skyblock_item' in dct:
        return SkyblockItem(**dct)
    return dct


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        'filename', help='the name of the JSON file that contains the item'
    )
    parser.add_argument(
        '--target', '-t', help='the target of the give command (default @p)'
    )
    parser.add_argument(
        '--output', '-o', help='the output stream of the '
                               'program (default stdout)'
    )
    args = parser.parse_args()
    return args


def get_data(args):
    with open(args.filename) as f:
        try:
            return json.load(f, object_hook=decode_skyblock)
        except json.JSONDecodeError:
            return None


def send_to_output(args, cmd):
    output = args.output
    if output is None:
        print(cmd)


def main():
    args = parse_args()
    item = get_data(args)
    if not isinstance(item, SkyblockItem):
        raise TypeError('Not a Skyblock item formatted file')
    cmd = item.give_cmd(args)
    send_to_output(args, cmd)


if __name__ == '__main__':
    main()
