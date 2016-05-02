import simplejson as json

from flask import (
    abort,
    Flask,
    redirect,
    render_template,
    session,
    url_for,
)
from flask.ext.socketio import (
    disconnect,
    emit,
    join_room,
    leave_room,
    rooms,
    SocketIO,
)
from shortuuid import ShortUUID

from board_model import GridColumnFullError
from game_store import (
    GameOverError,
    GameStore,
    OutOfTurnError,
)
from helpers import (
    authenticate,
    json_game_state,
)


### App configuration ###

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret!'
)
socketio = SocketIO(app)


### Routes ###

# TODO(nikrad): Add docstrings for routes

@app.route('/')
def index():
    new_game_id = GameStore.create()
    return redirect(url_for('game_page', game_id=new_game_id))


@app.route('/<game_id>')
def game_page(game_id):
    # Validate game id
    game = GameStore.get(game_id)
    if not game:
        abort(404)

    session_game_id = session.get('game_id')
    session_player_id = session.get('player_id')
    players = GameStore.get_players(game_id)
    if session_game_id != game.get('game_id') or session_player_id not in players:
        if len(players) == 2:
            # The game is full
            return render_template('game_is_full.html')

        # New player
        new_player_id = ShortUUID().random(length=16)
        position = GameStore.add_player(game_id, new_player_id)

        session['game_id'] = game_id
        session['player_id'] = new_player_id
    else:
        GameStore.add_player_connection(game_id, session_player_id)
        position = game["player_positions"][session_player_id]

    return render_template(
        "game.html",
        game_id=game_id,
        player_id=session['player_id'],
        position=position,
    )


@socketio.on('connect')
def handle_connect():
    game, player_id = authenticate(session)
    players = game["player_positions"]
    if not game:
        print('Invalid connection. Disconnecting!')
        return disconnect()

    game_id = game["game_id"]
    print("Player %d connected to game %s" % (players[player_id], game_id))
    if game_id not in rooms():
        join_room(game_id)

    json_data = json_game_state(game)
    emit('game_state', json_data, room=game_id)


@socketio.on('drop_disc')
def handle_drop_disc(json_data):
    game, player_id = authenticate(session)
    if not game:
        print('Invalid connection. Disconnecting!')
        return disconnect()

    # Play disc
    data = json.loads(json_data)
    column_index = data.get('column_index')
    game_id = game["game_id"]
    try:
        game = GameStore.play_turn(game_id, player_id, column_index)
        json_data = json_game_state(game)
        emit('game_state', json_data, room=game_id)
    except OutOfTurnError:
        print("Player %d out of turn" % game["player_positions"][player_id])
        data = dict(message="It's not your turn!")
        emit("alert", json.dumps(data))
    except GridColumnFullError:
        print("Column %d is full" % column_index)
        data = dict(message="This column is full. Please pick another column.")
        emit("alert", json.dumps(data))
    except GameOverError:
        print("The game has ended")
        data = dict(message="The game is over!")
        emit("alert", json.dumps(data))


@socketio.on('disconnect')
def handle_disconnect():
    game, player_id = authenticate(session)
    game_id = game["game_id"]
    players = game["player_positions"]

    if game and player_id in players:
        connections = GameStore.get_open_connections(game_id, player_id)
        position = game["player_positions"][player_id]
        if connections > 1:
            connections = GameStore.remove_player_connection(game_id, player_id)
            print("Player %d closed a window for game %s. %d windows left." % (position, game_id, connections)
            )
        else:
            GameStore.remove_player(game_id, player_id)
            leave_room(room=game_id)
            print("Player %s left game %s" % (position, game_id))

        emit('game_state', json.dumps(game), room=game_id)


if __name__ == '__main__':
    socketio.run(app)