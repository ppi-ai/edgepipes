#!/bin/bash

# Adding autocomplete lines to bashrc
echo 'bind '"\e[A": history-search-backward'' >> ~/.bashrc 
echo 'bind '"\e[B": history-search-forward'' >> ~/.bashrc 
echo 'alias rm='rm -i'' >> ~/.bashrc 
echo 'alias cl='clear'' >> ~/.bashrc 
echo 'alias lo='logout'' >> ~/.bashrc 

# setup git
git remote set-url origin https://github.com/ppi-ai/edgepipes.git
git pull
git checkout demo
git config user.name craston
git config user.email nieves.crasto@assaabloy.com
