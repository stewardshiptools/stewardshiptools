import json

from django.views.generic import TemplateView
from django.views.generic.base import ContextMixin
from django.core.urlresolvers import reverse_lazy, reverse
from rest_framework.reverse import reverse as drf_reverse
from rest_framework.renderers import JSONRenderer

from maps.models import LeafletMap
from maps.serializers import LeafletMapSerializer


class CommunityMapContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the map data to pass into context for json using the serializer and json renderer from DRF.
        try:
            leaflet_map = LeafletMap.objects.get(machine_name='community_map')
        except LeafletMap.DoesNotExist:
            try:
                leaflet_map = LeafletMap.objects.get(machine_name='map_default')
            except LeafletMap.DoesNotExist:
                leaflet_map = None  # TODO This might not work... need to test.

        leaflet_settings = JSONRenderer().render(LeafletMapSerializer(leaflet_map).data)

        context.update({
            'leaflet_settings': leaflet_settings,
            'place_ajax': "{}?as_geojson=1".format(drf_reverse('heritage:api:place-list'))
        })

        return context


class CommunityMapPage(CommunityMapContextMixin, TemplateView):
    template_name = 'communitymap/communitymap_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # This is being json serialized.  Easier to represent bools as 0 or 1.
        context['is_app_page'] = 0
        return context


class CommunityMapApp(CommunityMapContextMixin, TemplateView):
    template_name = 'communitymap/communitymap_app.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # This is being json serialized.  Easier to represent bools as 0 or 1.
        context['is_app_page'] = 1
        return context
