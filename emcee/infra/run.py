#! /usr/bin/python

from json import load
from os import access, getcwd, listdir, X_OK
from os.path import abspath, isfile, join as pathjoin
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
    print 'Executing %s number %d' % (executable, index)
    process = Popen([executable, abspath(getcwd()), game_id, str(index)],
                    cwd=component_dir)
    return process

def start_component_group(game_id, component_name, n):
    return map(lambda(i): start_component(game_id, component_name, i), range(n))

def start(components, game_id):
    return flatten(map(lambda(c): start_component_group(game_id, *c),
                       components.items()))

game_id = argv[1]
with open('game.json', 'r') as game_file:
    game_data = load(game_file)
processes = start(game_data['components'], game_id)

print 'Now running'
raw_input('Press Enter to stop')
map(lambda(p): p.kill(), processes)
