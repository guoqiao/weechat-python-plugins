#!/usr/bin/env python3
from os.path import basename
from weechat_plugin import WeeChatPlugin, weechat_plugin_return_code

DESC = 'quick config for weechat'

# get plugin name from file basename and remove extension
NAME = basename(__file__).rsplit('.', maxsplit=1)[0]
SERVER = 'canonical'

OPTION_HIGHLIGHT = 'weechat.look.highlight'
OPTION_SERVER_NICKS = 'irc.server.{server}.nicks'
OPTION_SERVER_AUTOJOIN = 'irc.server.{server}.autojoin'


parser = WeeChatPlugin(
    prog=NAME,
    description=DESC,
)

parser.add_argument(
    '-s', '--server', default=SERVER,
    help='irc server to config',
)

parser.add_argument(
    '-o', '--option', default=OPTION_HIGHLIGHT,
    help='target option',
)

parser.add_argument(
    '--hl', dest='highlight', action='store_true',
    help='shortcut for --option {}'.format(OPTION_HIGHLIGHT),
)

parser.add_argument(
    '--aj', dest='autojoin', action='store_true',
    help='shortcut for --option {}'.format(OPTION_SERVER_AUTOJOIN),
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
    parser.server = cli.server

    if cli.highlight:
        option = OPTION_HIGHLIGHT
    elif cli.autojoin:
        option = OPTION_SERVER_AUTOJOIN.format(server=cli.server)
    else:
        option = cli.option

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
