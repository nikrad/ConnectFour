# Connect Four

A bare-bones, web-based Connect Four game using WebSockets.

## Supported platforms

The app has been tested using:

* Mac OS X 10.11.4
* Python 2.7.10
* Google Chrome 50.0.2661
* Redis 3.0.7

## How to run

First, make sure you've installed the app's dependencies from the `requirements.txt` file:

```
pip install -r requirements.txt
```

Check that your Redis server is running and update `REDIS_CONNECTION_SETTINGS` in `game_store.py` if necessary. Then run the Flask web server:

```
python app.py
```

Lastly, visit `http://localhost:5000` in your browser to start a new game. Have fun!
