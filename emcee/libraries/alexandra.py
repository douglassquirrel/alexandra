from docstore import connect as docstore_connect
from json import dumps, loads
from pubsub import connect as pubsub_connect
from sys import argv

DEFAULT_GAME_TIMEOUT = 5

def request_game(game_name, game_id, pubsub_url='amqp://localhost',
                 timeout=DEFAULT_GAME_TIMEOUT):
    emcee_pubsub = pubsub_connect(pubsub_url, 'emcee')
    game_pubsub = pubsub_connect(pubsub_url, game_id)
    game_state_queue = game_pubsub.subscribe('game_state')

    game_info = {'name': game_name, 'id': game_id}
    emcee_pubsub.publish('game.wanted', dumps(game_info))

    return game_pubsub.get_message_block(game_state_queue, timeout) is not None

class Alexandra:
    def __init__(self, game_id=None, fetch_game_config=True,
                 docstore_url='http://localhost:8080',
                 pubsub_url='amqp://localhost'):
        if game_id is None:
            game_id = argv[2]
        self.game_id = game_id
        self.pubsub = pubsub_connect(pubsub_url, game_id,
                                     marshal=dumps, unmarshal=loads)
        self.docstore = docstore_connect(docstore_url + "/" + game_id)
        self.config = loads(self.docstore.get('/game.json'))
