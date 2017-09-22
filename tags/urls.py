from django.conf.urls import url, include

from tags.views import list_all_tags, list_tags

urlpatterns = [
    url(r'^list_all.json', list_all_tags, name='tags-list-all'),
    url(r'^list/$', list_tags, name='autosuggest-list'),
    url(r'^list/(?P<tagmodel>[\._\w]+)/$', list_tags,
        name='autosuggest-list'),
]
