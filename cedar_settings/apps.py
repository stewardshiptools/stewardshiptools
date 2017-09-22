from django.db.utils import ProgrammingError

from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

from .default_settings import default_settings


class CedarSettingsConfig(AppConfig):
    name = 'cedar_settings'
    verbose_name = 'Cedar Settings'

    general_settings_defaults = default_settings

    def ready(self):
        try:
            autodiscover_modules('cedar_settings')  # This should grab all the cedar_settings created by other enabled apps.
            GeneralSetting = self.get_model('GeneralSetting')

            for name, value in self.general_settings_defaults.items():
                if value is None:
                    continue

                if not GeneralSetting.objects.filter(name=name).exists():
                    GeneralSetting.objects.set(name, value[1], value[0])
        except ProgrammingError:
            pass
