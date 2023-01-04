import os
from flask import Flask
from .config import Default
import orson.view
from flask_sock import Sock


def callback(type, message):
    if type == 'room':
        # this is an announcement, send it up to the webserver
        orson.view.keeper.announcement(message)


def create_app(config=None):
    proj_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    static_path = os.path.join(proj_path, 'web/static')
    templates_path = os.path.join(proj_path, 'web/templates')

    app = Flask(__name__,
                static_url_path='/static',
                static_folder=static_path,
                template_folder=templates_path
                )
    if config is not None:
        app.config.from_pyfile(config)
    else:
        app.config.from_object(Default)

    # create the room-keeper
    orson.view.keeper = RoomKeeper()

    # start the message-queue
    orson.view.mq = MessageQueue('amqp://orson:orson@127.0.0.1:8001/%2F')
    orson.view.mq.init(callback)

    # attach the websocket
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        orson.view.sock = Sock(app)

    @orson.view.sock.route('/ws')
    def connect_ws(ws):
        from queue import Queue, Empty
        from flask_sock import ConnectionClosed
        queue = Queue()
        websockets[ws] = [queue]
        while True:
            try:
                command = queue.get(timeout=1)
                ws.send(command)
            except Empty:
                pass
            except ConnectionClosed:
                break
        if ws in websockets:
            del websockets[ws]

    # attach the 'normal' routes using a blueprint
    from .routes import route_blueprint
    app.register_blueprint(route_blueprint)

    return app

connection = None
sock = None
csrf = None
jwks = None

websockets = {}

from .mq import MessageQueue
from .roomkeeper import RoomKeeper
mq: MessageQueue = None
keeper: RoomKeeper = None


