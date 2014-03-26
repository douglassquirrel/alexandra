#! /usr/bin/python

from alexandra import Alexandra
from time import sleep

alex = Alexandra()
counter = 0
while True:
    alex.publish('tick', counter)
    sleep(alex.config['tick_seconds'])
