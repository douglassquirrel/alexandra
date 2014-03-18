#! /usr/bin/python

from os import access, listdir, X_OK
from os.path import isfile, join as pathjoin
from shutil import copy, copytree
from signal import SIGKILL
from subprocess import Popen
from tempfile import mkdtemp

COMPONENTS = ['library', 'bootstrap', 'collider', 'umpire',
              'world', 'client', 'walls', 'player']
CONFIG_COMPONENTS = ['library', 'bootstrap']

from random import shuffle
shuffle(COMPONENTS)

def full_path_listdir(d):
    return [pathjoin(d, name) for name in listdir(d)]

def copy_libraries_to(dest_dir):
    map(lambda(p): copy(p, dest_dir), full_path_listdir('libraries'))

def copy_config_to(dest_dir):
    copy('config.json', dest_dir)

def install_components(install_dir):
    installed_components_dir = pathjoin(install_dir, 'components')
    copytree('components', installed_components_dir)
    map(copy_libraries_to, full_path_listdir(installed_components_dir))
    map(lambda(c): copy_config_to(pathjoin(installed_components_dir, c)),
        CONFIG_COMPONENTS)

def is_executable_file(f):
    return isfile(f) and access(f, X_OK)

def start_component(component_name, run_dir):
    component_dir = pathjoin(run_dir, 'components', component_name)
    executable = filter(is_executable_file, full_path_listdir(component_dir))[0]
    print "Executing %s" % (executable,)
    process = Popen(executable, cwd=component_dir)
    return process

install_dir = mkdtemp(prefix='alexandra.')
print 'Running in %s' % (install_dir,)
install_components(install_dir)
processes = map(lambda(c): start_component(c, install_dir), COMPONENTS)
print 'Now running'
raw_input('Press Enter to stop')
map(lambda(p): p.kill(), processes)
