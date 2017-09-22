from django.apps import AppConfig


class DevelopmentConfig(AppConfig):
    name = 'development'
    verbose_name = 'Development'

    def ready(self):
        import development.signals
