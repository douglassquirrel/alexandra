#! /usr/bin/python

from json import load
from pubsub import create_channel, publish
from time import sleep
from urllib2 import URLError, urlopen

CONFIG_FILE = 'config.json'

def is_responsive(url):
    try:
        urlopen(url).read()
        return True
    except URLError:
        return False

def publish_url(host, port):
    channel = create_channel()
    url = 'http://%s:%d' % (host, port)

    while is_responsive(url + '/index.html'):
        publish(channel=channel, label='library_url', message=url)
        sleep(1)

with open(CONFIG_FILE) as config_file:
    config = load(config_file)
host, port = config['library_host'], config['library_port']
publish_url(host, port)
