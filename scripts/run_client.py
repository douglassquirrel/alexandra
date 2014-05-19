#! /usr/bin/python

from os.path import abspath, join as pathjoin
from sys import path
path.insert(0, abspath(pathjoin('..', 'libraries')))

from installer import install
from sys import argv

docstore_url, game_name = argv[1], argv[2]
game_client_dir = abspath(pathjoin('..', 'games', game_name, 'client'))
libraries_dir = pathjoin(abspath('..'), 'libraries')

options = [docstore_url, game_name]
if len(argv) > 3:
    pubsub_url = argv[3]
    print 'Using pubsub URL %s' % pubsub_url
    options.append(pubsub_url)

sources = [game_client_dir, libraries_dir]
install(game_name + '-client', sources, options)
