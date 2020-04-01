#!/usr/bin/env python3
from weechat_plugin import WeeChatPlugin, return_on_exit

NAME = 'sf'
DESC = 'print bootstack portal url for salesforce case in buffer(only visible to you)'


parser = WeeChatPlugin(
    prog=NAME,
    description=DESC,
)

parser.add_argument(
    'ids', metavar='SF_CASE_ID', nargs='+',
    help='salesforce case id, can repeat',
)

parser.hook_command('main')


@return_on_exit
def main(data, buffer, args):
    cli = parser.parse_args(args=args, buffer=buffer)
    for id_ in cli.ids:
        url = 'https://portal.admin.canonical.com/bootstack/cases/{}'.format(id_)
        parser.prnt(url)
