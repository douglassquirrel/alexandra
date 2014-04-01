#! /usr/bin/python

from os import listdir
from os.path import basename, join as pathjoin
from shutil import copy, copytree
from subprocess import call
from tempfile import mkdtemp

INFRA_FILES = ['game.json', 'infra.json', 'run.py']

def full_path_listdir(d):
    return [pathjoin(d, name) for name in listdir(d)]

def copy_libraries_to(dest_dir):
    map(lambda(p): copy(p, dest_dir), full_path_listdir('libraries'))

def install_components(install_dir):
    installed_components_dir = pathjoin(install_dir, 'components')
    copytree('components', installed_components_dir)
    map(copy_libraries_to, full_path_listdir(installed_components_dir))

def install_infra(install_dir):
    map(lambda(f): copy(f, install_dir), INFRA_FILES)

game_name = 'alexandra'
install_dir = mkdtemp(prefix=game_name + '.')
game_id = basename(install_dir)
print 'Installing in %s and using game id %s' % (install_dir, game_id)
install_components(install_dir)
install_infra(install_dir)
call([pathjoin(install_dir, 'run.py'), game_id], cwd=install_dir)
