import re
from django import template
from django.contrib.auth.models import Group

from cedar_settings.models import GeneralSetting
from cedar_settings.utils.parsers import get_choice_value

register = template.Library()


@register.filter()
def get_setting(setting_name):
    return GeneralSetting.objects.get(setting_name)


@register.assignment_tag()
def get_setting_as(setting_name):
    '''
    The getting_setting filter tag is helpful but not when it's in a loop.
    Use this for loopy times.
    :param setting_name:
    :return:
    '''
    return GeneralSetting.objects.get(setting_name)


@register.assignment_tag()
def get_choices_setting_value(setting_name, choice):
    '''
    Takes cedar_settings.choices text, parses it, returns value for the choice supplied.
    Use it on templates where one of these funny fields needs to be displayed.
    :param setting_name: eg 'development_project_primary_auth_choices'
    :param choice: eg 'FirstChoice'
    :return: text corresponding to the choice
    '''
    choices_text = GeneralSetting.objects.get(setting_name).strip()
    return get_choice_value(choices_text, choice)

