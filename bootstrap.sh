#!/bin/bash

set -xue

CODENAME=$(cat /etc/lsb-release | grep DISTRIB_CODENAME | cut -d= -f2)
echo "deb https://weechat.org/ubuntu $CODENAME main" | sudo tee /etc/apt/sources.list.d/weechat.list
sudo apt-key adv --keyserver hkps://keys.openpgp.org --recv-keys 11E9DE8848F2B65222AA75B8D1820DB22A11534E
sudo apt-get update

sudo apt-get install --yes dirmngr gpg-agent apt-transport-https
sudo apt-get install --yes weechat-curses weechat-plugins weechat-python weechat-perl
sudo apt-get autoremove --yes

# dev version
# sudo apt-get install weechat-devel-curses weechat-devel-plugins weechat-devel-python weechat-devel-perl

sudo python3 -m pip install -r requirements.txt
