from django.utils.module_loading import autodiscover_modules

OVERLAY_LAYERS = dict()


def discover_layer_plugins():
    autodiscover_modules('overlay-layers')


def get_overlay_layers():
    return OVERLAY_LAYERS


def register_overlay_layer(name, cls):
    OVERLAY_LAYERS[name] = cls
