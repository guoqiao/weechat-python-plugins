#!/usr/bin/env python3

import re
import json
import weechat

ACTIONS = ('TRIGGERED', 'UNACKNOWLEDGED', 'ASSIGNED', 'ESCALATED')
IRC_SERVER_NAME = 'canonical'
BUFFER_IS_BOOTSTACK_PD = 'irc.{}.#is-bootstack-pd'.format(IRC_SERVER_NAME)

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
    """
    weechat.prnt('', pretty_json(line))
    message = de_color(line['message'])
    words = message.split(maxsplit=2)
    if len(words) == 3:
        alert_id, action, content = words
        if MODE.is_mine(content):
            weechat.prnt('', message)
            if action in ACTIONS:  # turn into TRIGGERED status
                TRIGGERED_IDS.add(alert_id)
                weechat.prnt('', 'add {}'.format(alert_id))
            else:
                TRIGGERED_IDS.discard(alert_id)
                weechat.prnt('', 'discard {}'.format(alert_id))
            weechat.prnt('', 'current queue: {}'.format(TRIGGERED_IDS))


def on_timer(data, remaining_calls):
    weechat.prnt('', 'timer triggered, current queue: {}'.format(TRIGGERED_IDS))
    if TRIGGERED_IDS:
        str_buf_ptr = weechat.buffer_search('==', BUFFER_IS_BOOTSTACK_PD)
        cmd = 'z 4 {}'.format(' '.join(TRIGGERED_IDS))
        MODE.command(str_buf_ptr, cmd)  # ack mine quiet, TODO: zmq 1
        TRIGGERED_IDS.clear()
        weechat.prnt('', 'queue cleared')
    return weechat.WEECHAT_RC_OK


def main():
    weechat.register("snooze", "guoqiao", "20200301", "MIT", "auto snooze pagerduty alerts", "", "")
    weechat.prnt("", "snooze.py loaded")
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
