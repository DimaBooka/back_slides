from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from slides.models import Event

from django.views.decorators.clickjacking import xframe_options_exempt
from slide_li.settings import SOCKET_ADDR


class LivePresentationView(View):

    @xframe_options_exempt
    def get(self, request, pk):
        event = get_object_or_404(Event, id=pk)
        if event.date_started and not event.date_finished:
            template = 'master.html' if request.user == event.author else 'client.html'
            ctx = {
                'id': pk,
                'secret': event.secret,
                'slides': event.presentation.slides,
                'socket_addr': SOCKET_ADDR,
                }
        else:
            template = 'wait.html'
            ctx = {
                'state': event.get_state_display().lower(),
                'date': event.date if event.state in (1, 4) else None
            }
        return render(request, template, ctx)
