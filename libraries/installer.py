#! /usr/bin/python

from os import access, listdir, X_OK
from os.path import abspath, basename, isfile, isdir, join as pathjoin
from shutil import copy, copytree
from subprocess import Popen
from tempfile import mkdtemp

def install(name, sources, options, copies=1):
    install_dir = mkdtemp(prefix=name + '.')
    map(lambda d: _copy_dir_contents(d, install_dir), sources)
    executable = filter(_is_executable_file, _abspath_listdir(install_dir))[0]
    return map(lambda i: _run(executable, options + [str(i)], install_dir),
               range(copies))

def _run(executable, options, cwd):
    return Popen([executable] + options, cwd=cwd)

def _abspath_listdir(d):
    return [abspath(pathjoin(d, name)) for name in listdir(d)]

def _copy_item(item, to_dir):
    if isfile(item):
        copy(item, to_dir)
    elif isdir(item):
        copytree(item, pathjoin(to_dir, basename(item)))

def _copy_dir_contents(from_dir, to_dir):
    map(lambda f: _copy_item(f, to_dir), _abspath_listdir(from_dir))

def _is_executable_file(f):
    return isfile(f) and access(f, X_OK)
