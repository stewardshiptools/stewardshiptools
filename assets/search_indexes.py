import datetime
import sys
from haystack import indexes
from django.template import Context, loader, Template  # For loading the searchindex template


class DocumentIndex(indexes.SearchIndex):

    '''
        A Non-Indexing Document Index Parent Class.
        To add a new index in app X, create an index class like:
            class NewAssetIndex(DocumentIndex, indexes.Indexable):
                def get_model(self):
                    assetmodelclass

        "indexes.Indexable" - tells django-haystack to index that material. Without
            it the index is ignored.

    '''

    document_template_name = 'search/indexes/assets/genericasset_text.txt'

    text = indexes.CharField(document=True,)

    # I would like to deprecate this.
    asset_type = indexes.CharField(model_attr='asset_type', null=True)

    '''
    #################################################
    Meta Fields - Standard Set+
    #################################################
    '''
    contributor = indexes.CharField(null=True)
    coverage = indexes.CharField(null=True)
    creator = indexes.CharField(null=True)
    date = indexes.CharField(null=True)
    description = indexes.CharField(null=True)
    format = indexes.CharField(null=True)
    identifier = indexes.CharField(null=True)
    language = indexes.CharField(null=True)
    publisher = indexes.CharField(null=True)
    relation = indexes.CharField(null=True)
    rights = indexes.CharField(null=True)
    source = indexes.CharField(null=True)
    subject = indexes.CharField(null=True)
    title = indexes.CharField(null=True)
    type = indexes.CharField(null=True)

    '''
    End Meta Fields
    '''

    def index_queryset(self, using=None):
        '''
        Get the default QuerySet to index when doing a full update.
        Subclasses can override this method to avoid indexing certain objects.
        :param using:
        :return:
        '''
        return self.get_model().objects.all()

    def prepare(self, obj, using=None):
        data = super(DocumentIndex, self).prepare(obj)

        # This could also be a regular Python open() call, a StringIO instance
        # or the result of opening a URL. Note that due to a library limitation
        # file_obj must have a .name attribute even if you need to set one
        # manually before calling extract_file_contents:
        file_obj = obj.file

        print("DocumentIndex attempting to extract content from asset:", obj.file.name)

        try:
            # Getting the backend the way suggested by help files didn't work:
            # self.backend.extract_file_contents(file_obj)
            # So, had to do it this way, looks like a hay-hack:
            be = self._get_backend(using=None)

            # This is throwing exceptions. Maybe due to files with 0 bytes,
            # maybe not. Catching the exceptions here does nothing. Need to
            # find a way to ensure everything is indexed.
            # Update: on second look, it might just actually be a corrupted
            # word file! See HMTK2009_GH_003_Bio
            extracted_data = be.extract_file_contents(file_obj)

        except Exception as err:
            print("DocumentIndex failed to extract content from asset:", obj.file.name, ": ", str(err))
            extracted_data = None

        # Manually close the file object because the extractor doesn't
        # seem to do it itself. When indexing tons of stuff, we run into
        # too many files open error:
        file_obj.close()

        # Now we'll finally perform the template processing to render the
        # text field with *all* of our metadata visible for templating:
        t = loader.select_template((self.document_template_name,))

        rendered_content = t.render(Context({'object': obj, 'extracted': extracted_data}))
        data['text'] = rendered_content
        return data

    def prepare_asset_type(self, obj):
        # print ("Getting asset type for:", obj, ":", obj.asset_type.type_of_asset)
        return '' if not obj.asset_type else obj.asset_type.type_of_asset

    def prepare_contributor(self, obj):
        try:
            return obj.meta_document.contributor
        except AttributeError:
            return None

    def prepare_coverage(self, obj):
        try:
            return obj.meta_document.coverage
        except AttributeError:
            return None

    def prepare_creator(self, obj):
        try:
            return obj.meta_document.creator
        except AttributeError:
            return None

    def prepare_date(self, obj):
        try:
            return obj.meta_document.date
        except AttributeError:
            return None

    def prepare_description(self, obj):
        try:
            return obj.meta_document.description
        except AttributeError:
            return None

    def prepare_format(self, obj):
        try:
            return obj.meta_document.format
        except AttributeError:
            return None

    def prepare_identifier(self, obj):
        try:
            return obj.meta_document.identifier
        except AttributeError:
            return None

    def prepare_language(self, obj):
        try:
            return obj.meta_document.language
        except AttributeError:
            return None

    def prepare_publisher(self, obj):
        try:
            return obj.meta_document.publisher
        except AttributeError:
            return None

    def prepare_relation(self, obj):
        try:
            return obj.meta_document.relation
        except AttributeError:
            return None

    def prepare_rights(self, obj):
        try:
            return obj.meta_document.rights
        except AttributeError:
            return None

    def prepare_source(self, obj):
        try:
            return obj.meta_document.source
        except AttributeError:
            return None

    def prepare_subject(self, obj):
        try:
            return obj.meta_document.subject
        except AttributeError:
            return None

    def prepare_title(self, obj):
        try:
            return obj.meta_document.title
        except AttributeError:
            return None

    def prepare_type(self, obj):
        try:
            return obj.meta_document.type
        except AttributeError:
            return None

    def get_updated_field(self):
        return "modified"

