import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from geoinfo.models import GISLayerMaster, GISFeaturePoint, GISFeatureLine, GISFeaturePolygon, GISLayer, DBView,\
    SpatialReport
from geoinfo.utils.layers import GeomParser
from geoinfo.utils.reports import clear_report_caches

from cedar.utils import misc_utils

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def gis_layer_post_save(sender, instance, created, raw, using, update_fields, **kwargs):
    # Note we can't tell if a 'custom' input_type layer has been updated.  That needs handled elsewhere.
    # What is this if statement?!
    if created or \
                    instance.input_type != instance._GISLayerMaster__original_fields['input_type'] or \
                    instance.wkt != instance._GISLayerMaster__original_fields['wkt'] or \
                    instance.draw != instance._GISLayerMaster__original_fields['draw'] or \
                    instance.file != instance._GISLayerMaster__original_fields['file'] or \
                    instance.feature_titles_template != instance._GISLayerMaster__original_fields['feature_titles_template'] or \
                    instance.geomark != instance._GISLayerMaster__original_fields['geomark'] or \
                    instance.wfs_geojson != instance._GISLayerMaster__original_fields['wfs_geojson'] or \
                    instance.reload_features:

        # TODO Check if geomark has changed.
        logging.debug("gis_layer_post_save(): Instantiate layer parser for {}".format(instance))
        gp = GeomParser(instance)
        gp.process_geoinfo_to_layer()

        # We would also like to handle cache clearing in this case
        # ...Check if this layer is used in any spatial reports, or spatial report items, and clear the related
        # caches if it is.  Remember... we don't need to clear any caches if this is a created instance.
        reports = SpatialReport.objects.filter(report_on__pk__exact=instance.pk)
        reports |= SpatialReport.objects.filter(spatialreportitem__layer__pk__exact=instance.pk)

        # This is ugly, but it avoids triggering this signal and switches the reload_features value back to false
        qs = GISLayerMaster.objects.filter(pk=instance.pk)
        qs.update(reload_features=False)

        for report in reports:
            clear_report_caches(report)


def gis_layer_post_delete(sender, instance, using, **kwargs):
    # Delete any related database views:
    # DBView.objects.drop_related_dbviews(instance)
    pass


# Connect save signals to all inherited assets:
for classObj in misc_utils.recurse_subclasses(GISLayerMaster, []):
    post_save.connect(gis_layer_post_save, classObj)

# Connect delete signals to all inherited assets:
for classObj in misc_utils.recurse_subclasses(GISLayerMaster, []):
    post_delete.connect(gis_layer_post_delete, classObj)
