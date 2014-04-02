#! /usr/bin/python

from os import access, listdir, X_OK
from os.path import abspath, isfile, join as pathjoin
from shutil import copy
from subprocess import call
from sys import argv
from tempfile import mkdtemp

def full_path_listdir(d):
    return [pathjoin(d, name) for name in listdir(d)]

def copy_libraries_to(dest_dir):
    map(lambda(p): copy(p, dest_dir), full_path_listdir('libraries'))

def abspath_listdir(d):
    return [abspath(pathjoin(d, name)) for name in listdir(d)]

def is_executable_file(f):
    return isfile(f) and access(f, X_OK)

def get_client_files(game_name):
    game_dir = abspath(pathjoin('..', 'games', game_name))
    game_client_dir = pathjoin(game_dir, 'client')
    return full_path_listdir(game_client_dir)

def install_client(client_files, install_client_dir):
    map(lambda(f): copy(f, install_client_dir), client_files)
    copy_libraries_to(install_client_dir)

game_name = argv[1]
install_dir = mkdtemp(prefix=game_name + '-client.')
print 'Installing client in %s' % (install_dir,)

install_client(get_client_files(game_name), install_dir)
executable = filter(is_executable_file, abspath_listdir(install_dir))[0]
call([executable, game_name], cwd=install_dir)
