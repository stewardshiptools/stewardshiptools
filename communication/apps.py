from django.apps import AppConfig


class CommunicationConfig(AppConfig):
    name = 'communication'
    verbose_name = 'Communication'

    def ready(self):
        import communication.signals
