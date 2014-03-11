#!/bin/bash

PAUSE_SEC=1

trap 'killall' INT

killall() {
    trap '' INT TERM
    kill -TERM 0
    wait
}

echo "Starting library.py"
python library.py localhost 8080 config.json &
sleep $PAUSE_SEC

echo "Starting collider.py"
python collider.py &
sleep $PAUSE_SEC

echo "Starting umpire.py"
python umpire.py &
sleep $PAUSE_SEC

echo "Starting world.py"
python world.py &
sleep $PAUSE_SEC

echo "Starting client.py"
python client.py &
sleep $PAUSE_SEC

echo "Starting walls.py"
python walls.py &
sleep $PAUSE_SEC

echo "Starting player.py"
python player.py &
sleep $PAUSE_SEC

cat