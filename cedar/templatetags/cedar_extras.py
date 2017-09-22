import re
import random
import string
from django import template
from django.template import Context
from django.template.loader import get_template
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

from crm.models import Person

from cedar_settings.models import GeneralSetting

from cedar.utils.misc_utils import get_back_url_from_context

register = template.Library()


@register.inclusion_tag('cedar/react.html')
def react():
    pass


@register.inclusion_tag('cedar/react-dom.html')
def react_dom():
    pass


@register.inclusion_tag('cedar/griddle.html')
def griddle():
    pass


@register.inclusion_tag('cedar/spinner.html')
def spinner():
    pass


@register.inclusion_tag('cedar/back-arrow-link.html')
def back_arrow(div_classes="col s1"):
    return {
        'div_classes': div_classes
    }


@register.inclusion_tag('cedar/user-menu.html', takes_context=True)
def user_menu(context, *args, **kwargs):
    # Requires a kwarg: "user_menu_id".

    user_menu_id = kwargs.get('user_menu_id')
    try:
        if context['user'].is_authenticated():
            person = Person.objects.get(user_account=context['user'])
        else:
            raise PermissionDenied

    except Person.DoesNotExist:
        person = None
    # except
    return {
        'person': person,
        'user_menu_id': user_menu_id,
        'context': context,
    }


@register.inclusion_tag('cedar/messages.html', takes_context=True)
def messages(context, *args, **kwargs):
    return {'context': context, }



# is_choice_selected:
# For use when rebuilding modelmultiplechoice fields manually,
# trying to figure out which are selected.
@register.filter()
def is_choice_selected(choice, field_values):
    if not field_values:
        return ""
    # choice id is an int:
    if str(choice[0]) in field_values:
        return "selected"
    else:
        return ""


# is_disabled:
# takes a user object and a permission string and checks if the
# user has that permission. If he/she doesn't, it returns the string "disabled"
# which can be used in a materializecss button class.
@register.filter()
def is_disabled(user, permission):
    if user.has_perm(permission):
        return ""
    else:
        return "disabled"


# Use this to see if you are in a CREATEVIEW or an UPDATEVIEW.
# useful when re-using a model form for updates and creates:
# Usage:
#   {% is_update_view "Update Project" "Create Project" as submit_value %}
@register.assignment_tag(takes_context=True)
def is_update_view(context, text_if_true, text_if_false):
    try:
        object = context.get('object')
        int(object.pk)  # This should fail if an normal object w/ pk wasn't supplied.
        return text_if_true
    except AttributeError as e:
        return text_if_false


@register.assignment_tag()
def get_dict_val(dictionary, key):
    try:
        return dictionary[key]
    except:
        return None


@register.assignment_tag()
def dict_has_key(dictionary, key):
    if key in dictionary:
        return True
    else:
        return False


@register.filter()
def replace_highlight_tags(text, span_class):
    return text.replace("<em>", "<span class=\"{}\">".format(span_class)).replace("</em>", "</span>")


@register.assignment_tag(takes_context=True)
def chunkify_search_text(context, search_result, chunk_length):
    t = search_result.text
    return ['happy', 'trails']


@register.assignment_tag
def sanitize_old(text, repl_char, query):
    # Get list of interview participant initials:
    participants = Person.objects.filter(roles__name__contains="Participant")
    # initials = [participant.initials for participant in participants]
    for p in participants:

        # Redact initials:
        if len(p.initials) > 1:  # Skip bad or weird initials
            # text = text.replace(p.initials, repl_char * len(p.initials))
            initials_str = p.initials.strip()
            text = re.sub(r'\b{}\b'.format(initials_str), repl_char * len(initials_str), text)

        # Redact names - 5 variations:

        # # "Fname Lname"
        # name_str = "{} {}".format(p.name_first, p.name_last).strip()
        # text = text.replace(name_str, repl_char * len(name_str))
        #
        # # "FnameLname"
        # name_str = "{}{}".format(p.name_first, p.name_last).strip()
        # text = text.replace(name_str, repl_char * len(name_str))

        # "Fname"
        if p.name_first:
            name_str = p.name_first.strip()
            text = re.sub(r'\b{}\b'.format(name_str), repl_char * len(name_str), text)

        # "Lname"
        if p.name_first:
            name_str = p.name_last.strip()
            text = re.sub(r'\b{}\b'.format(name_str), repl_char * len(name_str), text)

        # "Indigenous"
        if p.indigenous_name:
            name_str = p.indigenous_name.strip()
            text = text.replace(name_str, repl_char * len(name_str))

    return text


