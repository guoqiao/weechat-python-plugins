#!/usr/bin/env python3

import re
import json
from os.path import basename

import weechat

DESC = "auto snooze pagerduty alerts"

NAME = basename(__file__).rsplit('.', maxsplit=1)[0]

ACTIONS = ('TRIGGERED', 'UNACKNOWLEDGED', 'ASSIGNED', 'ESCALATED')
IRC_SERVER_NAME = 'canonical'
IRC_CHANNEL_NAME = '#is-bootstack-pd'
BUFFER_IS_BOOTSTACK_PD = 'irc.{}.{}'.format(IRC_SERVER_NAME, IRC_CHANNEL_NAME)

TRIGGERED_IDS = set()


def seconds(n):
    return n * 1000


def minutes(n):
    return n * 1000 * 60


def get_username():
    return weechat.config_string(weechat.config_get("irc.server.{}.username".format(IRC_SERVER_NAME)))


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


def on_bs_pd_bot(data, line):
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
    weechat.prnt('', pretty_json(line))
    message = de_color(line['message'])
    str_buf_ptr = line['buffer']
    words = message.split(maxsplit=2)
    if len(words) == 3:
        alert_id, action, content = words
        if MODE.is_mine(content):
            weechat.prnt('', message)
            if action in ACTIONS:  # turn into TRIGGERED status
                TRIGGERED_IDS.add(alert_id)
                weechat.prnt(str_buf_ptr, 'add {}'.format(alert_id))
            else:
                TRIGGERED_IDS.discard(alert_id)
                weechat.prnt(str_buf_ptr, 'discard {}'.format(alert_id))
            weechat.prnt(str_buf_ptr, 'current: {}'.format(TRIGGERED_IDS))


def on_timer(data, remaining_calls):
    str_buf_ptr = weechat.buffer_search('==', BUFFER_IS_BOOTSTACK_PD)
    if TRIGGERED_IDS:
        cmd = 'z 4 {}'.format(' '.join(TRIGGERED_IDS))
        MODE.command(str_buf_ptr, cmd)  # ack mine quiet, TODO: zmq 1
        TRIGGERED_IDS.clear()
        weechat.prnt(str_buf_ptr, 'queue cleared')
    else:
        weechat.prnt(str_buf_ptr, 'timer: queue is empty')
    return weechat.WEECHAT_RC_OK


def main():
    weechat.register(NAME, "guoqiao", "20200406", "MIT", DESC, "", "")
    weechat.hook_timer(
        MODE.interval,  # interval in ms
        1,  # align_second
        0,  # max_calls, 0: no limit
        'on_timer',  # callback_name,
        '',  # callback_data,
    )
    weechat.hook_line(
        'formatted',  # buffer_type: formatted|free|*
        BUFFER_IS_BOOTSTACK_PD,  # buffer_name
        'irc_privmsg,nick_bs-pd-bot',  # filter tags on line
        'on_bs_pd_bot',  # callback name
        '',  # callback data
    )


if __name__ == "__main__":
    main()
