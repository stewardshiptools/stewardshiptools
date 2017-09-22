from rest_framework import serializers
from rest_framework.reverse import reverse


from crm.models import Person
from library.models import Item, CollectionTag, CaseBrief, Synthesis, PersonMentionedTag, PersonMentionedTaggedItem


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    collections = serializers.SerializerMethodField()
    people_mentioned = serializers.SerializerMethodField()
    animals = serializers.SerializerMethodField()
    plants = serializers.SerializerMethodField()

    cataloger_name = serializers.CharField(source='cataloger')
    cataloger_url = serializers.SerializerMethodField()
    reviewer_name = serializers.CharField(source='reviewer')
    reviewer_url = serializers.SerializerMethodField()

    spreadsheet_id = serializers.IntegerField(source='researcher_notes.spreadsheet_id')

    item_type = serializers.CharField(source='dublin_core.type')

    creation_date = serializers.DateField(source='dublin_core.date')

    class Meta:
        model = Item
        fields = ('id', 'url', 'name', 'collections', 'cataloger_name', 'cataloger_url', 'reviewer_name',
                  'reviewer_url', 'item_type', 'creation_date', 'people_mentioned', 'plants', 'animals', 'prefixed_id', 'spreadsheet_id')
        extra_kwargs = {
            "url": {'view_name': 'library:item-detail'}
        }

    def get_collections(self, obj):
        collections = []
        for collection in obj.collections.all():
            collections.append({'url': reverse('library:collectiontag-detail', kwargs={'pk': collection.pk}), 'name': collection.name})

        return collections

    def get_cataloger_url(self, obj):
        try:
            return reverse('crm:person-detail', kwargs={'pk': obj.cataloger.person.pk})
        except Person.DoesNotExist as e:
            return '#'
        except AttributeError as e:
            # the obj may not have had it's cataloger set on import ?
            return '#'

    def get_reviewer_name(self, obj):
        return str(obj.reviewer)

    def get_reviewer_url(self, obj):
        if obj.reviewer:
            try:
                return reverse('crm:person-detail', kwargs={'pk': obj.reviewer.person.pk})
            except Person.DoesNotExist as e:
                pass
        return '#'

    def get_people_mentioned(self, obj):
        instances = []
        if obj.review:
            for instance in obj.review.people_mentioned.all():
                instances.append({'url': reverse('library:personmentionedtag-detail', kwargs={'pk': instance.pk}), 'name': instance.name})
        return instances

    def get_animals(self, obj):
        instances = []
        if obj.review:
            for instance in obj.review.animals.all():
                instances.append({'url': instance.get_absolute_url(), 'name': instance.name})

        return instances

    def get_plants(self, obj):
        instances = []
        if obj.review:
            for instance in obj.review.plants.all():
                instances.append({'url': instance.get_absolute_url(), 'name': instance.name})
        return instances


class CollectionTagSerializer(serializers.HyperlinkedModelSerializer):
    items_count = serializers.SerializerMethodField()

    def get_items_count(self, obj):
        return obj.library_collectiontaggeditem_items.count()

    class Meta:
        model = CollectionTag
        fields = ('description', 'name', 'items_count', 'url')
        extra_kwargs = {
            "url": {'view_name': 'library:collectiontag-detail'}
        }


class CaseBriefSerializer(serializers.HyperlinkedModelSerializer):
    created = serializers.DateTimeField(format='%Y-%m-%d')
    modified = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta:
        model = CaseBrief
        fields = ('story_title', 'url', 'created', 'modified', 'prefixed_id')
        extra_kwargs = {
            "url": {'view_name': 'library:casebrief-detail'}
        }


class SynthesisSerializer(serializers.HyperlinkedModelSerializer):
    created = serializers.DateTimeField(format='%Y-%m-%d')
    modified = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta:
        model = Synthesis
        fields = ('name', 'url', 'created', 'modified', 'prefixed_id')
        extra_kwargs = {
            "url": {'view_name': 'library:synthesis-detail'}
        }


class PersonMentionedTagSerializer(serializers.HyperlinkedModelSerializer):
    items_count = serializers.SerializerMethodField()

    def get_items_count(self, obj):
        return PersonMentionedTaggedItem.objects.filter(tag=obj).count()

    class Meta:
        model = PersonMentionedTag
        fields = ('description', 'name', 'items_count', 'url')
        extra_kwargs = {
            "url": {'view_name': 'library:personmentionedtag-detail'}
        }

