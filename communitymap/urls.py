from django.conf.urls import url, include
from rest_framework import routers

from communitymap.views import CommunityMapPage, CommunityMapApp

router = routers.DefaultRouter()
# router.register(r'places', PlacesViewSet, 'places')


urlpatterns = [
    url(r'^(map/)?$', CommunityMapPage.as_view(), name='map'),
    url(r'^app/$', CommunityMapApp.as_view(), name='app'),  # The fullscreen version of the community map.
]
