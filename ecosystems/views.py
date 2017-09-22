import json

from django.conf import settings
from django.http import HttpResponse
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView, FormView
from django.forms import inlineformset_factory

from rest_framework import viewsets, filters
from rest_framework.reverse import reverse
from rest_framework import permissions

from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from help.mixins import HelpContextMixin
from cedar.mixins import NavContextMixin, EditObjectMixin

from assets.views import SecureAssetsDashboardView as LDV, SecureAssetListView as LLV, SecureAssetSearchView as LSV, \
    SecureAssetSearchViewCSV as LSVCSV,\
    SecureAssetDetailView, SecureAssetCreateView, SecureAssetUpdateView, SecureAssetDeleteView, SecureAssetViewSet

from assets.models import SecureAsset

from .models import EcosystemsAsset, EcosystemsGISLayer, EcosystemsProject, EcosystemsProjectAsset, FilingCode, PlantTag, AnimalTag, \
    PlantTaggedItem, AnimalTaggedItem, CommonPlantName, IndigenousPlantName, CommonAnimalName, IndigenousAnimalName
from .forms import EcosystemsAssetForm, EcosystemsGISLayerForm, EcosystemsProjectAssetForm, \
    EcosystemsProjectForm, EcosystemsProjectGISLayerForm, PlantTagForm, AnimalTagForm, CommonPlantNameForm, \
    IndigenousPlantNameForm, CommonAnimalNameForm, IndigenousAnimalNameForm
from .serializers import EcosystemsProjectSerializer, EcosystemsGISLayerFeatureGeoJSONSerializer, PlantTagSerializer, AnimalTagSerializer

from geoinfo.views import GISLayerCreateView, GISLayerDeleteView, GISLayerDetailView, GISLayerUpdateView, \
    GISLayerListView, GISLayerViewSet, GISLayerMasterListView, GISLayerMasterListAPIView, GISFeatureViewSet

from geoinfo.models import GISLayerMaster


from cedar_settings.models import GeneralSetting
from cedar_settings.utils.parsers import parse_choices
from cedar_settings.views import CedarSettingsView

from communication.models import HarvestCodePrefix


class EcosystemsSettingsView(CedarSettingsView):
    '''
    See the super for how it's done.
    '''

    def get_setting_fields(self):
        ct = ContentType.objects.get_for_model(EcosystemsProject)
        return [
            {
                'name': 'ecosystems_project_code_prefix',
                'data_type': 'reference',
                'queryset': HarvestCodePrefix.objects.filter(content_type=ct),
                'label': 'Default Harvest Code Prefix for Ecosystems Projects'
            },
        ]

    def get_success_url(self):
        return reverse_lazy("ecosystems:settings")


class DashboardView(HelpContextMixin, TemplateView):
    template_name = 'ecosystems/dashboard.html'
    page_help_name = 'ecosystems:dashboard'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['project_count'] = EcosystemsProject.objects.all().count()
        context['documents_count'] = EcosystemsAsset.objects.count()
        context['spatial_layers_count'] = EcosystemsGISLayer.objects.count()
        context['plants_count'] = PlantTag.objects.count()
        context['animals_count'] = AnimalTag.objects.count()
        return context

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)


class SecureAssetsDashboardView(LDV):
    template_name = 'ecosystems/secureasset_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(SecureAssetsDashboardView, self).get_context_data(**kwargs)
        context['create_asset_url'] = reverse('ecosystems:secureasset-create')
        context['secureasset_search_url'] = reverse('ecosystems:secureasset-search')
        context['secureasset_list_url'] = reverse('ecosystems:secureasset-list')
        context['documents_count'] = EcosystemsAsset.objects.count()
        return context


class SecureAssetListView(NavContextMixin, LLV):
    nav_url = reverse_lazy('ecosystems:secureasset-list')
    template_name = 'ecosystems/secureasset_list.html'
    asset_model = EcosystemsAsset

    def get_context_data(self, **kwargs):
        context = super(SecureAssetListView, self).get_context_data(**kwargs)
        context['total_files'] = self.asset_model.objects.count()
        context['secure_asset_list_ajax_url'] = reverse_lazy('ecosystems:api:secure-assets-list')
        return context


