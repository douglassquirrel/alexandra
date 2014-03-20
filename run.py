#! /usr/bin/python

from json import load
from os import access, getcwd, listdir, X_OK
from os.path import abspath, isfile, join as pathjoin
from subprocess import Popen

def flatten(list_of_lists):
    return sum(list_of_lists, [])

def abspath_listdir(d):
    return [abspath(pathjoin(d, name)) for name in listdir(d)]

def is_executable_file(f):
    return isfile(f) and access(f, X_OK)

def start_component(component_name, index):
    component_dir = abspath(pathjoin('components', component_name))
    executable = filter(is_executable_file, abspath_listdir(component_dir))[0]
    print "Executing %s number %d" % (executable, index)
    process = Popen([executable, abspath(getcwd()), str(index)],
                    cwd=component_dir)
    return process

def start_component_group(component_name, n):
    return map(lambda(i): start_component(component_name, i), range(n))

with open('game.json', 'r') as game_file:
    game_data = load(game_file)
components = game_data['components']
processes = flatten(map(lambda(c): start_component_group(*c),
                        components.items()))
print 'Now running'
print 'Press Space in game window to start'
raw_input('Press Enter in this window to stop\n')
map(lambda(p): p.kill(), processes)
