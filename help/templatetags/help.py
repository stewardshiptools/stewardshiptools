from django import template

register = template.Library()


@register.inclusion_tag('help_menu.html')
def help_menu(**kwargs):
    # app_help = kwargs.pop('app_help', None)
    # if app_help is not None:
    #     app_help_qs = AppHelp.objects.filter(app_name=app_help)
    # else:
    #     app_help_qs = AppHelp.objects.all()
    #
    # topic = kwargs.pop('topic', None)
    # if topic is not None:
    #     topic_qs = Topic.objects.all()
    # else:
    #     topic_qs = Topic.objects.all()
    #
    # help_item = kwargs.pop('help_item', None)
    # if help_item is not None:
    #     help_item_qs = HelpItem.objects.all()
    # else:
    #     help_item_qs = HelpItem.objects.all()
    #
    #
    # response = {
    #     'app_help': app_help_qs,
    #     'topic': topic_qs,
    #     'help_item': help_item_qs
    # }
    #
    # # Pass along remaining kwargs:
    # for k in kwargs.keys():
    #     response[k] = kwargs[k]
    #
    # # Render template:
    # return response
    pass


@register.inclusion_tag('help_modal_trigger.html', takes_context=True)
def help_button(context):
    page_help = context.get('page_help', None)
    return {'page_help': page_help}


@register.inclusion_tag('help_modal.html', takes_context=True)
def help_modal(context):
    page_help = context.get('page_help', None)
    return {'page_help': page_help}

@register.filter
def render_as_template(text):
    tpl = template.Template(text)
    context = template.Context({})  # The Template.render method requires a context.  An empty one is okay.
    return tpl.render(context)
