#!/usr/bin/env python3

import re
import json
from os.path import basename

import weechat

WEECHAT_PLUGIN_NAME = basename(__file__).rsplit('.', maxsplit=1)[0]
WEECHAT_PLUGIN_DESCRIPTION = "auto snooze pagerduty alerts"
WEECHAT_PLUGIN_AUTHOR = "guoqiao <guoqiao@gmail.com>"
WEECHAT_PLUGIN_VERSION = "20200408"
WEECHAT_PLUGIN_LICENSE = "GPL3"
WEECHAT_PLUGIN_DEBUG = False

IRC_SERVER = 'canonical'
IRC_CHANNEL = '#is-bootstack-pd'
IRC_NICK = 'bs-pd-bot'

ACTIONS = ('TRIGGERED', 'UNACKNOWLEDGED', 'ASSIGNED', 'ESCALATED')
TRIGGERED_IDS = set()


def info(message, buffer=''):
    message = '{}: {}'.format(WEECHAT_PLUGIN_NAME, message)
    weechat.prnt(buffer, message)


def debug(message, buffer=''):
    if WEECHAT_PLUGIN_DEBUG:
        info(message, buffer=buffer)


def seconds(n):
    return n * 1000


def minutes(n):
    return n * 1000 * 60


def get_username():
    return weechat.config_string(weechat.config_get("irc.server.{}.username".format(IRC_SERVER)))


class DebugMode:
    command = weechat.prnt
    interval = seconds(10)

    def is_mine(self, content):
        return True


class ProdMode:
    command = weechat.command
    interval = minutes(1)

    def is_mine(self, content):
        return get_username() in content


MODE = ProdMode()


def pretty_json(data):
    return json.dumps(data, indent=4)


def de_color(text):
    return weechat.string_remove_color(text, '')


def on_line(data, line):
    """
    target line example:
    PN6JZ6M *UNACKNOWLEDGED* CRITICAL: 'bootstack-libertyglobal-schiphol-openstack-service-checks-0-contrail_analytics_alarms' on 'bootstack-libertyglobal-schiphol-openstack-service-checks-0' @ andrea, guoqiao [BootStack Alerts - LibertyGlobal Schiphol] 

    please note that the actions are surrounded by color code.

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
    debug(pretty_json(line))
    message = de_color(line['message'])
    words = message.split(maxsplit=2)
    if len(words) == 3:
        alert_id, action, content = words
        if MODE.is_mine(content):
            debug(message)
            if action in ACTIONS:  # turn into TRIGGERED status
                TRIGGERED_IDS.add(alert_id)
                info('add {}'.format(alert_id))
            else:
                TRIGGERED_IDS.discard(alert_id)
                info('discard {}'.format(alert_id))
            info('current: {}'.format(TRIGGERED_IDS))


def on_timer(data, remaining_calls):
    buffer_name = data
    str_buffer_ptr = weechat.buffer_search('==', buffer_name)
    if TRIGGERED_IDS:
        cmd = 'zm 2'
        MODE.command(str_buffer_ptr, cmd)
        TRIGGERED_IDS.clear()
        info('queue cleared')
    else:
        info('queue empty')
    return weechat.WEECHAT_RC_OK


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
    buffer_name = 'irc.{}.{}'.format(IRC_SERVER, IRC_CHANNEL)
    weechat.hook_timer(
        seconds(67),
        1,  # align_second
        0,  # max_calls, 0: no limit
        'on_timer',  # callback_name,
        buffer_name,  # callback_data, must be str
    )
    weechat.hook_line(
        'formatted',  # buffer_type: formatted|free|*
        buffer_name,  # buffer_name
        'nick_{}'.format(IRC_NICK),  # filter tags on line
        'on_line',  # callback name
        '',  # callback data
    )


if __name__ == "__main__":
    main()
