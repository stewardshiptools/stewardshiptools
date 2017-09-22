from django.apps import AppConfig


class HeritageConfig(AppConfig):
    name = 'heritage'
    verbose_name = 'Heritage'

    def ready(self):
        import heritage.signals
