from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required, permission_required

from rest_framework import routers, serializers, viewsets

# Normal views:
from .views import DashboardView, SpeciesObservationView, SpeciesObservationDetailView ,\
    SpeciesView, SpeciesDetailView, SpeciesGroupView, ProjectListView, ProjectDetailView, \
    InterviewListView, InterviewDetailView, InterviewCreateView, InterviewUpdateView, InterviewDeleteView, \
    CulturalObservationDetailView, CulturalObservationListView, \
    ProjectCreateView, ProjectAssetCreateView, ProjectAssetDeleteView, \
    InterviewAssetCreateView, InterviewAssetDeleteView, ProjectUpdateView, ProjectDeleteView, LayerGroupCreateView, \
    LayerGroupUpdateView, LayerGroupDeleteView, HeritageGISLayerCreateView, HeritageGISLayerUpdateView, \
    HeritageGISLayerDeleteView, SessionAssetDeleteView, HeritageGISLayerDetailView, HeritageGISLayerListView, \
    InterviewAssetDetailView, InterviewAssetUpdateView, ProjectAssetDetailView, ProjectAssetUpdateView, ProjectDetailPrintView, \
    SessionAssetDetailView, GetHeritageAssetFileView

# Rest views:
from .views import SpeciesViewSet, SpeciesGroupViewSet, SpeciesObservationViewSet, \
    InterviewViewSet, InterviewAssetViewSet, SessionAssetViewSet, ProjectViewSet, ProjectDeepInfoViewSet, \
    ProjectParticipantViewSet, CulturalObservationViewSet, ProjectAssetViewSet, HeritageGISLayerFeatureViewSet, \
    HeritageGISLayerViewSet, HeritageAssetViewSet, PlaceViewSet

import heritage

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'species', SpeciesViewSet)
router.register(r'species-group', SpeciesGroupViewSet)
router.register(r'species-observation', SpeciesObservationViewSet, 'species-observation')
router.register(r'cultural-observation', CulturalObservationViewSet, 'cultural-observation')
router.register(r'interview', InterviewViewSet)
router.register(r'interview-asset', InterviewAssetViewSet, 'interview-asset')
router.register(r'session-asset', SessionAssetViewSet, 'session-asset')
router.register(r'project', ProjectViewSet, 'project')
router.register(r'project-asset', ProjectAssetViewSet, 'project-asset')
router.register(r'project-deep-info', ProjectDeepInfoViewSet, 'project-deep-info')
router.register(r'project-participant', ProjectParticipantViewSet, 'project-participant')
router.register(r'sites', HeritageGISLayerFeatureViewSet, 'sites')
router.register(r'gislayers', HeritageGISLayerViewSet, 'gislayers')
router.register(r'assets', HeritageAssetViewSet, 'secure-assets')
router.register(r'place', PlaceViewSet, 'place')


