#! /usr/bin/python

from os.path import join as pathjoin
from shutil import copy
from subprocess import call
from tempfile import mkdtemp

install_dir = mkdtemp(prefix='emcee.')
print 'Installing emcee in %s' % (install_dir,)

copy('emcee.py', install_dir)
copy(pathjoin('libraries', 'pubsub.py'), install_dir)
call([pathjoin(install_dir, 'emcee.py')], cwd=install_dir)
