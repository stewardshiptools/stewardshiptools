from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'role', views.RoleViewSet, 'role')
router.register(r'organization', views.OrganizationViewSet, 'organization')
router.register(r'person', views.PersonViewSet, 'person')

urlpatterns = [
    url(r'^person/list/$', views.PersonListView.as_view(), name='person-list'),
    url(r'^person/(?P<pk>[0-9]+)/$', views.PersonDetailView.as_view(), name='person-detail'),
    url(r'^person/new/$', views.PersonCreateView.as_view(), name='person-create'),
    url(r'^person/(?P<pk>[0-9]+)/update/$', views.PersonUpdateView.as_view(), name='person-update'),
    url(r'^person/(?P<pk>[0-9]+)/delete/$', views.PersonDeleteView.as_view(), name='person-delete'),

    url(r'^organization/list/$', views.OrganizationListView.as_view(), name='organization-list'),
    url(r'^organization/(?P<pk>[0-9]+)/$', views.OrganizationDetailView.as_view(), name='organization-detail'),
    url(r'^organization/(?P<pk>[0-9]+)/update/$', views.OrganizationUpdateView.as_view(), name='organization-update'),
    url(r'^organization/(?P<pk>[0-9]+)/delete/$', views.OrganizationDeleteView.as_view(), name='organization-delete'),
    url(r'^organization/new/$', views.OrganizationCreateView.as_view(), name='organization-create'),

    # Rest API URL routing.
    url(r'^api/', include(router.urls, namespace='api')),
]
