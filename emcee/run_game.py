#! /usr/bin/python

from os import listdir
from os.path import abspath, basename, join as pathjoin
from shutil import copy, copytree
from subprocess import call
from sys import argv
from tempfile import mkdtemp

def full_path_listdir(d):
    return [pathjoin(d, name) for name in listdir(d)]

def copy_libraries_to(dest_dir):
    map(lambda(p): copy(p, dest_dir), full_path_listdir('libraries'))

def install_game(game_dir, install_dir):
    game_json = pathjoin(game_dir, 'game.json')
    copy(game_json, install_dir)

    game_components_dir = pathjoin(game_dir, 'components')
    installed_components_dir = pathjoin(install_dir, 'components')
    copytree(game_components_dir, installed_components_dir)
    map(copy_libraries_to, full_path_listdir(installed_components_dir))

    map(lambda(f): copy(f, install_dir), full_path_listdir('infra'))

game_name, game_id = argv[1], argv[2]
game_dir = abspath(pathjoin('..', 'games', game_name))
install_dir = mkdtemp(prefix=game_id + '.')

print 'Installing game in %s' % (install_dir,)
print 'Using game id %s' % (game_id,)
install_game(game_dir, install_dir)
call([pathjoin(install_dir, 'run.py'), game_id], cwd=install_dir)
