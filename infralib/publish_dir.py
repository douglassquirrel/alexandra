from json import dumps
from os import access, listdir, X_OK
from os.path import abspath, basename, isdir, isfile, join as pathjoin

def _abspath_listdir(d):
    return [abspath(pathjoin(d, name)) for name in listdir(d)]

def _publish_file(root, path, pubsub):
    with open(path, 'r') as f:
        data = f.read()
    pubsub.publish(path[len(root)+1:], data)

def _is_executable_file(f):
    return isfile(f) and access(f, X_OK)

def _is_valid_file(filename):
    return not basename(filename).startswith('.')

def publish_dir(root, path, pubsub):
    contents = filter(_is_valid_file, _abspath_listdir(path))
    files = filter(isfile, contents)
    dirs = filter(isdir, contents)
    map(lambda f: _publish_file(root, f, pubsub), files)
    files_per_dir = map(lambda d: publish_dir(root, d, pubsub), dirs)
    num_files = len(files) + sum(files_per_dir)

    executables = filter(_is_executable_file, files)
    if len(executables) > 0:
        install_data = dumps({'executable': basename(executables[0])})
        pubsub.publish(path[len(root)+1:] + '/install.json', install_data)
        num_files += 1

    return num_files
