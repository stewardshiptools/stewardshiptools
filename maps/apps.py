from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class MapsConfig(AppConfig):
    name = 'maps'
    verbose = 'Maps Application for Cedar'

    def ready(self):
        #autodiscover_modules('overlay-layers')  # This should grab all the overlay-layers created by other enabled apps.
        # import maps.signals
        pass
