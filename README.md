# Connect Four

A bare-bones, web-based Connect Four game using WebSockets.

## Supported platforms

The app has been tested using:

* Mac OS X 10.11.4
* Python 2.7.10
* Google Chrome 50.0.2661
* Redis 3.0.7

## How to run

1. Make sure you've installed the app's dependencies from the `requirements.txt` file:

```
pip install -r requirements.txt
```

2. Check that your Redis server is running and update `REDIS_CONNECTION_SETTINGS` in `game_store.py` if necessary.

3. Run the Flask web server:

```
python app.py
```

4. Visit `http://localhost:5000` in your browser to start a new game. Have fun!
