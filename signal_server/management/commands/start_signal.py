from django.core.management.base import BaseCommand
from signal_server.server import BroadcastServerProtocol, BroadcastServerFactory
from slide_li.settings import RTC_FACTORY_ADRESS, RTC_CORO_IP, RTC_CORO_PORT


class Command(BaseCommand):
    help = "Start's up the signal server"

    def handle(self, *args, **options):
        import asyncio
        ServerFactory = BroadcastServerFactory
        factory = ServerFactory(RTC_FACTORY_ADRESS)
        factory.protocol = BroadcastServerProtocol

        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, RTC_CORO_IP, RTC_CORO_PORT)
        server = loop.run_until_complete(coro)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.close()