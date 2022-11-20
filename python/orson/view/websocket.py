from queue import Queue, Empty
from . import sock, websockets
from flask_sock import ConnectionClosed
from flask import session


@sock.route('/ws')
def echo(ws):
    queue = Queue()
    websockets[ws] = [queue]
    while True:
        try:
            command = queue.get(timeout=1)
            ws.send(command)
        except Empty:
            pass
        except ConnectionClosed:
            break
    if ws in websockets:
        del websockets[ws]