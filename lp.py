#!/usr/bin/env python3
from weechat_plugin import WeeChatPlugin, weechat_plugin_return_code

NAME = 'lp'
DESC = 'print url for launchpad bug in buffer(only visible to you)'


parser = WeeChatPlugin(
    prog=NAME,
    description=DESC,
)

parser.add_argument(
    'ids', metavar='LP_BUG_ID', nargs='+',
    help='launchpad bug id, can repeat',
)

parser.hook_command('main')


@weechat_plugin_return_code
def main(data, buffer, args):
    cli = parser.parse_args(args=args, buffer=buffer)
    for id_ in cli.ids:
        url = 'https://launchpad.net/bugs/{}'.format(id_)
        parser.prnt(url)
