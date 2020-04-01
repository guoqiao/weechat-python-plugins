#!/usr/bin/env python3
import io
import sys
import shlex
import argparse
import weechat

NAME = 'lp'
DESC = 'print url for launchpad bug'

VERBOSE = False

weechat.register(NAME, "guoqiao", "20200401", "MIT", DESC, "", "")


def log(message, buffer=''):
    weechat.prnt(buffer, '{}: {}'.format(NAME, message))


if VERBOSE:
    def verbose(message):
        log(message)
else:
    def verbose(message):
        pass


class WeeChatArgumentParser(argparse.ArgumentParser):

    def _print_message(self, message, file=None):
        """print message to core buffer.

        Help to avoid exception:

            AttributeError: module 'weechatOutputs' has no attribute 'flush'

        """
        if message:
            log(message)

    def exit(self, status=0, message=None):
        """convert exit code"""
        if message:
            self._print_message(message)
        if status == 0:
            code = weechat.WEECHAT_RC_OK
        else:
            code = weechat.WEECHAT_RC_ERROR
        sys.exit(code)

    def parse_args(self, args=None, namespace=None):
        """convert str args to argv list"""
        if args and isinstance(args, str):
            # --option "I have space" --> ["option", "I have space"]
            args = shlex.split(args)
        return super().parse_args(args=args, namespace=namespace)

    def hook_command(self, hook_func_name):
        weechat.hook_command(
            NAME,
            self.description,
            '',  # usage, included in help, no need to repeat
            self.format_help(),
            '',  # complete template
            hook_func_name,
            '',
        )


def set_option(option, value, save=True):
    cmd = '/set {} {}'.format(option, value)
    verbose(cmd)
    weechat.command('', cmd)
    if save:
        weechat.command('', '/save')


def get_option(option):
    return weechat.config_get(option)


def get_option_str(option):
    return weechat.config_string(get_option(option))


def build_parser():
    parser = WeeChatArgumentParser(
        prog=NAME,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=DESC,
    )

    parser.add_argument(
        'ids', metavar='LP_BUG_ID', nargs='+',
        help='launchpad bug id, can repeat',
    )

    return parser


parser = build_parser()
parser.hook_command('hook_command')


def hook_command(data, buffer, args):
    try:
        return main(data, buffer, args)
    except SystemExit as exc:
        # catch sys.exit and return proper code for weechat
        return exc.code
    except Exception as exc:
        log(exc)
        return weechat.WEECHAT_RC_ERROR


def main(data, buffer, args):
    cli = parser.parse_args(args=args)
    for id_ in cli.ids:
        url = 'https://launchpad.net/bugs/{}'.format(id_)
        log(url, buffer=buffer)
    return weechat.WEECHAT_RC_OK
