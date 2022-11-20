import os
from flask import render_template, send_from_directory, Flask, session
from . import app, keeper
import uuid


@app.before_request
def do_before_request():
    if 'user' not in session:
        session['user'] = {}
        session['user']['id'] = uuid.uuid4()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, '../web/static'),
                               './img/favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def front_page():
    map = {}
    return render_template("front.html", **map)


@app.route('/content')
def content():
    html = """
    <div>
        This is some text that is inserted
        by Python.<br>
        So we hove this is all there is.
    </div>
    """
    return html


@app.route('/rooms')
def rooms():
    rooms = keeper.get_rooms()
    lines = []
    for id, name in rooms.items():
        lines.append(f"""<li id="{id}" class="list-group-item">{name}</li>""")
    return f'''<ul class="list-group">\n{" ".join(lines)}\n</ul>'''
