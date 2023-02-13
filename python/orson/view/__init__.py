import os
from flask import Flask, session, request, current_app
from flask_sock import Sock
from flask_wtf.csrf import CSRFProtect
from celery import Celery, Task

from .config import Default
import orson.view
from .iface import RemoteRoom, Client, ClientManager, RoomKeeper, Caller
from .message_queue import MessageQueue
from .client_session import ClientSession, Client


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
    app.secret_key = app.config['SECRET_KEY']

    # place to store state information
    app.extensions["orson"] = {}
    app.extensions["orson"]["sessions"] = {}
    app.extensions["orson"]["websockets"] = {}

    #
    if app.testing:
        from .testing_caller import TestingCaller
        caller = TestingCaller()
    else:
        # create/attach celery
        from .celery_caller import CeleryCaller
        celery = celery_init_app(app)
        # celery = make_celery(app)
        caller = CeleryCaller(celery)

    # create the main components used by the Flask calls to implement functionality
    import orson.view.client_manager
    app.extensions["orson"]["manager"] = client_manager.ClientManagerImpl(app, caller)
    import orson.view.room_keeper
    app.extensions["orson"]["keeper"] = room_keeper.RoomKeeperImpl(app, caller)

    app.extensions["orson"]["sessions"]["0"] = ClientSession(app.extensions["orson"]["manager"].zero_client())

    @app.before_request
    def do_before_request():
        sessions = current_app.extensions["orson"]["sessions"]
        path = request.path
        if not path.startswith("/events"):
            if 'client_id' not in session or session['client_id']=='0' or session['client_id'] not in sessions:
                # create a new client and session
                client = current_app.extensions["orson"]["manager"].create_client()
                sessions[client.client_id] = ClientSession(client)
                session['client_id'] = client.client_id
                session.modified = True
        else:
            if 'client_id' not in session or session['client_id'] not in sessions:
                session['client_id'] = "0"

    # attach the websocket
    sock = None

    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        import orson.view
        sock = Sock(app)

    @sock.route('/ws')
    def connect_ws(ws):
        from queue import Queue, Empty
        from flask_sock import ConnectionClosed
        websockets = current_app.extensions["orson"]["websockets"]
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
        csrf = CSRFProtect(app)
        csrf.exempt(event_blueprint)

    return app


def celery_init_app(app: Flask) -> Celery:

    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(
        app.name,
        task_cls=FlaskTask,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        include=['orson.tasks']
    )
    celery_app.config_from_object('orson.tasks.config')
    # celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
