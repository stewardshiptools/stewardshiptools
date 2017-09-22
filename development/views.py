import datetime
from django.core.exceptions import PermissionDenied
from django.db.models import Q, F, Value, BooleanField, When, Case
from django.contrib import messages

from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView, FormView
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count

from django.core.urlresolvers import reverse_lazy
from django.forms import formset_factory, inlineformset_factory

from threadedcomments.models import ThreadedComment
from braces.views import PermissionRequiredMixin, LoginRequiredMixin

from cedar.mixins import NavContextMixin, FileResponseMixin, EditObjectMixin

from .models import DevelopmentProject, DevelopmentGISLayer, DevelopmentProjectAsset, FileNo,\
    DevelopmentAsset, FilingCode, ConsultationStage, DevelopmentProjectAction

from .serializers import DevelopmentProjectSerializer, DevelopmentGISLayerFeatureGeoJSONSerializer

from .forms import DevelopmentProjectForm, DevelopmentProjectGISLayerForm, DevelopmentGISLayerInlineFormset, \
    DevelopmentProjectAssetForm, DevelopmentSpatialReportForm, FileNoForm, DevelopmentSettings, DevelopmentAssetForm, SERForm

from development.utils import ser

from crm.models import Organization, Person

import django_filters
from rest_framework import viewsets, filters
from rest_framework.reverse import reverse
from rest_framework import permissions
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer

from cedar_settings.models import GeneralSetting
from cedar_settings.utils.parsers import parse_choices

from tags.models import Tag

from geoinfo.models import GISLayer, GISFeature, SpatialReport, SpatialReportItem, GISLayerMaster
from geoinfo.views import GISFeatureViewSet, GISLayerDetailView, GenericSpatialReportFormView, GISLayerViewSet, \
    GISLayerMasterListView, GISLayerMasterListAPIView

import assets
import cedar

from communication.models import HarvestCodePrefix

from help.mixins import HelpContextMixin

from cedar_settings.views import CedarSettingsView


class DevelopmentSettingsView(CedarSettingsView):
    '''
    See the super for how it's done.
    '''

    def get_setting_fields(self):
        ct = ContentType.objects.get_for_model(DevelopmentProject)
        return [
            {
                'name': 'development_project_code_prefix',
                'data_type': 'reference',
                'queryset': HarvestCodePrefix.objects.filter(content_type=ct),
                'label': 'Default Harvest Code Prefix for Development Projects'
            },
        ]

    def get_success_url(self):
        return reverse_lazy("development:settings")


class DashboardView(HelpContextMixin, TemplateView):
    template_name = 'development/dashboard.html'
    page_help_name = 'development:dashboard'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['project_count'] = DevelopmentProject.objects.all().count()
        context['documents_count'] = DevelopmentAsset.objects.count()
        context['spatial_layers_count'] = DevelopmentGISLayer.objects.count()
        return context

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)


class DevelopmentProjectCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    model = DevelopmentProject
    form_class = DevelopmentProjectForm
    page_help_name = 'development:project-create'
    file_number_formset = inlineformset_factory(DevelopmentProject, FileNo, form=FileNoForm, can_delete=True, extra=1)
    edit_object_cancel_url = reverse_lazy('development:project-list')

    def get_form_kwargs(self):
        kwargs = super(DevelopmentProjectCreateView, self).get_form_kwargs()
        kwargs['initial'].update({'initial_date': datetime.datetime.now().date()})
        return kwargs

    def get(self, request, *args, **kwargs):
        response = super(DevelopmentProjectCreateView, self).get(request, *args, **kwargs)

        # Try to stop form from auto-filling when the user hits back.
        response['Cache-Control'] = 'no-cache'  # Set Cache-Control Header
        return response

    def form_valid(self, form):
        response = super(DevelopmentProjectCreateView, self).form_valid(form)

        if self.request.method == 'POST':
            formset = self.file_number_formset(self.request.POST, self.request.FILES, instance=self.object)
            if formset.is_valid():
                formset.save()
            else:
                return self.form_invalid(form)

        return response

    def get_context_data(self, **kwargs):
        context = super(DevelopmentProjectCreateView, self).get_context_data(**kwargs)

        if self.request.method == 'POST':
            context['file_number_formset'] = self.file_number_formset(self.request.POST)
        else:
            context['file_number_formset'] = self.file_number_formset()

        textarea_names = parse_choices(GeneralSetting.objects.get('development_project_misc_textareas'), False)
        misc_textarea_fields = []
        for name in textarea_names:
            if name and name[0]:
                misc_textarea_fields.append("misc_textarea_%s" % name[0])

        context['misc_textarea_fields'] = misc_textarea_fields

        context['xml_file_form'] = SERForm()    # the xml upload form
        return context

    @method_decorator(permission_required('development.add_developmentproject', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DevelopmentProjectCreateView, self).dispatch(request, *args, **kwargs)


class DevelopmentProjectCreateFromSERView(DevelopmentProjectCreateView):
    xml_data = None

    def get_context_data(self, **kwargs):
        context = super(DevelopmentProjectCreateFromSERView, self).get_context_data(**kwargs)
        if self.is_upload_view():
            # no need to reparse xml data here, it was done in get_form_kwargs()

            # override the fileno formset with new initial data from xml:
            fileno_initial = []

            bc_filenos = self.xml_data.get('bc_filenos', None)
            if bc_filenos:
                for fileno in bc_filenos:
                    fileno_initial.append(fileno)

            app_filenos = self.xml_data.get('app_filenos', None)
            if app_filenos:
                for fileno in app_filenos:
                    fileno_initial.append(fileno)

            self.file_number_formset = inlineformset_factory(
                DevelopmentProject,
                FileNo,
                form=FileNoForm,
                can_delete=True,
                extra=len(fileno_initial) or 1
            )

            context['file_number_formset'] = self.file_number_formset(initial=fileno_initial)

        return context

    def get_form_kwargs(self):
        """
        set form initial to uploaded xml data (if present).
        :return: 
        """

        # something about the super's kwargs are messing with the form initial if I
        # try to update the kwargs inital and return that. Instead, I steal the initial
        # and return only initial as the kwargs. It's happier with that.
        kwargs = super(DevelopmentProjectCreateFromSERView, self).get_form_kwargs()

        initial = kwargs.get('initial', {})

        if self.is_upload_view():
            self.parse_xml()
            initial.update(**self.xml_data['project']['kwargs'])

            geomark_url = self.xml_data['geomark']['kwargs'].get('geomark', None)
            if geomark_url:
                initial.update({'geomark_url': geomark_url})

            geomark_notes = self.xml_data['geomark']['kwargs'].get('notes', None)
            if geomark_notes:
                initial.update({'geomark_notes': geomark_notes})

            # Word of caution - I stole this from the DEV PRJ update view code and modified bits and
            # pieces to make  it work. Use something else as reference for using he misc_textarea_field business.
            misc_textareas = self.xml_data['project']['kwargs'].get('misc_textareas', None)
            if misc_textareas is not None:
                textarea_names = parse_choices(GeneralSetting.objects.get('development_project_misc_textareas'), False)
                misc_textarea_fields = []
                for name in textarea_names:
                    if name and name[0] and name[1]:
                        key = "misc_textarea_%s" % name[0]

                        if name[0] in misc_textareas.keys():
                            value = misc_textareas[name[0]]
                            initial[key] = value

            return {'initial': initial}
        else:
            return kwargs


    def is_upload_view(self):
        '''
        Checkes the request for presence of the "template_document". If
        present it means that a user has upload an XML document template.
        :return: True/False
        '''
        if self.request.FILES:
            if self.request.FILES['template_document']:
                return True
        return False

    def parse_xml(self):
        """
        Parses uploaded xml and stores in class variable self.xml_data.
        Called by get_form() because it gets called early on. Could be put somewhere else
        as long as it gets called fairly early on.
        :return:
        """
        data = XMLParser().parse(self.request.FILES['template_document'])
        self.xml_data = ser.process_ser(data)

    def form_valid(self, form):
        """
        Override form_valid to create a Geomark layer (if supplied)
        :param form: 
        :return: 
        """
        response = super(DevelopmentProjectCreateFromSERView, self).form_valid(form)

        geomark_url = form.cleaned_data.get('geomark_url', None)
        if geomark_url:
            geomark_layer = DevelopmentGISLayer.objects.create(**{
                'name': DevelopmentGISLayer.suggest_layer_name(self.object),
                'project': self.object,
                'input_type': 'geomark',
                'geomark': geomark_url,
                'notes': form.cleaned_data.get('geomark_notes', ''),
                'author': self.request.user
            })
            geomark_layer.save()
        return response


class DevelopmentProjectUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    model = DevelopmentProject
    form_class = DevelopmentProjectForm
    page_help_name = 'development:project-update'
    file_number_formset = inlineformset_factory(DevelopmentProject, FileNo, form=FileNoForm, can_delete=True, extra=1)
    edit_object_delete_perm = 'development:delete_developmentproject'

    def get_edit_object_cancel_url(self):
        return reverse('development:project-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('development:project-delete', args=[self.object.id])

    def form_valid(self, form):
        response = super(DevelopmentProjectUpdateView, self).form_valid(form)

        if self.request.method == 'POST':
            formset = self.file_number_formset(self.request.POST, self.request.FILES, instance=self.object)
            if formset.is_valid():
                formset.save()

                for obj in formset.deleted_objects:
                    if obj.id:
                        obj.delete()
            else:
                return self.form_invalid(form)

        return response

    def get_initial(self):
        initial = super(DevelopmentProjectUpdateView, self).get_initial()

        if self.object.misc_textareas is not None:
            textarea_names = parse_choices(GeneralSetting.objects.get('development_project_misc_textareas'), False)
            misc_textarea_fields = []
            for name in textarea_names:
                if name and name[0] and name[1]:
                    key = "misc_textarea_%s" % name[0]

                    if name[1] in self.object.misc_textareas.keys():
                        value = self.object.misc_textareas[name[1]]
                        initial[key] = value

        return initial

    def get_context_data(self, **kwargs):
        context = super(DevelopmentProjectUpdateView, self).get_context_data(**kwargs)

        if self.request.method == 'POST':
            context['file_number_formset'] = self.file_number_formset(self.request.POST, instance=self.object)
        else:
            context['file_number_formset'] = self.file_number_formset(instance=self.object)

        textarea_names = parse_choices(GeneralSetting.objects.get('development_project_misc_textareas'), False)
        misc_textarea_fields = []
        for name in textarea_names:
            if name and name[0]:
                misc_textarea_fields.append("misc_textarea_%s" % name[0])

        context['misc_textarea_fields'] = misc_textarea_fields

        return context

    @method_decorator(permission_required('development.change_developmentproject', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DevelopmentProjectUpdateView, self).dispatch(request, *args, **kwargs)


class DevelopmentProjectDetailView(HelpContextMixin, DetailView):
    model = DevelopmentProject
    page_help_name = 'development:project-detail'

    def get_context_data(self, **kwargs):
        context = super(DevelopmentProjectDetailView, self).get_context_data(**kwargs)
        # project_assets = self.object.developmentprojectasset_set.all()
        # context['assets_list'] = project_assets
        feature_ajax_url = "{}?{}={}&as_geojson=1".format(reverse('development:api:feature-list'), 'project', self.object.id)
        context['feature_ajax_url'] = feature_ajax_url

        # Need to pass these strings into the detail view to preserve order.
        textarea_names = parse_choices(GeneralSetting.objects.get('development_project_misc_textareas'), False)
        misc_textarea_fields = []
        for name in textarea_names:
            if name and name[1]:
                misc_textarea_fields.append(name[1])

        context['misc_textarea_fields'] = misc_textarea_fields

        context['actions'] = DevelopmentProjectAction.objects.filter(project=self.object)

        return context

    @method_decorator(permission_required('development.view_developmentproject', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DevelopmentProjectDetailView, self).dispatch(request, *args, **kwargs)


class DevelopmentProjectDetailPrintView(DevelopmentProjectDetailView):
    model = DevelopmentProject
    page_help_name = 'development:project-detail-print'
    template_name = 'development/developmentproject_detail_print.html'


class DevelopmentProjectListView(HelpContextMixin, ListView):
    model = DevelopmentProject
    page_help_name = 'development:project-list'

    def get_context_data(self, **kwargs):
        context = super(DevelopmentProjectListView, self).get_context_data(**kwargs)
        context['ajax_url'] = reverse('development:api:project-list')

        # These key/value pairs are being passed into js where they will no longer be sorted... we must send them as
        # a sorted list of tuples (actually lists with two elements) to maintain order.
        context['consultation_stage_options'] = list(map(lambda x: [x['id'], x['stage_name']], ConsultationStage.objects.values('id', 'stage_name')))
        context['filing_code_options'] = list(map(lambda x: [x['code'], x['label']], FilingCode.objects.values('code', 'label')))
        context['people_options'] = list(map(lambda x: [x.id, x.name], Person.objects.all()))
        context['organization_options'] = list(map(lambda x: [x['id'], x['name']], Organization.objects.values('id', 'name')))

        context['tags_options'] = list(
            map(lambda x: [x.id, x.name],
                Tag.objects.filter(
                    tags_taggeditem_items__content_type=ContentType.objects.get_for_model(DevelopmentProject)
                ).distinct()
            )
        )

        return context

    @method_decorator(login_required())
    @method_decorator(permission_required('development.view_developmentproject', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DevelopmentProjectListView, self).dispatch(request, *args, **kwargs)


class DevelopmentProjectListPrintView(DevelopmentProjectListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_print_view'] = True
        return context


class DevelopmentProjectDeleteView(HelpContextMixin, DeleteView):
    model = DevelopmentProject
    success_url = reverse_lazy('development:project-list')
    page_help_name = 'development:project-delete'

    @method_decorator(permission_required('development.delete_developmentproject', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DevelopmentProjectDeleteView, self).dispatch(request, *args, **kwargs)


class DevelopmentGISLayerListView(GISLayerMasterListView):
    model = DevelopmentGISLayer
    page_help_name = 'development:layer-master-list'
    ajax_url_name = 'development:layer-master-list-api'
    # default_layer_type = 'Development Misc.'


class DevelopmentProjectGISLayerDetailView(NavContextMixin, GISLayerDetailView):
    model = DevelopmentGISLayer
    page_help_name = 'development:gislayer-detail'
    nav_url = reverse_lazy('development:gislayer-list')


class DevelopmentProjectGISLayerCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    model = DevelopmentGISLayer
    form_class = DevelopmentProjectGISLayerForm
    page_help_name = 'development:project-gislayer-create'

    def edit_object_cancel_url(self):
        project_pk = self.kwargs.get('project_pk')
        if project_pk:
            return reverse('development:project-detail', args=[project_pk])
        else:
            return reverse('development:gislayer-list')

    # Add devt project id to the form's kwargs:
    def get_form_kwargs(self):
        kwargs = super(DevelopmentProjectGISLayerCreateView, self).get_form_kwargs()
        kwargs['dev_project_id'] = self.kwargs.get('project_pk', None)
        return kwargs

    @method_decorator(permission_required('development.add_developmentgislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DevelopmentProjectGISLayerCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.project:
            return reverse('development:project-detail', kwargs={'pk': self.object.project.pk})
        else:
            return reverse('development:gislayer-detail', kwargs={'pk': self.object.pk})


class DevelopmentProjectGISLayerUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    model = DevelopmentGISLayer
    form_class = DevelopmentProjectGISLayerForm
    page_help_name = 'development:project-gislayer-update'
    edit_object_delete_perm = 'development:delete_developmentgislayer'

    def get_edit_object_cancel_url(self):
        return self.object.get_absolute_url()

    def get_edit_object_delete_url(self):
        return self.object.get_delete_url()

    # Add devt project id to the form's kwargs:
    def get_form_kwargs(self):
        kwargs = super(DevelopmentProjectGISLayerUpdateView, self).get_form_kwargs()
        kwargs['dev_project_id'] = self.kwargs.get('project_pk', None)
        return kwargs

    @method_decorator(permission_required('development.change_developmentgislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DevelopmentProjectGISLayerUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.project:
            return reverse('development:project-detail', kwargs={'pk': self.object.project.pk})
        else:
            return reverse('development:gislayer-detail', kwargs={'pk': self.object.pk})


class DevelopmentProjectGISLayerDeleteView(HelpContextMixin, DeleteView):
    model = DevelopmentGISLayer
    page_help_name = 'development:project-gislayer-delete'

    @method_decorator(permission_required('development.delete_developmentgislayer', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DevelopmentProjectGISLayerDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.project:
            return reverse('development:project-detail', kwargs={'pk': self.object.project.pk})
        else:
            return reverse('development:gislayer-list')

    def get_cancel_url(self):
        if self.object.project:
            return reverse('development:project-detail', kwargs={'pk': self.object.project.pk})
        else:
            return reverse('development:gislayer-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context_data = super(DevelopmentProjectGISLayerDeleteView, self).get_context_data(**kwargs)
        context_data['project_pk'] = self.kwargs.get('project_pk', None)
        return context_data


class DevelopmentAssetDetailView(NavContextMixin, HelpContextMixin, assets.views.SecureAssetDetailView):
    model = DevelopmentAsset
    template_name = 'development/developmentasset_detail.html'
    page_help_name = 'development:secureasset-detail'
    nav_url = reverse_lazy('development:secureasset-list')

    def get_context_data(self, **kwargs):
        context = super(DevelopmentAssetDetailView, self).get_context_data(**kwargs)
        context['edit_url'] = reverse('development:secureasset-update', kwargs={'pk': self.object.pk})
        context['delete_url'] = reverse('development:secureasset-delete', kwargs={'pk': self.object.pk})
        return context


class DevelopmentAssetCreateView(HelpContextMixin, assets.views.SecureAssetCreateView):
    permission_required = "development.add_developmentasset"
    model = DevelopmentAsset
    form_class = DevelopmentAssetForm
    page_help_name = 'development:secureasset-create'
    template_name = 'development/developmentasset_form.html'
    edit_object_cancel_url = reverse_lazy('development:secureasset-list')
    edit_object_delete_perm = 'development:delete_developmentasset'

    def get_success_url(self):
        return reverse('development:secureasset-detail', kwargs={'pk': self.object.pk})


class DevelopmentAssetUpdateView(NavContextMixin, HelpContextMixin, assets.views.SecureAssetUpdateView):
    permission_required = 'development.change_developmentasset'
    model = DevelopmentAsset
    form_class = DevelopmentAssetForm
    nav_url = reverse_lazy('development:secureasset-list')
    page_help_name = 'development:secureasset-create'
    template_name = 'development/developmentasset_form.html'
    edit_object_delete_perm = 'development:delete_developmentasset'

    def get_edit_object_cancel_url(self):
        return reverse('development:secureasset-detail', kwargs={'pk': self.object.pk})

    def get_success_url(self):
        return reverse('development:secureasset-detail', kwargs={'pk': self.object.pk})


class DevelopmentAssetDeleteView(NavContextMixin, HelpContextMixin, assets.views.SecureAssetDeleteView):
    permission_required = 'development.delete_developmentasset'
    page_help_name = 'development:secureasset-create'
    nav_url = reverse_lazy('development:secureasset-list')

    def get_context_data(self, **kwargs):
        context = super(DevelopmentAssetDeleteView, self).get_context_data(**kwargs)

        # This view thinks this is just a secureasset, get the developmentasset:
        development_asset = assets.models.SecureAsset.objects.get_subclass(pk=self.object.pk)
        context['cancel_url'] = reverse('development:secureasset-detail', kwargs={'pk': development_asset.pk})
        context['nav_url'] = reverse('development:secureasset-list')
        return context

    def get_success_url(self):
        return reverse('development:secureasset-list')


class DevelopmentProjectAssetDetailView(NavContextMixin, HelpContextMixin, assets.views.SecureAssetDetailView):
    model = DevelopmentProjectAsset
    template_name = 'development/developmentprojectasset_detail.html'
    page_help_name = 'development:project-secureasset-detail'
    nav_url = reverse_lazy('development:project-list')

    def get_context_data(self, **kwargs):
        context = super(DevelopmentProjectAssetDetailView, self).get_context_data(**kwargs)
        context['edit_url'] = reverse('development:project-secureasset-update',
                                      kwargs={'pk': self.object.pk, 'project_pk': self.object.project.pk})
        context['delete_url'] = reverse('development:project-secureasset-delete',
                                        kwargs={'pk': self.object.pk, 'project_pk': self.object.project.pk})
        return context


class DevelopmentProjectAssetCreateView(NavContextMixin, HelpContextMixin, assets.views.SecureAssetCreateView):
    permission_required = "development.add_developmentprojectasset"
    model = DevelopmentProjectAsset
    form_class = DevelopmentProjectAssetForm
    page_help_name = 'development:project-secureasset-create'
    template_name = 'development/developmentprojectasset_form.html'
    nav_url = reverse_lazy('development:project-list')

    def get_edit_object_cancel_url(self):
        return reverse('development:project-detail', args=[self.kwargs.get('project_pk')])

    # Add devt project id to the form's kwargs:
    def get_form_kwargs(self):
        kwargs = super(DevelopmentProjectAssetCreateView, self).get_form_kwargs()
        kwargs['dev_project_id'] = self.kwargs.get('project_pk', None)
        return kwargs

    def get_success_url(self):
        return reverse('development:project-detail', kwargs={'pk': self.object.project.pk}) + "#tab-files"


class DevelopmentProjectAssetUpdateView(NavContextMixin, HelpContextMixin, assets.views.SecureAssetUpdateView):
    permission_required = 'development.change_developmentprojectasset'
    model = DevelopmentProjectAsset
    form_class = DevelopmentProjectAssetForm
    page_help_name = 'development:project-secureasset-create'
    template_name = 'development/developmentprojectasset_form.html'
    edit_object_delete_perm = 'development:delete_developmentprojectasset'
    nav_url = reverse_lazy('development:project-list')

    def get_edit_object_cancel_url(self):
        return reverse('development:project-secureasset-detail',
                       args=[self.kwargs.get('project_pk'), self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('development:project-secureasset-delete',
                       args=[self.kwargs.get('project_pk'), self.object.id])

    # Add devt project id to the form's kwargs:
    def get_form_kwargs(self):
        kwargs = super(DevelopmentProjectAssetUpdateView, self).get_form_kwargs()
        kwargs['dev_project_id'] = self.kwargs.get('project_pk', None)
        return kwargs

    def get_success_url(self):
        return reverse('development:project-secureasset-detail', kwargs={'pk': self.object.pk, 'project_pk': self.object.project.pk})


class DevelopmentProjectAssetDeleteView(NavContextMixin, HelpContextMixin, assets.views.SecureAssetDeleteView):
    permission_required = 'development.delete_developmentprojectasset'
    page_help_name = 'development:project-secureasset-create'
    nav_url = reverse_lazy('development:project-list')

    def get_context_data(self, **kwargs):
        context = super(DevelopmentProjectAssetDeleteView, self).get_context_data(**kwargs)

        # This view thinks this is just a secureasset, get the developmentasset:
        development_asset = assets.models.SecureAsset.objects.get_subclass(id=self.object.id)
        context['cancel_url'] = reverse('development:project-detail', kwargs={'pk': development_asset.project.pk})
        context['nav_url'] = reverse('development:project-list')
        return context

    def get_success_url(self):
        # This view thinks this is just a secureasset, get the developmentasset:
        development_asset = assets.models.SecureAsset.objects.get_subclass(id=self.object.id)
        return reverse('development:project-detail', kwargs={'pk': development_asset.project.id}) + "#tab-files"


class DevelopmentSpatialReportFormView(GenericSpatialReportFormView):
    template_name = 'development/development_spatialreport_form.html'
    form_class = DevelopmentSpatialReportForm

    def get_edit_object_cancel_url(self):
        return reverse('development:project-detail', args=[self.project.id])

    def get_context_data(self, **kwargs):
        context = super(DevelopmentSpatialReportFormView, self).get_context_data(**kwargs)
        context['project'] = self.project
        return context

    def form_valid(self, form):
        name = form.cleaned_data['name']
        distance_cap = form.cleaned_data['distance_cap']
        report_on = GISLayerMaster.objects.filter(pk__in=self.project.developmentgislayer_set.values("pk"))

        item_id_list = []
        for item in form.cleaned_data['layers']:

            try:
                item_id_list.append(int(item))
            except ValueError:
                if item == 'development_projects':
                    for layer in DevelopmentGISLayer.objects.exclude(pk__in=self.project.developmentgislayer_set.values("pk")):
                        item_id_list.append(layer.pk)

        if item_id_list:
            item_layer_set = GISLayerMaster.objects.filter(pk__in=item_id_list)
        else:
            item_layer_set = GISLayerMaster.objects.none()

        try:
            report = SpatialReport.objects.get(name=name, distance_cap=distance_cap, report_on=report_on)
            report_items_layers = GISLayerMaster.objects.filter(pk__in=report.spatialreportitem_set.values("layer__pk"))

            if set(item_layer_set) != set(report_items_layers):
                report = self.create_new_report(name, distance_cap, report_on, item_layer_set)

        except SpatialReport.DoesNotExist:
            report = self.create_new_report(name, distance_cap, report_on, item_layer_set)

        self.report = report
        return super(DevelopmentSpatialReportFormView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(DevelopmentProject, id=self.kwargs.get('project_pk', None))
        return super(DevelopmentSpatialReportFormView, self).dispatch(request, *args, **kwargs)


class SERFormView(FileResponseMixin, FormView):
    """
    Presents the SER Form and returns formatted XML.
    Any fields let blank will be omitted from the XML.
    """
    form_class = SERForm
    template_name = 'development/ser_form.html'
    filename = 'cedar8-ser-{date}.xml'

    def form_valid(self, form):
        # data = form.cleaned_data
        data = {}

        # This will grab and send only the changed data
        # Change "form.changed_data" to "form.cleaned_data" to get
        # all form fields, empty or not.
        for field in form.changed_data:
            data[field] = form.cleaned_data[field]

        rendered_data = XMLRenderer().render(data)

        # update the filename and return:
        self.filename = self.filename.format(date=datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

        return self.xml_file_response(rendered_data)

    def get_initial_from_upload(self):
        '''
        Called by get_form in case a xml file was uploaded; initial
        form values should come from there instead.
        :return:
        '''
        if self.request.FILES:
            if self.request.FILES['template_document']:
                return XMLParser().parse(self.request.FILES['template_document'])

        raise AttributeError("get_initial_from_upload not possible.")

    def get_form(self, form_class=None):
        """
        Returns an instance of the form to be used in this view.
        Override to check if an xml file was uploaded. Create a fresh
        form instance from that if so.
        """
        if form_class is None:
            form_class = self.get_form_class()

        if self.is_upload_view():
            return form_class(**{'initial': self.get_initial_from_upload()})
        else:
            return form_class(**self.get_form_kwargs())

    def is_upload_view(self):
        '''
        Checkes the request for presence of the "template_document". If
        present it means that a user has upload an XML document template.
        :return: True/False
        '''
        if self.request.FILES:
            if self.request.FILES['template_document']:
                return True
        return False


# todo: Make the FileNo CRUD a little more useful
class FileNoCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    model = FileNo
    form_class = FileNoForm
    page_help_name = 'development:fileno-create'
    edit_object_cancel_url = reverse_lazy('development:project-list')

    @method_decorator(permission_required('development.add_fileno', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(FileNoCreateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("development:project-list")


class FileNoUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    model = FileNo
    form_class = FileNoForm
    page_help_name = 'development:fileno-update'
    edit_object_delete_perm = 'development:delete_fileno'
    edit_object_cancel_url = reverse_lazy('development:project-list')

    def get_edit_object_delete_url(self):
        return reverse('development:fileno-delete', self.object.pk)

    @method_decorator(permission_required('development.change_fileno', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(FileNoUpdateView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("development:project-list")


class FileNoDeleteView(HelpContextMixin, DeleteView):
    model = FileNo
    form_class = FileNoForm
    page_help_name = 'development:fileno-delete'

    @method_decorator(permission_required('development.delete_fileno', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(FileNoDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("development:project-list")


class SecureAssetsDashboardView(assets.views.SecureAssetsDashboardView):
    template_name = 'development/secureasset_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(SecureAssetsDashboardView, self).get_context_data(**kwargs)
        context['create_asset_url'] = reverse('development:secureasset-create')
        context['secureasset_search_url'] = reverse('development:secureasset-search')
        context['secureasset_list_url'] = reverse('development:secureasset-list')
        context['documents_count'] = DevelopmentAsset.objects.count()
        return context


class SecureAssetListView(cedar.mixins.NavContextMixin, assets.views.SecureAssetListView):
    nav_url = reverse_lazy('development:secureasset-list')
    template_name = 'development/secureasset_list.html'
    asset_model = DevelopmentAsset

    def get_context_data(self, **kwargs):
        context = super(SecureAssetListView, self).get_context_data(**kwargs)
        context['total_files'] = self.asset_model.objects.count()
        context['secure_asset_list_ajax_url'] = reverse_lazy('development:api:secure-assets-list')
        return context


class SecureAssetSearchView(cedar.mixins.NavContextMixin, HelpContextMixin, assets.views.SecureAssetSearchView):
    page_help_name = 'development:file-search'
    nav_url = reverse_lazy('development:secureasset-list')

    def get_queryset(self):
        sqs = super(SecureAssetSearchView, self).get_queryset().models(DevelopmentAsset)
        return sqs


class SecureAssetSearchViewCSV(assets.views.SecureAssetSearchViewCSV):
    pass


##################################################################################################
# Rest API:
##################################################################################################
class DevelopmentProjectFilterSet(filters.FilterSet):
    has_geom = django_filters.MethodFilter()
    filing_code = django_filters.CharFilter(name='filing_code__code')
    comments_contain = django_filters.CharFilter(name='comments__comment', method='filter_comments')
    file_number = django_filters.CharFilter(name='fileno__file_number')
    people = django_filters.ModelMultipleChoiceFilter(queryset=Person.objects.all(), method='filter_people')
    organizations = django_filters.ModelMultipleChoiceFilter(queryset=Organization.objects.all(), method='filter_organizations')
    tag = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(), method='filter_tags')

    class Meta:
        model = DevelopmentProject
        fields = ['id', 'highlight', 'status', 'tag', 'people', 'organizations', 'has_geom', 'consultation_stage', 'filing_code',
                  'comments_contain', 'file_number']

    def filter_has_geom(self, queryset, value):
        #  Get related layers, exclude layers with no features.
        layers = DevelopmentGISLayer.objects.annotate(feature_count=Count('gisfeature')).exclude(feature_count=0)
        projects_pks_with_layers = list(map(lambda x: x.project.pk, filter(lambda y: y.project, layers)))
        
        if value == 'yes':
            queryset = queryset.filter(pk__in=projects_pks_with_layers)
        else:
            queryset = queryset.exclude(pk__in=projects_pks_with_layers)

        return queryset

    def filter_comments(self, queryset, name, value):
        if value:
            # Need to use a list of project ids to filter comments because of
            # the weird way in which comments are constructed..
            matched_comments = ThreadedComment.objects.filter(
                comment__icontains=value,
                content_type=ContentType.objects.get_for_model(DevelopmentProject)
            )
            matched_comment_project_ids = [x.object_pk for x in matched_comments]

            queryset = queryset.filter(id__in=matched_comment_project_ids)
        return queryset

    def filter_people(self, queryset, _, value):
        if value:
            queryset = queryset.filter(
                Q(cedar_assessor__in=value) |
                Q(government_contact__in=value) |
                Q(company_contact__in=value)).distinct()
        return queryset

    def filter_organizations(self, queryset, _, value):
        if value:
            queryset = queryset.filter(
                Q(company__in=value) |
                Q(cedar_assessor__organizations__in=value) |
                Q(government_contact__organizations__in=value) |
                Q(company_contact__organizations__in=value)).distinct()
        return queryset

    def filter_tags(self, queryset, _, value):
        if value:
            queryset = queryset.filter(tags__in=value)
        return queryset


class DevelopmentProjectViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DevelopmentProjectSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('id', 'cedar_project_name', 'cedar_project_code_q', 'consultation_stage__stage_name',
                     'company__name', 'description')
    filter_class=DevelopmentProjectFilterSet
    ordering_fields = ['id', 'cedar_project_name', 'status', 'filing_code__code', 'company__name', 'initial_date',
                       'due_date', 'initial_date_null', 'due_date_null']
    ordering = ('-id',)  # Default sort field.

    def get_queryset(self):
        """
        get_queryset modified to query all any Person objects related to the project
         - because they are spread over several fields it was complicating
            the filter_fields set up. This looks for a url parameter "personid" and pre-filters
            based on that.
        """
        queryset = DevelopmentProject.objects.all()
        personid = self.request.query_params.get('personid', None)

        if personid is not None:
            queryset = queryset.filter(
                Q(cedar_assessor__in=[personid, ]) |
                Q(government_contact__in=[personid, ]) |
                Q(company_contact__in=[personid, ])).distinct()

        # TODO Solve the multiple aggregations problem
        # https://docs.djangoproject.com/en/1.10/topics/db/aggregation/#combining-multiple-aggregations
        # TODO If we don't solve the multiple aggregations problem them try solving the poorly performing distinct count
        # While it's nice to have sorting on these annotated columns, the following annotations perform TERRIBLY
        # until we solve one of the todos above, these must remain calculated on the front end in the serializer.
        # Add num_files, num_comms, and num_comments to the queryset so they can be used with sorting
        # queryset = queryset.annotate(
        #     num_files=Count('developmentprojectasset', distinct=True),
        #     num_comms=Count('comm_relationships', distinct=True)
        # )

        # for some reason trying to follow this pattern with comments causes issues finding the
        # threadedcomment.object_pk field.
        # queryset = queryset.annotate(num_comments=Count('comments'))

        queryset = queryset.annotate(initial_date_null=Case(
            When(initial_date__isnull=True, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ))

        queryset = queryset.annotate(due_date_null=Case(
            When(due_date__isnull=True, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ))

        return queryset


class DevelopmentGISLayerViewSet(GISLayerViewSet):
    queryset = DevelopmentGISLayer.objects.all()


class DevelopmentGISLayerMasterListAPIView(GISLayerMasterListAPIView):
    queryset = DevelopmentGISLayer.objects.all()

    # def get_queryset(self):
    #     return DevelopmentGISLayer.objects.filter(Q(layer_type='Development')| Q(layer_type='Misc.'))


class DevelopmentGISLayerFeatureViewSet(GISFeatureViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_fields = ('name', 'layer')
    search_fields = ('name',)
    ordering_fields = '__all__'
    ordering = ('name',)
    geojson_serializer_class = DevelopmentGISLayerFeatureGeoJSONSerializer

    def get_queryset(self):
        queryset = super(DevelopmentGISLayerFeatureViewSet, self).get_queryset()
        prj_id = self.request.query_params.get('project', None)
        if prj_id:
            layers = DevelopmentGISLayer.objects.filter(project=prj_id)
            queryset = queryset.filter(layer__in=layers)
        return queryset


class DevelopmentAssetViewSet(assets.views.SecureAssetViewSet):
    def get_queryset(self):
        return DevelopmentAsset.objects.all()
