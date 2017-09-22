from django import template

from rest_framework.reverse import reverse


from geoinfo.models import GISFeature, GISFeaturePoint, GISFeatureLine, GISFeaturePolygon

register = template.Library()


@register.inclusion_tag('geoinfo/gislayer_list_include.html')
def geoinfo_layer_list(attach_id, ajax_url=reverse('geoinfo:api:layer-list'), layer_type_choices=0, **kwargs):
    response = {
        'attach_id': attach_id,
        'ajax_url': ajax_url,
        'layer_type_choices': layer_type_choices,
        'pager': 1,
        'search': 1
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.inclusion_tag('geoinfo/gisfeature_list_include.html')
def geoinfo_feature_list(attach_id, ajax_url=reverse('geoinfo:api:feature-list'), **kwargs):
    response = {
        'attach_id': attach_id,
        'ajax_url': ajax_url,
        'pager': 1,
        'search': 1
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.inclusion_tag('geoinfo/gisfeature_map_include.html')
def geoinfo_feature_map(attach_id, map_settings, ajax_url=reverse('geoinfo:api:feature-list'), **kwargs):
    response = {
        'attach_id': attach_id,
        'ajax_url': ajax_url,
        'map_settings': map_settings,
        'pager': 1,
        'search': 1
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.inclusion_tag('geoinfo/spatialreport_list_include.html')
def geoinfo_report_list(attach_id, ajax_url=reverse('geoinfo:api:spatialreport-list'), **kwargs):
    response = {
        'attach_id': attach_id,
        'ajax_url': ajax_url,
        'pager': 1,
        'search': 1
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.assignment_tag()
def geoinfo_layer_stats(layer):
    stats = layer.get_stats

    if stats['polygon_area']:
        if stats['polygon_area'] < 10000:
            stats['polygon_area_units'] = 'm&sup2;'
        elif 10000 <= stats['polygon_area'] < 1000000:
            stats['polygon_area'] /= 10000
            stats['polygon_area_units'] = 'ha'
        else:
            stats['polygon_area'] /= 1000000
            stats['polygon_area_units'] = 'km&sup2;'

        stats['polygon_area'] = round(stats['polygon_area'], 2)

    return stats


@register.inclusion_tag('geoinfo/gislayer_stats.html')
def geoinfo_layer_chips(layer):
    """
    Takes the data returned by the assignment tag above, and formats it as chips
    :param layer: A Geoinfo.models.Layer instance
    :return: chips!  Materializecss style.
    """
    return geoinfo_layer_stats(layer)


@register.inclusion_tag('geoinfo/geoinfo_map_utils.html')
def geoinfo_load_map_utils():
    pass
