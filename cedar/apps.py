from django.apps import AppConfig


class CedarConfig(AppConfig):
    name = 'cedar'
    verbose_name = 'Cedar Apps'

    def ready(self):
        import cedar.signals
