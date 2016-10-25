import json
from uuid import uuid4
from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory


class BroadcastServerProtocol(WebSocketServerProtocol):
    def onOpen(self):
        self.uuid = uuid4().hex
        self.factory.register(self, self.uuid)
        self.factory.send_message(self, {'initial_uuid': self.uuid})  # for debug
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


# class BroadcastPreparedServerFactory(BroadcastServerFactory):
#
#     """
#     Functionally same as above, but optimized broadcast using
#     prepareMessage and sendPreparedMessage.
#     """
#
#     def broadcast(self, msg):
#         print("broadcasting prepared message '{}' ..".format(msg))
#         preparedMsg = self.prepareMessage(msg)
#         for c in self.clients:
#             c.sendPreparedMessage(preparedMsg)
#             print("prepared message sent to {}".format(c.peer))


if __name__ == '__main__':
    import asyncio

    ServerFactory = BroadcastServerFactory
    # ServerFactory = BroadcastPreparedServerFactory

    factory = ServerFactory(u"ws://127.0.0.1:10000")
    factory.protocol = BroadcastServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 10000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()