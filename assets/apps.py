from django.apps import AppConfig


class AssetsConfig(AppConfig):
    name = 'assets'
    verbose_name = 'Files'

    def ready(self):
        import assets.signals
