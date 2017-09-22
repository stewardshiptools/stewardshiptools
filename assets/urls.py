from django.conf.urls import include, url
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from rest_framework import routers

import assets

# api:
from .views import SecureAssetViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'assets', SecureAssetViewSet, 'secure-assets')

urlpatterns = [

    url(r'^media-secure/download/(?P<file_id>[0-9]+)/$',
        assets.views.GetSecureFileView.as_view(),
        kwargs={'as_attachment': True},
        name='secureasset-download'),
    url(r'^media-secure/serve/(?P<file_id>[0-9]+)/$',
        assets.views.GetSecureFileView.as_view(),
        kwargs={'as_attachment': False},
        name='secureasset-serve'),

    # url(r'^securefile/detail/(?P<pk>[0-9]+)/$', assets.views.SecureAssetDetailView.as_view(), name='secureasset-detail'),
    # url(r'^securefile/edit/(?P<pk>[0-9]+)/$', assets.views.SecureAssetUpdateView.as_view(), name='secureasset-update'),
    # url(r'^securefile/delete/(?P<pk>[0-9]+)/$', assets.views.SecureAssetDeleteView.as_view(), name='secureasset-delete'),
    # url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    url(r'^file-download/(?P<file_id>[0-9]+)/$',
        assets.views.GetInsecureFileView.as_view(),
        kwargs={'as_attachment': True},
        name='asset-download'),
    url(r'^file/(?P<file_id>[0-9]+)/$',
        assets.views.GetInsecureFileView.as_view(),
        kwargs={'as_attachment': False},
        name='asset-serve'),

    url(r'^file/new/$', assets.views.SecureAssetCreateView.as_view(), name='secureasset-create'),
    url(r'^file/detail/(?P<pk>[0-9]+)/$', assets.views.SecureAssetDetailView.as_view(), name='secureasset-detail'),
    url(r'^file/edit/(?P<pk>[0-9]+)/$', assets.views.SecureAssetUpdateView.as_view(), name='secureasset-update'),
    url(r'^file/delete/(?P<pk>[0-9]+)/$', assets.views.SecureAssetDeleteView.as_view(), name='secureasset-delete'),

    # I don't really like it here. I also wonder if it would be helpful to have a
    # url that takes a setting name as one of the url components.
    url(r'^file/setting/$', assets.views.SetFileSettingView.as_view(), name='asset-setting'),

    url('^dashboard/$', assets.views.SecureAssetsDashboardView.as_view(), name='secureasset-dashboard'),
    url('^search/$', assets.views.SecureAssetSearchView.as_view(), name='secureasset-search'),
    # url('^library/search/$', assets.views.SecureAssetSearchViewCSV.as_view(), name='secureasset-search-csv'),
    url('^list/$', assets.views.SecureAssetListView.as_view(), name='secureasset-list'),

    url('^manage$', assets.views.SecureAssetManageView.as_view(), name='manage'),

    # Wire up our API using automatic URL routing.
    url(r'^api/', include(router.urls, namespace='api')),

]
