import os
from flask import render_template, send_from_directory, session, Blueprint, request
from . import keeper, csrf
import uuid
route_blueprint = Blueprint('route_blueprint', __name__)


@route_blueprint.before_request
def do_before_request():
    if 'user' not in session:
        session['user'] = {}
        session['user']['id'] = uuid.uuid4()


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
    rooms = keeper.get_rooms()
    lines = []
    for id, name in rooms.items():
        lines.append(f"""<li id="{id}" class="list-group-item">{name}</li>""")
    return f'''<ul class="list-group">\n{" ".join(lines)}\n</ul>'''


@route_blueprint.route('/alert', methods=['POST'])
@csrf.exempt
def alert():
    message = request.get_json(silent=True)
    keeper.announcement(message)
    return message


