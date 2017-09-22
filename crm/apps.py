from django.apps import AppConfig


class CRMConfig(AppConfig):
    name = 'crm'
    # verbose_name = 'Cedar relationship management'
    verbose_name = 'Contacts'

    def ready(self):
        import crm.signals
