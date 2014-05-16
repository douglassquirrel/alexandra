#! /usr/bin/python

HEARTBEAT_TIMEOUT = 5

from shepherd import Herd
from docstore import connect as docstore_connect
from json import load, dumps
from os import access, getcwd, listdir, X_OK
from os.path import abspath, isfile, join as pathjoin
from pubsub import connect as pubsub_connect
from sys import argv

def heart_monitor(game_id, pubsub):
    heartbeat_queue = pubsub.subscribe('heartbeat')
    message = ''
    while message is not None:
        message = pubsub.get_message_block(queue=heartbeat_queue,
                                           timeout=HEARTBEAT_TIMEOUT)
def flatten(list_of_lists):
    return sum(list_of_lists, [])

def n_indexed_copies(x, n):
    return [(x,i) for i in range(n)]

def abspath_listdir(d):
    return [abspath(pathjoin(d, name)) for name in listdir(d)]

def is_executable_file(f):
    return isfile(f) and access(f, X_OK)

def add_component(herd, component_name, docstore_url, game_id, index):
    component_dir = abspath(pathjoin('components', component_name))
    executable = filter(is_executable_file, abspath_listdir(component_dir))[0]
    options = [docstore_url, game_id, str(index)]
    herd.add(executable, options, component_dir)

def make_herd(component_info, game_id, docstore_url):
    herd = Herd()
    components = flatten([n_indexed_copies(*c) for c in component_info.items()])
    map(lambda (c, i): add_component(herd, c, docstore_url, game_id, i),
        components)
    return herd

game_id, docstore_url = argv[1], argv[2]
with open('game.json', 'r') as game_file:
    game_data = load(game_file)
docstore = docstore_connect(docstore_url + "/" + game_id)
docstore.put(dumps(game_data), '/game.json', 'application/json')

herd = make_herd(game_data['components'], game_id, docstore_url)
herd.start()

pubsub_url = docstore_connect(docstore_url).get('/services/pubsub')
pubsub = pubsub_connect(pubsub_url, game_id)
pubsub.publish('game_state', 'running')
print 'Now running game %s' % (game_id,)
heart_monitor(game_id, pubsub)

print 'Game %s ending' % (game_id,)
herd.stop()
