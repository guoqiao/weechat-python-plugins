#!/usr/bin/env python3
import re
from os.path import basename
import weechat

WEECHAT_PLUGIN_NAME = basename(__file__).rsplit('.', maxsplit=1)[0]
WEECHAT_PLUGIN_DESCRIPTION = "watch sf id and print portal url"
WEECHAT_PLUGIN_AUTHOR = "guoqiao <guoqiao@gmail.com>"
WEECHAT_PLUGIN_VERSION = "20200408"
WEECHAT_PLUGIN_LICENSE = "GPL3"

# sf id is a 6-digit number starts with 2, e.g: 272160
SF_ID_RE = re.compile(r'\D0{0,2}(2\d{5})\b')


def main():
    weechat.register(
        WEECHAT_PLUGIN_NAME,
        WEECHAT_PLUGIN_AUTHOR,
        WEECHAT_PLUGIN_VERSION,
        WEECHAT_PLUGIN_LICENSE,
        WEECHAT_PLUGIN_DESCRIPTION,
        '',  # shutdown_function name
        '',  # charset, defaults to UTF-8 if blank
    )
    weechat.hook_line(
        'formatted',  # buffer_type: formatted|free|*
        '*',  # buffer_name, any
        'irc_privmsg',  # filter tags on line, ',' for OR, '+' for AND
        'on_line',  # callback name
        '',  # callback data
    )


def on_line(data, line):
    """ callback on a message line.

    the line object:
    {
        "tags": "irc_privmsg,notify_message,prefix_nick_lightcyan,nick_bs-pd-bot,host_bs-pd-bot@bs-pd-bot.bootstack.canonical.com,log1",
        "prefix": "\u0019F10\u0019F14bs-pd-bot",
        "displayed": "1",
        "message": "P0LYK43 |_ CHECK_NRPE: Socket timeout after 15 seconds.",
        "buffer_type": "formatted",
        "str_time": "\u00190204\u001903-\u00190206\u001903 \u00190200\u001903:\u00190225\u001903:\u00190229\u001928Z",
        "buffer_name": "irc.canonical.#is-bootstack-pd",
        "date": "1586132729",
        "tags_count": "6",
        "date_printed": "1586132729",
        "notify_level": "1",
        "buffer": "0x56479e5df1b0",
        "highlight": "0",
        "y": "-1"
    }
    """
    message = line['message']
    url_base = 'https://portal.admin.canonical.com/bootstack/cases'
    if url_base not in message:
        for sfid in SF_ID_RE.findall(message):
            url = '{}/{}'.format(url_base, sfid)
            weechat.prnt(line['buffer'], url)
    return weechat.WEECHAT_RC_OK


if __name__ == "__main__":
    main()
