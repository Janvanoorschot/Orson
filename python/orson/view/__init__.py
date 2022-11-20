app = None
connection = None
sock = None
csrf = None
jwks = None

websockets = {}

from .mq import MessageQueue
from .roomkeeper import RoomKeeper
mq: MessageQueue = None
keeper: RoomKeeper = None


