import django.views.generic


class HomeTemplate(django.views.generic.TemplateView):
    template_name = 'base.html'
