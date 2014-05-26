require "bunny"

module Pubsub

  class AMQPConnection
    def initialize(url, exchange_name, marshal, unmarshal)
      host = %r{amqp://(\w+)}.match(url)[1]
      conn = Bunny.new(:hostname => host)
      conn.start
      @channel = conn.create_channel
      @exchange = @channel.topic(exchange_name)
      @marshal, @unmarshal = marshal, unmarshal
    end

    def publish(topic, message)
      @exchange.publish(@marshal.call(message), :routing_key => topic)
    end

    def subscribe(topic)
      queue = @channel.queue("")
      queue.bind(@exchange, :routing_key => topic)
      return queue
    end

    def unsubscribe(queue)
      queue.delete
    end

    def consume_queue(queue, &block)
      queue.subscribe(:block => true) do |di, p, body|
        block.call(@unmarshal.call(body))
      end
    end

    def consume_topic(topic, &block)
      queue = subscribe(topic)
      consume_queue(queue, block)
    end

    def get_message(queue)
      delivery_info, properties, raw_message = queue.pop
      if nil != raw_message
        @unmarshal.call(raw_message)
      else
        nil
      end
    end

    def get_all_messages(queue)
      messages = []
      loop do
        message = get_message(queue)
        break if message == nil
        messages.push message
      end
      return messages
    end

    def get_message_block(queue, timeout=nil)
      alarm = Alarm.new(timeout)
      loop do
        message = get_message(queue)
        if message != nil
          return message
        elsif alarm.is_ringing()
          return nil
        end
      end
    end
  end

  def Pubsub.connect(url, exchange_name, marshal=-> x {x}, unmarshal=-> x {x})
    connection_classes = {'amqp' => AMQPConnection}
    protocol = %r{(\w+)://}.match(url)[1]
    conn_class = connection_classes[protocol]
    return conn_class.new(url, exchange_name, marshal, unmarshal)
  end

  class Alarm
    def initialize(duration=nil)
      if duration != nil
        @alarm_time = Time.now + duration
      else
        @alarm_time = nil
      end
    end

    def is_ringing()
      @alarm_time != nil and Time.now > @alarm_time
    end
  end

  class QueueMonitor
    def initialize(connection, queue)
      @connection = connection
      @queue = queue
      @latest = nil
    end

    def latest()
      messages = @connection.get_all_messages(@queue)
      if not messages.empty?
        @latest = messages.last
      end
      return @latest
    end
  end
end
