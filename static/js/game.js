'use strict';


// TODO(nikrad): Move components into separate files and explicitly declare dependencies via CommonJS or Require JS

class GameState {
    constructor (grid, playerCount, positionWithTurn, winner) {
        this.grid = grid;
        this.playerCount = playerCount;
        this.positionWithTurn = positionWithTurn;
        this.winner = winner;
    }

    static fromJSON(jsonString) {
        var data = JSON.parse(jsonString);
        return new GameState(data.grid, data.player_count, data.position_with_turn, data.winner);
    }
}


var BoardCell = React.createClass({
    displayName: 'BoardCell',

    propTypes: {
        columnIndex: React.PropTypes.number.isRequired,
        discType: React.PropTypes.number.isRequired,
        gameState: React.PropTypes.instanceOf(GameState),
        onClickCell: React.PropTypes.func.isRequired,
        playerPosition: React.PropTypes.number.isRequired
    },

    render: function () {
        var discClass = classNames({
            cell_dimension: true,
            disc: true,
            empty: this.props.discType === 0,
            player1: this.props.discType === 1,
            player2: this.props.discType === 2
        });
        var disc = React.createElement('div', {className: discClass}, '')

        return React.createElement('td', {className: 'cell_dimension', onClick: this.onClick}, disc);
    },

    onClick: function () {
        if (this.props.gameState.winner !== null) {
            alert('The game is over!');
        } else {
            if (this.props.gameState.playerCount === 2) {
                // The game is on!
                if (this.props.gameState.positionWithTurn === this.props.playerPosition) {
                    // Your move!
                    console.log('Clicked column ' + this.props.columnIndex);
                    this.props.onClickCell(this.props.columnIndex);
                } else {
                    alert("It's not your turn!");
                }
            } else {
                alert('Waiting for another player to join.');
            }
        }
    }
});


var Board = React.createClass({
    displayName: 'Board',

    propTypes: {
        gameState: React.PropTypes.instanceOf(GameState),
        onClickCell: React.PropTypes.func.isRequired,
        playerPosition: React.PropTypes.number.isRequired
    },

    render: function () {
        var getCell = (function (discType, j) {
            return React.createElement(BoardCell, {
                columnIndex: j,
                discType: discType,
                gameState: this.props.gameState,
                key: j,
                onClickCell: this.props.onClickCell,
                playerPosition: this.props.playerPosition
            });
        }).bind(this);

        var rows = this.props.gameState.grid.map(function (row, i) {
            var cells = row.map(getCell);
            return React.createElement('tr', {key: i}, cells);
        });

        return React.createElement(
            'table',
            {className: 'board'},
            React.createElement('tbody', {}, rows)
        );
    }
});


var WelcomeBar = React.createClass({
    displayName: 'WelcomeBar',

    propTypes: {
        playerColor: React.PropTypes.string.isRequired
    },

    render: function () {
        return React.createElement('p', {}, `Welcome! Your color is ${this.props.playerColor}.`)
    }
});


var StatusBar = React.createClass({
    displayName: 'StatusBar',

    propTypes: {
        gameState: React.PropTypes.instanceOf(GameState),
        onClickRestart: React.PropTypes.func.isRequired,
        playerPosition: React.PropTypes.number.isRequired
    },

    onClickRestart: function (e) {
        e.preventDefault();
        this.props.onClickRestart();
    },

    render: function () {
        var message, restart;
        if (this.props.gameState.winner !== null) {
            // The game is over
            if (this.props.gameState.winner === 0) {
                message = 'The game ended with no winner. '
            } else {
                message = this.props.playerPosition === this.props.gameState.winner ? "You won! " : "Sorry, you lost. ";
            }

            restart = React.createElement('a', {href: "#", onClick: this.onClickRestart}, 'Play again.');
        } else {
            if (this.props.gameState.playerCount === 2) {
                // The game is on!
                if (this.props.gameState.positionWithTurn === this.props.playerPosition) {
                    // Your move!
                    message = "It's your move.";
                } else {
                    // Waiting for other player to move
                    message = "Waiting for the other player to move."
                }
            } else {
                // Waiting for other player to join
                message = 'Waiting for another player to join.';
            }

            restart = React.createElement('span', {}, '');
        }

        var messageSpan = React.createElement('span', {}, message);

        return React.createElement('p', {className: 'status_bar'}, [messageSpan, restart]);
    }
});


var GameView = React.createClass({
    displayName: 'GameView',

    propTypes: {
        gameState: React.PropTypes.instanceOf(GameState),
        onClickCell: React.PropTypes.func.isRequired,
        onClickRestart: React.PropTypes.func.isRequired,
        playerColor: React.PropTypes.string.isRequired,
        playerPosition: React.PropTypes.number.isRequired
    },

    render: function () {
        return React.createElement('div', {}, [
            React.createElement(WelcomeBar, {
                key: 'welcome-bar',
                playerColor: this.props.playerColor
            }),
            React.createElement(StatusBar, {
                key: 'status-bar',
                gameState: this.props.gameState,
                onClickRestart: this.props.onClickRestart,
                playerPosition: this.props.playerPosition
            }),
            React.createElement(Board, {
                key: 'board',
                gameState: this.props.gameState,
                onClickCell: this.props.onClickCell,
                playerPosition: this.props.playerPosition,
            })
        ]);
    }
});


class Game {
    constructor (playerPosition) {
        this.playerPosition = playerPosition;
        this.playerColor = this.playerPosition === 1 ? 'yellow' : 'red';

        this.socket = io();
        this.socket.on('connect', this.handleConnect.bind(this));
    }

    handleConnect () {
        console.log('Connection established');
        this.listen();
    }

    listen () {
        this.socket.on('game_state', this.handleGameState.bind(this));
        this.socket.on('alert', this.handlerAlert);
    }

    handlerAlert (json) {
        var data = JSON.parse(json);
        alert(data.message);
    }

    handleGameState (jsonString) {
        var gameState = GameState.fromJSON(jsonString);
        console.log(gameState);

        ReactDOM.render(
            React.createElement(GameView, {
                gameState: gameState,
                onClickCell: this.dropDisc.bind(this),
                onClickRestart: this.restart.bind(this),
                playerColor: this.playerColor,
                playerPosition: this.playerPosition
            }),
            document.getElementById('game')
        );
    }

    dropDisc (columnIndex) {
        console.log('Playing disc in column ' + columnIndex);
        var json = JSON.stringify({'column_index': columnIndex});
        this.socket.emit('drop_disc', json);
    }

    restart () {
        console.log('Restarting game');
        this.socket.emit('restart');
    }
}
