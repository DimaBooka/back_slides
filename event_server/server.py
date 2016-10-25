import json

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory


class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        print('register')
        self.factory.register(self)

    def onMessage(self, payload, isBinary):

        if not isBinary:
            try:
                data = json.loads(payload.decode('utf8'))
                print(data)
                self.factory.broadcast(data)
            except (json.JSONDecodeError, UnicodeDecodeError) as err:
                print(payload)
                print(err)
        print("Some message received")

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []

    def register(self, client):
        if client not in self.clients:
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client: {}".format(client))
            self.clients.pop(client)

    def broadcast(self, data):
        for client in self.clients:
            client.sendMessage(json.dumps(data).encode('utf-8'))


