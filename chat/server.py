import json
from uuid import uuid4

import redis
from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from django.contrib.auth import get_user_model

from rest_framework.authtoken.models import Token

from slide_li import settings

User = get_user_model()
redis_con = redis.from_url(settings.REDIS_CON)


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
        data = json.loads(payload.decode('utf-8'))
        if data.get('room', '') and data.get('token', ''):
            self.room = data['room']
            self.token = data['token']
        broadcast = self.actions['broadcast']
        broadcast(self, payload)
        print("Some message received")

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self.uuid)


class BroadcastServerFactory(WebSocketServerFactory):
    rooms = {}
    chat_history = {}

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = {}

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
            user = False
        data_dict = json.loads(data.decode('utf-8'))

        if data_dict.get('text', '') and user:
            message = json.dumps({'message': data_dict['text'], 'user': user.username, 'datetime': data_dict['datetime']})
        else:
            message = False
        current_room = data_dict['room']

        if not data_dict['room'] in self.rooms.keys():
            self.rooms.update({current_room: [conn]})
        elif conn not in self.rooms[current_room]:
            self.rooms[current_room].append(conn)
            messages = [
                json.loads(msg.decode('utf-8'))
                for msg in redis_con.lrange(current_room, 0, -1)
            ]
            conn.sendMessage(json.dumps({'messages': messages}).encode('utf-8'))
        if message:
            for client in self.rooms[current_room]:
                client.sendMessage(bytes(message, encoding='utf-8'))
            redis_con.rpush(current_room, message)
            redis_con.expire(current_room, 7200)
