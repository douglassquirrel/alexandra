from docstore import connect
from json import load, loads, dumps
from os import access, chmod, listdir, makedirs, stat, X_OK
from os.path import abspath, basename, dirname, exists, \
                    isfile, isdir, join as pathjoin
from platform import node
from shutil import copy, copytree
from stat import S_IEXEC
from subprocess import Popen
from tempfile import mkdtemp

def install_docstore(name, sources, options,
                     docstore_url, group=None, copies=1):
    fetch_to = lambda d: _fetch_from_docstore(sources, d, docstore_url)
    _install(name, fetch_to, options, group, docstore_url, copies)

def install_dir(name, sources, options,
                docstore_url=None, group=None, copies=1):
    fetch_to = lambda d: _fetch_from_dir(sources, d)
    _install(name, fetch_to, options, group, docstore_url, copies)

def _install(name, fetch_to, options, group, docstore_url, copies):
    install_dir = mkdtemp(prefix=name + '.')
    fetch_to(install_dir)
    procs = _run_installed(install_dir, options, copies)
    if group is not None:
        _publish_group_pids(name, group, procs, docstore_url)

def _fetch_from_dir(sources, dest):
    map(lambda d: _copy_dir_contents(d, dest), sources)

def _fetch_from_docstore(sources, dest, docstore_url):
    docstore = connect(docstore_url)
    if docstore.wait_until_up() is False:
        print 'No docstore at %s for fetch for %s' % (docstore_url, name)
        return
    map(lambda s: _copy_source_docstore(s, dest, docstore), sources)

def _docstore_to_file_path(source, dest, path):
    return pathjoin(dest, *(path[len(source):].split('/')))

def _docstore_to_file(from_path, to_path, docstore):
    if not exists(dirname(to_path)):
        makedirs(dirname(to_path))
    with open(to_path, 'w') as f:
        f.write(docstore.get(from_path))

def _copy_source_docstore(source, dest, docstore):
    source = '/alexandra' + source
    docstore_paths = loads(docstore.get(source + '/index.json'))
    path_pairs = map(lambda p: (p, _docstore_to_file_path(source, dest, p)),
                     docstore_paths)
    map(lambda (f, t): _docstore_to_file(f, t, docstore), path_pairs)
    install_json_pairs = filter(lambda (f, t): f.endswith('install.json'),
                                path_pairs)
    map(lambda (f, t): _set_executable(t), install_json_pairs)

def _set_executable(install_json_file):
    with open(install_json_file, 'r') as f:
        install_data = load(f)
    executable = pathjoin(dirname(install_json_file),
                          install_data['executable'])
    _make_executable(executable)

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

def _make_executable(f):
    chmod(f, stat(f).st_mode | S_IEXEC)