class SecureAssetSearchView(NavContextMixin, HelpContextMixin, LSV):
    page_help_name = 'ecosystems:file-search'
    nav_url = reverse_lazy('ecosystems:secureasset-list')

    def get_queryset(self):
        sqs = super(SecureAssetSearchView, self).get_queryset().models(EcosystemsAsset)
        return sqs


class SecureAssetSearchViewCSV(LSVCSV):
    pass


# Permission mixin added in super
class EcosystemsAssetDetailView(NavContextMixin, HelpContextMixin, SecureAssetDetailView):
    model = EcosystemsAsset
    template_name = 'ecosystems/ecosystemsasset_detail.html'
    page_help_name = 'ecosystems:secureasset-detail'
    nav_url = reverse_lazy('ecosystems:secureasset-list')

    def get_context_data(self, **kwargs):
        context = super(EcosystemsAssetDetailView, self).get_context_data(**kwargs)
        context['edit_url'] = reverse('ecosystems:secureasset-update', kwargs={'pk': self.object.pk})
        context['delete_url'] = reverse('ecosystems:secureasset-delete', kwargs={'pk': self.object.pk})
        return context


# Permission mixin added in super
class EcosystemsAssetCreateView(NavContextMixin, HelpContextMixin, SecureAssetCreateView):
    permission_required = "ecosystems.add_ecosystemsasset"
    model = EcosystemsAsset
    form_class = EcosystemsAssetForm
    page_help_name = 'ecosystems:secureasset-create'
    template_name = 'ecosystems/ecosystemsasset_form.html'
    nav_url = reverse_lazy('ecosystems:secureasset-list')

    edit_object_cancel_url = reverse_lazy('ecosystems:secureasset-list')

    def get_success_url(self):
        return reverse('ecosystems:secureasset-detail', kwargs={'pk': self.object.pk})


# Permission mixin added in super
class EcosystemsAssetUpdateView(NavContextMixin, HelpContextMixin, SecureAssetUpdateView):
    permission_required = 'ecosystems.change_ecosystemsasset'
    model = EcosystemsAsset
    form_class = EcosystemsAssetForm
    page_help_name = 'ecosystems:secureasset-create'
    nav_url = reverse_lazy('ecosystems:secureasset-list')
    template_name = 'ecosystems/ecosystemsasset_form.html'

    edit_object_delete_perm = 'ecosystems:delete_ecosystemsasset'

    def get_edit_object_cancel_url(self):
        return reverse('ecosystems:secureasset-detail', kwargs={'pk': self.object.pk})

    def get_edit_object_edit_url(self):
        return reverse('ecosystems:secureasset-delete', kwargs={'pk': self.object.pk})

    def get_success_url(self):
        return reverse('ecosystems:secureasset-detail', kwargs={'pk': self.object.pk})


# Permission mixin added in super
class EcosystemsAssetDeleteView(NavContextMixin, HelpContextMixin, SecureAssetDeleteView):
    permission_required = 'ecosystems.delete_ecosystemsasset'

    page_help_name = 'ecosystems:secureasset-create'
    nav_url = reverse_lazy('ecosystems:secureasset-list')

    def get_context_data(self, **kwargs):
        context = super(EcosystemsAssetDeleteView, self).get_context_data(**kwargs)

        # This view thinks this is just a secureasset, get the ecosystemsasset:
        ecosystems_asset = SecureAsset.objects.get_subclass(pk=self.object.pk)
        context['cancel_url'] = reverse('ecosystems:secureasset-detail', kwargs={'pk': ecosystems_asset.pk})
        context['nav_url'] = reverse('ecosystems:secureasset-list')
        return context

    def get_success_url(self):
        return reverse('ecosystems:secureasset-list')


class EcosystemsProjectAssetDetailView(NavContextMixin, HelpContextMixin, SecureAssetDetailView):
    model = EcosystemsProjectAsset
    template_name = 'ecosystems/ecosystemsprojectasset_detail.html'
    page_help_name = 'ecosystems:project-secureasset-detail'
    nav_url = reverse_lazy('ecosystems:project-list')

    def get_context_data(self, **kwargs):
        context = super(EcosystemsProjectAssetDetailView, self).get_context_data(**kwargs)
        context['edit_url'] = reverse('ecosystems:project-secureasset-update',
                                      kwargs={'pk': self.object.pk, 'project_pk': self.object.project.pk})
        context['delete_url'] = reverse('ecosystems:project-secureasset-delete',
                                        kwargs={'pk': self.object.pk, 'project_pk': self.object.project.pk})
        return context


