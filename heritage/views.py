import csv
import json

from django.views.generic import ListView, TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseServerError
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType
from django.forms import inlineformset_factory

from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from rest_framework import viewsets, filters
from django_filters import MethodFilter
from rest_framework.reverse import reverse, reverse_lazy
from rest_framework import permissions

import django_filters

from assets.views import SecureAssetCreateView, SecureAssetDeleteView, SecureAssetDetailView, SecureAssetUpdateView, \
    SecureAssetViewSet, GetSecureFileView
from assets.models import SecureAsset
from assets import search_utils
import assets

from security.views import UserHasObjectSecurityClearanceMixin

from .models import Species, SpeciesGroup, MTKSpeciesRecord, Use, TimeFrame, HarvestMethod, FishingMethod, \
    EcologicalValue, TemporalTrend, SpeciesTheme, Project, Interview, InterviewAsset, ProjectAsset, Session, \
    MTKCulturalRecord, SessionAsset, HeritageAsset, LayerGroup, HeritageGISLayer, Place, AlternatePlaceName, \
    CommonPlaceName, PlaceType

from .serializers import SpeciesGroupSerializer, SpeciesSerializer, UseSerializer, TimeFrameSerializer, \
    HarvestMethodSerializer, FishingMethodSerializer, EcologicalValueSerializer, TemporalTrendSerializer, \
    SpeciesThemeSerializer, SpeciesObservationSerializer, ProjectSerializer, InterviewSerializer, InterviewSerializerSlim, \
    InterviewAssetSerializer, SessionAssetSerializer, ProjectAssetSerializer, ProjectDeepInfoSerializer,\
    CulturalObservationSerializer, InterviewAssetSanitizedSerializer, SessionAssetSanitizedSerializer, \
    HeritageGISLayerFeatureGeoJSONSerializer, HeritageGISLayerFeatureLazyGeoJSONSerializer, \
    PlaceSerializerWithGeoJSON, PlaceGeoJSONSerializer

from .forms import ProjectForm, InterviewForm, ProjectAssetForm, InterviewAssetForm, LayerGroupForm, \
    HeritageGISLayerForm, HeritageAssetForm, PlaceForm, AlternatePlaceNameForm, CommonPlaceNameForm

from crm.models import Person
from crm.serializers import PersonSerializer

from help.mixins import HelpContextMixin

from cedar.mixins import NavContextMixin, CSVResponseMixin, EditObjectMixin

from geoinfo.views import GISFeatureViewSet, GISLayerDetailView, GISLayerListView, GISLayerViewSet, \
    GISLayerMasterListAPIView, GISLayerMasterListView
from geoinfo.models import GISFeature, GISLayerMaster

from heritage.templatetags.heritage import get_interview_from_heritage_asset
from sanitizer.utils import sanitizer

from cedar_settings.views import CedarSettingsView

from communication.models import HarvestCodePrefix


class DashboardView(HelpContextMixin, TemplateView):
    template_name = 'heritage/dashboard.html'
    page_help_name = 'heritage:dashboard'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['project_count'] = Project.objects.all().count()
        context['interview_count'] = Interview.objects.all().count()
        context['session_count'] = Session.objects.all().count()
        context['cultural_records_count'] = MTKCulturalRecord.objects.filter(published=True).count()
        context['species_records_count'] = MTKSpeciesRecord.objects.filter(published=True).count()
        context['spatial_layers_count'] = HeritageGISLayer.objects.count()
        context['documents_count'] = HeritageAsset.objects.count()
        context['places_count'] = Place.objects.count()
        return context

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)


class HeritageSettingsView(CedarSettingsView):
    '''
    See the super for how it's done.
    '''

    def get_setting_fields(self):
        ct = ContentType.objects.get_for_model(Project)
        return [
            {
                'name': 'heritage__harvestprefix',
                'data_type': 'reference',
                'queryset': HarvestCodePrefix.objects.filter(content_type=ct),
                'label': 'Harvest Prefix'
            },
        ]

    def get_success_url(self):
        return reverse('heritage:settings')


class SpeciesView(TemplateView):
    template_name = 'species.html'

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(SpeciesView, self).dispatch(request, *args, **kwargs)


class SpeciesGroupView(TemplateView):
    template_name = 'species_group.html'

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(SpeciesGroupView, self).dispatch(request, *args, **kwargs)


class SpeciesObservationView(HelpContextMixin, TemplateView):
    template_name = 'heritage/speciesobservations_list.html'
    page_help_name = 'heritage:species-records'

    def get_context_data(self, **kwargs):
        context = super(SpeciesObservationView, self).get_context_data(**kwargs)
        context['ajax_url'] = reverse('heritage:api:species-observation-list')
        return context

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(SpeciesObservationView, self).dispatch(request, *args, **kwargs)


class SpeciesObservationDetailView(HelpContextMixin, DetailView):
    model = MTKSpeciesRecord
    template_name = 'heritage/speciesobservation_detail.html'
    page_help_name = 'heritage:species-record-detail'

    def get_context_data(self, **kwargs):
        context = super(SpeciesObservationDetailView, self).get_context_data(**kwargs)
        context['species_ajax_url'] = reverse('heritage:api:species-observation-detail',
                                              args=[self.object.id, ],
                                              request=self.request)
        return context

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(SpeciesObservationDetailView, self).dispatch(request, *args, **kwargs)


class SpeciesDetailView(HelpContextMixin, DetailView):
    model = Species
    template_name = 'species_detail.html'
    page_help_name = 'heritage:species-detail'

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(SpeciesDetailView, self).dispatch(request, *args, **kwargs)


