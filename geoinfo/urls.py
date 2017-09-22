from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'layer', views.GISLayerViewSet, 'layer')
router.register(r'feature', views.GISFeatureViewSet, 'feature')
router.register(r'spatialreport', views.SpatialReportViewSet, 'spatialreport')

urlpatterns = [
    url(r'^$', views.DashboardView.as_view(), name='dashboard'),

    # Layer views
    url(r'^layer/misc/(list/)?$', views.GISLayerListView.as_view(), name='layer-list'),
    url(r'^layer/all/(list/)?$', views.GISLayerMasterListView.as_view(), name='layer-master-list'),
    url(r'^layer/(?P<pk>[0-9]+)/$', views.GISLayerDetailView.as_view(), name='layer-detail'),
    url(r'^feature/(?P<pk>[0-9]+)/$', views.GISFeatureDetailView.as_view(), name='feature-detail'),
    url(r'^layer/new/', views.GISLayerCreateView.as_view(), name='layer-create'),
    url(r'^layer/(?P<pk>[0-9]+)/update/$', views.GISLayerUpdateView.as_view(), name='layer-update'),
    url(r'^layer/(?P<pk>[0-9]+)/delete/$', views.GISLayerDeleteView.as_view(), name='layer-delete'),

    # Spatial report views
    url(r'^spatialreport/(list/)?$', views.SpatialReportListView.as_view(), name='spatialreport-list'),
    url(r'^spatialreport/(?P<pk>[0-9]+)/$', views.SpatialReportDetailView.as_view(), name='spatialreport-detail'),
    url(r'^spatialreport/new/$', views.SpatialReportCreateView.as_view(), name='spatialreport-create'),
    url(r'^spatialreport/(?P<pk>[0-9]+)/update/$',
        views.SpatialReportUpdateView.as_view(), name='spatialreport-update'),
    url(r'^spatialreport/(?P<pk>[0-9]+)/delete/$',
        views.SpatialReportDeleteView.as_view(), name='spatialreport-delete'),

    # Spatial report item views
    url(r'^spatialreport/(?P<report_pk>[0-9]+)/item/new/$',
        views.SpatialReportItemCreateView.as_view(), name='spatialreportitem-create'),
    url(r'^spatialreport/(?P<report_pk>[0-9]+)/item/(?P<pk>[0-9]+)/update/$',
        views.SpatialReportItemUpdateView.as_view(), name='spatialreportitem-update'),
    url(r'^spatialreportitem/(?P<pk>[0-9]+)/delete/$',
        views.SpatialReportItemDeleteView.as_view(), name='spatialreportitem-delete'),

    # Rest API URL routing.
    url(r'^api/', include(router.urls, namespace='api')),
    url(r'^api/layer-master/$', views.GISLayerMasterListAPIView.as_view(), name='layer-master-list-api'),
    url(r'^api/feature-point/$', views.GISFeaturePointViewSet.as_view(), name='feature-point-list'),
    url(r'^api/feature-line/$', views.GISFeatureLineViewSet.as_view(), name='feature-line-list'),
    url(r'^api/feature-polygon/$', views.GISFeaturePolygonViewSet.as_view(), name='feature-polygon-list'),
]
