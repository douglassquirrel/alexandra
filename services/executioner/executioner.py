#! /usr/bin/python

from docstore import connect as docstore_connect
from json import loads
from os import getpid, kill
from platform import node
from pubsub import connect as pubsub_connect
from signal import SIGKILL
from sys import argv

def is_local(server_name):
    return server_name == node()

def get_local_pids(group_path, docstore):
    proc_paths = loads(docstore.get(group_path + '/processes/index.json'))
    proc_data = sum(map(lambda p: loads(docstore.get(p)), proc_paths), [])
    return [pid for (server, pid) in proc_data if is_local(server)]

def move_self_to_end(pids):
    self_pid = getpid()
    if self_pid in pids:
        pids.remove(self_pid)
        pids.append(self_pid)

def kill_group(group_path, docstore):
    local_pids = get_local_pids(group_path, docstore)
    move_self_to_end(local_pids)
    for pid in local_pids:
        kill(pid, SIGKILL)

docstore_url = argv[1]
docstore = docstore_connect(docstore_url)
pubsub_url = docstore.wait_and_get('/services/pubsub')
if pubsub_url is None:
    print 'No pubsub data on docstore, exiting'
    exit(1)
pubsub = pubsub_connect(pubsub_url, 'process', unmarshal=loads)
pubsub.consume_topic('kill', lambda m: kill_group(m, docstore))
