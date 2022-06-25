from django.views.generic import TemplateView
from . import models


class StatsView(TemplateView):
    model = models.Stats
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = models.Stats.objects.values_list("users", flat=True).get(pk=0)
        context['documents'] = models.Stats.objects.values_list("documents", flat=True).get(pk=0)
        return context
