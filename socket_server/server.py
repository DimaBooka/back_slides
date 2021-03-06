import json
import redis
from uuid import uuid4
from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.utils.timezone import now
from django.utils.text import Truncator

from slide_li import settings

User = get_user_model()
redis_con = redis.from_url(settings.REDIS_CON)


class BroadcastServerProtocol(WebSocketServerProtocol):
    room = ''
    token = ''

    def onOpen(self):
        """
        Defines list of actions and message mark (from_app)
        """
        print('New connection')
        self.actions = {
            'offer': self.factory.offer,
            'answer': self.factory.answer,
            'candidate': self.factory.candidate,
        }
        self.from_app = {
            'chat': self.chat_process_payload,
            'signal': self.signal_process_payload,
            'reveal': self.reveal_process_payload,
        }

    def onMessage(self, payload, isBinary):
        """
        Routes payload to specific handler depend of 'from'
        data['blank'] -- preserves automatic connection close
        :param payload: received payload
        """
        data = json.loads(payload.decode('utf8'))
        if data.get('blank', ''):
            return
        action = data.get('from', '')
        if action:
            self.from_app[action](payload)

    def signal_process_payload(self, payload):
        """Handles payload destined to WebRTC clients"""
        try:
            data = json.loads(payload.decode('utf8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as err:
            print(err)
            data = {}

        if data.get('register', ''):
            self.host = False
            hostname = data.get('hostname', '')
            if hostname:
                self.uuid = hostname
                self.host = True
            else:
                self.uuid = uuid4().hex
            self.factory.register_peer(self, self.uuid)
            self.factory.signal_send_message(self, {'initial_uuid': self.uuid})
        else:
            type = data['type']
            action = self.actions[type]
            action(data, self.uuid)
            print("Some message received")

    def chat_process_payload(self, payload):
        """Handles payload for chat clients"""
        print('Some message received')
        try:
            data = json.loads(payload.decode('utf8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as err:
            print(err)
            return
        if 'register' in data:
            self.factory.chat_register(self, data)
            self.factory.send_chat_history(self)
        else:
            self.factory.broadcast_chat_message(self, data)

    def reveal_process_payload(self, payload):
        """Handles payload for reveal clients, send last message to just registered user"""
        try:
            data = json.loads(payload.decode('utf8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as err:
            print(err)
            return
        if 'register' in data:
            self.reveal = True
            self.host = False
            if data.get('host', ''):
                self.host = True
            self.factory.rev_register(self)
            if 'waiter' not in data:
                last_message = redis_con.get('reveal' + str(data['socketId']))
                if last_message:
                    self.factory.rvl_send_message(self, json.loads(last_message.decode('utf-8')))
        else:
            self.factory.rev_broadcast(self, data)

        print("Some message received")

    def onClose(self, wasClean, code, reason):
        """Routes close event to specific for client unregister methods"""
        if hasattr(self, 'uuid'):
            self.factory.signal_unregister(self.uuid)
        if hasattr(self, 'room'):
            self.factory.chat_unregister(self)
        if hasattr(self, 'reveal'):
            self.factory.rev_unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):
    rooms = {}
    clients = {}
    rev_clients = []

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)

    def offer(self, data, current_uuid):
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.signal_send_message(conn, {
                'type': 'offer',
                'offer': data['offer'],
                'uuid': current_uuid,
            })

    def answer(self, data, current_uuid):
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.signal_send_message(conn, {
                'type': 'answer',
                'answer': data['answer'],
                'uuid': current_uuid,
            })

    def candidate(self, data, current_uuid):
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.signal_send_message(conn, {
                'type': 'candidate',
                'candidate': data['candidate'],
                'uuid': current_uuid,
            })

    def register_peer(self, client, uuid):
        self.uuid = uuid
        if uuid not in self.clients:
            print("registered client {}, uuid: {}".format(client.peer, uuid))
            self.clients[uuid] = client

    def chat_register(self, conn, data):
        room = data['room']
        conn.room = room
        if room in self.rooms:
            self.rooms[room].append(conn)
        else:
            self.rooms.update({room: [conn]})

    def send_chat_history(self, conn):
        message = {'messages': [
            json.loads(msg.decode('utf-8'))
            for msg in redis_con.lrange(conn.room, 0, -1)
        ]}
        self.cht_send_message(conn, message)

    def rev_register(self, client):
        if client not in self.rev_clients:
            self.rev_clients.append(client)

    def signal_unregister(self, uuid):
        """If host just disconnected - his subscribers must notified instantly"""
        if uuid in self.clients:
            print("unregistered signal client with uuid: {}".format(uuid))
            if self.clients[uuid].host:
                self.clients.pop(uuid)
                for client in self.clients.values():
                    self.signal_send_message(client, {'type': 'disconnected_host', 'uuid': uuid})

    def chat_unregister(self, conn):
        print('chat unregister')
        room = conn.room
        if room in self.rooms:
            if conn in self.rooms[room]:
                self.rooms[room].remove(conn)

    def rev_unregister(self, conn):
        if conn in self.rev_clients:
            self.rev_clients.remove(conn)

    def broadcast_chat_message(self, conn, data):
        token = data['token']
        try:
            user = Token.objects.select_related('user').get(key=token).user
        except Exception as e:
            print(e)
            self.cht_send_message(conn, {'error': 'Missing or incorrect token'})
            return

        if 'text' in data:
            text = Truncator(data['text'])
            message = {
                'message': text.chars(120, '\u2026'),
                'user': user.username,
                'datetime': now().strftime('%X'),
            }
            room = conn.room
            for client in self.rooms[room]:
                self.cht_send_message(client, message)
            redis_con.rpush(room, json.dumps(message).encode('utf-8'))
            redis_con.expire(room, 7200)

    def rev_broadcast(self, conn, data):
        if 'event' not in data:
            redis_con.set('reveal' + str(data['socketId']), json.dumps(data).encode('utf-8'))
        for client in self.rev_clients:
            if client is not conn and not client.host:
                self.rvl_send_message(client, data)
            
    def rvl_send_message(self, conn, message):
        message['to'] = 'reveal'
        conn.sendMessage(json.dumps(message).encode('utf-8'))

    def cht_send_message(self, conn, message):
        message.update({
            'to': 'chat',
            'room': conn.room,
        })
        conn.sendMessage(json.dumps(message).encode('utf-8'))

    def signal_send_message(self, conn, message):
        message['to'] = 'signal'
        conn.sendMessage(json.dumps(message).encode('utf-8'))
