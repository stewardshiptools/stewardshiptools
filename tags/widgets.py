""" TODO Let's return to this when we have some more time a knowledge of widgets.  I left off with this being happily
styled as select2, but not happily communicating with the tags field/manager.
"""

import copy

from django import forms
from django.apps import apps
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

from taggit_autosuggest.utils import edit_string_for_tags as edit_string_for_tags_taggit_autosuggest  # TODO Would like to remove this
from taggit_autosuggest.widgets import TagAutoSuggest  # TODO Would like to remove this

from django.template import Context

get_model = apps.get_model


MAX_SUGGESTIONS = getattr(settings, 'TAGGIT_AUTOSUGGEST_MAX_SUGGESTIONS', 20)


class TagAutoSuggestSelect2(forms.SelectMultiple):
    def __init__(self, *, tagmodel=None, ajax_url=None, min_input=1, freetagging=True, attrs=None, choices=()):
        self.tagmodel = settings.TAGGIT_AUTOSUGGEST_MODELS['default'] if tagmodel is None else tagmodel
        self.ajax_url = reverse_lazy('tags:autosuggest-list',
                                     kwargs={'tagmodel': self.tagmodel}) if ajax_url is None else ajax_url
        self.min_input = min_input
        self.freetagging = freetagging

        super().__init__(attrs=attrs, choices=choices)

    def value_from_datadict(self, data, files, name):
        """
        We need this function to translate the data returned by this widget into what a taggit field expects.
        
        :param data: A QueryDict of form data keyed by field id
        :param files: This isn't used here.
        :param name: The name/id of this field.
        :return: A string formatted for reading by taggit.  This is a little ugly, but its what taggit expects.
        """
        tag_data = data.getlist(name)
        # Wrap all tags in double quotes before returning.
        return ", ".join(list(map(lambda x: '"{}"'.format(x), tag_data)))

    def render(self, name, value, attrs=None, choices=()):
        # This is probably empty, but lets make sure.  We want to set choices on the fly.
        choices = ()

        # We don't care about the choices param... unless! There's existing values.
        # This the value param is going to be a queryset of taggeditems.  If not somethings wrong...
        if value and not isinstance(value, str):
            # We're keying by name instead of id because taggit expects names
            # anyways and using names makes it so that numbers can be tags.
            choices = tuple([(str(x.tag), str(x.tag)) for x in value])
            value = [str(x.tag) for x in value]

        # Prepare the widget HTML with necessary overrides.
        widget_attrs = copy.copy(attrs)
        widget_attrs['id'] += '__tagautosuggest_select2'
        widget_attrs['required'] = False
        widget_html = super().render(name,
                                     value,
                                     widget_attrs,
                                     choices)

        start_text = self.attrs.get('start_text') or _("Enter Tag Here")
        empty_text = self.attrs.get('empty_text') or _("No Results")
        prompt_text = self.attrs.get('prompt_text') or _("Enter a tag")
        limit_text = self.attrs.get('limit_text') or _('No More Selections Are Allowed')

        context = Context({
            'widget_id': widget_attrs['id'],
            'url': self.ajax_url,
            'min_input': self.min_input,
            'freetagging': self.freetagging,
            'start_text': start_text,
            'prompt_text': prompt_text,
            'empty_text': empty_text,
            'limit_text': limit_text,
            'retrieve_limit': MAX_SUGGESTIONS,
        })
        js = get_template('tags/taggable_input_select2.html')
        #
        # return result_html + widget_html + mark_safe(js)
        return widget_html + js.render(context)


class TaggitAutoSuggestExtended(TagAutoSuggest):
    """
    Slightly modified from parent class to allow some tweaks to widget attributes.
    Now accepts extra url params via the "extra_url_params" kwarg. Give it a dict and
    this widget will stringify it and append to the url.
    """

    def __init__(self, tagmodel, *args, **kwargs):
        self.extra_url_params = kwargs.pop('extra_url_params', {})
        super().__init__(tagmodel, *args, **kwargs)

    def render(self, name, value, attrs=None):
        """
        if you initialize the widget in a form class and specify the attrs kwarg you can
        override the 'startText' parameter. --- SEE library.forms.Item for examples.
        :param name: 
        :param value: 
        :param attrs: 
        :return: 
        """
        if hasattr(value, "select_related"):
            tags = [o.tag for o in value.select_related("tag")]
            value = edit_string_for_tags_taggit_autosuggest(tags)

        autosuggest_url = reverse('taggit_autosuggest-list', kwargs={'tagmodel': self.tagmodel})

        result_attrs = copy.copy(attrs) if attrs else {}
        result_attrs['type'] = 'hidden'
        result_html = super(TagAutoSuggest, self).render(name, value,
                                                         result_attrs)

        widget_attrs = copy.copy(attrs) if attrs else {}
        widget_attrs['id'] += '__tagautosuggest'
        widget_html = super(TagAutoSuggest, self).render(name, value,
                                                         widget_attrs)

        context = Context({
            'result_id': result_attrs['id'],
            'widget_id': widget_attrs['id'],
            'url': autosuggest_url,
            'start_text': self.attrs.get('startText') or _("Enter Tag Here"),
            'empty_text': _("No Results"),
            'limit_text': _('No More Selections Are Allowed'),
            'retrieve_limit': MAX_SUGGESTIONS,
            'extra_params': self.stringify_url_param_dict()  # "&belongs_to=heritage-library"
        })

        js = get_template('tags/taggable_input.html')
        return result_html + widget_html + js.render(context)

    def get_extra_url_params(self):
        return self.extra_url_params

    def stringify_url_param_dict(self):
        url_params = ""
        params_dict = self.get_extra_url_params()
        if params_dict: # if this is None then return empty string.
            for k in params_dict.keys():
                url_params += "&{prop}={val}".format(prop=k, val=params_dict[k])
        return url_params
