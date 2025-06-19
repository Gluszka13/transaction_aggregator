from django.http import JsonResponse
from django.conf import settings


class APITokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/ping'):
            token = request.headers.get('Authorization')
            expected = f"Token {settings.API_TOKEN}"
            if token != expected:
                return JsonResponse({'detail': 'Unauthorized'}, status=401)
        return self.get_response(request)
