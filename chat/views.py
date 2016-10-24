from django.shortcuts import render


def chat(request):
    return render(request, template_name='chat.html')
