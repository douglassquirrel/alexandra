#! /usr/bin/env ruby

require './alexandra.rb'
require 'json'

INDEX = ARGV[2].to_i
NAME = 'opponent_random_%s' % INDEX
WIDTH = 20
HEIGHT = 20
COLOUR = [255, 0, 0]
DELTAS = [[-5, 0], [5, 0], [0, -5], [0, 5]]

def init(alex)
  alex.docstore.put({'width' => WIDTH, 'height' => HEIGHT,
                      'colour' => COLOUR}.to_json,
                      '/opponent_random/opponent_random.json')
end

def move(world, alex)
  if not world['entities'].has_key? NAME
    position = [alex.config['player_start_x'] + 80 * (INDEX + 1),
                alex.config['player_start_y']]
    send_movement(position, position, world['tick'], alex)
    return
  end

  if not world['movements'].has_key? NAME
    delta = DELTAS.sample
  else
    movement = world['movements'][NAME]
    delta = [movement['to'][0] - movement['from'][0],
             movement['to'][1] - movement['from'][1]]
    if delta[0] == 0 and delta[1] == 0
      delta = DELTAS.sample
    end
  end

  position = world['entities'][NAME]['position']
  new_position = [position[0] + delta[0], position[1] + delta[1]]
  send_movement(position, new_position, world['tick'], alex)
end

def send_movement(from_position, to_position, tick, alex)
  movement = {'tick' => tick,
              'entity' => 'opponent_random', 'index' => INDEX,
              'from' => from_position, 'to' => to_position}
  alex.pubsub.publish('movement.opponent_random', movement)
end

alex = Alexandra::Alex.new(ARGV[0], ARGV[1])
init(alex)
alex.pubsub.consume_topic('world') { |w| move(w, alex)}
