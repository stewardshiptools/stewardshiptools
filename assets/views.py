import magic
import csv
import itertools

from django.conf import settings

from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, TemplateView, View
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required, user_passes_test
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_str
from django.forms import inlineformset_factory

from rest_framework import viewsets, filters
from rest_framework.reverse import reverse, reverse_lazy
from rest_framework import permissions
from rest_framework.response import Response

from haystack.generic_views import SearchView

from assets import search_utils
from .forms import SecureAssetSearchForm, MetaDocumentSecureAssetForm, MetaDocumentAssetForm, SecureAssetForm, AssetForm, FileSettingForm
from .models import SecureAsset, Asset, MetaDocumentAsset, MetaDocumentSecureAsset
from .serializers import SecureAssetSerializer

from .search_backend import CustomSearchQuerySet

from cedar_settings.models import GeneralSetting

from cedar.mixins import CSVResponseMixin, NavContextMixin, EditObjectMixin

from braces.views import PermissionRequiredMixin, LoginRequiredMixin, MultiplePermissionsRequiredMixin

# See re mime types:
# http://stackoverflow.com/questions/43580/how-to-find-the-mime-type-of-a-file-in-python


# TODO: Switch the permission check done in-view to the permission decorator. Make sure there is no login_url redirect weirdness.
# @permission_required('assets.view_secureasset', raise_exception=True)

class GetFileViewAbstract(View):
    '''
    This supersedes serve_private_file, download_private_file.
    This view should not be called directly.
    Requires a class-level variable "asset_class" to be set.
    Defined only GET http method.
    '''
    # asset_class = SecureAsset
    def get_object(self):
        assert self.asset_class
        return self.asset_class.objects.get(id=self.kwargs['file_id'])

    def get(self, request, *args, **kwargs):
        '''
        GET - the only http method defined by this class. If you want a straight download
        then set as_attachment = True.
        :param request:
        :param args:
        :param kwargs: file_id: not optional. as_attachment: optional.
        :return: returns a file via X-SendFile either as an attachment or inline.
        '''

        # make sure the View has been implemented properly:
        assert self.asset_class

        as_attachment = kwargs.pop('as_attachment', False)

        file_id = kwargs.pop('file_id', None)
        assert file_id is not None

        asset_obj = get_object_or_404(self.asset_class, id=file_id)
        full_path = asset_obj.file.path
        content_type = magic.from_file(full_path, mime=True)
        response = HttpResponse(content_type=content_type)

        if as_attachment:
            response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(asset_obj.name)
        else:
            response['Content-Disposition'] = 'inline'

        response['X-Sendfile'] = smart_str(full_path)
        return response


class GetSecureFileView(PermissionRequiredMixin, GetFileViewAbstract):
    asset_class = SecureAsset
    permission_required = "assets.view_secureasset"
    raise_exception = True


class GetInsecureFileView(GetFileViewAbstract):
    asset_class = Asset


class SecureAssetsDashboardView(TemplateView):
    template_name = 'assets/secureasset_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(SecureAssetsDashboardView, self).get_context_data(**kwargs)
        context['secureasset_search_url'] = reverse('assets:secureasset-search')
        context['secureasset_list_url'] = reverse('assets:secureasset-list')
        context['documents_count'] = SecureAsset.objects.count()
        return context


