#! /usr/bin/python

from os import listdir
from os.path import abspath, basename, join as pathjoin
from shutil import copy, copytree
from subprocess import call
from sys import argv
from tempfile import mkdtemp

INFRA_FILES = ['infra.json', 'run.py']

def full_path_listdir(d):
    return [pathjoin(d, name) for name in listdir(d)]

def copy_libraries_to(dest_dir):
    map(lambda(p): copy(p, dest_dir), full_path_listdir('libraries'))

def install_game(game_dir, install_dir):
    game_json = pathjoin(game_dir, 'game.json')
    game_components_dir = pathjoin(game_dir, 'components')

    copy(game_json, install_dir)
    installed_components_dir = pathjoin(install_dir, 'components')
    copytree(game_components_dir, installed_components_dir)
    map(copy_libraries_to, full_path_listdir(installed_components_dir))

    map(lambda(f): copy(f, install_dir), INFRA_FILES)

def install_client(game_dir, install_client_dir):
    game_client_dir = pathjoin(game_dir, 'client')
    game_files = full_path_listdir(game_client_dir)
    map(lambda(f): copy(f, install_client_dir), game_files)
    copy_libraries_to(install_client_dir)

game_name = argv[1]
game_dir = abspath(pathjoin('..', game_name))
install_dir = mkdtemp(prefix=game_name + '.')
game_id = basename(install_dir)
client_dir = mkdtemp(prefix=game_name + '-client.')

print 'Installing game in %s' % (install_dir,)
print 'Using game id %s' % (game_id,)
print 'To run client, cd %s and type client x %s 0' % (client_dir, game_id)
install_game(game_dir, install_dir)
install_client(game_dir, client_dir)
call([pathjoin(install_dir, 'run.py'), game_id], cwd=install_dir)
