require './docstore.rb'
require './pubsub.rb'

module Alexandra

  def Alexandra.request_game(game_name, game_id, pubsub_url, timeout=5)
    emcee_pubsub = pubsub.connect(pubsub_url, 'emcee', marshal=xxx)   
    game_pubsub = pubsub.connect(pubsub_url, game_id)
    game_state_queue = game_pubsub.subscribe('game_state')

    game_info = {'name' => game_name, 'id' => game_id}
    emcee_pubsub.publish('game_wanted', game_info)

    return game_pubsub.get_message_block(game_state_queue, timeout) != nil
  end
end
