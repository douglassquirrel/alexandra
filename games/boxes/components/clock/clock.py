#! /usr/bin/python

from alexandra import Alexandra
from time import sleep

def do_tick(tick, alex):
    sleep(alex.config['tick_seconds'])
    alex.publish('tick', tick + 1)

alex = Alexandra()
alex.consume('tick', do_tick, initial=lambda: do_tick(0, alex))
