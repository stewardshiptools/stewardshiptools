# from django.shortcuts import render
from django.views.generic.base import ContextMixin

from .models import PageHelp


class HelpContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super(HelpContextMixin, self).get_context_data(**kwargs)

        page_help, create = PageHelp.objects.get_or_create(
            page_name=self.page_help_name
        )

        context['page_help'] = page_help

        return context
