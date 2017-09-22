from django import template

from rest_framework.reverse import reverse

register = template.Library()


@register.inclusion_tag('cedar/cedar_list.html')
def cedar_list(attach_id, ajax_url='', **kwargs):
    response = dict()

    defaults = {
        'js_file': '',  # This should be a string that can be passed into {% static ... %}
        'attach_id': attach_id,
        'ajax_url': ajax_url,
        'pager': 1,
        'search': 1,
        'set_page_size': 1,
        'page_size_options': [5, 10, 25, 50, 100, 500, 1000],
        'default_page_size': 25,
        'filters': [],
        'set_sort': 1,
        'sort_field_options': [],
        'default_sort': None,
        'show_reset': 1,
        'show_filters': 1,
        'fields': [],
        'list_type': 'table',
        'extra_options': dict()
    }

    response.update(defaults)

    for k in kwargs.keys():
        if k in defaults.keys():
            response[k] = kwargs[k]
        else:
            response['extra_options'][k] = kwargs[k]

    return response
