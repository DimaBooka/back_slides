import json

import pytz
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
        if event.date_started and not event.date_finished:
            template = 'master.html' if request.user == event.author else 'client.html'
            ctx.update({
                'secret': event.secret,
                'slides': event.presentation.slides,
            })
        else:
            current_planned_date = event.date_planned
            current_finished_date = event.date_finished
            fmt = '%H:%M %Y %m %d'
            template = 'wait.html'
            if request.user.is_authenticated():
                date_planned_dict = self.get_user_time(request.user.timezone, fmt, current_planned_date)
                date_finished_dict = self.get_user_time(request.user.timezone, fmt, current_finished_date)
                hours = date_planned_dict.get('hours', '') if not date_finished_dict.get('hours', '') else date_finished_dict.get('hours', '')
                date = date_planned_dict.get('date', '') if not date_finished_dict.get('date', '') else date_finished_dict.get('date', '')
            else:
                date = event.date_planned.strftime(fmt)[:6] if not event.date_finished else event.date_finished.strftime(fmt)[:6]
                hours = event.date_planned.strftime(fmt)[6:] if not event.date_finished else event.date_finished.strftime(fmt)[6:]
            ctx.update({
                'state': 'planned' if not event.date_finished else 'finished',
                'date': date,
                'hours': hours,
            })
        return render(request, template, ctx)

    def get_user_time(self, timezone, fmt, current_time):
        if not current_time:
            return {'hours': '', 'date': ''}
        zone = pytz.timezone(timezone)
        server_time = current_time
        local_time = server_time.astimezone(zone)
        date = local_time.strftime(fmt)
        hours = date[:6]
        date = date[6:]
        return {'hours': hours, 'date': date}
