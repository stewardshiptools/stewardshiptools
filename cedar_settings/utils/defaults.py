from django.apps import apps


def get_default_settings():
    return apps.get_app_config('cedar_settings').general_settings_defaults
