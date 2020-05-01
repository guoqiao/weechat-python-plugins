#!/usr/bin/env python3
from os.path import basename
from weechat_plugin import WeeChatPlugin, weechat_plugin_return_code

DESC = 'highlight config for weechat'

# get plugin name from file basename and remove extension
NAME = basename(__file__).rsplit('.', maxsplit=1)[0]

OPTION_HIGHLIGHT = 'weechat.look.highlight'


parser = WeeChatPlugin(
    prog=NAME,
    description=DESC,
)

parser.add_argument(
    '-a', '--add', action='store_true',
    help='add items to option value',
)

parser.add_argument(
    '-r', '--remove', action='store_true',
    help='remove items from option value',
)

parser.add_argument(
    'items', metavar='ITEM', nargs='*', default=[],
    help='item for this option, can repeat',
)


parser.hook_command('main')


@weechat_plugin_return_code
def main(data, buffer, args):
    cli = parser.parse_args(args=args, buffer=buffer)
    option = OPTION_HIGHLIGHT
    current = parser.get_option_str(option)
    parser.prnt('current: {} = "{}"'.format(option, current))

    current_set = set(current.split(','))
    items_set = set(cli.items)

    if cli.add:
        expected_set = current_set | items_set
    elif cli.remove:
        expected_set = current_set - items_set
    else:
        expected_set = current_set

    if current_set != expected_set:
        expected = ','.join(sorted(expected_set))
        parser.prnt('expected: {} = "{}"'.format(option, expected))
        parser.set_option(option, expected)
