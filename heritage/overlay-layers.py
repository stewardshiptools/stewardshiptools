from maps.plugins import OverlayLayer
from maps.utils.layers import register_overlay_layer

from rest_framework.reverse import reverse


class SpeciesObservations(OverlayLayer):
    name = 'All species observations.'
    ajax_url = reverse('heritage:api:species-observation-list')
    ajax_filters = None
register_overlay_layer('Species observations', SpeciesObservations)


class SpeciesObservationsFilteredByInterview(OverlayLayer):
    name = 'All species observations referring to a single interview.'
    ajax_url = reverse('heritage:api:species-observation-list')
    ajax_filters = {
        'interview': None  # Field to link species observations to interviews.
    }
register_overlay_layer('Species observations by interview', SpeciesObservationsFilteredByInterview)
