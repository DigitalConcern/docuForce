from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy


class AuthRequiredMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info.lstrip('/')
        response = self.get_response(request)
        if not request.user.is_authenticated:
            if path != "login/":
                return HttpResponseRedirect(reverse_lazy("login"))
        return response

