from pika import BlockingConnection, ConnectionParameters

EXCHANGE_NAME = 'alexandra'

def create_channel():
    connection = BlockingConnection(ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, type='topic')
    return channel

def publish(channel, label, message):
    channel.basic_publish(exchange=EXCHANGE_NAME,
                          routing_key=label,
                          body=message)

def subscribe(channel, label):
    result = channel.queue_declare(exclusive=True)
    queue = result.method.queue
    channel.queue_bind(exchange=EXCHANGE_NAME,
                       queue=queue,
                       routing_key=label)
    return queue

def unsubscribe(channel, queue, label):
    channel.queue_unbind(exchange=EXCHANGE_NAME, queue=queue, routing_key=label)

def consume(channel, queue, f):
    def callback(ch, method, properties, body):
        f(body)

    channel.basic_consume(callback, queue=queue, no_ack=True)
    channel.start_consuming()

class QueueMonitor:
    def __init__(self, channel, queue):
        self._channel = channel
        self._queue = queue
        self._latest = None

    def latest(self):
        messages = get_all_messages(self._channel, self._queue)
        if len(messages) > 0:
            self._latest = messages[-1]
        return self._latest

def get_message(channel, queue):
    return channel.basic_get(0, queue=queue, no_ack=True)[2]

def get_all_messages(channel, queue):
    messages = []
    while True:
        message = get_message(channel, queue)
        if message is None:
            return messages
        else:
            messages.append(message)

def get_message_block(channel, queue):
    while True:
        message = get_message(channel, queue)
        if message is not None:
            return message
