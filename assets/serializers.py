from rest_framework import serializers

from assets.models import AssetType, SecureAsset, MetaDocumentSecureAsset

from django.utils import timezone

from cedar_settings.utils.datetime import localize_datetime

file_date_format_string = '%Y-%m-%d %I:%M%p'


class DateTimeFieldTZ(serializers.DateTimeField):
    '''
    Usage:
        start = DateTimeFieldTZ(format='%d %b %Y %I:%M %p')
        end = DateTimeFieldTZ(format='%d %b %Y %I:%M %p')
    '''
    def to_representation(self, value):
        value = timezone.localtime(value)
        # value = localize_datetime(value)
        return super(DateTimeFieldTZ, self).to_representation(value)


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = ('type_of_asset',)


class MetaDocumentSecureSerializer(serializers.ModelSerializer):
    # date = DateTimeFieldTZ(format=file_date_format_string)
    date = serializers.DateField()

    class Meta:
        model = MetaDocumentSecureAsset
        exclude = ('id',)


class SecureAssetSerializer(serializers.ModelSerializer):
    # asset_type = AssetTypeSerializer()
    file_size = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    meta_document = MetaDocumentSecureSerializer()
    modified = DateTimeFieldTZ(format=file_date_format_string)

    class Meta:
        model = SecureAsset
        exclude = ('file', 'delete_file_with_record', 'published', 'legacy_path')

    def get_file_size(self, instance):
        return instance.file_size_str

    def get_url(self, instance):
        return instance.url


