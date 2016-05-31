#! /bin/bash

while true; do
    git pull origin master
    python3 bot.py
    sleep 1
done
