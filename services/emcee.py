#! /usr/bin/python

from docstore import connect as docstore_connect
from json import loads
from os import listdir
from os.path import abspath, join as pathjoin
from pubsub import connect as pubsub_connect
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
    copy(pathjoin(libraries_dir, 'docstore.py'), install_dir)
    copy(pathjoin(libraries_dir, 'pubsub.py'), install_dir)
    copy(pathjoin(libraries_dir, 'shepherd.py'), install_dir)

def start_game(message, games_dir, libraries_dir, infra_dir, docstore_url):
    game_info = loads(message)
    name, id = game_info['name'], game_info['id']
    game_dir = abspath(pathjoin(games_dir, name))
    install_dir = mkdtemp(prefix=id + '.')

    print 'Running game %s in %s using id %s' % (name, install_dir, id)
    install_game(game_dir, install_dir, libraries_dir, infra_dir)
    call([pathjoin(install_dir, 'run_components.py'), id, docstore_url],
         cwd=install_dir)

games_dir, libraries_dir, infra_dir, docstore_url = argv[1:5]

docstore = docstore_connect(docstore_url)
pubsub_url = docstore.wait_and_get('/services/pubsub')
if pubsub_url is None:
    print 'No pubsub data on docstore, exiting'
    exit(1)
pubsub = pubsub_connect(pubsub_url, 'emcee')
pubsub.consume_topic('game.wanted', lambda m: start_game(m, games_dir, libraries_dir, infra_dir, docstore_url))
