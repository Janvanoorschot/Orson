
from flask import Blueprint, request
from . import keeper

event_blueprint = Blueprint('event_blueprint', __name__, url_prefix='/events')


@event_blueprint.route('/alert', methods=['POST'])
def alert():
    message = request.get_json(silent=True)
    keeper.announcement(message)
    return message


