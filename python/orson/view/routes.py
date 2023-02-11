import os
from flask import render_template, send_from_directory, session, Blueprint, request
from . import Client, manager, keeper, sessions

route_blueprint = Blueprint('route_blueprint', __name__)


@route_blueprint.route('/hello')
def hello():
    return 'Hello, World!'


@route_blueprint.route('/favicon.ico')
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
    if request.args.get('json',None) is None:
        map = {
            'rooms': keeper.get_rooms()
        }
        return render_template("rooms_matrix.html", **map)
    else:
        result = []
        for room_id, room in keeper.get_rooms().items():
            result.append({"room_id": room.get_room_id(), "room_name": room.get_room_name()})
        return result


@route_blueprint.route('/enter_room/<room_id>', methods=['GET', 'POST'])
def enter_room(room_id):
    if keeper.has_room(room_id):
        client: Client = sessions[session['client_id']].client
        room = keeper.get_room(room_id)
        if client.is_nowhere():
            manager.enter_room(client, room)
            return f'''<div id="messages">Entering room {room.name}</div>'''
        elif client.in_room():
            manager.leave_room(client)
            return f'''<div id="messages">Leaving room {room.name}</div>'''
        else:
            return f'''<div id="messages">Invalid state to enter room</div>'''

    else:
        return f'''<div id="messages">Unknown room {room_id}</div>'''

@route_blueprint.route('/leave_room')
def leave_room(room_id):
    client: Client = sessions[session['client_id']].client
    if client.in_room():
        manager.leave_room(client)
        return f'''<div id="messages">Leaving room</div>'''
    else:
        return f'''<div id="messages">Failed to leave room</div>'''

