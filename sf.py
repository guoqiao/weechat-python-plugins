#!/usr/bin/env python3
import weechat
from weechat_plugin import WeeChatPlugin

NAME = 'sf'
DESC = 'print bootstack portal url for salesforce case in buffer'


parser = WeeChatPlugin(
    prog=NAME,
    description=DESC,
)

parser.add_argument(
    'ids', metavar='SF_CASE_ID', nargs='+',
    help='salesforce case id, can repeat',
)

parser.hook_command('main')


def main(data, buffer, args):
    try:
        cli = parser.parse_args(args=args, buffer=buffer)
        for id_ in cli.ids:
            url = 'https://portal.admin.canonical.com/bootstack/cases/{}'.format(id_)
            parser.prnt(url)
        return weechat.WEECHAT_RC_OK
    except SystemExit as exc:
        # catch sys.exit from parse_args and return proper code for weechat
        return exc.code
    except Exception as exc:
        parser.prnt(exc)
        return weechat.WEECHAT_RC_ERROR
