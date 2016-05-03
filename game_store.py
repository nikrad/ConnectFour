import cPickle

import redis
from shortuuid import ShortUUID
from board_model import (
    Board,
    DiscType,
)

REDIS_CONNECTION_SETTINGS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
}

redis_client = redis.StrictRedis(**REDIS_CONNECTION_SETTINGS)


def set_value(key, value):
    redis_client.set(key, cPickle.dumps(value))


def get_value(key):
    pickled_value = redis_client.get(key)
    if pickled_value is None:
        return None

    return cPickle.loads(pickled_value)


### Exceptions ###

class GameError(Exception):
    pass


class GameOverError(GameError):
    pass


class OutOfTurnError(GameError):
    pass


class GameStore(object):
    # Getters
    @staticmethod
    def get(game_id):
        """Get data dictionary for a game.

        Args:
            game_id (str): uuid of the game

        Returns:
            The game's data dictionary if it exists, otherwise None
        """
        return get_value(game_id)

    @staticmethod
    def get_players(game_id):
        """Get a dictionary of player ids.

        Args:
            game_id (str): uuid of the game

        Returns:
            a map from player id to player position integer
        """
        game = get_value(game_id)
        return game["player_positions"]

    @staticmethod
    def get_open_connections(game_id, player_id):
        """Check how many socket connections the player has open.

        Args:
            game_id (str): uuid of the game
            player_id (str): uuid of the player

        Returns:
            an integer count of how many open socket connections the player has
        """
        game = get_value(game_id)
        return game["player_open_connections"].get(player_id)

    # Setters
    @staticmethod
    def create():
        """Create a new game.

        Returns:
            The new game's data dictionary
        """
        new_game_id = ShortUUID().random(length=12)
        new_game = {
            "game_id": new_game_id,
            "player_positions": {},
            "player_open_connections": {},
            "grid": Board().grid,
            "position_with_turn": 1,
            "winner": None,
        }
        # TODO(nikrad): add locking
        set_value(new_game_id, new_game)

        return new_game_id

    @staticmethod
    def restart(game_id):
        """Restart a game after it ends.

        Args:
            game_id (str): uuid of the game

        Returns:
            The latest game data dictionary
        """
        game = get_value(game_id)
        assert game
        assert game["winner"] is not None

        game["grid"] = Board().grid
        game["position_with_turn"] = 1
        game["winner"] = None

        # TODO(nikrad): add locking
        set_value(game["game_id"], game)

        return game

    @staticmethod
    def play_turn(game_id, player_id, column_index):
        """Play a Connect Four turn.

        Args:
            game_id (str): uuid of the game
            player_id (str): uuid of the player
            column_index (int): index of the grid column in which to drop a disc

        Returns:
            The latest game data dictionary

        Raises:
            OutOfTurnError: if it's not the player's turn
            GridColumnFullError: if the chosen grid column is already full
            GameOverError: if the game has finished
        """
        # TODO(nikrad): add locking
        game = get_value(game_id)
        if game["winner"] is not None:
            raise GameOverError("The game has ended")

        position = game["player_positions"].get(player_id)
        assert position

        if position != game["position_with_turn"]:
            raise OutOfTurnError("It's not player %d's turn." % position)

        board = Board(game["grid"])
        last_move_row_index, last_move_column_index = board.drop_disc(column_index, DiscType(position))
        winner = board.is_winning_disc(last_move_row_index, last_move_column_index)
        if winner:
            game["winner"] = winner
        else:
            if board.is_full():
                game["winner"] = 0
            else:
                next_position = 2 if game["position_with_turn"] == 1 else 1
                game["position_with_turn"] = next_position

        set_value(game["game_id"], game)

        return game

    @staticmethod
    def add_player_connection(game_id, player_id):
        """Increment a player's connection count.

        Args:
            game_id (str): uuid of the game
            player_id (str): uuid of the player

        Returns:
            the player's position integer
        """
        # TODO(nikrad): add locking
        game = get_value(game_id)
        if player_id not in game["player_open_connections"]:
            game["player_open_connections"][player_id] = 1
        else:
            game["player_open_connections"][player_id] += 1
        set_value(game["game_id"], game)

        return game["player_open_connections"][player_id]

    @staticmethod
    def remove_player_connection(game_id, player_id):
        """Decrement a player's connection count.

        Args:
            game_id (str): uuid of the game
            player_id (str): uuid of the player

        Returns:
            the player's position integer
        """
        # TODO(nikrad): add locking
        game = get_value(game_id)
        open_connections = game["player_open_connections"].get(player_id)
        assert open_connections, "Player has no open connections"

        game["player_open_connections"][player_id] -= 1
        set_value(game["game_id"], game)

        return game["player_open_connections"][player_id]

    @staticmethod
    def add_player(game_id, player_id):
        """Add a player to the game.

        Args:
            game_id (str): uuid of the game
            player_id (str): uuid of the player

        Returns:
            the player's position integer
        """
        # TODO(nikrad): add locking
        game = get_value(game_id)
        assert len(game["player_positions"]) < 2, "This game is full"
        assert player_id not in game["player_positions"], "This player has already joined the game"

        position = 2 if game["player_positions"].values() == [1] else 1
        game["player_positions"][player_id] = position
        if player_id not in game["player_open_connections"]:
            game["player_open_connections"][player_id] = 1
        else:
            game["player_open_connections"][player_id] += 1

        set_value(game["game_id"], game)

        return position

    @staticmethod
    def remove_player(game_id, player_id):
        """Remove a player from the game.

        Args:
            game_id (str): uuid of the game
            player_id (str): uuid of the player
        """
        game = get_value(game_id)
        assert player_id in game["player_positions"], "Player not in game"
        assert player_id in game["player_open_connections"], "Missing player connection"

        del game["player_open_connections"][player_id]
        del game["player_positions"][player_id]

        set_value(game_id, game)