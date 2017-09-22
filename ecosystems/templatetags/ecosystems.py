from django import template

from rest_framework.reverse import reverse

register = template.Library()


@register.inclusion_tag('ecosystems/ecosystemsproject_list_include.html')
def ecosystems_project_list(attach_id, ajax_url=reverse('ecosystems:api:project-list'), **kwargs):
    response = {
        'attach_id': attach_id,
        'ajax_url': ajax_url,
        'pager': 1,
        'search': 1,
        'set_page_size': 1,
        'default_page_size': 25,
        'set_sort': 1,
        'default_sort': None,
        'show_reset': 1,
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.inclusion_tag('ecosystems/ecosystems_gisfeature_map_include.html')
def ecosystems_geoinfo_feature_map(**kwargs):
    # Explicitly describe the kwargs we are interested in:
    response = {
        'attach_id': kwargs.pop('attach_id', None),
        'ajax_url': kwargs.pop('ajax_url', reverse('geoinfo:api:feature-list')),
        'map_settings': kwargs.pop('map_settings', None),
        'pager': kwargs.pop('pager', 1),
        'search': kwargs.pop('search', 1)
    }

    # Get remaining kwargs:
    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response
