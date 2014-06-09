from docstore import connect as docstore_connect
from pika import BlockingConnection, ConnectionParameters
from re import match
from time import time as now
from urllib2 import build_opener, HTTPHandler, Request, urlopen

EXCHANGE = 'alexandra'
HTTP_PATIENCE_SEC = 1

class AMQPConnection:
    def __init__(self, url, context, marshal, unmarshal):
        self._context = context
        self.marshal, self.unmarshal = marshal, unmarshal
        host = match(r"amqp://([\w\d\.]+)", url).group(1)
        connection = BlockingConnection(ConnectionParameters(host))
        self._channel = connection.channel()
        self._channel.exchange_declare(exchange=EXCHANGE, type='topic')
        self._init_docstore()

    def _init_docstore(self):
        location_queue = self._subscribe_raw('docstore', 'location')
        self._publish_raw('docstore', 'locate', 'locate')
        docstore_url = self._get_message_block_raw(location_queue, timeout=1)
        self._docstore = docstore_connect(docstore_url)

    def publish(self, topic, message):
        self._publish_raw(self._context, topic, self.marshal(message))

    def _publish_raw(self, context, topic, message):
        self._channel.basic_publish(exchange=EXCHANGE,
                                    routing_key=context + '.' + topic,
                                    body=message)


    def subscribe(self, topic):
        return self._subscribe_raw(self._context, topic)

    def _subscribe_raw(self, context, topic):
        result = self._channel.queue_declare()
        queue = result.method.queue
        self._channel.queue_bind(exchange=EXCHANGE,
                                 queue=queue,
                                 routing_key=context + '.' + topic)
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

    def consume_all(self, f):
        queue = self.subscribe('#')
        def callback(ch, method, properties, body):
            amqp_topic = method.routing_key
            context, topic = amqp_topic.split('.', 1)
            f(context, topic, self.unmarshal(body))

        self._channel.basic_consume(callback, queue=queue, no_ack=True)
        self._channel.start_consuming()

    def get_message(self, queue):
        raw_message = self._get_message_raw(queue)
        if raw_message is None:
            return None
        else:
            return self.unmarshal(raw_message)

    def _get_message_raw(self, queue):
        return self._channel.basic_get(0, queue=queue, no_ack=True)[2]

    def get_all_messages(self, queue):
        messages = []
        while True:
            message = self.get_message(queue)
            if message is None:
                return messages
            else:
                messages.append(message)

    def get_message_block(self, queue, timeout=None):
        return self._get_message_block(queue, self.get_message, timeout)

    def _get_message_block_raw(self, queue, timeout=None):
        return self._get_message_block(queue, self._get_message_raw, timeout)

    def _get_message_block(self, queue, fetcher, timeout):
        alarm = Alarm(timeout)
        while True:
            message = fetcher(queue)
            if message is not None:
                return message
            if alarm.is_ringing():
                return None

    def get_current_message(self, topic):
        raw_message = self._docstore.get('/%s/%s' % (self._context, topic))
        if raw_message is None:
            return None
        else:
            return self.unmarshal(raw_message)

    def make_topic_monitor(self, topic):
        return TopicMonitor(self, topic)

class HTTPConnection:
    def __init__(self, url, context, marshal, unmarshal):
        self._root_url = '%s/contexts/%s' % (url, context)
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

    def consume_all(self, f):
        pass #not implemented

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

def connect(url, context, marshal=identity, unmarshal=identity):
    protocol = match(r"(\w+)://", url).group(1)
    return connection_classes[protocol](url, context, marshal, unmarshal)

def firehose(url):
    return connect(url, '#')

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
