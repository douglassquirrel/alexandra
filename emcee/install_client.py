#! /usr/bin/python

from os import listdir
from os.path import abspath, join as pathjoin
from shutil import copy
from sys import argv
from tempfile import mkdtemp

def full_path_listdir(d):
    return [pathjoin(d, name) for name in listdir(d)]

def copy_libraries_to(dest_dir):
    map(lambda(p): copy(p, dest_dir), full_path_listdir('libraries'))

game_name = argv[1]
game_dir = abspath(pathjoin('..', 'games', game_name))
game_client_dir = pathjoin(game_dir, 'client')
install_client_dir = mkdtemp(prefix=game_name + '-client.')

print 'Installing client in %s' % (install_client_dir,)
client_files = full_path_listdir(game_client_dir)
map(lambda(f): copy(f, install_client_dir), client_files)
copy_libraries_to(install_client_dir)
