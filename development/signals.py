from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from communication.models import CommunicationAsset


#################################################################################
# SAVE SIGNALS
def development_communication_asset_post_save(sender, instance, **kwargs):
    '''
    Grabs communication assets when they are saved, finds related devt project,
    and imports the asset to the development project.
    :param sender: instance class
    :param instance: model instance
    :param kwargs: other things
    :return:
    '''

    # Figure out which development project this object belongs to:
    # sender.objects.filter(id=instance.id).update(modified=timezone.now())
    pass


post_save.connect(development_communication_asset_post_save, CommunicationAsset)
