from django.core.management.base import BaseCommand, CommandError
from event_server.server import BroadcastServerFactory, BroadcastServerProtocol


class Command(BaseCommand):
    help = 'Start websocket server for presentation streaming'

    def handle(self, *args, **options):
        import asyncio
        ServerFactory = BroadcastServerFactory

        factory = ServerFactory(u"ws://127.0.0.1:1948")
        factory.protocol = BroadcastServerProtocol

        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, '127.0.0.1', 1948)
        server = loop.run_until_complete(coro)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.close()