class SecureAssetSearchView(SearchView):
    '''
    There is a glaring problem with this view that I don't have time to address:
        - When a search is called, this view (or something below it) is calling
            the same search on solr 4 times in a row. May be the paginator, dunno.
            Watch the debug window for calls to solr.
    '''
    template_name = 'assets/secureasset_search.html'
    # load_all = False
    form_class = SecureAssetSearchForm
    queryset = CustomSearchQuerySet()  # Comment this out to go back to default --> Make sure to add () so it instantiates. Pain if not.
    return_as_csv = False

    def get_object_list_subtexts(self, context):
        # Paginated the queryset so we can process the text blocks of only
        # the current page:
        paginated = self.paginate_queryset(self.get_queryset(), GeneralSetting.objects.get('assets__default_search_results_per_page'))
        paginated_queryset = paginated[2]  # Seems to be the paginated query set.
        return search_utils.get_subtexts(paginated_queryset)

    def get_queryset(self):
        '''
        When you subclass this view, be sure to specify the asset model
        you want to query, otherwise it will query everything:
            eg. sqs = super(SecureAssetSearchView, self).get_queryset().models(HeritageAsset)
        :return:
        '''

        # TODO: Do something here to filter OUT asset types that require permission to view
        sqs = super(SecureAssetSearchView, self).get_queryset()

        # If wanted, we can return nothing if user not authorized:
        # if not self.request.user.has_perm('assets.search_secureasset'):
        #     return queryset.none()
        # else:
        #     return queryset
        return sqs

    def get_context_data(self, *args, **kwargs):
        context = super(SecureAssetSearchView, self).get_context_data(*args, **kwargs)
        context['object_list_subtexts'] = self.get_object_list_subtexts(context)
        self.kwargs.update({self.page_kwarg: kwargs.get(self.page_kwarg)})

        return context

    # The haystack searchform overrode the get_form_kwargs method and messed it up.
    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        elif self.request.method == 'GET':
            kwargs.update({
                'initial': self.request.GET,
            })
        kwargs.update({'searchqueryset': self.get_queryset()})

        return kwargs

    def form_valid(self, form):
        self.return_as_csv = form.cleaned_data.get("return_as_csv")

        # The paginator is not really set up to use a get, unless you
        # set a class-level kwarg with the page number BEFORE the paginator
        # is called -- calling form.search triggers the paginator so
        # this has to come first.
        self.kwargs.update({self.page_kwarg: form.cleaned_data.get('page')})

        self.queryset = form.search()
        context = self.get_context_data(**{
            self.form_name: form,
            'query': form.cleaned_data.get(self.search_field),
            'object_list': self.queryset,
        })

        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):

        if not self.return_as_csv or self.return_as_csv == 'no':
            # Return normal template response:
            return super(SecureAssetSearchView, self).render_to_response(context, **response_kwargs)
        else:
            # Build CSV Response:
            return self.make_csv_response(context, **response_kwargs)

    def make_csv_response(self, context, **response_kwargs):
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

        for result in search_qs:
            count += 1
            subtext_num = 0

            filename = result.object.name

            for subtext in subtexts[result.pk]:
                subtext_num += 1
                row = [
                    filename,
                    self.request.build_absolute_uri(result.object.url),
                    str(result.object.source_string),
                    self.request.build_absolute_uri(result.object.source_url),
                    subtext_num,
                    subtext
                ]
                writer.writerow(row)

        return response

    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(SecureAssetSearchView, self).dispatch(request, *args, **kwargs)


class SecureAssetSearchViewCSV(CSVResponseMixin, SecureAssetSearchView):
    template_name = 'search/search.html'  # needs a template, but it is not actually used.

    def post(self, request, *args, **kwargs):
        super(SecureAssetSearchViewCSV, self).post(request, *args, **kwargs)
        data = (('hello', 'world'), ('foo', 'bar'))
        return self.render_to_csv(data)

    def get(self, request, *args, **kwargs):
        data = (('hello', 'world'), ('foo', 'bar'))
        return self.render_to_csv(data)


class SecureAssetListView(TemplateView):
    template_name = 'assets/secureasset_list.html'
    asset_model = SecureAsset

    def get_context_data(self, **kwargs):
        context = super(SecureAssetListView, self).get_context_data(**kwargs)
        context['total_files'] = self.asset_model.objects.count()
        context['secure_asset_list_ajax_url'] = reverse_lazy('assets:api:secure-assets-list')

        context['fields'] = [
            ['name', {
                'verbose_name': "File name",
                'type': 'link',
                'url_field': 'url'
            }],
            ['modified', 'Date modified'],
            ['file_size', 'File size']
        ]

        context['sort_options'] = [
            ['name', 'Name'],
            ['id', 'ID']
        ]

        return context


