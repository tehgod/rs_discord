#!/bin/bash
git pull
docker stop poggies_bot
docker container rm poggies_bot
docker build -t discord_poggies_bot .
docker run -d --name poggies_bot --restart always -v /etc/localtime:/etc/localtime discord_poggies_bot