#! /usr/bin/python

from os.path import abspath, join as pathjoin
from shutil import copy
from subprocess import Popen
from tempfile import mkdtemp

install_dir = mkdtemp(prefix='emcee.')
games_dir = abspath(pathjoin('..', 'games'))
libraries_dir = abspath('libraries')
infra_dir = abspath('infra')
print 'Installing emcee in %s' % (install_dir,)
print 'Games in %s' % (games_dir,)
print 'Libraries in %s' % (libraries_dir,)
print 'Infrastructure files in %s' % (infra_dir,)

copy('emcee.py', install_dir)
copy('pubsub_ws.py', install_dir)
copy('pubsub_ws_doc.html', install_dir)
copy(pathjoin('libraries', 'pubsub.py'), install_dir)
processes = []
processes.append(Popen([pathjoin(install_dir, 'emcee.py'),
                        games_dir, libraries_dir, infra_dir],
                       cwd=install_dir))
processes.append(Popen([pathjoin(install_dir, 'pubsub_ws.py'), infra_dir],
                       cwd=install_dir))

print 'Now running'
raw_input('Press Enter to stop\n')
map(lambda(p): p.kill(), processes)
