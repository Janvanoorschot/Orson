
from flask import Blueprint, request, current_app

event_blueprint = Blueprint('event_blueprint', __name__, url_prefix='/events')


@event_blueprint.route('/alert', methods=['POST'])
def alert():
    keeper = current_app.extensions["orson"]["keeper"]
    message = request.get_json(silent=True)
    keeper.announcement(message)
    return message

@event_blueprint.route('/announcements', methods=['GET'])
def announcements():
    keeper = current_app.extensions["orson"]["keeper"]
    return keeper.get_announcements()




