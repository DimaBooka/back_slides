import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse

User = get_user_model()


class SlidesMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated() and not request.user.email and request.path != '/api/accept-email/' \
                                           and request.path != '/api/rest-auth/facebook/':
            return HttpResponse(content=json.dumps({"error": "need email"}), status=400, content_type='application/json',)

        return response
