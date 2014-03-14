#!/bin/bash

trap 'killall' INT

PAUSE_SEC=0.2

killall() {
    trap '' INT TERM
    kill -TERM 0
    wait
}

function run {
    echo "Starting $@"
    python $@ &
    sleep $PAUSE_SEC
}

COMMANDS=( "library.py" "collider.py" "umpire.py" "world.py" "client.py" \
           "walls.py" "player.py" )

for c in "${COMMANDS[@]}"
do
    run $c
done

cat