from django.utils.module_loading import autodiscover_modules
from django.db.models.signals import pre_init
from django.dispatch import receiver

from maps.models import LeafletMap
from maps.utils.layers import OVERLAY_LAYERS


@receiver(pre_init, sender=LeafletMap)
def autodiscover_overlay_layers(sender, **kwargs):
    # autodiscover_modules('overlay-layers')
    # kwargs['overlay_layer_choices'] = map(lambda x: (x, x), OVERLAY_LAYERS)
    # sender.overlay_layer_choices = map(lambda x: (x, x), OVERLAY_LAYERS)
    pass
