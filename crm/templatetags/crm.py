from django import template
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.reverse import reverse

from easy_thumbnails.templatetags.thumbnail import thumbnail_url
register = template.Library()


@register.inclusion_tag('crm/person_list_include.html')
def crm_person_list(attach_id, ajax_url=reverse('crm:api:person-list'), *args, **kwargs):
    response = {
        'attach_id': attach_id,
        'ajax_url': ajax_url,
        'pager': 1,
        'search': 1,
        'grid_class': None
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.inclusion_tag('crm/organization_list_include.html')
def crm_organization_list(attach_id, ajax_url=reverse('crm:api:organization-list'), *args, **kwargs):
    response = {
        'attach_id': attach_id,
        'ajax_url': ajax_url,
        'pager': 1,
        'search': 1
    }

    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.filter
def crm_get_avatar_url(obj):
    """
    Returns the url to the person's resized profile pic.
    Modified to permit person to either be User or Person
    :param obj: instance of crm.Person or auth.User
    :return:
    """

    default_img_url = static('crm/img/trees_small.jpg')

    person = crm_get_person_from_user(obj)

    if person:
        if person.pic:
            return thumbnail_url(person.pic, 'detail')

    return default_img_url


@register.filter
def crm_get_person_text(obj):
    """
    Returns the the person name.
    Modified to permit person to either be User or Person
    :param obj: instance of crm.Person or auth.User
    :return:
    """

    person = crm_get_person_from_user(obj)
    if person:
        return str(person)
    else:
        return str(obj)  # user


def crm_get_person_from_user(user):
    """
    Gets the Person instance related to a User instance. Handles exceptions here.
    :param user:
    :return: Person or None
    """
    if isinstance(user, User):
        try:
            person = user.person
        except ObjectDoesNotExist:
            person = None
    else:
        person = user
    return person