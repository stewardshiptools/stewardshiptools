from django.conf.urls import url, include

from rest_framework import routers

# from .models import Project
# from .views import DashboardView, DevelopmentProjectListView, DevelopmentProjectDetailView, DevelopmentProjectCreateView, \
#     DevelopmentProjectUpdateView, DevelopmentProjectGISLayerCreateView, DevelopmentProjectGISLayerUpdateView, \
#     DevelopmentProjectGISLayerDeleteView, DevelopmentProjectGISLayerDetailView
from . import views
import development

# api:
from .views import DevelopmentProjectViewSet, DevelopmentGISLayerFeatureViewSet, DevelopmentAssetViewSet, DevelopmentGISLayerViewSet


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'project', DevelopmentProjectViewSet, 'project')
router.register(r'feature', DevelopmentGISLayerFeatureViewSet, 'feature')
router.register(r'assets', DevelopmentAssetViewSet, 'secure-assets')
router.register(r'gislayers', DevelopmentGISLayerViewSet, 'gislayers')

urlpatterns = [
    url(r'^$', views.DashboardView.as_view(), name='dashboard'),
    url(r'^settings/$', development.views.DevelopmentSettingsView.as_view(), name='settings'),

    # url(r'^fileno/(list/)?$', development.views.DevelopmentProjectListView.as_view(), name='fileno-list'),
    url(r'^fileno/new/$', development.views.FileNoCreateView.as_view(), name='fileno-create'),
    url(r'^fileno/(?P<pk>\d+)/edit$', development.views.FileNoUpdateView.as_view(), name='fileno-update'),
    url(r'^fileno/(?P<pk>\d+)/delete/$', development.views.FileNoDeleteView.as_view(), name='fileno-delete'),

    url(r'^project/(list/)?$', development.views.DevelopmentProjectListView.as_view(), name='project-list'),
    url(r'^project/(list/)?report/$', development.views.DevelopmentProjectListPrintView.as_view(), name='project-list-print'),
    url(r'^project/(?P<pk>\d+)/$', development.views.DevelopmentProjectDetailView.as_view(), name='project-detail'),
    url(r'^project/print/(?P<pk>\d+)/$', development.views.DevelopmentProjectDetailPrintView.as_view(), name='project-detail-print'),
    url(r'^project/new/$', development.views.DevelopmentProjectCreateView.as_view(), name='project-create'),
    url(r'^project/new/xml/$', development.views.DevelopmentProjectCreateFromSERView.as_view(), name='project-create-xml'),


    url(r'^project/(?P<pk>\d+)/edit/$', development.views.DevelopmentProjectUpdateView.as_view(), name='project-update'),
    url(r'^project/(?P<pk>\d+)/delete/$', development.views.DevelopmentProjectDeleteView.as_view(), name='project-delete'),


    url(r'^project/(?P<project_pk>\d+)/location/new/$', development.views.DevelopmentProjectGISLayerCreateView.as_view(), name='project-location-create'),
    url(r'^project/(?P<project_pk>\d+)/location/(?P<pk>\d+)/edit/$', development.views.DevelopmentProjectGISLayerUpdateView.as_view(),
        name='project-location-edit'),
    url(r'^project/(?P<project_pk>\d+)/location/(?P<pk>\d+)/delete/$', development.views.DevelopmentProjectGISLayerDeleteView.as_view(),
        name='project-location-delete'),

    url(r'^gislayer/$', development.views.DevelopmentGISLayerListView.as_view(), name='gislayer-list'),
    url(r'^gislayer/(?P<pk>\d+)/$', development.views.DevelopmentProjectGISLayerDetailView.as_view(), name='gislayer-detail'),
    url(r'^gislayer/new/$', development.views.DevelopmentProjectGISLayerCreateView.as_view(), name='gislayer-create'),
    url(r'^gislayer/(?P<pk>\d+)/edit/$', development.views.DevelopmentProjectGISLayerUpdateView.as_view(), name='gislayer-update'),
    url(r'^gislayer/(?P<pk>\d+)/delete/$', development.views.DevelopmentProjectGISLayerDeleteView.as_view(), name='gislayer-delete'),

    url(r'^project/(?P<project_pk>\d+)/asset/(?P<pk>\d+)/$', development.views.DevelopmentProjectAssetDetailView.as_view(), name='project-secureasset-detail'),
    url(r'^project/(?P<project_pk>\d+)/asset/new/$', development.views.DevelopmentProjectAssetCreateView.as_view(), name='project-secureasset-create'),
    url(r'^project/(?P<project_pk>\d+)/asset/(?P<pk>\d+)/edit/$', development.views.DevelopmentProjectAssetUpdateView.as_view(), name='project-secureasset-update'),
    url(r'^project/(?P<project_pk>\d+)/asset/(?P<pk>\d+)/delete/$', development.views.DevelopmentProjectAssetDeleteView.as_view(), name='project-secureasset-delete'),

    url(r'^project/(?P<project_pk>\d+)/spatialreport/new/$', development.views.DevelopmentSpatialReportFormView.as_view(), name='project-spatialreport-form'),

    url(r'^file/dashboard/$', development.views.SecureAssetsDashboardView.as_view(), name='secureasset-dashboard'),
    url(r'^file/list', development.views.SecureAssetListView.as_view(), name='secureasset-list'),
    url(r'^file/search/$', development.views.SecureAssetSearchView.as_view(), name='secureasset-search'),
    url(r'^file/search/csv/$', development.views.SecureAssetSearchViewCSV.as_view(), name='secureasset-search-csv'),

    url(r'^assets/(?P<pk>\d+)/$', development.views.DevelopmentAssetDetailView.as_view(), name='secureasset-detail'),
    url(r'^assets/new/$', development.views.DevelopmentAssetCreateView.as_view(), name='secureasset-create'),
    url(r'^assets/(?P<pk>\d+)/edit/$', development.views.DevelopmentAssetUpdateView.as_view(), name='secureasset-update'),
    url(r'^assets/(?P<pk>\d+)/delete/$', development.views.DevelopmentAssetDeleteView.as_view(), name='secureasset-delete'),

    url(r'^ser/new/$', development.views.SERFormView.as_view(), name='ser-create'),

    # blow up the reversing. gah! it should work.
    # url('', include('library.urls', namespace='development-library', app_name='library'),

    # Wire up our API using automatic URL routing.
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/layer-master/$', views.DevelopmentGISLayerMasterListAPIView.as_view(), name='layer-master-list-api'),



]
