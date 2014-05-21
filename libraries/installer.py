#! /usr/bin/python

from docstore import connect
from json import dumps
from os import access, listdir, X_OK
from os.path import abspath, basename, isfile, isdir, join as pathjoin
from platform import node
from shutil import copy, copytree
from subprocess import Popen
from tempfile import mkdtemp

def install(name, sources, options, group=None, docstore_url=None, copies=1):
    install_dir = mkdtemp(prefix=name + '.')
    map(lambda d: _copy_dir_contents(d, install_dir), sources)
    procs = _run_installed(install_dir, options, copies)
    if group is not None:
        _publish_group_pids(name, group, procs, docstore_url)

def _run_installed(install_dir, options, copies):
    executable = _find_executable(install_dir)
    return map(lambda i: _run(executable, options + [str(i)], install_dir),
               range(copies))

def _publish_group_pids(name, group, procs, docstore_url):
    docstore = connect(docstore_url)
    if docstore.wait_until_up() is False:
        print 'No docstore at %s for pids for %s' % (docstore_url, name)
        return
    pids = map(lambda (n, p): (n, p.pid), procs)
    docstore.put(dumps(pids), '/%s/processes/%s.json' % (group, name))

def _run(executable, options, cwd):
    return (node(), Popen([executable] + options, cwd=cwd))

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

def _find_executable(d):
    return filter(_is_executable_file, _abspath_listdir(d))[0]
