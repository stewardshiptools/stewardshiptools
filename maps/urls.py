from django.conf.urls import url, include

from rest_framework import routers

from .views import LeafletMapViewSet


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'leaflet-map', LeafletMapViewSet, 'leaflet-map')

urlpatterns = [
    # Wire up our API using automatic URL routing.
    url(r'^api/', include(router.urls, namespace='api')),
]
