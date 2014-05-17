#! /usr/bin/python

from os import access, listdir, X_OK
from os.path import abspath, isfile, join as pathjoin
from shutil import copy
from subprocess import call
from sys import argv
from tempfile import mkdtemp

def full_path_listdir(d):
    return [pathjoin(d, name) for name in listdir(d)]

def copy_libraries_to(dest_dir):
    libraries_dir = pathjoin(abspath('..'), 'libraries')
    map(lambda(p): copy(p, dest_dir), full_path_listdir(libraries_dir))

def abspath_listdir(d):
    return [abspath(pathjoin(d, name)) for name in listdir(d)]

def is_executable_file(f):
    return isfile(f) and access(f, X_OK)

def install_client(game_name, install_client_dir):
    game_client_dir = abspath(pathjoin('..', 'games', game_name, 'client'))
    client_files = full_path_listdir(game_client_dir)
    map(lambda(f): copy(f, install_client_dir), client_files)
    copy_libraries_to(install_client_dir)

docstore_url, game_name = argv[1], argv[2]
install_dir = mkdtemp(prefix=game_name + '-client.')
print 'Installing client in %s' % (install_dir,)

install_client(game_name, install_dir)
executable = filter(is_executable_file, abspath_listdir(install_dir))[0]
args = [executable, docstore_url, game_name]
if len(argv) > 3:
    pubsub_url = argv[3]
    print 'Using pubsub URL %s' % pubsub_url
    args.append(pubsub_url)
call(args, cwd=install_dir)
