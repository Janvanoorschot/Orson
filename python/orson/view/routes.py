import os
from flask import render_template, send_from_directory, session, Blueprint
from . import Client, manager, keeper, sessions

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
    map = {
        'rooms': keeper.get_rooms()
    }
    return render_template("rooms_matrix.html", **map)


@route_blueprint.route('/enter_room/<room_id>')
def enter_room(room_id):
    if keeper.has_room(room_id):
        room = keeper.get_room(room_id)
        manager.enter_room(sessions[session['client_id']].client, room)
        return f'''<div id="messages">Entering room {room.name}</div>'''
    else:
        return f'''<div id="messages">Trying to enter unknown room {room_id}</div>'''

@route_blueprint.route('/leave_room')
def leave_room(room_id):
    client: Client = sessions[session['client_id']].client
    if client.in_room():
        manager.leave_room(client)
        return f'''<div id="messages">Leaving room</div>'''
    else:
        return f'''<div id="messages">Failed to leave room</div>'''

