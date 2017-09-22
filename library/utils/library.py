"""
Some helpful library things.
"""
from django.apps import apps
from django.core.urlresolvers import reverse
from rest_framework.reverse import reverse as rest_reverse
from rest_framework.request import Request as RestRequest

from library.models import Item, DublinCore, Holdings, Review, ResearcherNotes
from model_mommy import mommy

import re

def killallhumans():
    """
    Terrible, bad, scary method that deletes everything in the Library.
    This is only for Library development and should be removed.
    
    Note to self: when I accidentally did: apps.get_models() # PLURAL apps
    it set about deleting every damn thing. Cool and terrifying.
    :return:
    """

    # delete all in library:
    app = apps.get_app_config('library')
    for model in app.get_models():
        print("Deleting all {} instances of {}".format(model.objects.count(), model))
        if hasattr(model, 'deletable_objects'):
            for obj in model.deletable_objects.all():
                obj.delete(soft=False)
        else:
            model.objects.all().delete()


def fill_library_with_crap(quantiy=300):
    """
    WARNING: this will really fill the library with crap. Don't use it.
    :param quantiy: how many craps you want to put in the library.
    :return:
    """
    items = mommy.make(Item, _quantity=quantiy)
    dublin_cores = mommy.make(DublinCore, _fill_optional=True, _quantity=quantiy, make_m2m=True)
    holdings = mommy.make(Holdings, _fill_optional=True, _quantity=quantiy, make_m2m=True)
    reviews = mommy.make(Review, _fill_optional=True, _quantity=quantiy, make_m2m=True)
    researchnotes = mommy.make(ResearcherNotes, _fill_optional=True, _quantity=quantiy, make_m2m=True)

    for item in items:
        item.dublin_core = dublin_cores.pop()
        item.holdings = holdings.pop()
        item.review = reviews.pop()
        item.researcher_notes = researchnotes.pop()
        item.save()


def get_belongs_to_from_request(request):
    """
        TODO: teasing out the belongs_to property is not as cool as it should be.
    :param self: 
    :param request: 
    :return: 
    """

    # this is what I preferred but the bit with ":api:" started to throw
    # it all off. Hhhh.
    # return request.resolver_match.namespace
    return request.resolver_match.namespaces[0]


def get_belongs_to_from_rest_request(request):
    """
    NOTE: do not include the "library:" namespace when reversing with this.
    Finds the django request buried in the rest request and calls the other method to get 
    the belongs to.
    :param request: 
    :return: 
    """
    return get_belongs_to_from_request(request._request)


def library_reverse_rest(*args, **kwargs):
    if 'kwargs' in kwargs.keys():
        request = kwargs.pop('request', None)

        # return rest_reverse('library:collectiontag-detail', kwargs={'pk': collection.pk})
        if request:
            if isinstance(request, RestRequest):
                belongs_to = get_belongs_to_from_request(request)
                new_namespace = '{}:{}'.format(belongs_to, args[0])
                args_new = [new_namespace, ]
                args_new.extend(args[1:])
                args = args_new

            kwargs['kwargs'].update({'request': request})  # put it in the right spot for the rest reverse method.

    return rest_reverse(*args, **kwargs)


def library_reverse(*args, **kwargs):
    """
    Permits a "reqeust" kwarg for figuring out the proper current app. WTF django.
    :param args: 
    :param kwargs: 
    :return: 
    """
    current_app = kwargs.get('current_app', None)
    request = kwargs.pop('request', None)
    if current_app is None and request is not None:
        kwargs['current_app'] = request.resolver_match.namespaces[0]
    return reverse(*args, **kwargs)


def replace_nodes_with_prefixes(text, prefix_string="I-"):
    """
    Looks for numbers wrapped with parentheses and replaces
    that with the prefix. Eg (1234) becomes (I-1234)
    :param text: 
    :param prefix_string: 
    :return: 
    """
    pattern = '\((\d+)\)'
    return re.sub(pattern, lambda x: "(I-" + x.group(0)[1:], text)
