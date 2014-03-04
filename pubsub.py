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

def get_message(channel, queue):
    return channel.basic_get(0, queue=queue, no_ack=True)[2]
