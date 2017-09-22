from cedar_settings.models import GeneralSetting
from security.models import SecurityLevel


def get_security_level_or_default_from_object(obj):
    security_level = SecurityLevel.objects.get_for_object(obj)
    if security_level is None:
        return GeneralSetting.objects.get("security_level_default")
    return security_level.level


def get_security_level_or_default_value_from_object(obj):
    security_level = SecurityLevel.objects.get_for_object(obj)
    if security_level is None:
        level = GeneralSetting.objects.get("security_level_default")
    level = security_level.level

    choices = {x[0]: x[1] for x in SecurityLevel.level_choices}
    return choices[level]
