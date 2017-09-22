from django.contrib import admin
from django.conf.urls import url
from django.shortcuts import redirect
from django.core import management

from leaflet.admin import LeafletGeoAdmin

from assets.admin import SecureAssetAdmin

from .models import Project, Interview, Session, Species, Feature, DataSource, InfoType, Accuracy, \
    MTKRecord, MTKCulturalRecord, MTKSpeciesRecord, DataEntryId, EcologicalValue, FishingMethod, \
    Group, LinguisticGroup, HarvestMethod, ParticipantId, Season, ShapeType, TemporalTrend, TimeFrame, TravelMode, Use, \
    ProjectAsset, InterviewAsset, SessionAsset, InterviewerId, RecordSessionLink, SpeciesGroup, HeritageGISLayer,\
    HeritageAsset, Place, AlternatePlaceName, CommonPlaceName, PlaceType, GazetteerNameTag, GazetteerNameTaggedPlace

from geoinfo.admin import GISLayerAdmin


def sanitize_selected_interviews(interview_admin, request, queryset):
    '''
    calls sanitize_interviews on selected interviews
    :param interview_admin:
    :param request:
    :param queryset:
    :return:
    '''
    for interview in queryset.all():
        management.call_command('sanitize_interviews', str(interview.id), '--overwrite')

sanitize_selected_interviews.short_description = 'Sanitize selected interviews'


# Probably don't need to look at the super class, like, ever.
# @admin.register(MTKRecord)
# class MtkAdmin(admin.ModelAdmin):
#     pass

@admin.register(MTKCulturalRecord)
class FeatureAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MTKCulturalRecord._meta.fields if field.name != "id"]


@admin.register(MTKSpeciesRecord)
class SpeciesObservationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MTKSpeciesRecord._meta.fields if field.name != "id"]


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Feature._meta.fields if field.name != "id"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # list_display = Project._meta.get_all_field_names()
    list_display = [field.name for field in Project._meta.fields if field.name != "id"]


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    # list_display = Interview._meta.get_all_field_names()
    list_display = ['phase', 'primary_interviewer', 'participant_number', 'community', 'type', 'participant_list']
    list_filter = ('phase__name',)
    search_fields = ['primary_interviewer__initials',
                     'primary_interviewer__name_first',
                     'primary_interviewer__name_last',
                     'participants__name_first',
                     'participants__name_last',
                     'community']
    actions = [sanitize_selected_interviews,]

    def participant_list(self, obj):
        participants = []

        for per in obj.participants.all():
            participants.append(str(per))

        return ', '.join(participants)
    participant_list.short_description = 'Participants'


    def get_urls(self):
        '''
        updates admin class urls for adding custom view (for running sanitizer)
        :return:
        '''
        urls = super(InterviewAdmin, self).get_urls()
        urls = [url(r'^sanitize_interviews/$', self.sanitize_interviews, name='sanitize_interviews')] + urls
        return urls

    def sanitize_interviews(self, request):
        '''
        executes sanitizer on heritage interviews
        currently the button is HIDDEN.
        :param request:
        :return:
        '''
        print('santizing interviews from admin page...')
        if request.user.is_staff:
            # management.call_command('sanitize_interviews', '--overwrite')
            management.call_command('sanitize_interviews')
        return redirect('/admin/sanitizer/sensitivephrase')



@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Session._meta.fields if field.name != "id"]
    # list_display = ['number', 'date', 'transcript_file', 'duration', 'audio_file_code', 'audio_files', 'interview']
    list_filter = ('interview__phase__name', 'date')
    search_fields = ['interview__primary_interviewer__initials',
                     'interview__primary_interviewer__name_first',
                     'interview__primary_interviewer__name_last',
                     'interview__participants__name_first',
                     'interview__participants__name_last',
                     'interview__community']


@admin.register(Species)
class SpeciesCategoryAdmin(admin.ModelAdmin):
        list_display = [field.name for field in Species._meta.fields if field.name != "id"]


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
        list_display = [field.name for field in DataSource._meta.fields if field.name != "id"]


@admin.register(InfoType)
class InfoTypeAdmin(admin.ModelAdmin):
        list_display = [field.name for field in InfoType._meta.fields if field.name != "id"]


@admin.register(Accuracy)
class AccuracyAdmin(admin.ModelAdmin):
        list_display = [field.name for field in Accuracy._meta.fields if field.name != "id"]


