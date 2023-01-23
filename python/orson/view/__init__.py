import os
import asyncio
from flask import Flask, session, request
from flask_sock import Sock
from flask_wtf.csrf import CSRFProtect
from celery import Celery

from .config import Default
import orson

from .message_queue import MessageQueue
sessions = {}
websockets = {}
mq: MessageQueue
connection = None
sock = None
csrf = None
jwks = None

from .room_keeper import RoomKeeper
from .client_manager import ClientManager, Client
from .client_session import ClientSession
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
    # load the defaults from (in order):
    #   - a static Object inside the project (the default values)
    #   - a file (default is dev, optionaly overwritten during production
    #   - an (optional) argument blob
    #   - environment variables
    app.config.from_object(Default)
    if config is not None:
        app.config.from_mapping(config)
    app.config.from_prefixed_env()

    app.secret_key =app.config['SECRET_KEY']

    # attach the websocket
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        orson.view.sock = Sock(app)

    # attach the message queue
    mq = MessageQueue(app.config["PIKA_URL"])

    # create the room-keeper
    orson.view.keeper = RoomKeeper(mq)
    orson.view.manager = ClientManager()

    sessions["0"] = ClientSession(manager.zero_client(), orson.view.keeper, orson.view.manager)


    @app.before_request
    def do_before_request():
        if 'client_id' not in session or session['client_id'] not in sessions:
            if not request.url_rule.rule.startswith("/events"):
                # create a new client and session
                client = manager.create_client()
                sessions[client.client_id] = ClientSession(client, orson.view.keeper, orson.view.manager)
                session['client_id'] = client.client_id
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

    # create/attach celery
    celery = make_celery(app)
    app.celery = celery


    # attach the 'normal' routes using a blueprint
    from .routes import route_blueprint
    app.register_blueprint(route_blueprint)
    from .events import event_blueprint
    app.register_blueprint(event_blueprint)

    # enable CSRF protection
    orson.view.csrf = CSRFProtect(app)
    orson.view.jwks = []
    orson.view.csrf.exempt(event_blueprint)

    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        include=['orson.view.tasks']
    )

    class ContextTask(celery.Task):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

