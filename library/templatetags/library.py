from django.template import Context
from django.template.loader import get_template
from django import template

from assets.models import SecureAsset, Asset
from library.models import Item, Synthesis, SynthesisItem, CaseBrief, CollectionTag

register = template.Library()


@register.filter()
def get_facet_form_field(form, facet):
    try:
        return form["{}_facet".format(facet)]
    except KeyError:
        return None

@register.filter()
def render_search_result(result, object_list_subtexts):
    '''
    Render a haystack search result - if you want your model to
    define its own result tempaltes, add the property 'search_template'
    to the model that returns the path to the template you want to render.
    convention: 
        app/search/results/model_result.html
    :param result: 
    :return: 
    '''

    template_path = 'some_default_result_template_path'
    context = {}

    if hasattr(result.object, 'search_template'):
        template_path = result.object.search_template
    elif isinstance(result.object, Item):
        template_path = 'search/results/item_result.html'
    elif isinstance(result.object, Synthesis):
        template_path = 'search/results/synthesis_result.html'
    elif isinstance(result.object, SynthesisItem):
        template_path = 'search/results/synthesisitem_result.html'
    elif isinstance(result.object, CaseBrief):
        template_path = 'search/results/casebrief_result.html'
    elif isinstance(result.object, CollectionTag):
        template_path = 'search/results/collectiontag_result.html'
    else:
        template_path = 'search/results/default_result.html'

    template = get_template(template_path)

    context.update({
        'result': result,
        'object_list_subtexts': object_list_subtexts
    })
    return template.render(Context(context))


@register.filter()
def render_related_items(object):
    """
    Returns rendered list of items related to object
    Used in asset search result templates. Could be used elsewhere? Just
    add another isinstance() and your model type.
    :param object: 
    :return: 
    """
    context = {
        'items': Item.objects.none()
    }
    if isinstance(object, SecureAsset):
        context.update({
            'items': object.item_set.all()
        })

    template = get_template('library/related_items.html')
    return template.render(Context(context))


def library_default_kwargs():
    return {
        'card_css_classes': "s12 m6 l4",
        'belongs_to': None
    }


@register.inclusion_tag('library/dashboard_cards/items.html', takes_context=True)
def include_library_items(context, **kwargs):
    """
    Give it some kwargs. It likes:
        - card_css_classes: "s12 m6 l4"
    :param context: 
    :param kwargs: 
    :return: 
    """
    context.update(library_default_kwargs())
    context.update(kwargs)

    belongs_to = context.get('belongs_to', None)
    if belongs_to:
        context['items'] = Item.objects.filter(belongs_to=belongs_to)
    else:
        context['items'] = Item.objects.all()

    return context


@register.inclusion_tag('library/dashboard_cards/casebriefs.html', takes_context=True)
def include_library_casebriefs(context, **kwargs):
    """
    Give it some kwargs. It likes:
        - card_css_classes: "s12 m6 l4"
    :param context: 
    :param kwargs: 
    :return: 
    """
    context.update(library_default_kwargs())
    context.update(kwargs)

    belongs_to = context.get('belongs_to', None)
    if belongs_to:
        context['casebriefs'] = CaseBrief.objects.filter(belongs_to=belongs_to)
    else:
        context['casebriefs'] = CaseBrief.objects.all()

    return context


@register.inclusion_tag('library/dashboard_cards/collectiontags.html', takes_context=True)
def include_library_collectiontags(context, **kwargs):
    """
    Give it some kwargs. It likes:
        - card_css_classes: "s12 m6 l4"
    :param context: 
    :param kwargs: 
    :return: 
    """
    context.update(library_default_kwargs())
    context.update(kwargs)

    belongs_to = context.get('belongs_to', None)
    if belongs_to:
        context['collectiontags'] = CollectionTag.objects.filter(belongs_to=belongs_to)
    else:
        context['collectiontags'] = CollectionTag.objects.all()
    return context


@register.inclusion_tag('library/dashboard_cards/syntheses.html', takes_context=True)
def include_library_syntheses(context, **kwargs):
    """
    Give it some kwargs. It likes:
        - card_css_classes: "s12 m6 l4"
    :param context: 
    :param kwargs: 
    :return: 
    """
    context.update(library_default_kwargs())
    context.update(kwargs)
    belongs_to = context.get('belongs_to', None)
    if belongs_to:
        context['syntheses'] = Synthesis.objects.filter(belongs_to=belongs_to)
    else:
        context['syntheses'] = Synthesis.objects.all()
    return context


@register.inclusion_tag('library/dashboard_cards/search.html', takes_context=True)
def include_library_search(context, **kwargs):
    """
    Give it some kwargs. It likes:
        - card_css_classes: "s12 m6 l4"
    :param context: 
    :param kwargs: 
    :return: 
    """
    context.update(library_default_kwargs())
    context.update(kwargs)
    return context