@admin.register(DataEntryId)
class DataEntryIdAdmin(admin.ModelAdmin):
        list_display = [field.name for field in DataEntryId._meta.fields if field.name != "id"]


@admin.register(EcologicalValue)
class EcologicalValueAdmin(admin.ModelAdmin):
        list_display = [field.name for field in EcologicalValue._meta.fields if field.name != "id"]


@admin.register(FishingMethod)
class FishingMethodAdmin(admin.ModelAdmin):
        list_display = [field.name for field in FishingMethod._meta.fields if field.name != "id"]


@admin.register(Use)
class UseAdmin(admin.ModelAdmin):
        list_display = [field.name for field in Use._meta.fields if field.name != "id"]


@admin.register(RecordSessionLink)
class RecordSessionLinkAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'page_number', 'line_number', 'original_comment_on_map']
    search_fields = ['record__name', 'session__interview__phase__name',
                     'session__interview__primary_interviewer__initials', 'session__interview__type',
                     'session__interview__participant_number', 'session__number']


@admin.register(ShapeType)
class ShapeTypeAdmin(admin.ModelAdmin):
    list_display = ['description', 'database_code']


@admin.register(TravelMode)
class TravelModeAdmin(admin.ModelAdmin):
    list_display = ['description', 'database_code']


@admin.register(LinguisticGroup)
class LinguisticGroupAdmin(admin.ModelAdmin):
    list_display = ['description', 'database_code']


@admin.register(HeritageGISLayer)
class HeritageGISLayerAdmin(GISLayerAdmin):
    pass


@admin.register(HeritageAsset)
class HeritageAssetAdmin(SecureAssetAdmin):
    list_filter = ('asset_type__type_of_asset',)
    search_fields = ['name', 'legacy_path']


# We are not registering these with the decorators so that we can
# access the super() within init():
class ProjectAssetAdmin(SecureAssetAdmin):
    list_filter = ('project__name', 'asset_type__type_of_asset')
    search_fields = ['name', 'legacy_path']

    # Take all the settings from the super but add in the project field:
    def __init__(self, *args, **kwargs):
        super(ProjectAssetAdmin, self).__init__(*args, **kwargs)
        self.list_display.insert(0, 'project')

    # Disable modifying the project as that will screw up
    # the file structure:
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('project',)
        return self.readonly_fields


class InterviewAssetAdmin(SecureAssetAdmin):
    list_filter = ('interview__phase__name', 'asset_type__type_of_asset')
    search_fields = ['name', 'legacy_path']

    # Take all the settings from the super but add in the interview field:
    def __init__(self, *args, **kwargs):
        super(InterviewAssetAdmin, self).__init__(*args, **kwargs)
        self.list_display.insert(0, 'interview')

    # Disable modifying the interview as that will screw up
    # the file structure:
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('interview',)
        return self.readonly_fields


class SessionAssetAdmin(SecureAssetAdmin):
    list_filter = ('session__interview__phase__name', 'asset_type__type_of_asset')
    search_fields = ['name', 'legacy_path']

    # Take all the settings from the super but add in the session field:
    def __init__(self, *args, **kwargs):
        super(SessionAssetAdmin, self).__init__(*args, **kwargs)
        self.list_display.insert(0, 'session')

    # Disable modifying the session as that will screw up
    # the file structure:
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('session',)
        return self.readonly_fields


# Named places
class AlternatePlaceNameInline(admin.TabularInline):
    model = AlternatePlaceName


class CommonPlaceNameInline(admin.TabularInline):
    model = CommonPlaceName


@admin.register(PlaceType)
class PlaceTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Place)
class PlaceAdmin(LeafletGeoAdmin):
    inlines = [AlternatePlaceNameInline, CommonPlaceNameInline]


admin.site.register(Group)
admin.site.register(HarvestMethod)
admin.site.register(ParticipantId)
admin.site.register(Season)
admin.site.register(TemporalTrend)
admin.site.register(TimeFrame)
admin.site.register(SpeciesGroup)
admin.site.register(ProjectAsset, ProjectAssetAdmin)
admin.site.register(InterviewAsset, InterviewAssetAdmin)
admin.site.register(SessionAsset, SessionAssetAdmin)
admin.site.register(GazetteerNameTag)
admin.site.register(GazetteerNameTaggedPlace)
