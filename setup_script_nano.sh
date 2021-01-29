#!/bin/bash

# Adding autocomplete lines to bashrc
echo "Setting up bash"
echo 'bind '"\e[A": history-search-backward'' >> ~/.bashrc 
echo 'bind '"\e[B": history-search-forward'' >> ~/.bashrc 
echo 'alias rm='rm -i'' >> ~/.bashrc 
echo 'alias cl='clear'' >> ~/.bashrc 
echo 'alias lo='logout'' >> ~/.bashrc 
source ~/.bashrc

# Set up  gedit editor
echo "Setting up gedit"
gsettings set org.gnome.gedit.preferences.editor editor-font 'Monospace 14'
gsettings set org.gnome.gedit.preferences.editor highlight-current-line true
gsettings set org.gnome.gedit.preferences.editor display-line-numbers true
gsettings set org.gnome.gedit.preferences.editor bracket-matching true
gsettings set org.gnome.gedit.preferences.editor insert-spaces true
gsettings set org.gnome.gedit.preferences.editor tabs-size uint32 4
gsettings set org.gnome.gedit.preferences.editor auto-indent true
gsettings set org.gnome.gedit.preferences.editor display-overview-map true
gsettings set org.gnome.gedit.preferences.editor scheme 'oblivion'

# pip commands for edgepipes
pip install flask
pip install flask-socketio
pip install pyvis

# setup git
echo "Setting up git"
git remote set-url origin https://github.com/ppi-ai/edgepipes.git
git pull
git checkout demo
git config user.name craston
git config user.email nieves.crasto@assaabloy.com

#Change keyboard layout
sudo dpkg-reconfigure keyboard-configuration
