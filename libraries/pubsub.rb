require 'bunny'
require 'net/http'

EXCHANGE = 'alexandra'
HTTP_PATIENCE_SEC = 1

module Pubsub

  class AMQPConnection
    def initialize(url, context, marshal, unmarshal)
      host = %r{amqp://([\w\d\.]+)}.match(url)[1]
      conn = Bunny.new(:hostname => host)
      conn.start
      @channel = conn.create_channel
      @exchange = @channel.topic(EXCHANGE)
      @context = context
      @marshal, @unmarshal = marshal, unmarshal
    end

    def publish(topic, message)
      @exchange.publish(@marshal.call(message),
                        :routing_key => @context + '.' + topic)
    end

    def subscribe(topic)
      queue = @channel.queue("")
      queue.bind(@exchange, :routing_key => @context + '.' + topic)
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
      consume_queue(queue, &block)
    end

    def consume_all(&block)
      return nil # not implemented
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

    def make_topic_monitor(topic)
      return nil # not implemented
    end
  end

  class HTTPConnection
    def initialize(url, context, marshal, unmarshal)
      m = %r{http://([\w\d\.]+):(\d+)}.match(url)
      host, port = m[1], m[2].to_i
      @http = Net::HTTP.new(host, port)
      @prefix = '/contexts/%s' % context
      @marshal, @unmarshal = marshal, unmarshal
    end

    def publish(topic, message)
      path = '%s/%s' % [@prefix, topic]
      @http.send_request('POST', path, @marshal.call(message))
    end

    def subscribe(topic)
      response = @http.get('%s/%s' % [@prefix, topic])
      if response.code == "200"
        response.body
      else
        nil
      end
    end

    def consume_queue(queue, &block)
      path = '%s/queues/%s' % [@prefix, queue]
      loop do
        response = @http.get(path, {'Patience' => HTTP_PATIENCE_SEC.to_s})
        if response.code == "200" and response.body.length > 0
          block.call(@unmarshal.call(response.body))
        end
      end
    end

    def consume_topic(topic, &block)
      queue = subscribe(topic)
      consume_queue(queue, &block)
    end

    def consume_all(&block)
      return nil # not implemented
    end

    def unsubscribe(topic)
      path = '%s/queues/%s' % [@prefix, queue]
      @http.send_request('DELETE', path)
    end

    def get_message(queue)
      response = @http.get('%s/queues/%s' % [@prefix, queue])
      if response.code == "200" and response.body.length > 0
        @unmarshal.call(response.body)
      else
        nil
      end
    end

    def get_all_messages(queue)
      path = '%s/queues/%s' % [@prefix, queue]
      response = @http.get(path, {'Range' => 'all'})
      if response.code == "200" and response.body.length > 0
        messages = response.body.split("\n")
        messages.map(&@unmarshal)
      else
        nil
      end
    end

    def get_message_block(queue, timeout)
      path = '%s/queues/%s' % [@prefix, queue]
      alarm = Alarm.new(timeout)
      loop do
        response = @http.get(path, {'Patience' => HTTP_PATIENCE_SEC.to_s})
        if response.code == "200" and response.body.length > 0
          return @unmarshal.call(response.body)
        elsif alarm.is_ringing()
          return nil
        end
      end
    end

    def make_topic_monitor(topic)
      return nil # not implemented
    end
  end

  def Pubsub.connect(url, context, marshal=-> x {x}, unmarshal=-> x {x})
    connection_classes = {'amqp' => AMQPConnection, 'http' => HTTPConnection}
    protocol = %r{(\w+)://}.match(url)[1]
    conn_class = connection_classes[protocol]
    return conn_class.new(url, context, marshal, unmarshal)
  end

  def Pubsub.firehose(url)
    return nil # not implemented
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
