from json import dumps
from os import access, listdir, X_OK
from os.path import abspath, basename, isdir, isfile, join as pathjoin

def _abspath_listdir(d):
    return [abspath(pathjoin(d, name)) for name in listdir(d)]

def _publish_file(root, path, docstore):
    url_path = path[len(root):]
    with open(path, 'r') as f:
        data = f.read()
    docstore.put(data, url_path)

def _is_executable_file(f):
    return isfile(f) and access(f, X_OK)

def _is_valid_file(filename):
    return not basename(filename).startswith('.')

def publish_dir(root, path, docstore):
    contents = filter(_is_valid_file, _abspath_listdir(path))
    files = filter(isfile, contents)
    dirs = filter(isdir, contents)
    map(lambda f: _publish_file(root, f, docstore), files)
    map(lambda d: publish_dir(root, d, docstore), dirs)
    executables = filter(_is_executable_file, files)
    if len(executables) > 0:
        install_data = dumps({'executable': basename(executables[0])})
        docstore.put(install_data, path[len(root):] + '/install.json')
