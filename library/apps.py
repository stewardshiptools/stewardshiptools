from django.apps import AppConfig


class LibraryConfig(AppConfig):
    name = 'library'
    verbose_name = 'Library'

    def ready(self):
        # import library.signals
        pass
