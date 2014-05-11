from pika import BlockingConnection, ConnectionParameters
from re import match
from time import time as now
from urllib2 import build_opener, HTTPHandler, Request, urlopen

HTTP_PATIENCE_SEC = 1

class AMQPConnection:
    def __init__(self, url, exchange_name, marshal, unmarshal):
        self._exchange_name = exchange_name
        self.marshal, self.unmarshal = marshal, unmarshal
        host = match(r"amqp://(\w+)", url).group(1)
        connection = BlockingConnection(ConnectionParameters(host))
        self._channel = connection.channel()
        self._channel.exchange_declare(exchange=self._exchange_name,
                                       type='topic')

    def publish(self, topic, message):
        self._channel.basic_publish(exchange=self._exchange_name,
                                    routing_key=topic,
                                    body=self.marshal(message))

    def subscribe(self, topic):
        result = self._channel.queue_declare()
        queue = result.method.queue
        self._channel.queue_bind(exchange=self._exchange_name,
                                 queue=queue,
                                 routing_key=topic)
        return queue

    def unsubscribe(self, queue):
        self._channel.queue_delete(callback=None, queue=queue)

    def consume_queue(self, queue, f):
        def callback(ch, method, properties, body):
            f(self.unmarshal(body))

        self._channel.basic_consume(callback, queue=queue, no_ack=True)
        self._channel.start_consuming()

    def consume_topic(self, topic, f):
        queue = self.subscribe(topic)
        self.consume_queue(queue, f)

    def get_message(self, queue):
        raw_message = self._channel.basic_get(0, queue=queue, no_ack=True)[2]
        if raw_message is None:
            return None
        else:
            return self.unmarshal(raw_message)

    def get_all_messages(self, queue):
        messages = []
        while True:
            message = self.get_message(queue)
            if message is None:
                return messages
            else:
                messages.append(message)

    def get_message_block(self, queue, timeout=None):
        alarm = Alarm(timeout)
        while True:
            message = self.get_message(queue)
            if message is not None:
                return message
            if alarm.is_ringing():
                return None

    def make_topic_monitor(self, topic):
        return TopicMonitor(self, topic)

class HTTPConnection:
    def __init__(self, url, exchange_name, marshal, unmarshal):
        self._root_url = '%s/exchanges/%s' % (url, exchange_name)
        self.marshal, self.unmarshal = marshal, unmarshal

    def publish(self, topic, message):
        url = '%s/%s' % (self._root_url, topic)
        self._visit_url(url=url, data=self.marshal(message), method='POST')

    def subscribe(self, topic):
        return self._visit_url('%s/%s' % (self._root_url, topic))

    def unsubscribe(self, queue):
        url = '%s/queues/%s' % (self._root_url, queue)
        self._visit_url(url=url, method='DELETE')

    def consume_queue(self, queue, f):
        url = '%s/queues/%s' % (self._root_url, queue)
        headers = [('Patience', HTTP_PATIENCE_SEC)]
        while True:
            message = self._visit_url(url=url, headers=headers)
            if len(message) > 0:
                f(self.unmarshal(message))

    def consume_topic(self, topic, f):
        queue = self.subscribe(topic)
        self.consume_queue(queue, f)

    def get_message(self, queue):
        url = '%s/queues/%s' % (self._root_url, queue)
        message = self._visit_url(url)
        if len(message) == 0:
            return None
        else:
            return self.unmarshal(message)

    def get_all_messages(self, queue):
        url = '%s/queues/%s' % (self._root_url, queue)
        headers = [('Range', 'all')]
        result = self._visit_url(url=url, headers=headers)
        if len(result) == 0:
            return []
        else:
            return map(self.unmarshal, result.split('\n'))

    def get_message_block(self, queue, timeout=None):
        url = '%s/queues/%s' % (self._root_url, queue)
        headers = [('Patience', HTTP_PATIENCE_SEC)]
        alarm = Alarm(timeout)
        while True:
            message = self._visit_url(url=url, headers=headers)
            if len(message) > 0:
                return self.unmarshal(message)
            if alarm.is_ringing():
                return None

    def make_topic_monitor(self, topic):
        return TopicMonitor(self, topic)

    def _visit_url(self, url, data=None, method='GET', headers=[]):
        opener = build_opener(HTTPHandler)
        request = Request(url)
        request.get_method = lambda: method
        for header in headers:
            request.add_header(*header)
        return opener.open(request, data).read()

connection_classes = {'amqp': AMQPConnection, 'http': HTTPConnection}
def identity(x):
    return x

def connect(url, exchange_name, marshal=identity, unmarshal=identity):
    protocol = match(r"(\w+)://", url).group(1)
    return connection_classes[protocol](url, exchange_name, marshal, unmarshal)

class Alarm:
    def __init__(self, duration):
        if duration is not None:
            self.alarm_time = now() + duration
        else:
            self.alarm_time = None

    def is_ringing(self):
        return self.alarm_time is not None and now() > self.alarm_time

class TopicMonitor:
    def __init__(self, connection, topic):
        self._connection = connection
        self._queue = connection.subscribe(topic)
        self._latest = None

    def latest(self):
        messages = self._connection.get_all_messages(self._queue)
        if len(messages) > 0:
            self._latest = messages[-1]
        return self._latest