@register.filter()
def concat(val1, val2):
    return str(val1) + str(val2)


@register.assignment_tag()
def get_model_class(obj):
    return obj.__class__


@register.assignment_tag()
def get_model_class_name(obj):
    return obj.__class__.__name__


@register.filter()
def get_subclass_model_class_name(obj):
    model = obj.__class__
    return model.objects.get_subclass(id=obj.id).__class__.__name__


@register.assignment_tag()
def get_model_subclass(obj):
    model = obj.__class__
    return model.objects.get_subclass(id=obj.id)


@register.assignment_tag()
def is_submodel(obj1, obj2):
    return issubclass(obj1.__class__, obj2.__class__)


# -------------------------------------------
# DEPRECATED. See Readme for implementing permissions.
# To use: wrap any html elements with:
#       {% if request.user|can_view_sensitive %} {% endif %}
# and they will be filtered out based on user role.
# Currently, "Explorers" are the only restricted group,
# any other role will be able to see stuff.
# -------------------------------------------
@register.filter
def can_view_sensitive(user):
    try:
        if Group.objects.get(name='Explorer') in user.groups.all():
            return False
        else:
            return True
    except Exception as err:
        return False


@register.inclusion_tag('cedar/back_button.html', takes_context=True)
def back_button(context, extra=None):
    '''
    Tries to set a button anchor with the http referer url. Disables
    button if no url present
    :param context:
    :param extra: something to append on to the end of the url
    :return:
    '''
    back_url = get_back_url_from_context(context)
    if back_url:
        if extra:
            # add ending slash if not present
            if back_url[-1] != "/":
                back_url += "/"
            back_url += extra
        return {'BACK_URL': back_url}
    else:
        return {'BACK_URL': False}


@register.inclusion_tag('cedar/cancel_button.html', takes_context=True)
def cancel_button(context, extra=None):
    '''
    Tries to set a button anchor with the http referer url. Disables
    button if no url present.
    This actually just called back_button()
    :param context:
    :param extra: something to append on to the end of the url
    :return:
    '''
    return back_button(context, extra)


@register.inclusion_tag('cedar/edit_submit_button.html', takes_context=True)
def edit_submit_button(context, form_selector, action_text=None):
    '''

    :param context:
    :param form_selector: jquery selector string to get the form
    :param action_text: button text. if None, will try to decide if it's a New or Update form
    :return:
    '''
    if not action_text:
        action_text = is_update_view(context, "Update", "Create")
    return {
        'form_selector': form_selector,
        'action_text': action_text
    }


@register.inclusion_tag('cedar/edit_delete_button.html', takes_context=True)
def edit_delete_button(context, delete_url_string, perm=None):
    '''

    :param context:
    :param delete_url_string: if I call it "delete_url" it would conflict with the template var "delete_url"
    :param perm: permission to check, if user doesn't have perm the button will be disabled. Can be None for no check.
    :return:
    '''
    return {
        'delete_url': delete_url_string,
        'disabled_css': '' if not perm else is_disabled(context.request.user, perm)
    }


@register.inclusion_tag('cedar/edit_cancel_button.html', takes_context=True)
def edit_cancel_button(context, cancel_url_string):
    '''
    What's that, a THIRD cancel button tag? Yes, yes it is.
    :param context:
    :param cancel_url_string
    :return:
    '''
    return {
        'cancel_url': cancel_url_string,
    }


@register.assignment_tag()
def get_background_url():
    url_obj = GeneralSetting.objects.get('cedar__default_splash_page_background_img')
    if isinstance(url_obj, str):
        return url_obj
    else:
        return url_obj.file.url


@register.filter()
def render_boolean(value):
    bool_template = get_template("cedar/boolean_template.html")
    return bool_template.render(Context({'value': value}))


@register.assignment_tag()
def random_string(num_chars=4):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(num_chars))
