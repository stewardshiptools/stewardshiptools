import re

from django.core.cache import cache
from django.contrib.gis.measure import D
from rest_framework.reverse import reverse

from geoinfo.models import GISLayerMaster


def clear_report_caches(report):
    cache_keys = get_spatialreport_cache_keys(report)

    for cache_key in cache_keys:
        clear_api_cache_by_key(cache_key)


def clear_api_cache_from_view(view_instance, request):
    cache_key = get_api_cache_key_from_view(view_instance, request)
    clear_api_cache_by_key(cache_key)


def clear_api_cache_by_key(cache_key):
    cache.delete(cache_key)


def get_spatialreport_cache_keys(report):
    cache_keys = []
    model_names = ['GISFeaturePoint', 'GISFeatureLine', 'GISFeaturePolygon']
    list_types = ['geojson', 'flat']
    distance_from = ','.join([str(x.pk) for x in report.report_on.all()])

    distance_cap_pattern = re.compile(r'(\d+) *(.+)')

    distance_cap_raw = report.distance_cap
    match = distance_cap_pattern.match(distance_cap_raw)
    if match:
        d_tuple = {match.group(2): match.group(1)}
        distance = D(**d_tuple)

        distance_cap = distance.m
    else:
        return False

    for item in report.spatialreportitem_set.all():
        # If the item overrides the distance_cap, use it.
        if item.distance_cap:
            distance_cap_raw = report.distance_cap
            match = distance_cap_pattern.match(distance_cap_raw)
            if match:
                d_tuple = {match.group(2): match.group(1)}
                distance = D(**d_tuple)

                distance_cap = distance.m

        layer = item.layer.pk

        # Now we have all the parts we need, lets start making keys!
        for model_name in model_names:
            for list_type in list_types:
                cache_key = get_api_cache_key(model_name, distance_from, layer, distance_cap, list_type)
                cache_keys.append(cache_key)

    return cache_keys


def get_api_cache_key_from_view(view_instance, request):
    # A cached entry is unique to the api request.  So a cache may possibly be used for multiple reports.
    as_geojson = request.query_params.get('as_geojson', 0)
    if as_geojson:
        list_type = 'geojson'
    else:
        list_type = 'flat'

    model_name = view_instance.model.__name__
    distance_from = request.query_params.get('distance_from', None)
    layer = request.query_params.get('layer', None)
    distance_cap = request.query_params.get('distance_cap', None)

    return get_api_cache_key(model_name, distance_from, layer, distance_cap, list_type)


def get_api_cache_key(model_name, distance_from, layer, distance_cap, list_type):
    cache_key = "spatialreport-%s-%s-%s-%f-%s" % (
        model_name,
        distance_from,
        layer,

        # To make sure the key given here is the same as the key created below in the extract_urls function.
        float(distance_cap),

        list_type
    )

    return cache_key


def extract_ajax_urls_from_spatialreport(report):

    if not report.report_on:
        return []

    urls = []

    default_distance_cap = report.distance_cap

    for item in report.spatialreportitem_set.all():
        distance_cap_raw = item.distance_cap or default_distance_cap
        match = re.match(r'(\d+) *(.+)', distance_cap_raw)
        if match:
            d_tuple = {match.group(2): match.group(1)}
            distance = D(**d_tuple)

            distance_cap = distance.m

            point_url = "%s?distance_from=%s&layer=%d&distance_cap=%f" % (
                reverse('geoinfo:feature-point-list'),
                ','.join([str(x.id) for x in report.report_on.all()]),
                item.layer.id,
                distance_cap
            )

            line_url = "%s?distance_from=%s&layer=%d&distance_cap=%f" % (
                reverse('geoinfo:feature-line-list'),
                ','.join([str(x.id) for x in report.report_on.all()]),
                item.layer.id,
                distance_cap
            )

            polygon_url = "%s?distance_from=%s&layer=%d&distance_cap=%f" % (
                reverse('geoinfo:feature-polygon-list'),
                ','.join([str(x.id) for x in report.report_on.all()]),
                item.layer.id,
                distance_cap
            )

            layer_model = item.layer.__class__
            layer_subclass = layer_model.objects.get_subclass(id=item.layer.id)

            urls.append({
                'item': {
                    'id': item.id,
                    'name': item.layer.name,
                    'distance_cap': distance_cap_raw
                },
                'layer': {
                    'id': item.layer.id,
                    'url': layer_subclass.get_absolute_url()
                },
                'urls': {
                    'point': point_url,
                    'line': line_url,
                    'polygon': polygon_url
                },
                'report_item': 1
            })

    # Finally... add the layers that are being reported on.

    for layer in report.report_on.all():
        layer_model = layer.__class__
        layer_subclass = layer_model.objects.get_subclass(id=layer.id)

        urls.append({
            'item': 0,
            'layer': {
                'id': layer.id,
                'url': layer_subclass.get_absolute_url()
            },
            'urls': {
                'all': "%s?layer=%d" % (
                    reverse('geoinfo:api:feature-list'),
                    layer.id
                )
            },
            'report_item': 0
        })

    return urls
