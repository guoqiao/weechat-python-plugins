#!/usr/bin/env python3
import io
import sys
import shlex
import argparse
import weechat

NAME = 'qc'
DESC = 'Quick Config for WeeChat'

SERVER = 'canonical'
VERBOSE = False

OPTIONS = {
    'hl': 'weechat.look.highlight',
    'ch': 'irc.server.{}.autojoin'.format(SERVER),
}
weechat.register(NAME, "guoqiao", "20200331", "MIT", DESC, "", "")


def log(message, buffer=''):
    weechat.prnt(buffer, '{}: {}'.format(NAME, message))


if VERBOSE:
    def verbose(message):
        log(message)
else:
    def verbose(message):
        pass


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
    parser = argparse.ArgumentParser(
        prog=NAME,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=DESC,
    )

    parser.add_argument(
        '-o', '--option', choices=list(OPTIONS.keys()), default='hl',
        help='short name for option',
    )

    parser.add_argument(
        '-a', '--add', metavar='KW', nargs='+', default=[],
        help='add keyword to option value, can repeat',
    )

    parser.add_argument(
        '-r', '--rm', metavar='KW', nargs='+', default=[],
        help='rm keyword from option value, can repeat',
    )

    return parser


parser = build_parser()


def main(data, buffer, args):
    args = shlex.split(args)
    verbose(args)

    stdout = sys.stdout
    stderr = sys.stderr

    output = io.StringIO()
    sys.stdout = output
    sys.stderr = output
    try:
        cli = parser.parse_args(args=args)
    except SystemExit:
        log(output.getvalue())
        return weechat.WEECHAT_RC_ERROR
    finally:
        sys.stdout = stdout
        sys.stderr = stderr

    option = OPTIONS[cli.option]
    current_str = get_option_str(option)
    log('current: {} = {}'.format(option, current_str))

    current = set(current_str.split(','))
    add = set(cli.add)
    rm = set(cli.rm)
    final = (current | add) - rm

    if final != current:
        final_str = ','.join(sorted(final))
        log('final: {} = {}'.format(option, final_str))
        set_option(option, final_str)

    return weechat.WEECHAT_RC_OK


def hook_command(data, buffer, args):
    try:
        return main(data, buffer, args)
    except BaseException as exc:
        log(exc)
        return weechat.WEECHAT_RC_ERROR


weechat.hook_command(
    NAME,
    parser.description,
    '',  # usage, included in help
    parser.format_help(),
    '',  # complete template
    'hook_command',
    '',
)
