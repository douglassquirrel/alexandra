#! /usr/bin/python

from alexandra import Alexandra
from time import sleep

def do_tick(tick, alex):
    sleep(alex.config['tick_seconds'])
    alex.pubsub.publish('tick', tick + 1)

alex = Alexandra()
tick_queue = alex.pubsub.subscribe('tick')
do_tick(0, alex)
alex.pubsub.consume_queue(tick_queue, lambda t: do_tick(t, alex))
