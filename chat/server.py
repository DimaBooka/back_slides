import json
from uuid import uuid4

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from django.contrib.auth import get_user_model


from rest_framework.authtoken.models import Token

User = get_user_model()


class BroadcastServerProtocol(WebSocketServerProtocol):
    room = ''
    token = ''

    def onOpen(self):
        uuid = uuid4().hex
        self.factory.register(self, uuid)
        self.actions = {
            'leave': self.factory.leave,
            'broadcast': self.factory.broadcast,
        }

    def onMessage(self, payload, isBinary):

        if not isBinary:
            try:
                data = json.loads(payload.decode('utf8'))
                uuid = data.get('uuid', '')
                if uuid:
                    self.uuid = uuid
            except:
                self.token = payload.decode('utf-8')
                return
        broadcast = self.actions['broadcast']
        broadcast(self, payload)
        print("Some message received")

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self.uuid)


class BroadcastServerFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = {}
        self.rooms = {}

    def leave(self, data):
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            print("Disconnecting user from {} with uuid: {}".format(conn.peer, uuid))

    def register(self, client, uuid):
        if uuid not in self.clients:
            print("registered client {}, uuid: {}".format(client.peer, uuid))
            self.clients[uuid] = client

    def unregister(self, uuid):
        if uuid in self.clients:
            print("unregistered client with uuid: {}".format(uuid))
            self.clients.pop(uuid)

    def broadcast(self, conn, data):
        token = conn.http_headers.get('Authorization', conn.token)
        try:
            # token = token.split(' ')[1]
            user = Token.objects.select_related('user').get(key=token).user
        except:
            conn.sendMessage(bytes(json.dumps({'error': 'Missing or incorrect token'}), encoding='utf-8'))
            conn.dropConnection()
            return
        data_dict = json.loads(data.decode('utf-8'))
        message = json.dumps({'message': data_dict['text'], 'user': user.username})
        current_room = data_dict['room']
        if not data_dict['room'] in self.rooms.keys():
            self.rooms.update({current_room: [conn]})
        elif conn not in self.rooms[current_room]:
            self.rooms[current_room].append(conn)
        print("broadcasting message '{}' ..".format(message))
        for client in self.rooms[current_room]:
            client.sendMessage(bytes(message, encoding='utf-8'))


if __name__ == '__main__':
    import asyncio

    ServerFactory = BroadcastServerFactory

    factory = ServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = BroadcastServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 9000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
