require './docstore.rb'
require 'json'
require './pubsub.rb'

module Alexandra

  def Alexandra.request_game(game_name, game_id, pubsub_url, timeout=5)
    emcee_pubsub = Pubsub::connect(pubsub_url, 'emcee',
                                  marshal=-> x {x.to_json},
                                  unmarshal=-> x {JSON.parse(x)})
    game_pubsub = Pubsub::connect(pubsub_url, game_id)
    game_state_queue = game_pubsub.subscribe('game_state')

    game_info = {'name' => game_name, 'id' => game_id}
    emcee_pubsub.publish('game.wanted', game_info)

    return game_pubsub.get_message_block(game_state_queue, timeout) != nil
  end

  class Alex
    attr_reader :game_id, :pubsub, :docstore, :config

    def initialize(docstore_url, game_id, pubsub_url=nil)
      @game_id = game_id
      if pubsub_url == nil
        pubsub_url = Docstore::connect(docstore_url).get('/services/pubsub')
      end
      @pubsub = Pubsub::connect(pubsub_url, game_id,
                                marshal=-> x {x.to_json},
                                unmarshal=-> x {JSON.parse(x)})
      @docstore = Docstore::connect(docstore_url + "/" + game_id)
      @config = JSON.parse(@docstore.get('/game.json'))
    end
  end
end
