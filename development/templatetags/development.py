from django import template

from rest_framework.reverse import reverse

register = template.Library()


@register.inclusion_tag('development/developmentproject_list_include.html')
def development_project_list(attach_id, ajax_url=reverse('development:api:project-list'), **kwargs):
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
        'show_filters': 1,
        'stage_options': [],
        'filing_code_options': [],
        'people_options': [],
        'org_options': [],
        'tags_options': []
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.inclusion_tag('development/development_gisfeature_map_include.html')
def development_geoinfo_feature_map(**kwargs):
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
