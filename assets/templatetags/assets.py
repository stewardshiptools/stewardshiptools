from django import template

register = template.Library()


@register.inclusion_tag('assets/metadocument_inline_form.html', takes_context=True)
def include_metadocument_inline_form(context, **kwargs):
    response = {'context': context}
    for k in kwargs.keys():
        response[k] = kwargs[k]
    return response


@register.assignment_tag()
def form_field_has_data(form_field, result_if_has_value=True, result_if_no_value=''):
    '''
    Can use this to set an element class depending on whether the form field has any
     data in it or not --- used in setting expanded/collapsed collection items.
    :param form_field:
    :param result_if_has_value:
    :param result_if_no_value:
    :return:
    '''
    try:
        if form_field.form.initial[form_field.name]:
            return result_if_has_value
    except KeyError:
        pass
    return result_if_no_value


@register.assignment_tag()
def get_child_asset(asset_instance):
    return asset_instance.__class__.objects.get_subclass(pk=asset_instance.pk)
