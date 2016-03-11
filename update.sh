#!/usr/bin/env bash

sudo pkill -SIGKILL -f jaruchinho.py

git pull

sudo python jaruchinho.py &> /dev/null & disown