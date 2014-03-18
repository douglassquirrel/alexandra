#! /usr/bin/python

from os import access, listdir, X_OK
from os.path import abspath, isfile, join as pathjoin
from subprocess import Popen

def abspath_listdir(d):
    return [abspath(pathjoin(d, name)) for name in listdir(d)]

def is_executable_file(f):
    return isfile(f) and access(f, X_OK)

def start_component(component_name):
    component_dir = abspath(pathjoin('components', component_name))
    executable = filter(is_executable_file, abspath_listdir(component_dir))[0]
    print "Executing %s" % (executable,)
    process = Popen(executable, cwd=component_dir)
    return process

processes = map(start_component, listdir('components'))
print 'Now running'
raw_input('Press Enter to stop')
map(lambda(p): p.kill(), processes)