class SecureAssetCreateView(EditObjectMixin, PermissionRequiredMixin, CreateView):
    permission_required = "assets.add_secureasset"
    raise_exception = True
    include_metadocument = True
    model = SecureAsset
    metadocument_formset = inlineformset_factory(SecureAsset, MetaDocumentSecureAsset, form=MetaDocumentSecureAssetForm, can_delete=False, extra=1, max_num=1)
    template_name = 'assets/genericasset_form.html'
    form_class = SecureAssetForm
    edit_object_cancel_url = reverse_lazy('assets:secureasset-list')

    def get_success_url(self):
        return reverse("assets:secureasset-detail", args=[self.object.id])

    def form_valid(self, form):
        response = super(SecureAssetCreateView, self).form_valid(form)
        if self.request.method == 'POST':
            if self.include_metadocument:
                formset = self.metadocument_formset(self.request.POST, self.request.FILES, instance=self.object)
                if formset.is_valid():
                    formset.save()
        return response

    def get_context_data(self, **kwargs):
        context = super(SecureAssetCreateView, self).get_context_data(**kwargs)
        if self.include_metadocument:
            context['metadocument_formset'] = self.metadocument_formset()
        return context


class SecureAssetUpdateView(EditObjectMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "assets.change_secureasset"
    raise_exception = True
    include_metadocument = True

    model = SecureAsset
    metadocument_formset = inlineformset_factory(SecureAsset, MetaDocumentSecureAsset, form=MetaDocumentSecureAssetForm, can_delete=False, extra=1, max_num=1)
    template_name = 'assets/genericasset_form.html'
    form_class = SecureAssetForm

    edit_object_delete_perm = 'assets.delete_secureasset'

    def get_edit_object_cancel_url(self):
        return reverse_lazy('assets:secureasset-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse_lazy('assets:secureasset-delete', args=[self.object.id])

    def get_success_url(self):
        return reverse("assets:secureasset-detail", args=[self.object.id])

    def form_valid(self, form):
        response = super(SecureAssetUpdateView, self).form_valid(form)
        if self.request.method == 'POST':
            if self.include_metadocument:
                formset = self.metadocument_formset(self.request.POST, self.request.FILES, instance=self.object)
                if formset.is_valid():
                    formset.save()

        return response

    def get_context_data(self, **kwargs):
        context = super(SecureAssetUpdateView, self).get_context_data(**kwargs)
        if self.include_metadocument:
            context['metadocument_formset'] = self.metadocument_formset(instance=self.object)
        return context


class SecureAssetDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "assets.view_secureasset"
    raise_exception = True

    model = SecureAsset
    template_name = 'assets/genericasset_detail.html'


class SecureAssetDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "assets.delete_secureasset"
    raise_exception = True

    model = SecureAsset
    template_name = 'assets/genericasset_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super(SecureAssetDeleteView, self).get_context_data(**kwargs)
        context['cancel_url'] = reverse("assets:secureasset-detail", args=[self.object.id])
        context['nav_url'] = ''  # reverse("assets:secureasset-details", kwargs={'file_id': self.object.id})
        return context

    def get_success_url(self):
        '''
        TODO: Make this redirect to something useful.
        :return:
        '''
        return reverse('assets:secureasset-dashboard')


class SecureAssetManageView(TemplateView):
    template_name = 'assets/secureasset_manage.html'


#######################################################
# INSECURE ASSETS. Initially will be be used for setting the
# background cedar splash.

class AssetCreateView(EditObjectMixin, LoginRequiredMixin, MultiplePermissionsRequiredMixin, CreateView):
    permissions = {
        "all": ("assets.add_asset",),
        # "any": ("blog.delete_post", "user.change_user")
    }
    raise_exception = True

    model = Asset
    metadocument_formset = inlineformset_factory(Asset, MetaDocumentAsset, form=MetaDocumentAssetForm, can_delete=False,
                                                 extra=1, max_num=1)
    template_name = 'assets/genericasset_form.html'
    form_class = AssetForm

    # edit_object_cancel_url = reverse_lazy('assets:asset-list')

    def get_success_url(self):
        return reverse("assets:secureasset-detail", args=[self.object.id])

    def form_valid(self, form):
        response = super(AssetCreateView, self).form_valid(form)
        if self.request.method == 'POST':
            formset = self.metadocument_formset(self.request.POST, self.request.FILES, instance=self.object)
            if formset.is_valid():
                formset.save()

        return response

    def get_context_data(self, **kwargs):
        context = super(AssetCreateView, self).get_context_data(**kwargs)
        context['metadocument_formset'] = self.metadocument_formset()
        return context


class AssetUpdateView(EditObjectMixin, PermissionRequiredMixin, UpdateView):
    permission_required = "assets.change_asset"
    raise_exception = True

    model = Asset
    metadocument_formset = inlineformset_factory(Asset, MetaDocumentAsset, form=MetaDocumentAssetForm, can_delete=False,
                                                 extra=1, max_num=1)
    template_name = 'assets/genericasset_form.html'
    form_class = AssetForm

    edit_object_delete_perm = 'assets.delete_asset'

    # def get_edit_object_cancel_url(self):
    #     return reverse_lazy('assets:asset-detail', args=[self.object.id])
    #
    # def get_edit_object_delete_url(self):
    #     return reverse_lazy('assets:asset-delete', args=[self.object.id])

    def get_success_url(self):
        return reverse("assets:secureasset-detail", args=[self.object.id])

    def form_valid(self, form):
        response = super(AssetUpdateView, self).form_valid(form)
        if self.request.method == 'POST':
            formset = self.metadocument_formset(self.request.POST, self.request.FILES, instance=self.object)
            if formset.is_valid():
                formset.save()

        return response

    def get_context_data(self, **kwargs):
        context = super(AssetUpdateView, self).get_context_data(**kwargs)
        context['metadocument_formset'] = self.metadocument_formset(instance=self.object)
        return context


class AssetDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "assets.view_asset"   # this probablye isn't necessary
    raise_exception = True

    model = Asset
    template_name = 'assets/genericasset_detail.html'

    def get_context_data(self, **kwargs):
        context = super(AssetDetailView, self).get_context_data(**kwargs)
        context['edit_url'] = reverse('assets:secureasset-update', kwargs={'pk': self.object.pk})
        context['delete_url'] = reverse('assets:secureasset-delete', kwargs={'pk': self.object.pk})
        return context


class AssetDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "assets.delete_asset"
    raise_exception = True

    model = Asset
    template_name = 'assets/genericasset_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super(AssetDeleteView, self).get_context_data(**kwargs)
        context['cancel_url'] = reverse("assets:secureasset-detail", args=[self.object.id])
        context['nav_url'] = ''  # reverse("assets:secureasset-details", kwargs={'file_id': self.object.id})
        return context

    def get_success_url(self):
        '''
        TODO: Make this redirect to something useful.
        :return:
        '''
        return reverse('assets:secureasset-list')


class SetFileSettingView(AssetCreateView):
    permissions = {
        "all": ("assets.add_asset", "cedar_settings.change_generalsetting"),
    }
    raise_exception = True

    template_name = 'assets/genericassetfilesetting_form.html'
    form_class = FileSettingForm

    def get_context_data(self, **kwargs):
        context = super(SetFileSettingView, self).get_context_data(**kwargs)
        context['hide_meta_doc'] = True
        return context

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(SetFileSettingView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('home')

###############################################
# REST API
###############################################


class SecureAssetViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    API Endpoing that lists all assets - Secure ONLY for now.
    '''
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('id', )
    serializer_class = SecureAssetSerializer

    search_fields = ('name',
                     'asset_type__type_of_asset',
                     'modified',
                     'comment',
                     "meta_document__contributor",
                     "meta_document__coverage",
                     "meta_document__creator",
                     "meta_document__date",
                     "meta_document__description",
                     "meta_document__format",
                     "meta_document__identifier",
                     "meta_document__language",
                     "meta_document__publisher",
                     "meta_document__relation",
                     "meta_document__rights",
                     "meta_document__source",
                     "meta_document__subject",
                     "meta_document__title",
                     "meta_document__type",
                     )

    ordering_fields = ('name', 'id')

    def get_queryset(self):
        return SecureAsset.objects.all()
