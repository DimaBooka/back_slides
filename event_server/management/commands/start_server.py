from django.core.management.base import BaseCommand
from event_server.server import BroadcastServerFactory, BroadcastServerProtocol
from slide_li.settings import RVL_FACTORY_ADRESS, RVL_CORO_IP, RVL_CORO_PORT

class Command(BaseCommand):
    help = 'Start websocket server for presentation streaming'

    def handle(self, *args, **options):
        import asyncio
        ServerFactory = BroadcastServerFactory

        factory = ServerFactory(RVL_FACTORY_ADRESS)
        factory.protocol = BroadcastServerProtocol

        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, RVL_CORO_IP, RVL_CORO_PORT)
        server = loop.run_until_complete(coro)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.close()
