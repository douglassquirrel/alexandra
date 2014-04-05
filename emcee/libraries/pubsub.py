from pika import BlockingConnection, ConnectionParameters
from time import time as now

class Connection:
    def __init__(self, exchange_name):
        self._exchange_name = exchange_name
        connection = BlockingConnection(ConnectionParameters('localhost'))
        self._channel = connection.channel()
        self._channel.exchange_declare(exchange=self._exchange_name,
                                       type='topic')

    def publish(self, topic, message):
        self._channel.basic_publish(exchange=self._exchange_name,
                                    routing_key=topic,
                                    body=message)

    def subscribe(self, topic):
        result = self._channel.queue_declare(exclusive=True)
        queue = result.method.queue
        self._channel.queue_bind(exchange=self._exchange_name,
                                 queue=queue,
                                 routing_key=topic)
        return queue

    def unsubscribe(self, queue, topic):
        self._channel.queue_unbind(exchange=self._exchange_name,
                                   queue=queue,
                                   routing_key=topic)

    def consume(self, queue, f):
        def callback(ch, method, properties, body):
            f(body)

        self._channel.basic_consume(callback, queue=queue, no_ack=True)
        self._channel.start_consuming()

    def get_message(self, queue):
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
        alarm = Alarm(timeout)
        while True:
            message = self.get_message(queue)
            if message is not None:
                return message
            if alarm.is_ringing():
                return None

class Alarm:
    def __init__(self, duration):
        if duration is not None:
            self.alarm_time = now() + duration
        else:
            self.alarm_time = None

    def is_ringing(self):
        return self.alarm_time is not None and now() > self.alarm_time

class QueueMonitor:
    def __init__(self, connection, queue):
        self._connection = connection
        self._queue = queue
        self._latest = None

    def latest(self):
        messages = self._connection.get_all_messages(self._queue)
        if len(messages) > 0:
            self._latest = messages[-1]
        return self._latest
