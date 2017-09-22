from django.conf.urls import include, url

from rest_framework import routers

from library.views import ItemListView, ItemCreateView, ItemDetailView, ItemDetailPrintView, ItemUpdateView, CollectionTagListView, \
    CollectionTagCreateView, CollectionTagUpdateView, CollectionTagDetailView, CollectionTagDeleteView, LibraryDashboardView, \
    CaseBriefCreateView, CaseBriefDetailView, CaseBriefListView, CaseBriefDetailPrintView, CaseBriefUpdateView, CaseBriefDeleteView, \
    SynthesisCreateView, SynthesisDetailView, SynthesisListView, SynthesisDetailPrintView, SynthesisUpdateView, LibrarySearchView,\
    PersonMentionedTagListView, PersonMentionedTagDetailView, PersonMentionedTagUpdateView, PersonMentionedTagDeleteView, \
    PersonMentionedTagViewSet, ItemDeleteView, SynthesisDeleteView

# ViewSets
from library.views import ItemViewSet, CollectionTagViewSet, CaseBriefViewSet, SynthesisViewSet


router = routers.DefaultRouter()
router.register(r'item', ItemViewSet, 'item')
router.register(r'collection', CollectionTagViewSet, 'collectiontag')
router.register(r'casebrief', CaseBriefViewSet, 'casebrief')
router.register(r'synthesis', SynthesisViewSet, 'synthesis')
router.register(r'personmentioned', PersonMentionedTagViewSet, 'personmentionedtag')

# app_name = 'library'    # for furture django version.
urlpatterns = [
    url(r'^item/(list/)?$', ItemListView.as_view(), name='item-list'),
    url(r'^item/new/$', ItemCreateView.as_view(), name='item-create'),
    url(r'^item/(?P<pk>[0-9]+)/$', ItemDetailView.as_view(), name='item-detail'),
    url(r'^item/(?P<pk>[0-9]+)/report$', ItemDetailPrintView.as_view(), name='item-detail-print'),
    url(r'^item/(?P<pk>[0-9]+)/edit/$', ItemUpdateView.as_view(), name='item-update'),
    url(r'^item/(?P<pk>[0-9]+)/delete/$', ItemDeleteView.as_view(), name='item-delete'),

    url(r'^collection/(list/)?$', CollectionTagListView.as_view(), name='collectiontag-list'),
    url(r'^collection/new/$', CollectionTagCreateView.as_view(), name='collectiontag-create'),
    url(r'^collection/(?P<pk>[0-9]+)/$', CollectionTagDetailView.as_view(), name='collectiontag-detail'),
    url(r'^collection/(?P<pk>[0-9]+)/edit/$', CollectionTagUpdateView.as_view(), name='collectiontag-update'),
    url(r'^collection/(?P<pk>\d+)/delete/$', CollectionTagDeleteView.as_view(), name='collectiontag-delete'),

    url(r'^casebrief/(list/)?$', CaseBriefListView.as_view(), name='casebrief-list'),
    url(r'^casebrief/new/$', CaseBriefCreateView.as_view(), name='casebrief-create'),
    url(r'^casebrief/(?P<pk>[0-9]+)/$', CaseBriefDetailView.as_view(), name='casebrief-detail'),
    url(r'^casebrief/(?P<pk>[0-9]+)/report$', CaseBriefDetailPrintView.as_view(), name='casebrief-detail-print'),
    url(r'^casebrief/(?P<pk>[0-9]+)/edit/$', CaseBriefUpdateView.as_view(), name='casebrief-update'),
    url(r'^casebrief/(?P<pk>\d+)/delete/$', CaseBriefDeleteView.as_view(), name='casebrief-delete'),

    url(r'^synthesis/(list/)?$', SynthesisListView.as_view(), name='synthesis-list'),
    url(r'^synthesis/new/$', SynthesisCreateView.as_view(), name='synthesis-create'),
    url(r'^synthesis/(?P<pk>[0-9]+)/$', SynthesisDetailView.as_view(), name='synthesis-detail'),
    url(r'^synthesis/(?P<pk>[0-9]+)/#synthesis-item-(?P<synthesisitem_id>[0-9]+)/$', SynthesisDetailView.as_view(), name='synthesisitem-detail'),
    url(r'^synthesis/(?P<pk>[0-9]+)/report$', SynthesisDetailPrintView.as_view(), name='synthesis-detail-print'),
    url(r'^synthesis/(?P<pk>[0-9]+)/edit/$', SynthesisUpdateView.as_view(), name='synthesis-update'),
    url(r'^synthesis/(?P<pk>[0-9]+)/delete/$', SynthesisDeleteView.as_view(), name='synthesis-delete'),

    url(r'^personmentioned/(list/)?$', PersonMentionedTagListView.as_view(), name='personmentionedtag-list'),
    url(r'^personmentioned/(?P<pk>[0-9]+)/$', PersonMentionedTagDetailView.as_view(), name='personmentionedtag-detail'),
    url(r'^personmentioned/(?P<pk>[0-9]+)/edit/$', PersonMentionedTagUpdateView.as_view(), name='personmentionedtag-update'),
    url(r'^personmentioned/(?P<pk>\d+)/delete/$', PersonMentionedTagDeleteView.as_view(), name='personmentionedtag-delete'),

    # url(r'^dashboard/$', LibraryDashboardView.as_view(), name='dashboard'),

    url('^search/$', LibrarySearchView.as_view(), name='search'),

    url(r'^api/', include(router.urls, namespace='api'))
]
