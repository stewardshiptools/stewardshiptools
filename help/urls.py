from django.views.generic import TemplateView
from django.conf.urls import url

urlpatterns = [
    url(r'^help-sketch$', TemplateView.as_view(template_name='help_sketch_page.html'), name='help-sketch'),
]
