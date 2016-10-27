import json
import redis
from uuid import uuid4
from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from django.contrib.auth import get_user_model
from slide_li import settings

User = get_user_model()
redis_con = redis.from_url(settings.REDIS_CON)

class BroadcastServerProtocol(WebSocketServerProtocol):
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
        self.registered_in_chat = False

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
        self.token = self.http_headers.get('authorization', '').split(' ')[1]
        if data.get('action', '') == 'history':
            self.send_history(data['room'])
            return
        if not self.token:
            self.sendMessage(json.dumps({'error': 'Not logged in'}).encode('utf-8'))
            return

        if data.get('action', '') == 'register':
            self.room = data['room']
            self.factory.register_chat_user(self)
            self.registered_in_chat = True
        else:
            if hasattr(self, 'user'):
                self.factory.broadcast_chat_message(self, data)
        print("Some message received")


    def send_history(self, room):
        messages = [
            json.loads(msg.decode('utf-8'))
            for msg in redis_con.lrange(room, 0, -1)
            ]
        self.sendMessage(json.dumps({'messages': messages}).encode('utf-8'))


    def onClose(self, wasClean, code, reason):
        self.factory.unregister(self.uuid)



class BroadcastServerFactory(WebSocketServerFactory):
    rooms = {}
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

    def register_chat_user(self, conn):
        if conn.room not in self.rooms:
            self.rooms[conn.room] = {}
        try:
            user = User.objects.get(auth_token__key=conn.token)
        except:
            conn.sendMessage(json.dumps({'error': 'Missing or incorrect token'}).encode('utf-8'))
            user = None
        print(user)
        if user:
            conn.user = user.username
            if conn.token not in self.rooms[conn.room]:
                self.rooms[conn.room][conn.token] = conn

    def unregister_chat_user(self, conn):
        self.rooms[conn.room].pop(conn.token)

    def broadcast_chat_message(self, conn, data):
        message = json.dumps({'message': data['text'], 'user': conn.user, 'datetime': data['datetime']})
        for connect in self.rooms[conn.room].values():
            connect.sendMessage(message.encode('utf-8'))
        redis_con.rpush(conn.room, message)
        redis_con.expire(conn.room, 7200)