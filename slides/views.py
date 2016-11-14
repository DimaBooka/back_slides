import json

from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from slides.models import Event
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt


class LivePresentationView(View):

    @xframe_options_exempt
    def get(self, request, pk):
        event = get_object_or_404(Event, id=pk)
        ctx = {
            'id': pk,
            'socket_addr': settings.SOCKET_ADDR,
            'prefix': 'wss' if settings.SSL else 'ws',
            'ice_servers': json.dumps(settings.WEBRTC_ICE_SERVERS),
        }
        print(request.user, event.author)
        if event.date_started and not event.date_finished:
            template = 'master.html' if request.user == event.author else 'client.html'
            ctx.update({
                'secret': event.secret,
                'slides': event.presentation.slides,
            })
        else:
            template = 'wait.html'
            ctx.update({
                'state': 'planned' if not event.date_finished else 'finished',
                'date': event.date_planned if not event.date_finished else None,
            })
        return render(request, template, ctx)
