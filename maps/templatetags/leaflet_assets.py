from django import template
from rest_framework.reverse import reverse

from maps.models import LeafletMap
from maps.serializers import LeafletMapSerializer

register = template.Library()


@register.inclusion_tag('maps/leaflet_assets_css.html')
def leaflet_assets_css():
    pass


@register.inclusion_tag('maps/leaflet_assets_js.html')
def leaflet_assets_js(**kwargs):
    pass


@register.inclusion_tag('maps/leaflet_load_map.html')
def leaflet_load_map(map_name):
    # Make sure this is called before leaflet_load_main
    try:
        leaflet_map = LeafletMap.objects.get(machine_name=map_name)
        leaflet_map_machine_name = leaflet_map.machine_name
        leaflet_map_url = reverse('maps:api:leaflet-map-detail', args=(leaflet_map.id,))
    except LeafletMap.DoesNotExist:
        leaflet_map_machine_name = ''
        leaflet_map_url = ''

    return {
        'machine_name': leaflet_map_machine_name,
        'map_url': leaflet_map_url
    }


@register.assignment_tag
def leaflet_map_ajax_url(map_name):
    # Make sure this is called before leaflet_load_main
    try:
        leaflet_map = LeafletMap.objects.get(machine_name=map_name)
        leaflet_map_url = reverse('maps:api:leaflet-map-detail', args=(leaflet_map.id,))
    except LeafletMap.DoesNotExist:
        leaflet_map_url = ''

    return leaflet_map_url


@register.assignment_tag
def leaflet_map_json(map_name):
    # Make sure this is called before leaflet_load_main
    try:
        leaflet_map = LeafletMap.objects.get(machine_name=map_name)
        serializer = LeafletMapSerializer(leaflet_map)
        map_json = serializer.data
    except LeafletMap.DoesNotExist:
        map_json = ''

    return map_json


@register.inclusion_tag('maps/leaflet_load_main.html')
def leaflet_load_main():
    pass
