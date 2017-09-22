from django.apps import AppConfig


class GeoInfoConfig(AppConfig):
    name = 'geoinfo'
    verbose_name = 'Spatial Tools'

    def ready(self):
        import geoinfo.signals
