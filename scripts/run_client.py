#! /usr/bin/python

from os.path import abspath, join as pathjoin
from sys import path
path.insert(0, abspath(pathjoin('..', 'libraries')))
path.insert(0, abspath(pathjoin('..', 'infralib')))

from installer import install_docstore
from sys import argv

docstore_url, game_name = argv[1], argv[2]

options = [docstore_url, game_name]
if len(argv) > 3:
    pubsub_url = argv[3]
    print 'Using pubsub URL %s' % pubsub_url
    options.append(pubsub_url)

sources = ['/games/%s/client' % game_name, '/libraries']
install_docstore(game_name + '-client', sources, options, docstore_url)
