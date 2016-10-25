from django.shortcuts import render


def chat(request):
    token = request.user.auth_token
    response = render(request, template_name='chat.html', context={'token': token})
    return response
