from django.conf.urls import url, include
from rest_framework import routers

from ecosystems.views import DashboardView, SecureAssetsDashboardView, SecureAssetListView,\
    SecureAssetSearchView, SecureAssetSearchViewCSV, EcosystemsAssetDetailView, EcosystemsAssetCreateView,\
    EcosystemsAssetUpdateView, EcosystemsAssetDeleteView, EcosystemsGISLayerCreateView, EcosystemsGISLayerDeleteView, EcosystemsGISLayerDetailView,\
    EcosystemsGISLayerUpdateView, EcosystemsGISLayerListView, EcosystemsGISLayerViewSet, EcosystemsAssetViewSet, \
    EcosystemsGISLayerMasterListAPIView, EcosystemsProjectViewSet, EcosystemsGISLayerFeatureViewSet, PlantTagListView, PlantTagViewSet, \
    PlantTagDetailView, PlantTagCreateView, PlantTagUpdateView, PlantTagDeleteView, \
    AnimalTagViewSet, AnimalTagListView, AnimalTagDetailView, AnimalTagUpdateView, AnimalTagCreateView, AnimalTagDeleteView, \
    list_plant_or_animal_tags

import ecosystems

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'gislayers', EcosystemsGISLayerViewSet, 'gislayers')
router.register(r'assets', EcosystemsAssetViewSet, 'secure-assets')
router.register(r'project', EcosystemsProjectViewSet, 'project')
router.register(r'feature', EcosystemsGISLayerFeatureViewSet, 'feature')
router.register(r'plant', PlantTagViewSet, 'planttag')
router.register(r'animal', AnimalTagViewSet, 'animaltag')

