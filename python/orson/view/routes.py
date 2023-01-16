import os
import datetime
import uuid
from flask import render_template, send_from_directory, session, Blueprint, request
from . import keeper, csrf, ClientSession, sessions
route_blueprint = Blueprint('route_blueprint', __name__)

zero_session = ClientSession("0", datetime.datetime.now())
sessions["0"] = zero_session



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
    client_id = session.get('client_id', None)
    if client_id:
        return sessions[client_id].enter_room(room_id, keeper)
    else:
        return f'''<div id="messages">huh?</div>'''



@route_blueprint.route('/events/alert', methods=['POST'])
@csrf.exempt
def alert():
    message = request.get_json(silent=True)
    keeper.announcement(message)
    return message


