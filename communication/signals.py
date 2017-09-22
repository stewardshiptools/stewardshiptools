import logging
from django.db.models.signals import post_delete, pre_delete

from django.contrib.contenttypes.models import ContentType

from communication.models import Communication, PhoneCall, Fax, Message, Letter, CommunicationFileRelation

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

'''
    Adding the communication_type_post_delete was triggering a loop - deleting the comm object
    triggered another delete of the comm_type object.

    UPDATE:
        The loop issue doesn't seem to be presenting now. Worries me a little, but things seem
        to be ok now.
'''


def communication_post_delete(sender, instance, **kwargs):
    '''
    Fired when a Communication instance is deleted.
    Try to delete the Comm Type with it (Phone, Fax...)
    Exception - if the Comm Type is a Message, then call wipe(), not delete().
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    '''
    # Clean up relations and other comm objects (phone, message, etc.)
    logger.debug("Running post delete cleanup on comms object: \"{}\". id: {}"
                 .format(instance, instance.id))
    try:
        if isinstance(instance.comm_type, Message):
            logger.debug("Post delete cleanup encountered a Message object. Call wipe instead: \"{}\". id: {}"
                         .format(instance, instance.id))
            instance.comm_type.wipe()
        else:
            instance.comm_type.delete()
    except AttributeError as err:
        # probably instance doesn't exist and we tried to delete a None here.
        logger.debug("AttributeError on post delete cleanup of comms object: \"{}\". id: {}. Error: \"{}\"."
                     .format(instance, instance.id, str(err)))


def communication_type_post_delete(sender, instance, **kwargs):
    '''
    Cleans up Communication object when a communication type (Phone, fax, etc.) is deleted.
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    '''
    # Clean up communication instances & files related to this communication type instance
    comm_type_ct = ContentType.objects.get_for_model(instance)

    try:
        logger.debug("Running post delete cleanup on comms type object: \"{}\". comm_type: {}. id: {}"
                     .format(instance, comm_type_ct, instance.id))

        Communication.objects.filter(
            comm_type_oid=instance.id,
            comm_type_ct=comm_type_ct
        ).delete()
        for cfr in CommunicationFileRelation.objects.filter(
                comm_type_oid=instance.id,
                comm_type_ct=comm_type_ct):
            cfr.asset.delete()
            cfr.delete()

    except AttributeError as err:
        # probably instance doesn't exist and we tried to delete a None here.
        logger.debug("AttributeError on post delete cleanup on comms type object:  \"{}\". comm_type: {}. id: {}. Error \"{}\""
                     .format(instance, comm_type_ct, instance.id, str(err)))


post_delete.connect(communication_post_delete, Communication)

post_delete.connect(communication_type_post_delete, PhoneCall)
post_delete.connect(communication_type_post_delete, Fax)
post_delete.connect(communication_type_post_delete, Message)
post_delete.connect(communication_type_post_delete, Letter)
