#! /usr/bin/python

from json import load
from os.path import abspath, join as pathjoin
from shutil import copy
from subprocess import Popen
from tempfile import mkdtemp

INFRA_FILES = ['emcee.py', 'http_docstore.py', 'pubsub_ws.py',
               'pubsub_ws_doc.html', pathjoin('libraries', 'pubsub.py')]

install_dir = mkdtemp(prefix='emcee.')
games_dir = abspath(pathjoin('..', 'games'))
libraries_dir = abspath('libraries')
infra_dir = abspath('infra')
print 'Installing emcee in %s' % (install_dir,)
print 'Games in %s' % (games_dir,)
print 'Libraries in %s' % (libraries_dir,)
print 'Infrastructure files in %s' % (infra_dir,)

map(lambda f: copy(f, install_dir), INFRA_FILES)

config_file_path = pathjoin(infra_dir, 'infra.json')
with open(config_file_path, 'r') as config_file:
    config = load(config_file)
docstore_host = config['docstore_host']
docstore_port = str(config['docstore_port'])
pubsub_host = config['pubsub_host']
pubsub_port = str(config['pubsub_port'])

options = {'emcee.py':         [games_dir, libraries_dir, infra_dir],
           'http_docstore.py': [docstore_host, docstore_port],
           'pubsub_ws.py':     [pubsub_host, pubsub_port]}

def start_process(filename):
    return Popen([pathjoin(install_dir, filename)] + options[filename],
                 cwd=install_dir)

processes = map(start_process, options.keys())

print 'Now running'
raw_input('Press Enter to stop\n')
map(lambda(p): p.kill(), processes)
