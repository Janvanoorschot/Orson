import os
import datetime
import uuid
from flask import Flask, session, request
from flask_sock import Sock
from flask_wtf.csrf import CSRFProtect

from .config import Default
import orson

sessions = {}
websockets = {}

from .room_keeper import RoomKeeper
from .client_manager import ClientManager
from .client_session import ClientSession

connection = None
sock = None
csrf = None
jwks = None


keeper: RoomKeeper
manager: ClientManager


def create_app(config=None):
    proj_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    static_path = os.path.join(proj_path, 'web/static')
    templates_path = os.path.join(proj_path, 'web/templates')

    app = Flask(__name__,
                static_url_path='/static',
                static_folder=static_path,
                template_folder=templates_path
                )
    # load the defaults from a static Object inside the project
    app.config.from_object(Default)
    if config is not None:
        app.config.from_mapping(config)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    # enable CSRF protection
    orson.view.csrf = CSRFProtect(app)
    orson.view.jwks = []

    # create the room-keeper
    orson.view.keeper = RoomKeeper()
    orson.view.manager = ClientManager()

    # attach the websocket
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        orson.view.sock = Sock(app)

    @app.before_request
    def do_before_request():
        if 'client_id' not in session or session['client_id'] not in sessions:
            if not request.url_rule.rule.startswith("/events"):
                client_id = str(uuid.uuid4())
                t = datetime.datetime.now()
                sessions[client_id] = ClientSession(client_id, t)
                session['client_id'] = client_id
            else:
                session['client_id'] = "0"
            session.modified = True


    @orson.view.sock.route('/ws')
    def connect_ws(ws):
        from queue import Queue, Empty
        from flask_sock import ConnectionClosed
        queue = Queue()
        websockets[ws] = [queue]
        while True:
            try:
                html_blob = queue.get(timeout=1)
                ws.send(html_blob)
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
