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
        print(payload)
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
        data = json.loads(payload.decode('utf-8'))
        if data.get('room', '') and data.get('token', ''):
            self.room = data['room']
            self.token = data['token']
        self.factory.broadcast_chat_message(self, payload)
        print("Some message received")

    def reveal_process_payload(self, payload):
        """Handles payload for reveal clients, send last message to just registered user"""
        try:
            data = json.loads(payload.decode('utf8'))
            print('reveal data', data)
            if data.get('register', ''):
                self.factory.rev_register(self)
                self.reveal = True
                last_message = redis_con.get(data['socketId'])
                print('last message', last_message)
                if last_message:
                    self.factory.rvl_send_message(self, json.loads(last_message.decode('utf-8')))
            else:
                self.factory.rev_broadcast(data)

        except (json.JSONDecodeError, UnicodeDecodeError) as err:
            print(payload)
            print(err)
        print("Some message received")

    def onClose(self, wasClean, code, reason):
        """Routes close event to specific for client unregister methods"""
        if hasattr(self, 'uuid'):
            self.factory.signal_unregister(self.uuid)
        if hasattr(self, 'room'):
            self.factory.chat_unregister(self, self.room)
        if hasattr(self, 'reveal'):
            self.factory.rev_unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):
    rooms = {}
    chat_history = {}
    clients = {}
    rev_clients = []

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)

    def offer(self, data, current_uuid):
        #print(data)
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.signal_send_message(conn, {
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
            self.signal_send_message(conn, {
                'type': 'answer',
                'answer': data['answer'],
                'uuid': current_uuid,
            })
            print("Answer to {} with from: {}".format(conn.peer, uuid))

    def candidate(self, data, current_uuid):
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.signal_send_message(conn, {
                'type': 'candidate',
                'candidate': data['candidate'],
                'uuid': current_uuid,
            })
            print("Candidate from {} with uuid: {}".format(conn.peer, uuid))

    def register_peer(self, client, uuid):
        self.uuid = uuid
        if uuid not in self.clients:
            print("registered client {}, uuid: {}".format(client.peer, uuid))
            self.clients[uuid] = client
        #print(self.clients)

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

    def chat_unregister(self, conn, room):
        if room in self.rooms:
            if conn in self.rooms[room]:
                self.rooms[room].remove(conn)

    def rev_unregister(self, conn):
        if conn in self.rev_clients:
            self.rev_clients.remove(conn)

    def broadcast_chat_message(self, conn, data):
        token = conn.http_headers.get('Authorization', conn.token)

        try:
            # token = token.split(' ')[1]
            user = Token.objects.select_related('user').get(key=token).user
        except:
            self.cht_send_message(conn, {'error': 'Missing or incorrect token'})
            user = False
        data_dict = json.loads(data.decode('utf-8'))

        if data_dict.get('text', '') and user:
            message = {'message': data_dict['text'], 'user': user.username, 'datetime': data_dict['datetime']}
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
            self.cht_send_message(conn, {'messages': messages})
        if message:
            for client in self.rooms[current_room]:
                self.cht_send_message(client, message)
            redis_con.rpush(current_room, json.dumps(message).encode('utf-8'))
            redis_con.expire(current_room, 7200)

    def rev_broadcast(self, data):
        print(data)
        redis_con.set(data['socketId'], json.dumps(data).encode('utf-8'))
        for client in self.rev_clients:
            #print(json.dumps(data).encode('utf-8'))
            self.rvl_send_message(client, data)
            
    def rvl_send_message(self, conn, message):
        message['to'] = 'reveal'
        print('Sending message:', message)
        conn.sendMessage(json.dumps(message).encode('utf-8'))

    def cht_send_message(self, conn, message):
        message['to'] = 'chat'
        print('Sending message:', message)
        conn.sendMessage(json.dumps(message).encode('utf-8'))

    def signal_send_message(self, conn, message):
        message['to'] = 'signal'
        print('Sending message:', message)
        conn.sendMessage(json.dumps(message).encode('utf-8'))
