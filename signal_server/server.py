import json
from uuid import uuid4
from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory


class BroadcastServerProtocol(WebSocketServerProtocol):
    def onOpen(self):
        print('New connection')
        self.actions = {
            'offer': self.factory.offer,
            'answer': self.factory.answer,
            'candidate': self.factory.candidate,
            'leave': self.factory.leave,
        }

    def onMessage(self, payload, isBinary):
        if not isBinary:
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
            self.factory.register(self, self.uuid)
            self.factory.send_message(self, {'initial_uuid': self.uuid})
        else:
            type = data['type']
            action = self.actions[type]
            action(data, self.uuid)
            print("Some message received")

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self.uuid)



class BroadcastServerFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = {}

    def offer(self, data, current_uuid):
        print(data)
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.send_message(conn, {
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
            self.send_message(conn, {
                'type': 'answer',
                'answer': data['answer'],
                'uuid': current_uuid,
            })
            print("Answer to {} with from: {}".format(conn.peer, uuid))

    def candidate(self, data, current_uuid):
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.send_message(conn, {
                'type': 'candidate',
                'candidate': data['candidate'],
                'uuid': current_uuid,
            })
            print("Candidate from {} with uuid: {}".format(conn.peer, uuid))

    def leave(self, data, current_uuid):
        uuid = data['uuid']
        if uuid in self.clients:
            conn = self.clients[uuid]
            self.send_message(conn, {
                'type': 'leave',
                'uuid': current_uuid,
            })
            print("Disconnecting user from {} with uuid: {}".format(conn.peer, uuid))

    def register(self, client, uuid):
        self.uuid = uuid
        if uuid not in self.clients:
            print("registered client {}, uuid: {}".format(client.peer, uuid))
            self.clients[uuid] = client
        print(self.clients)

    def unregister(self, uuid):
        if uuid in self.clients:
            print("unregistered client with uuid: {}".format(uuid))
            self.clients.pop(uuid)

    def send_message(self, conn, message):
        print("sending message '{}' ..".format(message))
        conn.sendMessage(json.dumps(message).encode('utf-8'))
        print("message sent to {}".format(conn.peer))