#! /usr/bin/python

HEARTBEAT_TIMEOUT = 5

from json import load
from os import access, getcwd, listdir, X_OK
from os.path import abspath, isfile, join as pathjoin
from pubsub import connect
from subprocess import Popen
from sys import argv

def flatten(list_of_lists):
    return sum(list_of_lists, [])

def abspath_listdir(d):
    return [abspath(pathjoin(d, name)) for name in listdir(d)]

def is_executable_file(f):
    return isfile(f) and access(f, X_OK)

def start_component(game_id, component_name, index):
    component_dir = abspath(pathjoin('components', component_name))
    executable = filter(is_executable_file, abspath_listdir(component_dir))[0]
    process = Popen([executable, abspath(getcwd()), game_id, str(index)],
                    cwd=component_dir)
    return process

def start_component_group(game_id, component_name, n):
    return map(lambda(i): start_component(game_id, component_name, i), range(n))

def start(components, game_id):
    return flatten(map(lambda(c): start_component_group(game_id, *c),
                       components.items()))

def heart_monitor(game_id):
    connection = connect('amqp://localhost', game_id)
    heartbeat_queue = connection.subscribe('heartbeat')
    message = ''
    while message is not None:
        message = connection.get_message_block(queue=heartbeat_queue,
                                               timeout=HEARTBEAT_TIMEOUT)

game_id = argv[1]
with open('game.json', 'r') as game_file:
    game_data = load(game_file)
processes = start(game_data['components'], game_id)

print 'Now running game %s' % (game_id,)
heart_monitor(game_id)
print 'Game %s ending' % (game_id,)
map(lambda(p): p.kill(), processes)
