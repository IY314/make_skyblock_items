from argparse import ArgumentParser
import json


class SkyblockItem:
    def __init__(self, **kwargs):
        self.enchantments = self.reforges = self.stats = {}

        for kw in kwargs:
            if kw == 'skyblock_item':
                continue
            elif kw in ('name', 'type', 'item'):
                setattr(self, kw, kwargs[kw])
            elif kw == 'rarity':
                setattr(self, kw, self.resolve_ref(kwargs[kw]))
            elif kw in ('enchantments', 'stats', 'reforges'):
                getattr(self, f'get_{kw}')(kwargs[kw])

        self.final_stats = self.calculate_stats()

    @classmethod
    def resolve_ref(cls, string):
        path = string.split('.')
        try:
            with open(f'items/{path[0]}.json') as f:
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

    def calculate_stats(self):
        stats = {}
        for stat, quantifier in self.stats.items():
            if quantifier.endswith('%'):
                percent = True
                value = int(quantifier[:-1])
            else:
                percent = False
                value = int(quantifier)

            stats[stat] = value, percent

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

    def give_cmd(self, args):
        result = '/give '
        if (target := args.target) is None:
            target = '@p'
        result += f'{target} {self.item}'
        enchantments = []
        display_enchantments = []
        name = {'text': ''}
        lore = []

        for stat in self.final_stats:
            quantifier = str(self.final_stats[stat][0])
            if self.final_stats[stat][1]:
                quantifier += '%'
            line = [{'text': f'{stat} ', 'color': 'gray'},
                    {'text': quantifier, 'color': 'red'}]
            for reforge, ref_stats in self.reforges.items():
                if stat in ref_stats:
                    line.append({
                        'text': f' ({reforge} {ref_stats[stat]})',
                        'color': 'dark_gray'
                    })
            lore.append(line)

        for ench, (desc, lvl, vanilla) in self.enchantments.items():
            if vanilla is not None:
                enchantments.append({'id': vanilla, 'lvl': lvl})
            display_enchantments.append((ench, desc))


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
        '--target', '-t', help='the target of the give command'
    )
    args = parser.parse_args()
    return args


def get_data(args):
    with open(args.filename) as f:
        try:
            return json.load(f, object_hook=decode_skyblock)
        except json.JSONDecodeError:
            return None


def main():
    args = parse_args()
    item = get_data(args)
    if not isinstance(item, SkyblockItem):
        raise TypeError('Not a Skyblock item formatted file')


if __name__ == '__main__':
    main()