class EcosystemsProjectAssetCreateView(NavContextMixin, HelpContextMixin, SecureAssetCreateView):
    permission_required = "ecosystems.add_ecosystemsprojectasset"
    model = EcosystemsProjectAsset
    form_class = EcosystemsProjectAssetForm
    page_help_name = 'ecosystems:project-secureasset-create'
    nav_url = reverse_lazy('ecosystems:project-list')
    template_name = 'ecosystems/ecosystemsprojectasset_form.html'

    def get_edit_object_cancel_url(self):
        return reverse('ecosystems:project-detail', args=[self.kwargs.get('project_pk')])

    # Add eco project id to the form's kwargs:
    def get_form_kwargs(self):
        kwargs = super(EcosystemsProjectAssetCreateView, self).get_form_kwargs()
        kwargs['eco_project_id'] = self.kwargs.get('project_pk', None)
        return kwargs

    def get_success_url(self):
        return reverse('ecosystems:project-detail', kwargs={'pk': self.object.project.pk}) + "#tab-files"


class EcosystemsProjectAssetUpdateView(NavContextMixin, HelpContextMixin, SecureAssetUpdateView):
    permission_required = 'ecosystems.change_ecosystemsprojectasset'
    model = EcosystemsProjectAsset
    form_class = EcosystemsProjectAssetForm
    page_help_name = 'ecosystems:project-secureasset-create'
    template_name = 'ecosystems/ecosystemsprojectasset_form.html'
    nav_url = reverse_lazy('ecosystems:project-list')

    edit_object_delete_perm = 'ecosystems:delete_ecosystemsprojectasset'

    def get_edit_object_cancel_url(self):
        return reverse('ecosystems:project-secureasset-detail',
                       args=[self.kwargs.get('project_pk'), self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('ecosystems:project-secureasset-delete',
                       args=[self.kwargs.get('project_pk'), self.object.id])

    # Add eco project id to the form's kwargs:
    def get_form_kwargs(self):
        kwargs = super(EcosystemsProjectAssetUpdateView, self).get_form_kwargs()
        kwargs['eco_project_id'] = self.kwargs.get('project_pk', None)
        return kwargs

    def get_success_url(self):
        return reverse('ecosystems:project-secureasset-detail', kwargs={'pk': self.object.pk, 'project_pk': self.object.project.pk})


class EcosystemsProjectAssetDeleteView(NavContextMixin, HelpContextMixin, SecureAssetDeleteView):
    permission_required = 'ecosystems.delete_ecosystemsprojectasset'
    page_help_name = 'ecosystems:project-secureasset-create'
    nav_url = reverse_lazy('ecosystems:project-list')

    def get_context_data(self, **kwargs):
        context = super(EcosystemsProjectAssetDeleteView, self).get_context_data(**kwargs)

        # This view thinks this is just a secureasset, get the ecosystemsasset:
        ecosystems_asset = SecureAsset.objects.get_subclass(id=self.object.id)
        context['cancel_url'] = reverse('ecosystems:project-detail', kwargs={'pk': ecosystems_asset.project.pk})
        context['nav_url'] = reverse('ecosystems:project-list')
        return context

    def get_success_url(self):
        # This view thinks this is just a secureasset, get the ecosystemsasset:
        ecosystems_asset = SecureAsset.objects.get_subclass(id=self.object.id)
        return reverse('ecosystems:project-detail', kwargs={'pk': ecosystems_asset.project.id}) + "#tab-files"


class EcosystemsGISLayerCreateView(NavContextMixin, GISLayerCreateView):
    model = EcosystemsGISLayer
    form_class = EcosystemsGISLayerForm
    nav_url = reverse_lazy('ecosystems:gislayer-list')
    edit_object_cancel_url = reverse_lazy('ecosystems:gislayer-list')

    def get_success_url(self):
        return reverse('ecosystems:gislayer-detail', args=[self.object.id])


class EcosystemsGISLayerUpdateView(NavContextMixin, GISLayerUpdateView):
    model = EcosystemsGISLayer
    form_class = EcosystemsGISLayerForm
    nav_url = reverse_lazy('ecosystems:gislayer-list')
    edit_object_delete_perm = 'ecosystems:delete_gislayer'

    def get_edit_object_delete_url(self):
        return reverse("ecosystems:gislayer-delete", args=[self.object.id])

    def get_success_url(self):
        return reverse('ecosystems:gislayer-detail', args=[self.object.id])


class EcosystemsGISLayerDeleteView(NavContextMixin, GISLayerDeleteView):
    model = EcosystemsGISLayer
    success_url = reverse_lazy('ecosystems:gislayer-list')
    nav_url = reverse_lazy('ecosystems:gislayer-list')


class EcosystemsGISLayerDetailView(NavContextMixin, GISLayerDetailView):
    model = EcosystemsGISLayer
    nav_url = reverse_lazy('ecosystems:gislayer-list')


class EcosystemsGISLayerListView(NavContextMixin, GISLayerMasterListView):
    model = EcosystemsGISLayer
    ajax_url_name = 'ecosystems:layer-master-list-api'
    page_help_name = 'ecosystems:layer-master-list'
    nav_url = reverse_lazy('ecosystems:gislayer-list')
    # default_layer_type = 'Ecosystems Misc.'


class EcosystemsProjectGISLayerDetailView(NavContextMixin, GISLayerDetailView):
    model = EcosystemsGISLayer
    page_help_name = 'ecosystems:gislayer-detail'
    nav_url = reverse_lazy('ecosystems:gislayer-list')


class EcosystemsProjectGISLayerCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    model = EcosystemsGISLayer
    form_class = EcosystemsProjectGISLayerForm
    page_help_name = 'ecosystems:project-gislayer-create'

    def edit_object_cancel_url(self):
        project_pk = self.kwargs.get('project_pk')
        if project_pk:
            return reverse('ecosystems:project-detail', args=[project_pk])
        else:
            return reverse('ecosystems:gislayer-list')

    # Add eco project id to the form's kwargs:
    def get_form_kwargs(self):
        kwargs = super(EcosystemsProjectGISLayerCreateView, self).get_form_kwargs()
        kwargs['eco_project_id'] = self.kwargs.get('project_pk', None)
        return kwargs

    @method_decorator(permission_required('ecosystems.add_ecosystemsgislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(EcosystemsProjectGISLayerCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.project:
            return reverse('ecosystems:project-detail', kwargs={'pk': self.object.project.pk})
        else:
            return reverse('ecosystems:gislayer-detail', kwargs={'pk': self.object.pk})


class EcosystemsProjectGISLayerUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    model = EcosystemsGISLayer
    form_class = EcosystemsProjectGISLayerForm
    page_help_name = 'ecosystems:project-gislayer-update'
    edit_object_delete_perm = 'ecosystems:delete_ecosystemsgislayer'

    def get_edit_object_cancel_url(self):
        return self.object.get_absolute_url()

    def get_edit_object_delete_url(self):
        return self.object.get_delete_url()

    # Add eco project id to the form's kwargs:
    def get_form_kwargs(self):
        kwargs = super(EcosystemsProjectGISLayerUpdateView, self).get_form_kwargs()
        kwargs['eco_project_id'] = self.kwargs.get('project_pk', None)
        return kwargs

    @method_decorator(permission_required('ecosystems.change_ecosystemsgislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(EcosystemsProjectGISLayerUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.project:
            return reverse('ecosystems:project-detail', kwargs={'pk': self.object.project.pk})
        else:
            return reverse('ecosystems:gislayer-detail', kwargs={'pk': self.object.pk})


class EcosystemsProjectGISLayerDeleteView(HelpContextMixin, DeleteView):
    model = EcosystemsGISLayer
    page_help_name = 'ecosystems:project-gislayer-delete'

    @method_decorator(permission_required('ecosystems.delete_ecosystemsgislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(EcosystemsProjectGISLayerDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.project:
            return reverse('ecosystems:project-detail', kwargs={'pk': self.object.project.pk})
        else:
            return reverse('ecosystems:gislayer-list')

    def get_cancel_url(self):
        if self.object.project:
            return reverse('ecosystems:project-detail', kwargs={'pk': self.object.project.pk})
        else:
            return reverse('ecosystems:gislayer-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context_data = super(EcosystemsProjectGISLayerDeleteView, self).get_context_data(**kwargs)
        context_data['project_pk'] = self.kwargs.get('project_pk', None)
        return context_data


class EcosystemsProjectCreateView(EditObjectMixin, NavContextMixin, HelpContextMixin, CreateView):
    """
    Similar to EcosystemsProjectCreateView.
    file_number_formset has been removed (external file numbers not needed), however,
    at some point in the near future we will implemente FileNo inlines - refer to
    EcosystemsProjectCreateView for how best to do that.
    """
    model = EcosystemsProject
    form_class = EcosystemsProjectForm
    nav_url = reverse_lazy('ecosystems:project-list')
    page_help_name = 'ecosystems:project-create'
    edit_object_cancel_url = reverse_lazy('ecosystems:project-list')

    def get(self, request, *args, **kwargs):
        response = super(EcosystemsProjectCreateView, self).get(request, *args, **kwargs)

        # Try to stop form from auto-filling when the user hits back.
        response['Cache-Control'] = 'no-cache'  # Set Cache-Control Header
        return response

    def get_context_data(self, **kwargs):
        context = super(EcosystemsProjectCreateView, self).get_context_data(**kwargs)

        textarea_names = parse_choices(GeneralSetting.objects.get('ecosystems_project_misc_textareas'), False)
        misc_textarea_fields = []
        for name in textarea_names:
            if name and name[0]:
                misc_textarea_fields.append("misc_textarea_%s" % name[0])

        context['misc_textarea_fields'] = misc_textarea_fields

        return context


class EcosystemsProjectUpdateView(EditObjectMixin, NavContextMixin, HelpContextMixin, UpdateView):
    model = EcosystemsProject
    form_class = EcosystemsProjectForm
    nav_url = reverse_lazy('ecosystems:project-list')
    page_help_name = 'ecosystems:project-update'
    edit_object_delete_perm = 'ecosystems:delete_ecosystemsproject'

    def get_edit_object_cancel_url(self):
        return reverse('ecosystems:project-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('ecosystems:project-delete', args=[self.object.id])

    def get_initial(self):
        initial = super(EcosystemsProjectUpdateView, self).get_initial()

        if self.object.misc_textareas is not None:
            textarea_names = parse_choices(GeneralSetting.objects.get('ecosystems_project_misc_textareas'), False)
            misc_textarea_fields = []
            for name in textarea_names:
                if name and name[0] and name[1]:
                    key = "misc_textarea_%s" % name[0]

                    if name[1] in self.object.misc_textareas.keys():
                        value = self.object.misc_textareas[name[1]]
                        initial[key] = value

        return initial

    def get_context_data(self, **kwargs):
        context = super(EcosystemsProjectUpdateView, self).get_context_data(**kwargs)

        textarea_names = parse_choices(GeneralSetting.objects.get('ecosystems_project_misc_textareas'), False)
        misc_textarea_fields = []
        for name in textarea_names:
            if name and name[0]:
                misc_textarea_fields.append("misc_textarea_%s" % name[0])

        context['misc_textarea_fields'] = misc_textarea_fields

        return context

    @method_decorator(permission_required('ecosystems.change_ecosystemsproject', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(EcosystemsProjectUpdateView, self).dispatch(request, *args, **kwargs)


class EcosystemsProjectDetailView(HelpContextMixin, DetailView):
    model = EcosystemsProject
    page_help_name = 'ecosystems:project-detail'

    def get_context_data(self, **kwargs):
        context = super(EcosystemsProjectDetailView, self).get_context_data(**kwargs)
        # project_assets = self.object.ecosystemsprojectasset_set.all()
        # context['assets_list'] = project_assets
        feature_ajax_url = "{}?{}={}&as_geojson=1".format(reverse('ecosystems:api:feature-list'), 'project', self.object.id)
        context['feature_ajax_url'] = feature_ajax_url

        # Need to pass these strings into the detail view to preserve order.
        textarea_names = parse_choices(GeneralSetting.objects.get('ecosystems_project_misc_textareas'), False)
        misc_textarea_fields = []
        for name in textarea_names:
            if name and name[1]:
                misc_textarea_fields.append(name[1])

        context['misc_textarea_fields'] = misc_textarea_fields

        return context

    @method_decorator(permission_required('ecosystems.view_ecosystemsproject', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(EcosystemsProjectDetailView, self).dispatch(request, *args, **kwargs)


class EcosystemsProjectDetailPrintView(EcosystemsProjectDetailView):
    model = EcosystemsProject
    page_help_name = 'ecosystems:project-detail-print'
    template_name = 'ecosystems/ecosystemsproject_detail_print.html'


class EcosystemsProjectListView(HelpContextMixin, ListView):
    model = EcosystemsProject
    page_help_name = 'ecosystems:project-list'

    def get_context_data(self, **kwargs):
        context = super(EcosystemsProjectListView, self).get_context_data(**kwargs)
        context['ajax_url'] = reverse('ecosystems:api:project-list')
        return context

    @method_decorator(permission_required('ecosystems.view_ecosystemsproject', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(EcosystemsProjectListView, self).dispatch(request, *args, **kwargs)


class EcosystemsProjectDeleteView(HelpContextMixin, DeleteView):
        model = EcosystemsProject
        success_url = reverse_lazy('ecosystems:project-list')
        page_help_name = 'ecosystems:project-delete'

        @method_decorator(permission_required('ecosystems.delete_ecosystemsproject', raise_exception=True))
        def dispatch(self, request, *args, **kwargs):
            return super(EcosystemsProjectDeleteView, self).dispatch(request, *args, **kwargs)


class SpeciesAlternateNameFormsetMixin(FormView):
    """ This Mixin is meant to be mixed in with a Create or Update view.  It's assumed that
    self.model and self.object exist in the class this is mixed into.
    """
    common_name_model = None  # Override this in the create/update view
    common_name_form = None

    indigenous_name_model = None
    indigenous_name_form = None

    def get_common_name_formset(self):
        # self.model is declared in the inheriting class.
        return inlineformset_factory(self.model, self.common_name_model, form=self.common_name_form,
                                     can_delete=True, extra=1)

    def get_indigenous_name_formset(self):
        # self.model is declared in the inheriting class.
        return inlineformset_factory(self.model, self.indigenous_name_model, form=self.indigenous_name_form,
                                     can_delete=True, extra=1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        common_name_formset = self.get_common_name_formset()
        indigenous_name_formset = self.get_indigenous_name_formset()

        if self.request.method == 'POST':
            if self.object:
                context['common_name_formset'] = common_name_formset(self.request.POST, self.request.FILES,
                                                                     instance=self.object)
                context['indigenous_name_formset'] = indigenous_name_formset(self.request.POST, self.request.FILES,
                                                                             instance=self.object)
            else:
                context['common_name_formset'] = common_name_formset(self.request.POST, self.request.FILES)
                context['indigenous_name_formset'] = indigenous_name_formset(self.request.POST, self.request.FILES)
        else:
            # NOTE: The initial can't be set on the empty form, so in the form_valid method we make sure that property
            # is correctly set.
            if self.object:
                context['common_name_formset'] = common_name_formset(instance=self.object)
                context['indigenous_name_formset'] = indigenous_name_formset(instance=self.object)
            else:
                context['common_name_formset'] = common_name_formset()
                context['indigenous_name_formset'] = indigenous_name_formset()

        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        common_name_formset = self.get_common_name_formset()
        indigenous_name_formset = self.get_indigenous_name_formset()

        common_name_forms = common_name_formset(self.request.POST, self.request.FILES, instance=self.object)
        if common_name_forms.is_valid():
            common_name_forms.save()

        indigenous_name_forms = indigenous_name_formset(self.request.POST, self.request.FILES, instance=self.object)
        if indigenous_name_forms.is_valid():
            indigenous_name_forms.save()

        return response


class PlantTagListView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, ListView):
    model = PlantTag
    page_help_name = 'ecosystems:planttag-list'

    nav_url = reverse_lazy('ecosystems:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ajax_url'] = reverse('ecosystems:api:planttag-list')

        context['fields'] = [
            ['name',
             {
                 'verbose_name': 'Name',
                 'type': 'link',
                 'url_field': 'url'
             }],
            ['items_count', 'References to this Plant']
        ]

        context['sort_options'] = [
            ['name', 'Name']
        ]
        context['filters'] = []

        return context


class PlantTagDetailView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, DetailView):
    model = PlantTag
    page_help_name = 'ecosystems:planttag-detail'
    nav_url = reverse_lazy('ecosystems:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_things'] = PlantTaggedItem.objects.filter(tag=self.object)
        return context


class PlantTagCreateView(PermissionRequiredMixin, NavContextMixin, HelpContextMixin, SpeciesAlternateNameFormsetMixin,
                         EditObjectMixin, CreateView):
    model = PlantTag
    page_help_name = 'ecosystems:planttag-create'
    nav_url = reverse_lazy('ecosystems:dashboard')
    form_class = PlantTagForm
    permission_required = 'ecosystems.add_planttag'
    edit_object_cancel_url = reverse_lazy('ecosystems:planttag-list')

    common_name_model = CommonPlantName
    common_name_form = CommonPlantNameForm

    indigenous_name_model = IndigenousPlantName
    indigenous_name_form = IndigenousPlantNameForm

    def get_success_url(self):
        return reverse('ecosystems:planttag-detail', args=[self.object.id, ])


class PlantTagUpdateView(PermissionRequiredMixin, NavContextMixin, HelpContextMixin, SpeciesAlternateNameFormsetMixin,
                         EditObjectMixin, UpdateView):
    model = PlantTag
    page_help_name = 'ecosystems:planttag-update'
    nav_url = reverse_lazy('ecosystems:dashboard')
    form_class = PlantTagForm
    permission_required = 'ecosystems.change_planttag'
    edit_object_cancel_url = reverse_lazy('ecosystems:planttag-list')

    common_name_model = CommonPlantName
    common_name_form = CommonPlantNameForm

    indigenous_name_model = IndigenousPlantName
    indigenous_name_form = IndigenousPlantNameForm

    def get_edit_object_cancel_url(self):
        return reverse('ecosystems:planttag-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('ecosystems:planttag-delete', args=[self.object.id])

    def get_success_url(self):
        return reverse('ecosystems:planttag-detail', args=[self.object.id, ])


class PlantTagDeleteView(PermissionRequiredMixin, NavContextMixin, HelpContextMixin, DeleteView):
    model = PlantTag
    success_url = reverse_lazy('ecosystems:planttag-list')
    page_help_name = 'ecosystems:planttag-delete'
    nav_url = reverse_lazy('ecosystems:dashboard')
    permission_required = 'ecosystems.delete_planttag'


class AnimalTagListView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, ListView):
    model = AnimalTag
    page_help_name = 'ecosystems:animaltag-list'

    nav_url = reverse_lazy('ecosystems:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ajax_url'] = reverse('ecosystems:api:animaltag-list')

        context['fields'] = [
            ['name',
             {
                 'verbose_name': 'Name',
                 'type': 'link',
                 'url_field': 'url'
             }],
            ['items_count', 'References to this Plant']
        ]

        context['sort_options'] = [
            ['name', 'Name']
        ]
        context['filters'] = []

        return context


class AnimalTagDetailView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, DetailView):
    model = AnimalTag
    page_help_name = 'ecosystems:animaltag-detail'
    nav_url = reverse_lazy('ecosystems:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_things'] = AnimalTaggedItem.objects.filter(tag=self.object)
        return context


class AnimalTagCreateView(PermissionRequiredMixin, NavContextMixin, HelpContextMixin, SpeciesAlternateNameFormsetMixin,
                          EditObjectMixin, CreateView):
    model = AnimalTag
    page_help_name = 'ecosystems:animaltag-create'
    nav_url = reverse_lazy('ecosystems:dashboard')
    form_class = AnimalTagForm
    permission_required = 'ecosystems.add_animaltag'
    edit_object_cancel_url = reverse_lazy('ecosystems:animaltag-list')

    common_name_model = CommonAnimalName
    common_name_form = CommonAnimalNameForm

    indigenous_name_model = IndigenousAnimalName
    indigenous_name_form = IndigenousAnimalNameForm

    def get_success_url(self):
        return reverse('ecosystems:animaltag-detail', args=[self.object.id, ])


class AnimalTagUpdateView(PermissionRequiredMixin, NavContextMixin, HelpContextMixin, SpeciesAlternateNameFormsetMixin,
                          EditObjectMixin, UpdateView):
    model = AnimalTag
    page_help_name = 'ecosystems:animaltag-update'
    nav_url = reverse_lazy('ecosystems:dashboard')
    form_class = AnimalTagForm
    permission_required = 'ecosystems.change_animaltag'
    edit_object_delete_perm = 'ecosystems:delete_animaltag'

    common_name_model = CommonAnimalName
    common_name_form = CommonAnimalNameForm

    indigenous_name_model = IndigenousAnimalName
    indigenous_name_form = IndigenousAnimalNameForm

    def get_edit_object_cancel_url(self):
        return reverse('ecosystems:animaltag-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('ecosystems:animaltag-delete', args=[self.object.id])

    def get_success_url(self):
        return reverse('ecosystems:animaltag-detail', args=[self.object.id, ])


class AnimalTagDeleteView(PermissionRequiredMixin, NavContextMixin, HelpContextMixin, DeleteView):
    model = AnimalTag
    success_url = reverse_lazy('ecosystems:animaltag-list')
    page_help_name = 'ecosystems:animaltag-delete'
    nav_url = reverse_lazy('ecosystems:dashboard')
    permission_required = 'ecosystems.delete_animaltag'


############################################################
# API
############################################################
class EcosystemsGISLayerViewSet(GISLayerViewSet):
    queryset = EcosystemsGISLayer.objects.all()


class EcosystemsGISLayerMasterListAPIView(GISLayerMasterListAPIView):
    queryset = EcosystemsGISLayer.objects.all()

    # def get_queryset(self):
    #     return GISLayerMaster.objects.filter(Q(layer_type='Ecosystems') | Q(layer_type='Misc.'))


class EcosystemsGISLayerFeatureViewSet(GISFeatureViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_fields = ('name', 'layer')
    search_fields = ('name',)
    ordering_fields = '__all__'
    ordering = ('name',)
    geojson_serializer_class = EcosystemsGISLayerFeatureGeoJSONSerializer

    def get_queryset(self):
        queryset = super(EcosystemsGISLayerFeatureViewSet, self).get_queryset()
        prj_id = self.request.query_params.get('project', None)
        if prj_id:
            layers = EcosystemsGISLayer.objects.filter(project=prj_id)
            queryset = queryset.filter(layer__in=layers)
        return queryset


class EcosystemsAssetViewSet(SecureAssetViewSet):
    def get_queryset(self):
        return EcosystemsAsset.objects.all()


class EcosystemsProjectViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EcosystemsProjectSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('id', 'tags__tag', 'cedar_project_name', 'cedar_project_code_q', )
    filter_fields = ('id',)
    ordering_fields = '__all__'
    ordering = ('-id',)  # Default sort field.

    def get_queryset(self):
        """
        get_queryset modified to query all any Person objects related to the project
         - because they are spread over several fields it was complicating
            the filter_fields set up. This looks for a url parameter "personid" and pre-filters
            based on that.
        """
        queryset = EcosystemsProject.objects.all()
        personid = self.request.query_params.get('personid', None)

        if personid is not None:
            queryset = queryset.filter(
                Q(author__in=[personid, ]) |
                Q(contacts__in=[personid, ])).distinct()

        return queryset


class PlantTagViewSet(viewsets.ModelViewSet):
    queryset = PlantTag.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PlantTagSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('id', 'description', 'name')
    ordering_fields = ('-item_count',)


class AnimalTagViewSet(viewsets.ModelViewSet):
    queryset = AnimalTag.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AnimalTagSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('id', 'description', 'name')
    ordering_fields = ('-item_count',)


def list_plant_or_animal_tags(request, model_name=None):
    """
    Returns a list of JSON objects with a `name` and a `value` property that
    all start like your query string `q` (not case sensitive).
    
    Takes 'plant' or 'animal' as a switch to choose the model to use.
    """
    model = None
    if model_name == 'plant':
        model = PlantTag
    elif model_name == 'animal':
        model = AnimalTag
    else:
        raise Exception("Pass either 'plant' or 'animal' as the argument for this function.")

    query = request.GET.get('q', '')
    max_suggestions = getattr(settings, 'TAGGIT_AUTOSUGGEST_MAX_SUGGESTIONS', 20)
    limit = request.GET.get('limit', max_suggestions)
    try:
        request.GET.get('limit', max_suggestions)
        limit = min(int(limit), max_suggestions)  # max or less
    except (ValueError, TypeError):
        limit = max_suggestions

    tag_name_qs = model.objects.filter(Q(name__icontains=query)|Q(common_names__name__icontains=query)|Q(indigenous_names__name__icontains=query)). \
        values('pk', 'name')

    if callable(getattr(model, 'request_filter', None)):
        tag_name_qs = tag_name_qs.filter(model.request_filter(request)).distinct()

    data = [{'id': n['pk'], 'name': n['name'], 'value': n['name']} for n in tag_name_qs[:limit]]

    return HttpResponse(json.dumps(data), content_type='application/json')
