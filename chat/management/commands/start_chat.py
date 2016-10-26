import django
from django.core.management.base import BaseCommand
from chat.server import BroadcastServerFactory, BroadcastServerProtocol
from slide_li.settings import CHT_FACTORY_ADRESS, CHT_CORO_IP, CHT_CORO_PORT


class Command(BaseCommand):
    help = 'Start websocket server for chat'

    def handle(self, *args, **options):
        import asyncio
        ServerFactory = BroadcastServerFactory

        factory = ServerFactory(CHT_FACTORY_ADRESS)
        factory.protocol = BroadcastServerProtocol

        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, CHT_CORO_IP, CHT_CORO_PORT)
        server = loop.run_until_complete(coro)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.close()
