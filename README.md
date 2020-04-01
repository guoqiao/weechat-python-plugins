# WeeChat Python Plugins

WeeChat Python Plugins Collection and Utils based on argparse module.

## usage

    cd ~/.weechat/
    git clone git@github.com:guoqiao/weechat-python-scripts.git python

To enable autoload for a plugin:

    cd autoload/
    ln -s ../xx.py .

Then in core buffer `weechat`:

    /python reload

show help for a plugin:

    /help xx
    /xx -h
    /xx --help
