import simplejson as json

from game_store import GameStore


def json_game_state(game):
    """Convert game dictionary to JSON object with game state to send to clients.

    Args:
        game (dict): the game data dictionary

    Returns:
        JSON object with game state for clients
    """
    return json.dumps(dict(
        grid=game["grid"],
        position_with_turn=game["position_with_turn"],
        player_count=len(game["player_positions"]),
        winner=game["winner"],
    ))


def authenticate(session):
    """Authenticate a WebSocket request.

    Args:
        session (session): Flask's session object

    Returns:
        If the session's game id and player id correctly match an existing game, we'll return
        the tuple (game, player_id), otherwise we'll return (None, None)
    """

    session_game_id = session.get('game_id')
    session_player_id = session.get('player_id')
    game = GameStore.get(session_game_id)
    positions_by_player_id = game["player_positions"]
    if not game or session_player_id not in positions_by_player_id:
        return None, None

    return game, session_player_id


