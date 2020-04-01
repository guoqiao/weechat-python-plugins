# WeeChat Python Plugins

WeeChat Python Scripts Utils and Collection

## usage

    cd ~/.weechat/
    git clone git@github.com:guoqiao/weechat-python-scripts.git python

To enable autoload for a plugin:

    ln -s ../xx.py .

Then in core buffer `weechat`:

    /python reload

show help for a plugin:

    /help xx
    /xx -h
    /xx --help
