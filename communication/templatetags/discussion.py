import string
from django.template import Context
from django.template.loader import get_template
from django import template

register = template.Library()

import crm


@register.inclusion_tag('comments/form.html')
def render_cedar_comment_form(**kwargs):
    object = kwargs.pop('object', None)
    parent_id = kwargs.pop('parent_id', None)   # id of parent comment

    if object is None:
        raise AssertionError("object kwarg cannot be None")
    else:
        return {
            'object': object,
            'parent_id': parent_id
        }
    #
    # response = {
    #     'element_id': kwargs.pop('element_id', None),
    #     'data': data,
    #     'related_object': related_object,
    #     'include_toolbar': kwargs.pop('include_toolbar', True)
    # }
    return response


# @register.filter
# def render_related_communication_items(related_object):
#     '''
#     Called by the CommunicationViewset
#     to render data if html is requested.
#     :param related_object:
#     :return: rendered communication items list (<ul>)
#     '''
#     comms_objects = Communication.get_communications_related_to(related_object)
#     context = Context({'data': comms_objects})
#     t = get_template("communication/communication_items.html")
#     return t.render(context)
