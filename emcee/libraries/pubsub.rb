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

    end
  end

end
