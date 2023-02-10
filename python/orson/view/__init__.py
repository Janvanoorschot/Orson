import os
from flask import Flask, session, request
from flask_sock import Sock
from flask_wtf.csrf import CSRFProtect
from celery import Celery

from .config import Default
import orson.view
from .iface import RemoteRoom, Client, ClientManager, RoomKeeper, Caller
from .message_queue import MessageQueue
from .client_session import ClientSession, Client


# sharable components, filled during create-app()
manager: ClientManager
keeper: RoomKeeper
sessions = {}
websockets = {}
mq: MessageQueue
connection = None
sock = None
csrf = None
jwks = None


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

    #
    if app.testing:
        from .testing_caller import TestingCaller
        caller = TestingCaller()
    else:
        # create/attach celery
        from .celery_caller import CeleryCaller
        celery = make_celery(app)
        caller = CeleryCaller(celery)



    # create the main components used by the Flask calls to implement functionality
    import orson.view.room_keeper
    orson.view.keeper = room_keeper.RoomKeeperImpl(caller)
    import orson.view.client_manager
    orson.view.manager = client_manager.ClientManagerImpl(caller)

    sessions["0"] = ClientSession(manager.zero_client())

    @app.before_request
    def do_before_request():
        if 'client_id' not in session or session['client_id'] not in sessions:
            path = request.path
            if not path.startswith("/events"):
                # create a new client and session
                client = manager.create_client()
                sessions[client.client_id] = ClientSession(client)
                session['client_id'] = client.client_id
            else:
                session['client_id'] = "0"
            session.modified = True

    # attach the websocket
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        import orson.view
        orson.view.sock = Sock(app)

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
    from .events import event_blueprint
    app.register_blueprint(event_blueprint)

    if not app.testing:
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
        include=['orson.tasks']
    )
    celery.config_from_object('orson.tasks.config')
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

