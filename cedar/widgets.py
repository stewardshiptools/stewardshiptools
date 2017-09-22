from django import forms
from django.template import Context
from django.template.loader import get_template

from django.utils.translation import ugettext_lazy as _


class Select2Ajax(forms.SelectMultiple):
    def __init__(self, ajax_url=None, min_input=1, max_suggestions=20, attrs=None, choices=()):
        self.ajax_url = ajax_url
        self.min_input = min_input
        self.max_suggestions = max_suggestions
        super().__init__(attrs=attrs, choices=choices)

    def render(self, name, value, attrs=None, choices=()):
        widget_html = super().render(name, value, attrs, choices)

        if self.ajax_url:
            start_text = self.attrs.get('start_text') or _("Enter Tag Here")
            empty_text = self.attrs.get('empty_text') or _("No Results")
            prompt_text = self.attrs.get('prompt_text') or _("Enter a tag")
            limit_text = self.attrs.get('limit_text') or _('No More Selections Are Allowed')

            context = Context({
                'widget_id': attrs['id'],
                'ajax_url': self.ajax_url,
                'min_input': self.min_input,
                'start_text': start_text,
                'prompt_text': prompt_text,
                'empty_text': empty_text,
                'limit_text': limit_text,
                'retrieve_limit': self.max_suggestions
            })

            js = get_template('cedar/select2_ajax_field.html')
            return widget_html + js.render(context)

        return widget_html