urlpatterns = [
    url(r'^$', DashboardView.as_view(), name='dashboard'),
    url(r'^settings/$', ecosystems.views.EcosystemsSettingsView.as_view(), name='settings'),

    url(r'^file/dashboard/$', SecureAssetsDashboardView.as_view(), name='secureasset-dashboard'),
    url(r'^file/list', SecureAssetListView.as_view(), name='secureasset-list'),
    url(r'^file/search/$', SecureAssetSearchView.as_view(), name='secureasset-search'),
    url(r'^file/search/csv/$', SecureAssetSearchViewCSV.as_view(), name='secureasset-search-csv'),

    url(r'^assets/(?P<pk>\d+)/$', EcosystemsAssetDetailView.as_view(), name='secureasset-detail'),
    url(r'^assets/new/$', EcosystemsAssetCreateView.as_view(), name='secureasset-create'),
    url(r'^assets/(?P<pk>\d+)/edit/$', EcosystemsAssetUpdateView.as_view(), name='secureasset-update'),
    url(r'^assets/(?P<pk>\d+)/delete/$', EcosystemsAssetDeleteView.as_view(), name='secureasset-delete'),

    url(r'^gislayer/new/$', EcosystemsGISLayerCreateView.as_view(), name='gislayer-create'),
    url(r'^gislayer/(?P<pk>\d+)/edit/$', EcosystemsGISLayerUpdateView.as_view(), name='gislayer-update'),
    url(r'^gislayer/(?P<pk>\d+)/delete/$', EcosystemsGISLayerDeleteView.as_view(), name='gislayer-delete'),
    url(r'^gislayer/list$', EcosystemsGISLayerListView.as_view(), name='gislayer-list'),
    url(r'^gislayer/(?P<pk>\d+)/$', EcosystemsGISLayerDetailView.as_view(), name='gislayer-detail'),

    # eco prjs:
    url(r'^project/(list/)?$', ecosystems.views.EcosystemsProjectListView.as_view(), name='project-list'),
    url(r'^project/(?P<pk>\d+)/$', ecosystems.views.EcosystemsProjectDetailView.as_view(), name='project-detail'),
    # url(r'^project/print/(?P<pk>\d+)/$', ecosystems.views.EcosystemsProjectDetailPrintView.as_view(), name='project-detail-print'),
    url(r'^project/new/$', ecosystems.views.EcosystemsProjectCreateView.as_view(), name='project-create'),
    url(r'^project/(?P<pk>\d+)/edit/$', ecosystems.views.EcosystemsProjectUpdateView.as_view(), name='project-update'),
    url(r'^project/(?P<pk>\d+)/delete/$', ecosystems.views.EcosystemsProjectDeleteView.as_view(), name='project-delete'),

    # eco prj locations (gis layers):
    url(r'^project/(?P<project_pk>\d+)/location/new/$', ecosystems.views.EcosystemsProjectGISLayerCreateView.as_view(),
        name='project-location-create'),
    url(r'^project/(?P<project_pk>\d+)/location/(?P<pk>\d+)/edit/$', ecosystems.views.EcosystemsProjectGISLayerUpdateView.as_view(),
        name='project-location-edit'),
    url(r'^project/(?P<project_pk>\d+)/location/(?P<pk>\d+)/delete/$', ecosystems.views.EcosystemsProjectGISLayerDeleteView.as_view(),
        name='project-location-delete'),

    # eco prj assets:
    url(r'^project/(?P<project_pk>\d+)/asset/(?P<pk>\d+)/$', ecosystems.views.EcosystemsProjectAssetDetailView.as_view(),
        name='project-secureasset-detail'),
    url(r'^project/(?P<project_pk>\d+)/asset/new/$', ecosystems.views.EcosystemsProjectAssetCreateView.as_view(), name='project-secureasset-create'),
    url(r'^project/print/(?P<pk>\d+)/$', ecosystems.views.EcosystemsProjectDetailPrintView.as_view(), name='project-detail-print'),
    url(r'^project/(?P<project_pk>\d+)/asset/(?P<pk>\d+)/edit/$', ecosystems.views.EcosystemsProjectAssetUpdateView.as_view(),
        name='project-secureasset-update'),
    url(r'^project/(?P<project_pk>\d+)/asset/(?P<pk>\d+)/delete/$', ecosystems.views.EcosystemsProjectAssetDeleteView.as_view(),
        name='project-secureasset-delete'),


    url(r'^plant/(list/)?$', PlantTagListView.as_view(), name='planttag-list'),
    url(r'^plant/new/$', PlantTagCreateView.as_view(), name='planttag-create'),
    url(r'^plant/(?P<pk>[0-9]+)/$', PlantTagDetailView.as_view(), name='planttag-detail'),
    url(r'^plant/(?P<pk>[0-9]+)/edit/$', PlantTagUpdateView.as_view(), name='planttag-update'),
    url(r'^plant/(?P<pk>\d+)/delete/$', PlantTagDeleteView.as_view(), name='planttag-delete'),
    
    url(r'^animal/(list/)?$', AnimalTagListView.as_view(), name='animaltag-list'),
    url(r'^animal/new/$', AnimalTagCreateView.as_view(), name='animaltag-create'),
    url(r'^animal/(?P<pk>[0-9]+)/$', AnimalTagDetailView.as_view(), name='animaltag-detail'),
    url(r'^animal/(?P<pk>[0-9]+)/edit/$', AnimalTagUpdateView.as_view(), name='animaltag-update'),
    url(r'^animal/(?P<pk>\d+)/delete/$', AnimalTagDeleteView.as_view(), name='animaltag-delete'),

    # Ajax search views for plant/animal autosuggestions
    url(r'^suggest_plant/$', list_plant_or_animal_tags, {'model_name': 'plant'}, name='plant-suggestions'),
    url(r'^suggest_animal/$', list_plant_or_animal_tags, {'model_name': 'animal'}, name='animal-suggestions'),

    # Wire up our API using automatic URL routing.
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/layer-master/$', EcosystemsGISLayerMasterListAPIView.as_view(), name='layer-master-list-api'),
]
