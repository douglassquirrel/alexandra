from json import dumps, loads
from os import getenv
from pubsub import connect as pubsub_connect

def request_game(game_name, game_id, pubsub_url, timeout=5):
    emcee_pubsub = pubsub_connect(pubsub_url, 'emcee', marshal=dumps)
    game_pubsub = pubsub_connect(pubsub_url, 'games-' + game_id)
    game_state_queue = game_pubsub.subscribe('game_state')

    game_info = {'name': game_name, 'id': game_id}
    emcee_pubsub.publish('game.wanted', game_info)

    return game_pubsub.get_message_block(game_state_queue, timeout) is not None

class Alexandra:
    def __init__(self, game_id):
        self.game_id = game_id
        pubsub_url = getenv('ALEXANDRA_PUBSUB')
        self.pubsub = pubsub_connect(pubsub_url, 'games-' + game_id,
                                     marshal=dumps, unmarshal=loads)
        self.config = None
        while self.config is None:
            self.config = self.pubsub.get_current_message('game.json')
