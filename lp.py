#!/usr/bin/env python3
import weechat
from weechat_plugin import WeeChatPlugin

NAME = 'lp'
DESC = 'print url for launchpad bug in buffer'


parser = WeeChatPlugin(
    prog=NAME,
    description=DESC,
)

parser.add_argument(
    'ids', metavar='LP_BUG_ID', nargs='+',
    help='launchpad bug id, can repeat',
)

parser.hook_command('main')


def main(data, buffer, args):
    try:
        cli = parser.parse_args(args=args, buffer=buffer)
        for id_ in cli.ids:
            url = 'https://launchpad.net/bugs/{}'.format(id_)
            parser.prnt(url)
        return weechat.WEECHAT_RC_OK
    except SystemExit as exc:
        # catch sys.exit from parse_args and return proper code for weechat
        return exc.code
    except Exception as exc:
        parser.prnt(exc)
        return weechat.WEECHAT_RC_ERROR
