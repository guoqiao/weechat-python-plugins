#!/usr/bin/env python3
from os.path import basename
from weechat_plugin import WeeChatPlugin, weechat_plugin_return_code

DESC = 'quick config for weechat'

# get plugin name from file basename and remove extension
NAME = basename(__file__).rsplit('.', maxsplit=1)[0]
SERVER = 'canonical'
OPTION_ALIASES = {
    'hl': 'weechat.look.highlight',
    'aj': 'irc.server.{}.autojoin'.format(SERVER),
}
OPTION_ALIASES_HELP = ', '.join('{} -> {}'.format(k, v) for k, v in OPTION_ALIASES.items())

OPTION_HIGHLIGHT = 'weechat.look.highlight'
OPTION_SERVER_NICKS = 'irc.server.{server}.nicks'
OPTION_SERVER_AUTOJOIN = 'irc.server.{server}.autojoin'


parser = WeeChatPlugin(
    prog=NAME,
    description=DESC,
)

parser.add_argument(
    '-o', '--option', default=OPTION_HIGHLIGHT,
    help='target option',
)

parser.add_argument(
    '-S', '--server', default=SERVER,
    help='irc server to config',
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
    '-a', '--add', metavar='KW', nargs='+', default=[],
    help='add keyword to option value, can repeat',
)

parser.add_argument(
    '-r', '--remove', metavar='KW', nargs='+', default=[],
    help='rm keyword from option value, can repeat',
)

parser.add_argument(
    '-s', '--set', metavar='VALUE',
    help='set option to this value',
)

parser.hook_command('main')


@weechat_plugin_return_code
def main(data, buffer, args):
    cli = parser.parse_args(args=args, buffer=buffer)
    server = cli.server

    if cli.highlight:
        option = OPTION_HIGHLIGHT
    elif cli.autojoin:
        option = OPTION_SERVER_AUTOJOIN.format(server=server)
    else:
        option = cli.option

    current = parser.get_option_str(option)
    parser.prnt('current: {} = "{}"'.format(option, current))

    expected = None

    if cli.set is not None:
        expected = cli.set
    else:
        current_set = set(current.split(','))
        add_set = set(cli.add)
        remove_set = set(cli.remove)
        expected_set = (current_set | add_set) - remove_set
        expected = ','.join(sorted(expected_set))
        if buffer and ('autojoin' in option):
            for channel in add_set:
                # /join only works in server, channel or private
                parser.cmd('/join {}'.format(channel))

    if expected is not None and expected != current:
        parser.prnt('expected: {} = "{}"'.format(option, expected))
        parser.set_option(option, expected)
