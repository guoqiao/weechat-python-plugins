#!/usr/bin/env python3
import shlex
import argparse
import weechat


class WeeChatPlugin(argparse.ArgumentParser):

    def __init__(
            self,
            *args,
            author='guoqiao',
            version='0.1',
            license='MIT',
            **kwargs):

        if not kwargs.get('formatter_class'):
            kwargs['formatter_class'] = argparse.ArgumentDefaultsHelpFormatter

        super().__init__(*args, **kwargs)

        self.buffer = ''  # core buffer by default

        # add verbose option for all
        self.add_argument(
            '-v', '--verbose', action='store_true',
            help='Be verbose',
        )

        weechat.register(
            self.prog,
            author,
            version,
            license,
            self.description,
            "",  # shutdown_function name, called when script is unloaded
            "",  # charset, default to UTF-8
        )

    def prnt(self, message):
        if message:
            weechat.prnt(self.buffer, '{}'.format(message))

    def verbose(self, message):
        """print message when verbose is on"""
        if self._verbose:
            self.prnt(message)

    def _print_message(self, message, file=None):
        """print message to core buffer.

        Help to avoid exception:

            AttributeError: module 'weechatOutputs' has no attribute 'flush'

        """
        self.prnt(message)

    def exit(self, status=0, message=None):
        """convert exit code"""
        if status == 0:
            status = weechat.WEECHAT_RC_OK
        else:
            status = weechat.WEECHAT_RC_ERROR
        super().exit(status=status, message=message)

    def parse_args(self, args=None, namespace=None, buffer=''):
        """convert str args to argv list"""
        self.buffer = buffer
        if args and isinstance(args, str):
            # --option "I have space" --> ["option", "I have space"]
            args = shlex.split(args)
        cli = super().parse_args(args=args, namespace=namespace)
        self._verbose = cli.verbose
        return cli

    def hook_command(self, hook_func_name):
        weechat.hook_command(
            self.prog,
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


def return_on_exit(func):
    def hook_command(data, buffer, args):
        try:
            # if func doesn't return anything, return ok for it
            return func(data, buffer, args) or weechat.WEECHAT_RC_OK
        except SystemExit as exc:
            # catch sys.exit from parse_args and return proper code for weechat
            return exc.code
        except Exception as exc:
            # catch any other exception from python and print error to buffer
            weechat.prnt(buffer, str(exc))
            return weechat.WEECHAT_RC_ERROR
    return hook_command
