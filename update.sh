#!/usr/bin/env bash

sudo pkill -f jaruchinho.py

git pull

sudo nohup python jaruchinho.py & disown