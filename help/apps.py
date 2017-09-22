from django.apps import AppConfig


class HelpConfig(AppConfig):
    name = 'help`'
    verbose_name = 'Help'

    def ready(self):
        # import assets.signals
        pass
