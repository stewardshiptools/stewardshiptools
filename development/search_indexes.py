import datetime
from haystack import indexes
import development

from assets.search_indexes import DocumentIndex


class DevelopmentAssetIndex(DocumentIndex, indexes.Indexable):
    def get_model(self):
            return development.models.DevelopmentAsset

