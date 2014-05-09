require "bunny"

module Pubsub

  class AMQPConnection
    def initialize(url, exchange_name)
      host = %r{amqp://(\w+)}.match(url)[1]
      conn = Bunny.new(:hostname => host)
      conn.start
      @channel = conn.create_channel
      @exchange = @channel.topic(exchange_name)
    end

    def publish(topic, message)
      @exchange.publish(message, :routing_key => topic)
    end

    def subscribe(topic)
      queue = @channel.queue("")
      queue.bind(@exchange, :routing_key => topic)
      return queue
    end

    def unsubscribe(queue)
      queue.delete
    end

    def consume(queue, &block)
      queue.subscribe(:block => true) do |di, p, body|
        block.call(body)
      end
    end

    def get_message(queue)
      delivery_info, properties, payload = queue.pop
      return payload
    end
  end

end
