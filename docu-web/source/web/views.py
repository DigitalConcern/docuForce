from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from . import models


class StatsView(TemplateView):
    model = models.Stats
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = models.Stats.objects.values_list("users", flat=True).get(pk=0)
        context['documents'] = models.Stats.objects.values_list("documents", flat=True).get(pk=0)
        context['command_tasks'] = models.Stats.objects.values_list("command_tasks", flat=True).get(pk=0)
        context['command_documents'] = models.Stats.objects.values_list("command_documents", flat=True).get(pk=0)
        context['command_search'] = models.Stats.objects.values_list("command_search", flat=True).get(pk=0)
        context['command_messages'] = models.Stats.objects.values_list("command_messages", flat=True).get(pk=0)
        context['tasks_done'] = models.Stats.objects.values_list("tasks_done", flat=True).get(pk=0)
        context['messages_done'] = models.Stats.objects.values_list("messages_done", flat=True).get(pk=0)
        return context


class LoginView(auth_views.LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('home')

