from django.shortcuts import render
from slide_li.settings import SOCKET_ADDR


def chat(request):
    if request.user.is_authenticated:
        token = request.user.auth_token
    else:
        token = ''
    response = render(request, template_name='chat.html', context={'token': token, 'socket_addr': SOCKET_ADDR})
    return response

