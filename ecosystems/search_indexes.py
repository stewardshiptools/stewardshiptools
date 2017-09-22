import datetime
from haystack import indexes
import ecosystems

from assets.search_indexes import DocumentIndex


class EcosystemsAssetIndex(DocumentIndex, indexes.Indexable):
    def get_model(self):
            return ecosystems.models.EcosystemsAsset

