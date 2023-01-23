import os
import datetime
from flask import render_template, send_from_directory, session, Blueprint, request, current_app
from . import manager, keeper, csrf, ClientSession, sessions

route_blueprint = Blueprint('route_blueprint', __name__)


@route_blueprint.route('/hello')
def hello():
    return 'Hello, World!'


def favicon():
    static_path = os.path.join(route_blueprint.root_path, '../../web/static')
    return send_from_directory(static_path,'./img/favicon.ico', mimetype='image/vnd.microsoft.icon')


@route_blueprint.route('/')
def front_page():
    map = {}
    return render_template("front.html", **map)


@route_blueprint.route('/content')
def content():
    html = """
    <div>
        This is some text that is inserted
        by Python.<br>
        So we hove this is all there is.
    </div>
    """
    return html


@route_blueprint.route('/rooms')
def rooms():
    return ClientSession.rooms(keeper)

# message from client to server


@route_blueprint.route('/enter_room/<room_id>')
def enter_room(room_id):

    result = current_app.celery.send_task("tasks.publish_message", args=["ha jan"])
    r = result.get()
    return sessions[session['client_id']].enter_room(room_id)


