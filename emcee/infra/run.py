#! /usr/bin/python

HEARTBEAT_TIMEOUT = 5

from docstore import connect as docstore_connect
from json import load, dumps
from os import access, getcwd, listdir, X_OK
from os.path import abspath, isfile, join as pathjoin
from pubsub import connect as pubsub_connect
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

def heart_monitor(game_id, pubsub):
    heartbeat_queue = pubsub.subscribe('heartbeat')
    message = ''
    while message is not None:
        message = pubsub.get_message_block(queue=heartbeat_queue,
                                           timeout=HEARTBEAT_TIMEOUT)

game_id, docstore_url = argv[1], argv[2]
with open('game.json', 'r') as game_file:
    game_data = load(game_file)
docstore = docstore_connect(docstore_url + "/" + game_id)
docstore.put(dumps(game_data), '/game.json', 'application/json')
processes = start(game_data['components'], game_id)

pubsub = pubsub_connect('amqp://localhost', game_id)
pubsub.publish('game_state', 'running')
print 'Now running game %s' % (game_id,)
heart_monitor(game_id, pubsub)
print 'Game %s ending' % (game_id,)
map(lambda(p): p.kill(), processes)
