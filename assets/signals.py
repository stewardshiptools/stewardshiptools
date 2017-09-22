# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import pre_delete, post_delete, post_save
from django.utils import timezone

from haystack import connection_router, connections
from haystack.exceptions import NotHandled

from cedar.utils import misc_utils

from .search_utils import remove_asset_from_index_signal_method

from .models import Asset, SecureAsset


#################################################################################
# DELETE SIGNALS
# This checks if the delete flag is set on the asset class and
# removes the file on the local operating system if true:
def model_post_delete(sender, instance, **kwargs):
    if instance.delete_file_with_record:
        instance.file.delete(False)

    """
    Remove the asset from the search index.

    NOTE: this will be attached to all levels of asset subclass
            hierarchy so it will be called multiple times per asset and
            also on assets that don't even have indexes. Not really a big
            deal though. Better to put the signal method here then have to
            add it to every sub asset model that does use the search index.
    """
    remove_asset_from_index_signal_method(sender, instance)


# Use recursive connect below so that the remove index method catches all.
for classObj in misc_utils.recurse_subclasses(SecureAsset, []):
    post_delete.connect(model_post_delete, classObj)
for classObj in misc_utils.recurse_subclasses(Asset, []):
    post_delete.connect(model_post_delete, classObj)


#################################################################################
# SAVE SIGNALS
def model_post_save(sender, instance, **kwargs):
    # SecureAssetIndex().update_object(kwargs['instance'].secureasset)

    # Use updated to as to avoid any infinite loop silliness:
    sender.objects.filter(id=instance.id).update(modified=timezone.now())


# Connect save signals to all inherited assets:
for classObj in misc_utils.recurse_subclasses(SecureAsset, []):
    post_save.connect(model_post_save, classObj)
for classObj in misc_utils.recurse_subclasses(Asset, []):
    post_save.connect(model_post_save, classObj)
