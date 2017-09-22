import json

from django.conf import settings
from django.http import HttpResponse

from tags.models import Tag

from django.apps import apps
get_model = apps.get_model


# Including these declarations here because it would be nice to not rely on the taggit autosuggest app
MAX_SUGGESTIONS = getattr(settings, 'TAGGIT_AUTOSUGGEST_MAX_SUGGESTIONS', 20)
TAG_MODELS = getattr(settings, 'TAGGIT_AUTOSUGGEST_MODELS', {'default': ('taggit', 'Tag')})
if not type(TAG_MODELS) == dict:
    TAG_MODELS = {'default': TAG_MODELS}


def list_all_tags(request):
    """Returns all the tags in the database"""
    all_tags = Tag.objects.all().values_list('name', flat=True)
    return HttpResponse(json.dumps(list(all_tags)), content_type='application/json')


def list_tags(request, tagmodel=None):
    """
    Returns a list of JSON objects with a `name` and a `value` property that
    all start like your query string `q` (not case sensitive).
    """
    if not tagmodel or tagmodel not in TAG_MODELS:
        TAG_MODEL = get_model(*TAG_MODELS['default'])
    else:
        TAG_MODEL = get_model(*TAG_MODELS[tagmodel])

    query = request.GET.get('q', '')
    limit = request.GET.get('limit', MAX_SUGGESTIONS)
    try:
        request.GET.get('limit', MAX_SUGGESTIONS)
        limit = min(int(limit), MAX_SUGGESTIONS)  # max or less
    except ValueError:
        limit = MAX_SUGGESTIONS
    except TypeError:
        pass

    tag_name_qs = TAG_MODEL.objects.filter(name__icontains=query).order_by('name', 'id'). \
        values('pk', 'name')

    if callable(getattr(TAG_MODEL, 'request_filter', None)):
        tag_name_qs = tag_name_qs.filter(TAG_MODEL.request_filter(request)).distinct()

    if MAX_SUGGESTIONS:
        data = [{'id': n['pk'], 'name': n['name'], 'value': n['name']} for n in tag_name_qs[:limit]]
    else:
        data = [{'id': n['pk'], 'name': n['name'], 'value': n['name']} for n in tag_name_qs]

    return HttpResponse(json.dumps(data), content_type='application/json')
