#! /usr/bin/python

from os.path import abspath, join as pathjoin
from sys import path
path.insert(0, abspath(pathjoin('..', 'libraries')))

from json import load
from shepherd import Herd
from shutil import copy
from subprocess import Popen
from tempfile import mkdtemp

install_dir = mkdtemp(prefix='emcee.')
games_dir = abspath(pathjoin('..', 'games'))
libraries_dir = abspath(pathjoin('..', 'libraries'))
infra_dir = abspath('infra')
print 'Installing services in %s' % (install_dir,)
print 'Games in %s' % (games_dir,)
print 'Libraries in %s' % (libraries_dir,)
print 'Infrastructure files in %s' % (infra_dir,)

INFRA_FILES = ['emcee.py', 'docstore_server_http.py', 'pubsub_ws.py',
               'pubsub_ws_doc.html',
               pathjoin(libraries_dir, 'pubsub.py'),
               pathjoin(libraries_dir, 'shepherd.py'),]

map(lambda f: copy(f, install_dir), INFRA_FILES)

config_file_path = pathjoin(infra_dir, 'infra.json')
with open(config_file_path, 'r') as config_file:
    config = load(config_file)
docstore_host = config['docstore_host']
docstore_port = str(config['docstore_port'])
pubsub_host = config['pubsub_host']
pubsub_port = str(config['pubsub_port'])

def add_service(herd, executable, options):
    herd.add(pathjoin(install_dir, executable), options, install_dir)

options = {'emcee.py':                [games_dir, libraries_dir, infra_dir],
           'docstore_server_http.py': [docstore_host, docstore_port],
           'pubsub_ws.py':            [pubsub_host, pubsub_port]}

herd = Herd()
map(lambda (e, o): add_service(herd, e, o), options.items())
herd.start()

print 'Now running'
raw_input('Press Enter to stop\n')
herd.stop()
