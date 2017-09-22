import string
from django.template import Context
from django.template.loader import get_template
from django import template
from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from collections import OrderedDict
from rest_framework.reverse import reverse

from communication.models import Communication

register = template.Library()

import communication


@register.inclusion_tag('communication/communications.html')
def render_communication_tools(**kwargs):
    '''
    Renders the communications list and toolbar
    :param kwargs:
        related_object: the HER/DEV project (other?) that these comms are related to.
        element_id: the parent html element that the communications tool will go into.
        include_toolbar: True/False, whether to render the filters or not.
        loadall: True/False, if wanting to override the initial dataset that is loaded (use only for print view really)
    :return:
    '''
    related_object = kwargs.pop('related_object', False)  # False is more useful in the js than None.

    data = []   # should be left empty unless loadall is specified.

    if kwargs.pop('loadall', False):
        if not related_object:
            data = Communication.objects.all()
        else:
            data = Communication.get_communications_related_to(related_object)

    response = {
        'element_id': kwargs.pop('element_id', None),
        'data': data,
        'related_object': related_object,
        'include_toolbar': kwargs.pop('include_toolbar', True)
    }
    return response


@register.filter
def render_related_communication_items(related_object):
    '''
    Called by the CommunicationViewset
    to render data if html is requested.
    :param related_object:
    :return: rendered communication items list (<ul>)
    '''
    comms_objects = Communication.get_communications_related_to(related_object)
    context = Context({'data': comms_objects})
    t = get_template("communication/communication_items.html")
    return t.render(context)


@register.filter
def get_model_title_singular(object):
    return object._meta.verbose_name.title()


@register.filter
def get_model_title_plural(object):
    return object._meta.verbose_name_plural.title()


@register.inclusion_tag('communication/communication_items.html')
def render_communication_items(**kwargs):
    # Explicitly describe the kwargs we are interested in.
    # Note: 'data' should be a list of communications instances. Bad name,
    # but DRF template render breaks if named otherwise.

    response = {
        'comms_list_id': kwargs.pop('comms_list_id', None),
        'data': kwargs.pop('data', None),
    }

    # Get remaining kwargs:
    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.filter
def render_communication_item(communication_object):
    '''
    Called by the communication_items.html template to render each separate
    communication item.
    :param communication_object:
    :return: rendered communication item (<li>)
    '''
    # the api will return an ordered dict instead of a Communication instance,
    # so check for that here and get the actual comm object:

    # We may have gotten an OrderedDict from the serializer for a CommunicationRelation,
    # get the Communication object via the comm key:
    if isinstance(communication_object, OrderedDict):

        if 'comm' in communication_object:
            communication_object = Communication.objects.get(id=communication_object['comm'])
        else:
            communication_object = Communication.objects.get(id=communication_object['id'])
            # communication_object = Communication.objects.get(id=communication_object['id'])

    context = Context({'object': communication_object})

    if isinstance(communication_object.comm_type, communication.models.Message):
        t = get_template("communication/items/item_message.html")
    elif isinstance(communication_object.comm_type, communication.models.PhoneCall):
        t = get_template("communication/items/item_phonecall.html")
    elif isinstance(communication_object.comm_type, communication.models.Fax):
        t = get_template("communication/items/item_fax.html")
    elif isinstance(communication_object.comm_type, communication.models.Letter):
        t = get_template("communication/items/item_letter.html")
    else:
        return None
    return t.render(context)


@register.inclusion_tag('communication/communication_toolbar.html')
def render_communication_toolbar(**kwargs):
    # For certain tools to work we should have a related_object:
    related_object = kwargs.pop('related_object', None)
    if related_object:
        related_ct = ContentType.objects.get_for_model(related_object)
    else:
        related_ct = None

    response = {
        'element_id': kwargs.pop('element_id', None),
        'related_object': related_object,
        'related_ct': related_ct,
        'base_url': reverse('communication:api:communication-list')
    }

    # Get remaining kwargs:
    for k in kwargs.keys():
        response[k] = kwargs[k]

    return response


@register.assignment_tag
def direction_icon_type(incoming):
    if incoming:
        return 'call_received'
    else:
        return 'call_made'


@register.assignment_tag
def get_comm_type_names_list(related_object=None):
    '''
    Takes a related object (eg Development Project instance) and should
    give back a list of related communication type names. Used in dropdown filtering:
    phone call, fax, etc.
    :param related_object:
    :return: list of dicts - ct_name and pretty_name
    '''
    if related_object:
        comms_qs = Communication.get_communications_related_to(related_object=related_object)
    else:
        comms_qs = Communication.objects.all()

    # See http://stackoverflow.com/a/9018019 for why we need an empty order by at the end. Seems
    # any hidden order bys will confuse a distinct.

    comm_type_model_names = comms_qs.values_list("comm_type_ct__model").distinct().order_by()

    # change from tuples to normal string list items:
    names = []
    for name_tuple in comm_type_model_names:
        name = name_tuple[0]
        if name == 'message':
            names.append({
                'ct_name': name,
                'pretty_name': 'Email'
            })
        else:
            names.append({
                'ct_name': name,
                'pretty_name': string.capwords(name)
            })
    return names


@register.assignment_tag
def get_content_type(some_instance):
    try:
        return ContentType.objects.get_for_model(some_instance)
    except ContentType.DoesNotExist:
        return None


@register.assignment_tag
def get_attribute_of_first_obj(reverse_obj_manager, attribute_name):
    '''
    Use this as a short-cut when dealing with generic reverse object managers.
    In communcations we know that there is only one comm_type per communication,
    this will save the needless loop structure in the template neede to get the
    attribute we want.
    :param reverse_obj_manager:
    :param attribute_name:
    :return: attribute value, or None
    '''
    return getattr(reverse_obj_manager.first(), attribute_name, None)


@register.assignment_tag
def get_communication_object(reverse_obj_manager):
    '''
    Use this as a short-cut when dealing with generic reverse object managers.
    In communcations we know that there is only one comm_type per communication,
    this will save the needless loop structure in the template neede to get the
    communication instance we want.
    :param reverse_obj_manager: a communication property on a Message, Fax, Phonecall, etc.
    :return: communication instance or None
    '''
    return reverse_obj_manager.first()