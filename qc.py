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


parser = WeeChatPlugin(
    prog=NAME,
    description=DESC,
)

parser.add_argument(
    '-o', '--option', default='hl',
    help='target option, support alias: {}'.format(OPTION_ALIASES_HELP),
)

parser.add_argument(
    '-a', '--add', metavar='KW', nargs='+', default=[],
    help='add keyword to option value, can repeat',
)

parser.add_argument(
    '-r', '--rm', metavar='KW', nargs='+', default=[],
    help='rm keyword from option value, can repeat',
)

parser.hook_command('main')


@weechat_plugin_return_code
def main(data, buffer, args):
    cli = parser.parse_args(args=args, buffer=buffer)
    option = OPTION_ALIASES.get(cli.option, cli.option)
    current_str = parser.get_option_str(option)
    parser.prnt('current: {} = {}'.format(option, current_str))

    current = set(current_str.split(','))
    add = set(cli.add)
    rm = set(cli.rm)
    final = (current | add) - rm

    if final != current:
        final_str = ','.join(sorted(final))
        parser.prnt('final: {} = {}'.format(option, final_str))
        parser.set_option(option, final_str)