urlpatterns = [
    url(r'^$', DashboardView.as_view(), name='dashboard'),

    url(r'^settings/$', heritage.views.HeritageSettingsView.as_view(), name='settings'),

    url(r'^species-records/$', SpeciesObservationView.as_view(), name='species-observations'),
    url(r'^species-records/(?P<pk>\d+)/$', SpeciesObservationDetailView.as_view(), name='species-observation-detail'),
    url(r'^species/(?P<pk>\d+)/$', SpeciesDetailView.as_view(), name='species-detail'),
    url(r'^species-group/$', SpeciesGroupView.as_view(), name='species-groups'),
    url(r'^species/$', SpeciesView.as_view(), name='species'),

    url(r'^interview/$', InterviewListView.as_view(), name='interviews'),
    url(r'^interview/new/$', InterviewCreateView.as_view(), name='interview-create'),
    url(r'^interview/(?P<pk>\d+)/$', InterviewDetailView.as_view(), name='interview-detail'),
    url(r'^interview/(?P<pk>\d+)/edit/$', InterviewUpdateView.as_view(), name='interview-update'),
    url(r'^interview/(?P<pk>\d+)/delete/$', InterviewDeleteView.as_view(), name='interview-delete'),

    url(r'^interview/(?P<interview_pk>\d+)/dataset/new/$', LayerGroupCreateView.as_view(), name='layergroup-create'),
    url(r'^interview/(?P<interview_pk>\d+)/dataset/(?P<pk>\d+)/edit/$', LayerGroupUpdateView.as_view(), name='layergroup-update'),
    url(r'^interview/(?P<interview_pk>\d+)/dataset/(?P<pk>\d+)/delete/$', LayerGroupDeleteView.as_view(), name='layergroup-delete'),

    url(r'^interview/(?P<interview_pk>\d+)/dataset/(?P<layergroup_pk>\d+)/gislayer/new/$',
        HeritageGISLayerCreateView.as_view(), name='gislayer-create'),
    url(r'^interview/(?P<interview_pk>\d+)/dataset/(?P<layergroup_pk>\d+)/gislayer/(?P<pk>\d+)/edit/$',
        HeritageGISLayerUpdateView.as_view(), name='gislayer-update'),
    url(r'^interview/(?P<interview_pk>\d+)/dataset/(?P<layergroup_pk>\d+)/gislayer/(?P<pk>\d+)/delete/$',
        HeritageGISLayerDeleteView.as_view(), name='gislayer-delete'),

    url(r'^gislayer/$',
        HeritageGISLayerListView.as_view(), name='gislayer-list'),
    url(r'^gislayer/(?P<pk>\d+)/$',
        HeritageGISLayerDetailView.as_view(), name='gislayer-detail'),

    url(r'^gislayer/new/$',
        HeritageGISLayerCreateView.as_view(), name='gislayer-create-generic'),
    url(r'^gislayer/(?P<pk>\d+)/edit/$',
        HeritageGISLayerUpdateView.as_view(), name='gislayer-update-generic'),
    url(r'^gislayer/(?P<pk>\d+)/delete/$',
        HeritageGISLayerDeleteView.as_view(), name='gislayer-delete-generic'),

    url(r'^interview/(?P<interview_pk>\d+)/asset/(?P<pk>\d+)/$', InterviewAssetDetailView.as_view(), name='interview-secureasset-detail'),
    url(r'^interview/(?P<interview_pk>\d+)/asset/new/$', InterviewAssetCreateView.as_view(), name='interview-secureasset-create'),
    url(r'^interview/(?P<interview_pk>\d+)/asset/(?P<pk>\d+)/edit/$', InterviewAssetUpdateView.as_view(), name='interview-secureasset-update'),
    url(r'^interview/(?P<interview_pk>\d+)/asset/(?P<pk>\d+)/delete/$', InterviewAssetDeleteView.as_view(), name='interview-secureasset-delete'),

    url(r'^session/(?P<session_pk>\d+)/asset/(?P<pk>\d+)/$', SessionAssetDetailView.as_view(), name='session-secureasset-detail'),
    url(r'^session/(?P<session_pk>\d+)/asset/delete/(?P<pk>\d+)/$', SessionAssetDeleteView.as_view(), name='session-secureasset-delete'),

    url(r'^project/list/$', ProjectListView.as_view(), name='project-list'),
    url(r'^project/(?P<pk>\d+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^project/print/(?P<pk>\d+)/$', ProjectDetailPrintView.as_view(), name='project-detail-print'),
    url(r'^project/new/$', ProjectCreateView.as_view(), name='project-create'),
    url(r'^project/(?P<pk>\d+)/update$', ProjectUpdateView.as_view(), name='project-update'),
    url(r'^project/(?P<pk>\d+)/delete/$', ProjectDeleteView.as_view(), name='project-delete'),

    url(r'^project/(?P<project_pk>\d+)/asset/(?P<pk>\d+)/$', ProjectAssetDetailView.as_view(), name='project-secureasset-detail'),
    url(r'^project/(?P<project_pk>\d+)/asset/new/$', ProjectAssetCreateView.as_view(), name='project-secureasset-create'),
    url(r'^project/(?P<project_pk>\d+)/asset/(?P<pk>\d+)/edit/$', ProjectAssetUpdateView.as_view(), name='project-secureasset-update'),
    url(r'^project/(?P<project_pk>\d+)/asset/(?P<pk>\d+)/delete/$', ProjectAssetDeleteView.as_view(), name='project-secureasset-delete'),

    url(r'^cultural-records/$', CulturalObservationListView.as_view(), name='cultural-observations'),
    url(r'^cultural-records/(?P<pk>\d+)/$', CulturalObservationDetailView.as_view(), name='cultural-observation-detail'),

    url(r'^file/dashboard/$', heritage.views.SecureAssetsDashboardView.as_view(), name='secureasset-dashboard'),
    url(r'^file/list', heritage.views.SecureAssetListView.as_view(), name='secureasset-list'),
    url(r'^file/search/$', heritage.views.SecureAssetSearchView.as_view(), name='secureasset-search'),
    url(r'^file/search/csv/$', heritage.views.SecureAssetSearchViewCSV.as_view(), name='secureasset-search-csv'),

    url(r'^assets/new/$', heritage.views.HeritageAssetCreateView.as_view(), name='secureasset-create'),
    url(r'^assets/(?P<pk>\d+)/$', heritage.views.HeritageAssetDetailView.as_view(), name='secureasset-detail'),
    url(r'^assets/(?P<pk>\d+)/edit/$', heritage.views.HeritageAssetUpdateView.as_view(), name='secureasset-update'),
    url(r'^assets/(?P<pk>\d+)/delete/$', heritage.views.HeritageAssetDeleteView.as_view(), name='secureasset-delete'),

    url(r'^media-secure/download/(?P<file_id>[0-9]+)/$',
        GetHeritageAssetFileView.as_view(),
        kwargs={'as_attachment': True},
        name='secureasset-download'),
    url(r'^media-secure/serve/(?P<file_id>[0-9]+)/$',
        GetHeritageAssetFileView.as_view(),
        kwargs={'as_attachment': False},
        name='secureasset-serve'),

    url(r'^place/(list/)?$', heritage.views.PlaceListView.as_view(), name='place-list'),
    url(r'^place/new/$', heritage.views.PlaceCreateView.as_view(), name='place-create'),
    url(r'^place/(?P<pk>[0-9]+)/$', heritage.views.PlaceDetailView.as_view(), name='place-detail'),
    url(r'^place/(?P<pk>[0-9]+)/edit/$', heritage.views.PlaceUpdateView.as_view(), name='place-update'),
    url(r'^place/(?P<pk>[0-9]+)/delete/$', heritage.views.PlaceDeleteView.as_view(), name='place-delete'),

    url(r'^place/suggest.json/$', heritage.views.list_places_json, name='place-suggestions'),

    # blow up the reversing. gah! it should work.
    # url('', include('library.urls', namespace='heritage-library', app_name='library'),

    # Wire up our API using automatic URL routing.
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/layer-master/$', heritage.views.HeritageGISLayerMasterListAPIView.as_view(), name='layer-master-list-api'),
]
