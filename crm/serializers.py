from rest_framework import serializers
from easy_thumbnails.templatetags.thumbnail import thumbnail_url

from .models import Role, Organization, Person


class ThumbnailAvatarSerializer(serializers.ImageField):
    def to_representation(self, instance):
        return thumbnail_url(instance, 'avatar')


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        extra_kwargs = {
            "url": {'view_name': 'crm:organization-detail'}
        }


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    roles = serializers.StringRelatedField(many=True)
    # project_ids = serializers.SerializerMethodField()
    organizations = OrganizationSerializer(many=True)
    pic = ThumbnailAvatarSerializer()


    class Meta:
        model = Person
        # fields = '__all__'
        exclude = ('user_account',)
        extra_kwargs = {
            "url": {'view_name': 'crm:person-detail'}
        }