class InterviewListView(HelpContextMixin, ListView):
    template_name = 'heritage/interviews.html'
    model = Interview
    page_help_name = 'heritage:interview-list'

    def get_context_data(self, **kwargs):
        context = super(InterviewListView, self).get_context_data(**kwargs)
        context['interview_ajax_url'] = reverse('heritage:api:interview-list') + "?&slim=1"
        context['session_count'] = Session.objects.all().count()
        return context

    @method_decorator(permission_required('heritage.view_interview', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(InterviewListView, self).dispatch(request, *args, **kwargs)


class InterviewDetailView(HelpContextMixin, DetailView):
    model = Interview
    template_name = 'heritage/interview_detail.html'
    page_help_name = 'heritage:interview-detail'

    def get_context_data(self, **kwargs):
        context = super(InterviewDetailView, self).get_context_data(**kwargs)

        # Uniquefy the sessions by date and count:
        unique_session_dates = self.object.session_set.values("date").annotate(num_dates=Count("date")).order_by()
        context['unique_session_dates'] = unique_session_dates.order_by('date')

        search_interviewassets_by_interview_url = "{}?{}={}".format(reverse('heritage:api:interview-asset-list'), 'interview__id', self.object.id)
        context['assets_interviews_ajax_url'] = search_interviewassets_by_interview_url

        search_sessionassets_by_interview_url = "{}?{}={}".format(reverse('heritage:api:session-asset-list'), 'interviewid', self.object.id)
        context['assets_sessions_ajax_url'] = search_sessionassets_by_interview_url

        context['species_data_url'] = reverse('heritage:api:species-observation-list')
        context['cultural_data_url'] = reverse('heritage:api:cultural-observation-list')
        context['ajax_url_filter_by_interview_id'] = "interview_id={}".format(self.object.id)

        context['cultural_records_count'] = MTKCulturalRecord.objects.filter(published=True, session__interview=self.object).count()
        context['species_records_count'] = MTKSpeciesRecord.objects.filter(published=True, session__interview=self.object).count()

        return context

    @method_decorator(permission_required('heritage.view_interview', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(InterviewDetailView, self).dispatch(request, *args, **kwargs)


class InterviewCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    model = Interview
    form_class = InterviewForm
    page_help_name = 'heritage:interview-create'

    def get_edit_object_cancel_url(self):
        return reverse('heritage:project-detail', args=[int(self.request.GET.get('project_pk'))])

    def get_form_kwargs(self):
        kwargs = super(InterviewCreateView, self).get_form_kwargs()
        kwargs['project_pk'] = self.request.GET.get('project_pk', '')
        return kwargs

    @method_decorator(permission_required('heritage.add_interview', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(InterviewCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InterviewCreateView, self).get_context_data(**kwargs)
        context['project_pk'] = self.request.GET.get('project_pk', '')
        return context


class InterviewUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    model = Interview
    form_class = InterviewForm
    page_help_name = 'heritage:interview-update'
    edit_object_delete_perm = 'heritage.delete_interview'

    def get_edit_object_cancel_url(self):
        return reverse('heritage:interview-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('heritage:interview-delete', args=[self.object.id])

    def get_form_kwargs(self):
        kwargs = super(InterviewUpdateView, self).get_form_kwargs()
        kwargs['project_pk'] = self.object.phase.pk
        return kwargs

    @method_decorator(permission_required('heritage.add_interview', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(InterviewUpdateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InterviewUpdateView, self).get_context_data(**kwargs)
        context['project_pk'] = self.object.phase.pk
        return context


class InterviewDeleteView(HelpContextMixin, DeleteView):
    model = Interview
    page_help_name = 'heritage:interview-delete'

    @method_decorator(permission_required('heritage.delete_interview', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(InterviewDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('heritage:project-detail', kwargs={'pk': self.object.phase.pk})


class ProjectListView(HelpContextMixin, ListView):
    model = Project
    template_name = 'heritage/project_list.html'
    page_help_name = 'heritage:project-list'

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        context['ajax_url'] = reverse('heritage:api:project-list')
        return context

    @method_decorator(permission_required('heritage.view_project', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectListView, self).dispatch(request, *args, **kwargs)


class ProjectDetailView(HelpContextMixin, DetailView):
    model = Project
    template_name = 'heritage/project_detail.html'
    page_help_name = 'heritage:project-detail'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context['project_info_ajax_url'] = reverse('heritage:api:project-deep-info-detail',
                                                   args=[self.object.id, ],
                                                   request=self.request)
        # context['person_info_ajax_url'] = reverse('crm:api:person-list')
        context['person_info_ajax_url'] = "{}?{}={}".format(reverse('heritage:api:project-participant-list'),
                                                            'project', self.object.id)

        search_interviews_by_project_url = "{}?{}={}&slim=1".format(reverse('heritage:api:interview-list'), 'phase__id', self.object.id)
        context['interview_ajax_url'] = search_interviews_by_project_url

        # Gather up the assets -- only doing project-level assets now. Uncomment
        # the following lines to gather up interview & session assets if desired:
        project_assets = self.object.projectasset_set.all()
        # interview_assets = InterviewAsset.objects.filter(interview__phase=self.object.id)
        # session_assets = SessionAsset.objects.filter(session__interview__phase=self.object.id)
        # assets = result_lst = list(chain(project_assets, interview_assets, session_assets))
        # context['assets_list'] = assets
        context['assets_list'] = project_assets

        return context

    @method_decorator(permission_required('heritage.view_project', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectDetailView, self).dispatch(request, *args, **kwargs)


class ProjectDetailPrintView(ProjectDetailView):
    model = Project
    page_help_name = 'heritage:project-detail-print'
    template_name = 'heritage/project_detail_print.html'


class ProjectCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    # Template by default/convention looks for project_form.html
    model = Project
    form_class = ProjectForm
    page_help_name = 'heritage:project-create'
    edit_object_cancel_url = reverse_lazy('heritage:project-list')

    def form_valid(self, form):
        response = super(ProjectCreateView, self).form_valid(form)
        return response

    def form_invalid(self, form):
        response = super(ProjectCreateView, self).form_invalid(form)
        return response

    @method_decorator(permission_required('heritage.add_project', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(request, *args, **kwargs)


class ProjectUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    # Template by default/convention looks for project_form.html
    model = Project
    form_class = ProjectForm
    page_help_name = 'heritage:project-update'
    edit_object_delete_perm = 'heritage:delete_project'

    def get_edit_object_cancel_url(self):
        return reverse('heritage:project-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('heritage:project-delete', args=[self.object.id])

    def form_valid(self, form):
        response = super(ProjectUpdateView, self).form_valid(form)
        return response

    def form_invalid(self, form):
        response = super(ProjectUpdateView, self).form_invalid(form)
        return response

    @method_decorator(permission_required('heritage.change_project', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectUpdateView, self).dispatch(request, *args, **kwargs)


class ProjectDeleteView(HelpContextMixin, DeleteView):
    model = Project
    page_help_name = 'heritage:project-delete'

    @method_decorator(permission_required('heritage.delete_project', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('heritage:project-list')


class CulturalObservationDetailView(HelpContextMixin, DetailView):
    model = MTKCulturalRecord
    template_name = 'heritage/culturalobservation_detail.html'
    page_help_name = 'heritage:culture-record-detail'

    def get_context_data(self, **kwargs):
        context = super(CulturalObservationDetailView, self).get_context_data(**kwargs)
        context['cultural_ajax_url'] = reverse('heritage:api:cultural-observation-detail',
                                               args=[self.object.id, ],
                                               request=self.request)
        return context

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(CulturalObservationDetailView, self).dispatch(request, *args, **kwargs)


class CulturalObservationListView(HelpContextMixin, TemplateView):
    template_name = 'heritage/culturalobservations_list.html'
    page_help_name = 'heritage:culture-records'

    def get_context_data(self, **kwargs):
        context = super(CulturalObservationListView, self).get_context_data(**kwargs)
        context['ajax_url'] = reverse('heritage:api:cultural-observation-list')
        return context

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(CulturalObservationListView, self).dispatch(request, *args, **kwargs)


class LayerGroupCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    model = LayerGroup
    form_class = LayerGroupForm
    page_help_name = 'heritage:layer-group-create'

    def get_edit_object_cancel_url(self):
        return reverse('heritage:interview-detail', args=[self.kwargs.get('interview_pk')])

    def get_form_kwargs(self):
        kwargs = super(LayerGroupCreateView, self).get_form_kwargs()
        kwargs['interview_pk'] = self.kwargs.get('interview_pk', None)
        return kwargs

    @method_decorator(permission_required('heritage.add_layergroup', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(LayerGroupCreateView,self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LayerGroupCreateView, self).get_context_data(**kwargs)
        context['interview_pk'] = self.kwargs.get('interview_pk', None)
        return context


class LayerGroupUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    model = LayerGroup
    form_class = LayerGroupForm
    page_help_name = 'heritage:layer-group-update'
    edit_object_delete_perm = 'heritage:delete_layergroup'

    def get_edit_object_cancel_url(self):
        return reverse('heritage:interview-detail', args=[self.kwargs.get('interview_pk')])

    def get_edit_object_delete_url(self):
        return reverse('heritage:layergroup-delete', args=[self.kwargs.get('interview_pk'), self.object.id])

    def get_form_kwargs(self):
        kwargs = super(LayerGroupUpdateView, self).get_form_kwargs()
        kwargs['interview_pk'] = self.kwargs.get('interview_pk', None)
        return kwargs

    @method_decorator(permission_required('heritage.change_layergroup', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(LayerGroupUpdateView,self).dispatch(request, *args, **kwargs)


class LayerGroupDeleteView(HelpContextMixin, DeleteView):
    model = LayerGroup
    page_help_name = 'heritage:layer-group-delete'

    @method_decorator(permission_required('heritage.delete_layergroup', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(LayerGroupDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('heritage:interview-detail', kwargs={'pk': self.object.interview.pk})


class HeritageGISLayerListView(GISLayerMasterListView):
    model = HeritageGISLayer
    page_help_name = 'heritage:layer-master-list'
    ajax_url_name = 'heritage:layer-master-list-api'
    # default_layer_type = 'Heritage Misc.'


class HeritageGISLayerDetailView(NavContextMixin, GISLayerDetailView):
    '''
    GISLayerDetailView already inherits the help context mixin.
    '''
    model = HeritageGISLayer
    template_name = 'geoinfo/gislayer_detail.html'
    page_help_name = 'heritage:gislayer-detail'
    nav_url = reverse_lazy("heritage:gislayer-list")


class HeritageGISLayerCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    """
    This may be a GENERIC heritage gis layer view, or a heritage gis layer with
    an interview key and a layergroup key.
    """
    model = HeritageGISLayer
    form_class = HeritageGISLayerForm
    page_help_name = 'heritage:gislayer-create'

    def get_edit_object_cancel_url(self):
        interview_pk = self.kwargs.get('interview_pk')
        if interview_pk:
            return reverse('heritage:interview-detail', args=[interview_pk])
        else:
            return reverse('heritage:gislayer-list')

    def get_form_kwargs(self):
        kwargs = super(HeritageGISLayerCreateView, self).get_form_kwargs()
        kwargs['group_pk'] = self.kwargs.get('layergroup_pk', None)
        return kwargs

    @method_decorator(permission_required('heritage.add_heritagegislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(HeritageGISLayerCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.group:
            return reverse('heritage:interview-detail', kwargs={'pk': self.object.group.interview.pk})
        else:
            return reverse('heritage:gislayer-detail', kwargs={'pk': self.object.pk})


class HeritageGISLayerUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    """
    This may be a GENERIC heritage gis layer view, or a heritage gis layer with
    an interview key and a layergroup key.
    """

    model = HeritageGISLayer
    form_class = HeritageGISLayerForm
    page_help_name = 'heritage:gislayer-update'
    edit_object_delete_perm = 'heritage:delete_heritagegislayer'

    def get_edit_object_cancel_url(self):
        interview_pk = self.kwargs.get('interview_pk')
        if interview_pk:
            return reverse('heritage:interview-detail', args=[interview_pk])
        else:
            return reverse('heritage:gislayer-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        interview_pk = self.kwargs.get('interview_pk')
        layergroup_pk = self.kwargs.get('layergroup_pk')
        if interview_pk:
            return reverse('heritage:gislayer-delete', args=[interview_pk, layergroup_pk, self.object.id])
        else:
            return reverse('heritage:gislayer-delete-generic', args=[self.object.id])

    def get_form_kwargs(self):
        kwargs = super(HeritageGISLayerUpdateView, self).get_form_kwargs()
        kwargs['group_pk'] = self.kwargs.get('layergroup_pk', None)
        return kwargs

    @method_decorator(permission_required('heritage.change_heritagegislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(HeritageGISLayerUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.group:
            return reverse('heritage:interview-detail', kwargs={'pk': self.object.group.interview.pk})
        else:
            return reverse('heritage:gislayer-detail', kwargs={'pk': self.object.pk})


class HeritageGISLayerDeleteView(HelpContextMixin, DeleteView):
    model = HeritageGISLayer
    page_help_name = 'heritage:gislayer-delete'

    @method_decorator(permission_required('heritage.delete_heritagegislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(HeritageGISLayerDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.group:
            return reverse_lazy('heritage:interview-detail', kwargs={'pk': self.object.group.interview.pk})
        else:
            return reverse_lazy('heritage:gislayer-list')


# Permission mixin added in super
class GetHeritageAssetFileView(UserHasObjectSecurityClearanceMixin, GetSecureFileView):
    object_attr = 'item_set.all'
    relative_fallback_result = True


# Permission mixin added in super
class HeritageAssetDetailView(UserHasObjectSecurityClearanceMixin, HelpContextMixin, SecureAssetDetailView):
    model = HeritageAsset
    template_name = 'heritage/heritageasset_detail.html'
    page_help_name = 'heritage:secureasset-detail'
    object_attr = 'item_set.all'
    relative_fallback_result = True

    def get_context_data(self, **kwargs):
        context = super(HeritageAssetDetailView, self).get_context_data(**kwargs)
        context['edit_url'] = reverse('heritage:secureasset-update', kwargs={'pk': self.object.pk})
        context['delete_url'] = reverse('heritage:secureasset-delete', kwargs={'pk': self.object.pk})
        return context


# Permission mixin added in super
class HeritageAssetCreateView(HelpContextMixin, SecureAssetCreateView):
    permission_required = "heritage.add_heritageasset"
    model = HeritageAsset
    template_name = 'heritage/heritageasset_form.html'
    form_class = HeritageAssetForm
    page_help_name = 'heritage:secureasset-create'
    include_metadocument = False
    edit_object_cancel_url = reverse_lazy('heritage:secureasset-list')

    def get_success_url(self):
        return reverse('heritage:secureasset-detail', kwargs={'pk': self.object.pk})


# Permission mixin added in super
class HeritageAssetUpdateView(HelpContextMixin, SecureAssetUpdateView):
    permission_required = 'heritage.change_heritageasset'
    model = HeritageAsset
    template_name = 'heritage/heritageasset_form.html'
    form_class = HeritageAssetForm
    page_help_name = 'heritage:secureasset-update'
    include_metadocument = False

    edit_object_delete_perm = 'heritage:delete_heritageasset'

    def get_edit_object_cancel_url(self):
        return reverse('heritage:secureasset-detail', kwargs={'pk': self.object.pk})

    def get_success_url(self):
        return reverse('heritage:secureasset-detail', kwargs={'pk': self.object.pk})


class HeritageAssetDeleteView(HelpContextMixin, SecureAssetDeleteView):
    permission_required = 'heritage.delete_heritageasset'
    page_help_name = 'heritage:secureasset-delete'

    def get_context_data(self, **kwargs):
        context = super(HeritageAssetDeleteView, self).get_context_data(**kwargs)

        # This view thinks this is just a secureasset, get the heritageasset:
        heritage_asset = SecureAsset.objects.get_subclass(pk=self.object.pk)
        context['cancel_url'] = reverse('heritage:secureasset-detail', kwargs={'pk': heritage_asset.pk})
        context['nav_url'] = reverse('heritage:secureasset-dashboard')
        return context

    def get_success_url(self):
        return reverse('heritage:secureasset-list')


class ProjectAssetDetailView(HelpContextMixin, SecureAssetDetailView):
    model = ProjectAsset
    template_name = 'heritage/projectasset_detail.html'
    page_help_name = 'heritage:project-secureasset-detail'

    def get_context_data(self, **kwargs):
        context = super(ProjectAssetDetailView, self).get_context_data(**kwargs)
        context['edit_url'] = reverse('heritage:project-secureasset-update',
                                      kwargs={'pk': self.object.pk, 'project_pk': self.object.project.pk})
        context['delete_url'] = reverse('heritage:project-secureasset-delete',
                                        kwargs={'pk': self.object.pk, 'project_pk': self.object.project.pk})
        return context


# Permission mixin added in super
class ProjectAssetCreateView(HelpContextMixin, SecureAssetCreateView):
    permission_required = "heritage.add_projectasset"
    model = ProjectAsset
    template_name = 'heritage/projectasset_form.html'
    form_class = ProjectAssetForm
    page_help_name = 'heritage:project-secureasset-create'
    include_metadocument = False

    def get_edit_object_cancel_url(self):
        return reverse('heritage:project-detail', args=[self.kwargs.get('project_pk')])

    # Add project id to the form's kwargs:
    def get_form_kwargs(self):
        kwargs = super(ProjectAssetCreateView, self).get_form_kwargs()
        kwargs['h_project_id'] = self.kwargs.get('project_pk', None)
        return kwargs

    def get_success_url(self):
        return reverse('heritage:project-detail', kwargs={'pk': self.object.project.id}) + "#tab-files"


# Permission mixin added in super
class ProjectAssetUpdateView(HelpContextMixin, SecureAssetUpdateView):
    permission_required = 'heritage.change_projectasset'
    model = ProjectAsset
    template_name = 'heritage/projectasset_form.html'
    form_class = ProjectAssetForm
    page_help_name = 'heritage:project-secureasset-update'
    include_metadocument = False
    edit_object_delete_perm = 'heritage:delete_projectasset'

    def get_edit_object_cancel_url(self):
        return reverse('heritage:project-secureasset-detail', args=[self.kwargs.get('project_pk'), self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('heritage:project-secureasset-delete', args=[self.kwargs.get('project_pk'), self.object.id])

    # Add project id to the form's kwargs:
    def get_form_kwargs(self):
        kwargs = super(ProjectAssetUpdateView, self).get_form_kwargs()
        kwargs['h_project_id'] = self.kwargs.get('project_pk', None)
        return kwargs

    def get_success_url(self):
        return reverse('heritage:project-secureasset-detail', kwargs={'pk': self.object.pk, 'project_pk': self.object.project.pk})


# Permission mixin added in super
class ProjectAssetDeleteView(HelpContextMixin, SecureAssetDeleteView):
    permission_required = 'heritage.delete_projectasset'
    page_help_name = 'heritage:project-secureasset-create'

    def get_context_data(self, **kwargs):
        context = super(ProjectAssetDeleteView, self).get_context_data(**kwargs)

        # This view thinks this is just a secureasset, get the projectasset:
        project_asset = SecureAsset.objects.get_subclass(id=self.object.id)
        context['cancel_url'] = reverse('heritage:project-detail', kwargs={'pk': project_asset.project.id})
        context['nav_url'] = reverse('heritage:project-list')
        return context

    def get_success_url(self):
        # This view thinks this is just a secureasset, get the projectasset:
        project_asset = SecureAsset.objects.get_subclass(id=self.object.id)
        return reverse('heritage:project-detail', kwargs={'pk': project_asset.project.id}) + "#tab-files"


# Permission mixin added in super
class InterviewAssetDetailView(HelpContextMixin, SecureAssetDetailView):
    model = InterviewAsset
    template_name = 'heritage/interviewasset_detail.html'
    page_help_name = 'heritage:interview-secureasset-detail'

    def get_context_data(self, **kwargs):
        context = super(InterviewAssetDetailView, self).get_context_data(**kwargs)
        context['edit_url'] = reverse('heritage:interview-secureasset-update', kwargs={'pk': self.object.pk, 'interview_pk': self.object.interview.pk})
        context['delete_url'] = reverse('heritage:interview-secureasset-delete', kwargs={'pk': self.object.pk, 'interview_pk': self.object.interview.pk})
        return context


# Permission mixin added in super
class InterviewAssetCreateView(HelpContextMixin, SecureAssetCreateView):
    permission_required = "heritage.add_interviewasset"
    model = InterviewAsset
    template_name = 'heritage/interviewasset_form.html'  # SecureAssetCreateView specifies assets/genericasset_form.html
    form_class = InterviewAssetForm
    page_help_name = 'heritage:interview-secureasset-create'
    include_metadocument = False

    def get_edit_object_cancel_url(self):
        return reverse('heritage:interview-detail', args=[self.kwargs.get('interview_pk')])

    # Add interview id to the form's kwargs:
    def get_form_kwargs(self):
        kwargs = super(InterviewAssetCreateView, self).get_form_kwargs()
        kwargs['h_interview_id'] = self.kwargs.get('interview_pk', None)
        return kwargs

    def get_success_url(self):
        return reverse('heritage:interview-detail', kwargs={'pk': self.object.interview.pk}) + "#tab-files"


# Permission mixin added in super
class InterviewAssetUpdateView(HelpContextMixin, SecureAssetUpdateView):
    permission_required = 'heritage.change_interviewasset'
    model = InterviewAsset
    template_name = 'heritage/interviewasset_form.html'
    form_class = InterviewAssetForm
    page_help_name = 'heritage:interview-secureasset-update'
    include_metadocument = False
    edit_object_delete_perm = 'heritage.delete_interviewasset'

    def get_edit_object_cancel_url(self):
        return reverse('heritage:interview-secureasset-detail', args=[self.kwargs.get('interview_pk'), self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('heritage:interview-secureasset-delete', args=[self.kwargs.get('interview_pk'), self.object.id])

    def get_form_kwargs(self):
        kwargs = super(InterviewAssetUpdateView, self).get_form_kwargs()
        kwargs['h_interview_id'] = self.kwargs.get('interview_pk', None)
        return kwargs

    def get_success_url(self):
        return reverse('heritage:interview-secureasset-detail', kwargs={'pk': self.object.pk, 'interview_pk': self.object.interview.pk})


# Permission mixin added in super
class InterviewAssetDeleteView(HelpContextMixin, SecureAssetDeleteView):
    permission_required = "heritage.delete_interviewasset"
    page_help_name = 'heritage:interview-secureasset-delete'

    def get_context_data(self, **kwargs):
        context = super(InterviewAssetDeleteView, self).get_context_data(**kwargs)

        # This view thinks this is just a secureasset, get the interviewasset:
        interview_asset = SecureAsset.objects.get_subclass(id=self.object.id)
        context['cancel_url'] = reverse('heritage:interview-detail', kwargs={'pk': interview_asset.interview.id})
        context['nav_url'] = reverse('heritage:interviews')
        return context

    def get_success_url(self):
        # This view thinks this is just a secureasset, get the interviewasset:
        interview_asset = SecureAsset.objects.get_subclass(id=self.object.id)
        return reverse('heritage:interview-detail', kwargs={'pk': interview_asset.interview.id}) + "#tab-files"


class SessionAssetDetailView(HelpContextMixin, SecureAssetDetailView):
    model = SessionAsset
    template_name = 'heritage/sessionasset_detail.html'
    page_help_name = 'heritage:session-secureasset-detail'

    def get_context_data(self, **kwargs):
        context = super(SessionAssetDetailView, self).get_context_data(**kwargs)
        # context['edit_url'] = reverse('heritage:interview-secureasset-update', kwargs={'pk': self.object.pk, 'interview_pk': self.object.interview.pk})
        # context['delete_url'] = reverse('heritage:interview-secureasset-delete', kwargs={'pk': self.object.pk, 'interview_pk': self.object.interview.pk})
        return context


class SessionAssetDeleteView(HelpContextMixin, SecureAssetDeleteView):
    permission_required = "heritage.delete_sessionasset"
    page_help_name = 'heritage:session-secureasset-delete'

    def get_context_data(self, **kwargs):
        context = super(SessionAssetDeleteView, self).get_context_data(**kwargs)

        # This view thinks this is just a secureasset, get the session asset:
        session_asset = SecureAsset.objects.get_subclass(id=self.object.id)
        context['cancel_url'] = reverse('heritage:interview-detail', kwargs={'pk': session_asset.session.interview.id})
        context['nav_url'] = reverse('heritage:interviews')
        return context

    def get_success_url(self):
        # This view thinks this is just a secureasset, get the session asset:
        session_asset = SecureAsset.objects.get_subclass(id=self.object.id)
        return reverse('heritage:interview-detail', kwargs={'pk': session_asset.session.interview.id}) + "#tab-files"


class SecureAssetsDashboardView(assets.views.SecureAssetsDashboardView):
    template_name = 'heritage/secureasset_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(SecureAssetsDashboardView, self).get_context_data(**kwargs)
        context['create_asset_url'] = reverse('heritage:secureasset-create')
        context['secureasset_search_url'] = reverse('heritage:secureasset-search')
        context['secureasset_list_url'] = reverse('heritage:secureasset-list')
        context['documents_count'] = HeritageAsset.objects.count()
        return context


class SecureAssetListView(NavContextMixin, assets.views.SecureAssetListView):
    nav_url = reverse_lazy('heritage:secureasset-dashboard')
    template_name = 'heritage/secureasset_list.html'
    asset_model = HeritageAsset

    def get_context_data(self, **kwargs):
        context = super(SecureAssetListView, self).get_context_data(**kwargs)
        context['total_files'] = self.asset_model.objects.count()
        context['secure_asset_list_ajax_url'] = reverse_lazy('heritage:api:secure-assets-list')
        return context


class SecureAssetSearchView(NavContextMixin, HelpContextMixin, assets.views.SecureAssetSearchView):
        '''
        Searches the HeritageAsset index.
        Render to response has been overriden to switch to a CSV File Response
        if a form field value has been set. Otherwise returns a normal template.
        '''
        template_name = 'heritage/secureasset_search.html'
        page_help_name = 'heritage:file-search'
        nav_url = reverse_lazy('heritage:secureasset-dashboard')

        def get_queryset(self):
            sqs = super(SecureAssetSearchView, self).get_queryset().models(HeritageAsset)
            return sqs

        def make_csv_response(self, context, **response_kwargs):
            '''
            Override default csv preparation
            :param context:
            :param response_kwargs:
            :return:
            '''
            response = HttpResponse(content_type='text/csv')
            cd = 'attachment; filename="{0}"'.format("search_results.csv")
            response['Content-Disposition'] = cd

            writer = csv.writer(response)
            header = [
                "File",
                "File URL",
                "Source",
                "Source URL",
                "Excerpt #",
                "Excerpt"
            ]
            writer.writerow(header)

            # Do ALL or only current page:
            if self.return_as_csv == 'all':
                search_qs = self.queryset.load_all()
            elif self.return_as_csv == 'page':
                search_qs = context['page_obj']
            else:
                raise HttpResponseServerError("argument missing for download request - must be 'all' or 'page'")

            subtexts = search_utils.get_subtexts(search_qs)
            count = 0

            # Do this here to possibly save on db hits:
            user_can_view_sensitive = self.request.user.has_perm('heritage.view_sensitive_interview_data')

            for result in search_qs:
                count += 1
                subtext_num = 0
                heritage_object = get_interview_from_heritage_asset(result.object)

                # sanitize filename and all subtexts here if needed:
                if not user_can_view_sensitive:
                    print("sanitizing")
                    filename = sanitizer.sanitize(result.object.name, obj=heritage_object)
                    sani_subtexts = []
                    for subtext in subtexts[result.pk]:
                        sani_subtexts.append(sanitizer.sanitize(subtext, obj=heritage_object))
                    subtexts[result.pk] = sani_subtexts
                    print("done sanitizing")
                else:
                    filename = result.object.name

                for subtext in subtexts[result.pk]:
                    subtext_num += 1
                    row = [
                        filename,
                        self.request.build_absolute_uri(result.object.url),
                        str(heritage_object),
                        self.request.build_absolute_uri(result.object.source_url),
                        subtext_num,
                        subtext
                    ]
                    writer.writerow(row)

            return response


class SecureAssetSearchViewCSV(assets.views.SecureAssetSearchViewCSV):
    pass


class PlaceCreateView(PermissionRequiredMixin, EditObjectMixin, NavContextMixin, HelpContextMixin, CreateView):
    model = Place
    page_help_name = 'heritage:place-create'
    nav_url = reverse_lazy('heritage:dashboard')
    form_class = PlaceForm
    permission_required = 'heritage.add_place'
    alternate_name_formset = inlineformset_factory(Place, AlternatePlaceName, form=AlternatePlaceNameForm,
                                                   can_delete=True, extra=1)
    common_name_formset = inlineformset_factory(Place, CommonPlaceName, form=CommonPlaceNameForm,
                                                   can_delete=True, extra=1)

    edit_object_cancel_url = reverse_lazy('heritage:place-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # I'm pretty sure this view will never be loaded with a POST request...
        if self.request.method == 'POST':
            context['alternate_name_formset'] = self.alternate_name_formset(self.request.POST, self.request.FILES)
            context['common_name_formset'] = self.common_name_formset(self.request.POST, self.request.FILES)
        else:
            # NOTE: The initial can't be set on the empty form, so in the form_valid method we make sure that property
            # is correctly set.
            context['alternate_name_formset'] = self.alternate_name_formset()
            context['common_name_formset'] = self.common_name_formset()

        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        alternate_name_formset = self.alternate_name_formset(self.request.POST, self.request.FILES,
                                                             instance=self.object)
        if alternate_name_formset.is_valid():
            alternate_name_formset.save()

        common_name_formset = self.common_name_formset(self.request.POST, self.request.FILES,
                                                             instance=self.object)
        if common_name_formset.is_valid():
            common_name_formset.save()

        return response

    def get_success_url(self):
        return reverse('heritage:place-detail', kwargs={'pk': self.object.pk})


class PlaceUpdateView(PermissionRequiredMixin, EditObjectMixin, NavContextMixin, HelpContextMixin, UpdateView):
    model = Place
    page_help_name = 'heritage:place-update'
    nav_url = reverse_lazy('heritage:dashboard')
    form_class = PlaceForm
    permission_required = 'heritage.change_place'
    alternate_name_formset = inlineformset_factory(Place, AlternatePlaceName, form=AlternatePlaceNameForm,
                                                   can_delete=True, extra=1)
    common_name_formset = inlineformset_factory(Place, CommonPlaceName, form=CommonPlaceNameForm,
                                                   can_delete=True, extra=1)
    edit_object_delete_perm = 'heritage:delete_place'

    def get_edit_object_cancel_url(self):
        return reverse('heritage:place-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('heritage:place-delete', args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # I'm pretty sure this view will never be loaded with a POST request...
        if self.request.method == 'POST':
            context['alternate_name_formset'] = self.alternate_name_formset(self.request.POST, self.request.FILES, instance=self.object)
            context['common_name_formset'] = self.common_name_formset(self.request.POST, self.request.FILES, instance=self.object)
        else:
            # NOTE: The initial can't be set on the empty form, so in the form_valid method we make sure that property
            # is correctly set.
            context['alternate_name_formset'] = self.alternate_name_formset(instance=self.object)
            context['common_name_formset'] = self.common_name_formset(instance=self.object)

        return context

    def form_valid(self, form):
        alternate_name_formset = self.alternate_name_formset(self.request.POST, self.request.FILES,
                                                             instance=self.object)
        if alternate_name_formset.is_valid():
            alternate_name_formset.save()
            for obj in alternate_name_formset.deleted_objects:
                if obj.id:
                    obj.delete()
        else:
            return self.form_invalid(form)

        common_name_formset = self.common_name_formset(self.request.POST, self.request.FILES,
                                                             instance=self.object)
        if common_name_formset.is_valid():
            common_name_formset.save()
            for obj in common_name_formset.deleted_objects:
                if obj.id:
                    obj.delete()
        else:
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('heritage:place-detail', kwargs={'pk': self.object.pk})


class PlaceDetailView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, DetailView):
    model = Place
    page_help_name = 'heritage:place-detail'
    nav_url = reverse_lazy('heritage:dashboard')


class PlaceDeleteView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, DeleteView):
    model = Place
    page_help_name = 'heritage:place-delete'
    nav_url = reverse_lazy('heritage:dashboard')
    success_url = reverse_lazy('heritage:place-list')


class PlaceListView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, ListView):
    model = Place
    page_help_name = 'heritage:place-list'
    nav_url = reverse_lazy('heritage:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ajax_url'] = reverse('heritage:api:place-list')

        context['fields'] = [
            ['prefixed_id', 'Place ID'],
            ['name', {
                'verbose_name': 'Name',
                'type': 'link',
                'url_field': 'url'
            }],
            ['alternate_names', 'Alternate name(s)'],
            ['common_names', 'Common name(s)'],
            ['gazetteer_names', 'Gazetteer name(s)'],
            ['place_types', 'Place type(s)'],
        ]

        context['sort_options'] = [
            ['name', 'Name'],
            ['id', 'ID']
        ]

        context['filters'] = [
            {
                'name': 'id',
                'verbose_name': 'ID',
                'id': 'id-filter',
                'default_value': '',
                'component': 'text',
            },
            {
                'name': 'name',
                'verbose_name': 'Name',
                'id': 'name-filter',
                'default_value': '',
                'component': 'text',
            },
            {
                'name': 'place_types',
                'verbose_name': 'Place types',
                'id': 'place-type-filter',
                'options': list(
                    map(lambda x: [x.id, x.place_type],
                        PlaceType.objects.all()
                        )
                ),
                'default_value': [],
                'component': "select",
                'labelClasses': "active",
                'select_type': 'select2',
                'is_multiple': "true"
            },
            {
                'name': 'notes',
                'verbose_name': 'Notes',
                'id': 'notes-filter',
                'default_value': '',
                'component': 'text',
            }
        ]

        return context


# -----------------------------------------------------------------
# Rest API Views
# -----------------------------------------------------------------
class SpeciesGroupViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SpeciesGroup.objects.all()
    serializer_class = SpeciesGroupSerializer


class SpeciesViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer


class UseViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Use.objects.all()
    serializer_class = UseSerializer


class TimeFrameViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TimeFrame.objects.all()
    serializer_class = TimeFrameSerializer


class HarvestMethodViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = HarvestMethod.objects.all()
    serializer_class = HarvestMethodSerializer


class FishingMethodViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = FishingMethod.objects.all()
    serializer_class = FishingMethodSerializer


class EcologicalValueViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = EcologicalValue.objects.all()
    serializer_class = EcologicalValueSerializer


class TemporalTrendViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TemporalTrend.objects.all()
    serializer_class = TemporalTrendSerializer


class SpeciesThemeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SpeciesTheme.objects.all()
    serializer_class = SpeciesThemeSerializer


# FilterSet for Records
class RecordFilterSet(filters.FilterSet):
    interview_id = MethodFilter()

    class Meta:
        model = None
        fields = ['interview_id']

    def filter_interview_id(self, queryset, value):
        if value:
            return queryset.filter(session__interview=value)
        return queryset


class SpeciesRecordFilterSet(RecordFilterSet):

    class Meta:
        model = MTKSpeciesRecord
        fields = RecordFilterSet.Meta.fields


class CulturalRecordFilterSet(RecordFilterSet):

    class Meta:
        model = MTKCulturalRecord
        fields = RecordFilterSet.Meta.fields


class SpeciesObservationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = MTKSpeciesRecord.objects.filter(published=True)
    serializer_class = SpeciesObservationSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = SpeciesRecordFilterSet
    search_fields = ('id', 'use__description', 'species__description', 'time_frame_start__description',
                     'time_frame_end__description', 'harvest_method__name', 'fishing_method__description',
                     'ecological_value__description', 'species_theme__name', 'temporal_trend__description',
                     'link_code', 'gazetted_place_name', 'local_place_name')

    ordering_fields = '__all__'
    ordering = ('species',)  # Default sort field.


class CulturalObservationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = MTKCulturalRecord.objects.filter(published=True)
    serializer_class = CulturalObservationSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = CulturalRecordFilterSet
    search_fields = ('id', 'gazetted_place_name', 'first_nations_place_name', 'ecological_feature__description',
                     'local_place_name',
                     'cultural_feature__description', 'industrial_feature__description',
                     'management_feature__description', 'comments', 'link_code')
    # search_fields = ('comments', 'cultural_feature__description')
    ordering_fields = '__all__'
    ordering = ('id',)  # Default sort field.


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'phase_code', 'start_date', 'end_date', 'location', 'background')
    filter_fields = ('id',)
    ordering_fields = '__all__'
    ordering = ('start_date', 'end_date', 'name')  # Default sort fields.


class ProjectDeepInfoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Project.objects.all()
    serializer_class = ProjectDeepInfoSerializer
    #
    # def list(self, request):
    #     queryset = Project.objects.all()
    #     serializer = ProjectDeepInfoSerializer(queryset, many=True)
    #     return Response(serializer.data)
    #
    # def retrieve(self, request, pk=None):
    #     queryset = Project.objects.all()
    #     project = get_object_or_404(queryset, pk=pk)
    #     serializer = ProjectDeepInfoSerializer(project)
    #     return Response(serializer.data)


class ProjectParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PersonSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    ordering = ('name_last', 'name_first', 'date_of_birth')

    def get_queryset(self):
        project_id = self.request.query_params.get('project', None)
        if project_id is not None:
            interviews = Interview.objects.filter(phase__id=project_id)

            if self.request.user.has_perm('heritage.view_sensitive_interview_data'):
                people = Person.objects.filter(
                    Q(interviews_conducted__in=interviews) |
                    Q(interviews_assisted__in=interviews) |
                    Q(interview__in=interviews) |
                    Q(interviews_attended__in=interviews)
                ).distinct()
            else:
                people = Person.objects.filter(
                    Q(interviews_conducted__in=interviews) |
                    Q(interviews_assisted__in=interviews)
                ).distinct()

            return people

        return Person.objects.all()


# InterviewViewSet
#   Also looks for special "personid" url parameter, see get_queryset for info.
class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    Note: if `slim=1` is present as a url parameter, the default InterviewSerializer will
    be swapped out for InterviewSerializerSlim
    '''
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('id', 'phase__id',)

    def get_queryset(self):
        """
        get_queryset modified to query all any Person objects related to the interview
         - because they are spread over three (potentially four) fields it was complicating
            the filter_fields set up. This looks for a url parameter "personid" and pre-filters
            based on that.
        """
        queryset = Interview.objects.all()
        personid = self.request.query_params.get('personid', None)

        if personid is not None:
            if self.request.user.has_perm('heritage.view_sensitive_interview_data'):
                queryset = queryset.filter(
                    Q(primary_interviewer=personid) |
                    Q(participants__in=[personid, ]) |
                    Q(attendees__in=[personid, ]) |
                    Q(other_interviewers__in=[personid, ])
                ).distinct()
            else:
                queryset = queryset.filter(
                    Q(primary_interviewer=personid) |
                    Q(other_interviewers__in=[personid, ])
                ).distinct()
        return queryset

    def get_serializer_class(self):
        # Decide whether to give it the normal or the slim serializer:

        slim = int(self.request.query_params.get('slim', 0))

        if slim:
            return InterviewSerializerSlim

        return self.serializer_class


class InterviewAssetViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = InterviewAsset.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('id', 'interview__id',)

    def get_serializer_class(self):
        if self.request.user.has_perm('heritage.can_view_sensitive_interview_data'):
            return InterviewAssetSerializer
        else:
            return InterviewAssetSanitizedSerializer


class SessionAssetViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SessionAsset.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('id', 'session__id',)

    def get_queryset(self):
        """
        get_queryset modified to get all sessions related to an interview:
        """
        queryset = SessionAsset.objects.all()
        interviewid = self.request.query_params.get('interviewid', None)

        if interviewid is not None:
            queryset = queryset.filter(Q(session__interview__id=interviewid))
        return queryset

    def get_serializer_class(self):
        if self.request.user.has_perm('heritage.can_view_sensitive_interview_data'):
            return SessionAssetSerializer
        else:
            return SessionAssetSanitizedSerializer


class ProjectAssetViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectAssetSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('id', 'project__id',)


class HeritageGISLayerViewSet(GISLayerViewSet):
    queryset = HeritageGISLayer.objects.all()


class HeritageGISLayerMasterListAPIView(GISLayerMasterListAPIView):
    queryset = HeritageGISLayer.objects.all()


class HeritageGISLayerFeatureViewSet(GISFeatureViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    geojson_serializer_class = HeritageGISLayerFeatureGeoJSONSerializer
    default_serializer_class = HeritageGISLayerFeatureLazyGeoJSONSerializer

    def get_queryset(self):
        queryset = super(HeritageGISLayerFeatureViewSet, self).get_queryset()

        group_pk = self.request.query_params.get('group', None)

        if group_pk is None:
            layers = HeritageGISLayer.objects.all()
            queryset = queryset.filter(layer__in=layers)

        layers = HeritageGISLayer.objects.filter(group__pk=group_pk)
        queryset = queryset.filter(layer__in=layers)

        return queryset


class HeritageAssetViewSet(SecureAssetViewSet):
    def get_queryset(self):
        return HeritageAsset.objects.all()


class PlaceFilterSet(filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='contains')
    notes = django_filters.CharFilter(lookup_type='contains')
    place_types = django_filters.ModelMultipleChoiceFilter(queryset=PlaceType.objects.all(),
                                                           method='filter_place_types')

    class Meta:
        model = Place
        fields = ('id', 'name', 'notes', 'place_types')

    def filter_place_types(self, queryset, _, value):
        if value:
            queryset = queryset.filter(place_types__in=value)
        return queryset.distinct()  # distinct is needed because this is a multifilter on a multifield.


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = PlaceFilterSet
    search_fields = ('id', 'name', 'notes', 'place_types__place_type', 'alternateplacename__name',
                     'commonplacename__name', 'gazetteer_names__name', 'prefixed_id_q')
    ordering_fields = ('name', 'id')

    default_serializer_class = PlaceSerializerWithGeoJSON
    geojson_serializer_class = PlaceGeoJSONSerializer

    def get_serializer_class(self):
        include_geoms = int(self.request.query_params.get('as_geojson', 0))

        if include_geoms:
            return self.geojson_serializer_class

        return self.default_serializer_class


def list_places_json(request, max_suggestions=None):
    """
    Returns a list of JSON objects with a `id` and a `text` property
    returned after querying with your query term `q` (not case sensitive).

    """
    query = request.GET.get('q', '')
    limit = request.GET.get('limit', max_suggestions)
    try:
        request.GET.get('limit', max_suggestions)
        limit = min(int(limit), max_suggestions)  # max or less
    except ValueError:
        limit = max_suggestions
    except TypeError:
        pass

    tag_name_qs = Place.objects.filter(
        Q(name__icontains=query) | Q(alternateplacename__name__icontains=query) | Q(commonplacename__name__icontains=query) | Q(gazetteer_names__name__icontains=query)). \
        order_by('name', 'id').values('pk', 'name').distinct()

    data = None
    if max_suggestions:
        data = [{'id': n['pk'], 'text': n['name']} for n in tag_name_qs[:limit]]
    else:
        data = [{'id': n['pk'], 'text': n['name']} for n in tag_name_qs]

    return HttpResponse(json.dumps(data), content_type='application/json')
