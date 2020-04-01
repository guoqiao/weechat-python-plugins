#!/usr/bin/env python3
import sys
import shlex
import argparse
import weechat

NAME = 'lp'
DESC = 'print url for launchpad bug'
AUTHOR = 'guoqiao'
VERSION = '20200401'
LICENCE = 'MIT'

VERBOSE = False


class WeeChatPlugin(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        weechat.register(NAME, AUTHOR, VERSION, LICENCE, DESC, "", "")
        if not kwargs.get('formatter_class'):
            kwargs['formatter_class'] = argparse.ArgumentDefaultsHelpFormatter
        super().__init__(*args, **kwargs)

    def prnt(self, message, buffer=''):
        if message:
            weechat.prnt(buffer, '{}'.format(message))

    def verbose(self, message):
        if VERBOSE:
            self.prnt(message)

    def _print_message(self, message, file=None):
        """print message to core buffer.

        Help to avoid exception:

            AttributeError: module 'weechatOutputs' has no attribute 'flush'

        """
        self.prnt(message)

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

    def set_option(self, option, value, save=True):
        cmd = '/set {} {}'.format(option, value)
        self.verbose(cmd)
        weechat.command('', cmd)
        if save:
            weechat.command('', '/save')

    def get_option(self, option):
        return weechat.config_get(option)

    def get_option_str(self, option):
        return weechat.config_string(self.get_option(option))


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
        cli = parser.parse_args(args=args)
        for id_ in cli.ids:
            url = 'https://launchpad.net/bugs/{}'.format(id_)
            parser.prnt(url, buffer=buffer)
        return weechat.WEECHAT_RC_OK
    except SystemExit as exc:
        # catch sys.exit from parse_args and return proper code for weechat
        return exc.code
    except Exception as exc:
        parser.prnt(exc)
        return weechat.WEECHAT_RC_ERROR
