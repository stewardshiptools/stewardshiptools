from django import template


register = template.Library()


@register.simple_tag()
def distance_cap(report, item):
    if item.distance_cap:
        return item.distance_cap

    return report.distance_cap


@register.inclusion_tag('geoinfo/spatialreport_feature_list_include.html')
def spatialreports_feature_list(attach_id, ajax_urls, **kwargs):
    response = {
        'attach_id': attach_id,
        'ajax_urls': ajax_urls,
        'pager': 1,
        'search': 1
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.inclusion_tag('geoinfo/spatialreport_feature_map_include.html')
def spatialreports_feature_map(attach_id, map_settings, ajax_urls, **kwargs):
    response = {
        'attach_id': attach_id,
        'ajax_urls': ajax_urls,
        'map_settings': map_settings,
        'pager': 1,
        'search': 1
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response
