"""
General heritage utils
"""
import logging
from heritage.models import Place, AlternatePlaceName, CommonPlaceName
from library.utils import library as lib_utils

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def swap_place_nodes_for_prefixes():
    """
    Swaps out (nodeid) for (I-nodeid) on the following models/fields:
        Place.notes
        AlternatePlaceName.name
        CommonPlaceName.name
    :return: 
    """
    replace_these =[(Place, 'notes'), (AlternatePlaceName, 'name'), (CommonPlaceName, 'name')]

    for model, field in replace_these:
        logger.info("Processing {}:{}".format(Place.__name__, field))
        for instance in model.objects.all():
            val = getattr(instance, field)
            if val:
                setattr(instance, field, lib_utils.replace_nodes_with_prefixes(val, 'I-'))
                instance.save()

