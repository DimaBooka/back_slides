import json
import redis
from uuid import uuid4
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
        print('New connection')
        self.actions = {
            'offer': self.factory.offer,
            'answer': self.factory.answer,
            'candidate': self.factory.candidate,
            'leave': self.factory.leave,
        }
        self.from_app = {
            'chat': self.chat_process_payload,
            'signal': self.signal_process_payload,
        }

    def onMessage(self, payload, isBinary):
        data = json.loads(payload.decode('utf8'))
        action = data.get('from', '')
        if action:
            self.from_app[action](payload)

    def signal_process_payload(self, payload):
        try:
            data = json.loads(payload.decode('utf8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as err:
            print(err)
            data = {}

        if data.get('register', ''):
            hostname = data.get('hostname', '')
            if hostname:
                self.uuid = hostname
            else:
                self.uuid = uuid4().hex
            self.factory.register_peer(self, self.uuid)
            self.factory.send_signal_message(self, {'initial_uuid': self.uuid})
        else:
            type = data['type']
            action = self.actions[type]
            action(data, self.uuid)
            print("Some message received")

    def chat_process_payload(self, payload):
        data = json.loads(payload.decode('utf-8'))
        if data.get('room', '') and data.get('token', ''):
            self.room = data['room']
            self.token = data['token']
        self.factory.broadcast_chat_message(self, payload)
        print("Some message received")

    def onClose(self, wasClean, code, reason):
        if hasattr(self, 'uuid'):
            self.factory.unregister(self.uuid)



class BroadcastServerFactory(WebSocketServerFactory):
    rooms = {}
    chat_history = {}
    clients = {}

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)

    def offer(self, data, current_uuid):
        print(data)
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.send_signal_message(conn, {
                'type': 'offer',
                'offer': data['offer'],
                'uuid': current_uuid,
            })
            print("Offer to {} with uuid: {}".format(conn.peer, uuid))

    def answer(self, data, current_uuid):
        print(data)
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.send_signal_message(conn, {
                'type': 'answer',
                'answer': data['answer'],
                'uuid': current_uuid,
            })
            print("Answer to {} with from: {}".format(conn.peer, uuid))

    def candidate(self, data, current_uuid):
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.send_signal_message(conn, {
                'type': 'candidate',
                'candidate': data['candidate'],
                'uuid': current_uuid,
            })
            print("Candidate from {} with uuid: {}".format(conn.peer, uuid))

    def leave(self, data, current_uuid):
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.send_signal_message(conn, {
                'type': 'leave',
                'uuid': current_uuid,
            })
            print("Disconnecting user from {} with uuid: {}".format(conn.peer, uuid))

    def register_peer(self, client, uuid):
        self.uuid = uuid
        if uuid not in self.clients:
            print("registered client {}, uuid: {}".format(client.peer, uuid))
            self.clients[uuid] = client
        print(self.clients)

    def unregister(self, uuid):
        if uuid in self.clients:
            print("unregistered client with uuid: {}".format(uuid))
            self.clients.pop(uuid)

    def send_signal_message(self, conn, message):
        print("sending message '{}' ..".format(message))
        conn.sendMessage(json.dumps(message).encode('utf-8'))
        print("message sent to {}".format(conn.peer))


    def broadcast_chat_message(self, conn, data):
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