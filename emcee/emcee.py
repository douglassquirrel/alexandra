#! /usr/bin/python

from json import loads
from os import listdir
from os.path import abspath, join as pathjoin
from pubsub import connect
from shutil import copy, copytree
from subprocess import call
from sys import argv
from tempfile import mkdtemp

def full_path_listdir(d):
    return [pathjoin(d, name) for name in listdir(d)]

def copy_libraries_to(libraries_dir, dest_dir):
    map(lambda(p): copy(p, dest_dir), full_path_listdir(libraries_dir))

def install_game(game_dir, install_dir, libraries_dir, infra_dir):
    game_json = pathjoin(game_dir, 'game.json')
    copy(game_json, install_dir)

    game_components_dir = pathjoin(game_dir, 'components')
    installed_components_dir = pathjoin(install_dir, 'components')
    copytree(game_components_dir, installed_components_dir)
    map(lambda(d): copy_libraries_to(libraries_dir, d),
        full_path_listdir(installed_components_dir))

    map(lambda(f): copy(f, install_dir), full_path_listdir(infra_dir))
    copy(pathjoin(libraries_dir, 'pubsub.py'), install_dir)

def start_game(message, games_dir, libraries_dir, infra_dir):
    game_info = loads(message)
    name, id = game_info['name'], game_info['id']
    game_dir = abspath(pathjoin(games_dir, name))
    install_dir = mkdtemp(prefix=id + '.')

    print 'Running game %s in %s using id %s' % (name, install_dir, id)
    install_game(game_dir, install_dir, libraries_dir, infra_dir)
    call([pathjoin(install_dir, 'run.py'), id], cwd=install_dir)

games_dir, libraries_dir, infra_dir = argv[1], argv[2], argv[3]
connection = connect('amqp://localhost', 'emcee')
queue = connection.subscribe('game.wanted')
connection.consume(queue, lambda(m): start_game(m, games_dir, libraries_dir, infra_dir))
