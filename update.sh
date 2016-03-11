#!/usr/bin/env bash

pkill -f jaruchinho.py

git pull

sudo nohup python jaruchinho.py &

disown