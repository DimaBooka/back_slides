from django.shortcuts import render
from slide_li.settings import CHT_SOCKET_ADDR

def chat(request):
    token = request.user.auth_token
    response = render(request, template_name='chat.html', context={'token': token, 'socket_addr': CHT_SOCKET_ADDR})
    return response
