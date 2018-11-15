#!/usr/bin/env bash

#start a constellation instance

echo "[*] Killing all running Constellation Node(s)"
killall constellation-node

echo "[*] Starting Constellation Node"
nohup $constellation_binary $constellation_config_file 2>> $constellation_log_file &
