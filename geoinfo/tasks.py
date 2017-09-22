from __future__ import absolute_import

from celery import shared_task
import time

from geoinfo.models import GISLayer, GISLayerMaster
from geoinfo.utils.layers import GeomParser


@shared_task()
def get_layer_name(id):
    layer = GISLayer.objects.get(id=id)

    time.sleep(10)
    return layer.name


@shared_task()
def reload_layer_features(pk):
    layer = GISLayerMaster.objects.get(pk=pk)
    gp = GeomParser(layer)
    return gp.process_geoinfo_to_layer()  # I don't think this returns anything, but meh.
