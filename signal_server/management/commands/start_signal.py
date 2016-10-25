from django.core.management.base import BaseCommand, CommandError
from signal_server.server import BroadcastServerProtocol, BroadcastServerFactory

class Command(BaseCommand):
    help = "Start's up the signal server"

    def handle(self, *args, **options):
        import asyncio
        ServerFactory = BroadcastServerFactory
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
