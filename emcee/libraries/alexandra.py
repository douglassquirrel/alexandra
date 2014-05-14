from docstore import connect as docstore_connect
from json import dumps, loads
from pubsub import connect as pubsub_connect
from sys import argv

def request_game(game_name, game_id, pubsub_url='amqp://localhost'):
    connection = pubsub_connect(pubsub_url, 'emcee')
    game_info = {'name': game_name, 'id': game_id}
    connection.publish('game.wanted', dumps(game_info))

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
        if fetch_game_config is True:
            self._wait_for_game_config()

    def _wait_for_game_config(self):
        config_file = None
        while config_file is None:
            config_file = self.docstore.get('/game.json')
        self.config = loads(config_file)
