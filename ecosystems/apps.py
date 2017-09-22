from django.apps import AppConfig


class EcosystemsConfig(AppConfig):
    name = 'ecosystems'
    verbose_name = 'Ecosystems'

    def ready(self):
        # import ecosystems.signals
        pass
