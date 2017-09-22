from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView, View
from django.views.generic.detail import SingleObjectMixin, ContextMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Value, BooleanField, When, Case
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory, modelformset_factory
from django.apps import apps

from rest_framework import viewsets, filters
from rest_framework.reverse import reverse as drf_reverse
from rest_framework import permissions

from haystack.generic_views import SearchView
from haystack.query import SQ, Raw

import django_filters

from tags.models import Tag

from braces.views import LoginRequiredMixin, PermissionRequiredMixin

from heritage.models import HeritageAsset, Place

from library.models import Item, ItemAssetRelation, DublinCore, Holdings, Review, ResearcherNotes, Confidentiality, CollectionTag, CaseBrief, \
    CaseBriefTag, Synthesis, SynthesisItem, SynthesisCategory, PersonMentionedTag, PersonMentionedTaggedItem,  ItemType
from library.forms import ItemForm, DublinCoreForm, HoldingsForm, ReviewForm, ResearcherNotesForm, ConfidentialityForm, CollectionTagForm, \
    CaseBriefForm, SynthesisForm, SynthesisItemForm, LibrarySearchForm, PersonMentionedTagForm
from library.serializers import ItemSerializer, CollectionTagSerializer, CaseBriefSerializer, SynthesisSerializer,\
    PersonMentionedTagSerializer
from library.search_backend import CustomSearchQuerySet
from library import search_utils

from help.mixins import HelpContextMixin
from cedar.mixins import NavContextMixin, EditObjectMixin
from security.views import UserHasSecurityLevelQuerySetFilterMixin, UserHasObjectSecurityClearanceMixin

from ecosystems.models import PlantTag, AnimalTag

from cedar_settings.models import GeneralSetting


def get_item_list_context(request):
    context = dict()

    context['ajax_url'] = drf_reverse('{namespace}:api:item-list'.format(namespace=request.resolver_match.namespace))

    context['fields'] = [
        ['prefixed_id', 'Item ID'],
        ['name', {
            'verbose_name': 'Name',
            'type': 'link',
            'url_field': 'url'
        }],
        ['collections', {
            'verbose_name': 'Collections',
            'type': 'link-list'
        }],
        ['cataloger_name', {
            'verbose_name': 'Cataloger',
            'type': 'link',
            'url_field': 'cataloger_url'
        }],
        ['reviewer_name', {
            'verbose_name': 'Reviewer',
            'type': 'link',
            'url_field': 'reviewer_url'
        }],
        ['item_type', 'Type'],
        ['creation_date', 'Creation Date'],
    ]

    context['sort_options'] = [
        ['id', 'ID'],
        ['name', 'Name'],
        ['created_date_null,dublin_core__date', 'Creation date']
    ]

    context['filters'] = [
        {
            'name': 'date_on',
            'verbose_name': 'Created on',
            'id': 'date-on-filter',
            'component': 'date',
            'default_value': '',
            'select_years': 800,  # These library items can be pretty old.  Big number!
            'limit_years': 1,  # A boolean 0/1 true means to limit years to the current date.
        },
        {
            'name': 'date_start',
            'verbose_name': 'Created after',
            'id': 'date-start-filter',
            'component': 'date',
            'default_value': '',
            'select_years': 800,  # These library items can be pretty old.  Big number!
            'limit_years': 1,  # A boolean 0/1 true means to limit years to the current date.
        },
        {
            'name': 'date_end',
            'verbose_name': 'Created before',
            'id': 'date-end-filter',
            'component': 'date',
            'default_value': '',
            'select_years': 800,  # These library items can be pretty old.  Big number!
            'limit_years': 1,  # A boolean 0/1 true means to limit years to the current date.
        },
        {
            'name': 'item_type',
            'verbose_name': 'Item types',
            'id': 'item-type-filter',
            'options': list(
                map(lambda x: [x.id, x.name],
                    ItemType.objects.all()
                    )
            ),
            'default_value': [],
            'component': "select",
            'labelClasses': "active",
            'select_type': 'select2',
            'is_multiple': "true"
        },
        {
            'name': 'tag',
            'verbose_name': 'Tags',
            'id': 'tags-filter',
            'options': list(
                map(lambda x: [x.id, x.name],
                    Tag.objects.filter(
                        tags_taggeditem_items__content_type=ContentType.objects.get_for_model(Item)
                    ).distinct()
                    )
            ),
            'default_value': [],
            'initial_value': request.GET.getlist('tag', 'undefined'),
            'component': "select",
            'labelClasses': "active",
            'select_type': 'select2',
            'is_multiple': "true"
        },
        {
            'name': 'collection',
            'verbose_name': 'Collections',
            'id': 'collections-filter',
            'options': list(
                map(lambda x: [x.id, x.name],
                    CollectionTag.objects.all()
                    )
            ),
            'default_value': [],
            'component': "select",
            'labelClasses': "active",
            'select_type': 'select2',
            'is_multiple': "true"
        },
        {
            'name': 'personmentioned',
            'verbose_name': 'People Mentioned',
            'id': 'personmentioned-filter',
            'options': list(
                map(lambda x: [x.id, x.name],
                    PersonMentionedTag.objects.all()
                    )
            ),
            'default_value': [],
            'component': "select",
            'labelClasses': "active",
            'select_type': 'select2',
            'is_multiple': "true"
        },
        {
            'name': 'plants',
            'verbose_name': 'Plants',
            'id': 'plants-filter',
            'options': list(
                map(lambda x: [x.id, x.name],
                    PlantTag.objects.all()
                    )
            ),
            'default_value': [],
            'component': "select",
            'labelClasses': "active",
            'select_type': 'select2',
            'is_multiple': "true"
        },
        {
            'name': 'animals',
            'verbose_name': 'Animals',
            'id': 'animals-filter',
            'options': list(
                map(lambda x: [x.id, x.name],
                    AnimalTag.objects.all()
                    )
            ),
            'default_value': [],
            'component': "select",
            'labelClasses': "active",
            'select_type': 'select2',
            'is_multiple': "true"
        },
        {
            'name': 'spreadsheet_id',
            'verbose_name': 'Spreadsheet ID',
            'id': 'spreadsheet-id-filter',
            'default_value': [],
            'component': 'text',

        },
    ]
    return context


class LibraryViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.belongs_to = self.get_belongs_to(request)
        self.default_asset_model = self.get_default_asset_model(kwargs)
        self.default_asset_modelform = self.get_default_asset_modelform(kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_belongs_to(self, request):
        # TODO: teasing out the belongs_to property is not as cool as it should be.
        # this is what I preferred but the bit with ":api:" started to throw
        # it all off. Hhhh.
        # return request.resolver_match.namespace
        return request.resolver_match.namespaces[0]

    def get_default_asset_model(self, kwargs):
            asset_model = kwargs.pop('default_asset_model').split(".")
            return apps.get_model(app_label=asset_model[0], model_name=asset_model[1])

    def get_default_asset_modelform(self, kwargs):
            return kwargs.pop('default_asset_modelform')


class LibraryListViewMixin(LibraryViewMixin):
    """
    Use on list views (api as well). Filters the queryset based on the belongs_to property.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(belongs_to=self.belongs_to)


class LibraryFormViewMixin(LibraryViewMixin):
    """
    Inserts the belongs_to value into form kwargs
    """

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {'belongs_to': self.belongs_to}
        )
        return initial


class LibraryDashboardView(NavContextMixin, HelpContextMixin, LibraryListViewMixin, TemplateView):
    """
    Main library access view
    """
    template_name = 'library/dashboard.html'
    page_help_name = 'library:dashboard'


class ItemListView(LoginRequiredMixin, UserHasSecurityLevelQuerySetFilterMixin, NavContextMixin, HelpContextMixin, LibraryListViewMixin, ListView):
    model = Item
    page_help_name = 'library:item-list'

    # This might be its own app, but to a large extent it lives inside heritage.
    nav_url = reverse_lazy('library:item-list')

    def get_context_data(self, **kwargs):
        context = super(ItemListView, self).get_context_data(**kwargs)
        context.update(get_item_list_context(self.request))

        return context


class ItemEditViewAbstract(LoginRequiredMixin, NavContextMixin, HelpContextMixin, LibraryViewMixin, TemplateView):
    """
    Item editing abstract view, subclassed by ItemCreateView and ItemUpdateView.

    Tricky, has (or will have) several inline forms.
    Handles the ugly logic that applies to both create/update views.

    Note: belongs_to will be passed in as a kwarg via the url conf.
    NOTE: The default asset form is passed through cedar/urls.py

    Maybe this:
    http://stackoverflow.com/questions/34251412/how-to-validate-mulitple-forms-in-a-single-formview-class-django/34275307#34275307
    """
    page_help_name = 'library:item-list'
    nav_url = reverse_lazy('heritage:dashboard')
    template_name = 'library/item_form.html'

    def _prepare_frm_item(self):
        kwargs = {
            'prefix': 'frm_item_px',
        }

        instance = None
        initial = None
        if hasattr(self, 'object'):  # update view will have this, createview will not.
            try:
                instance = self.object
            except Item.DoesNotExist:
                pass

        # set initial if this is a CREATE view.
        if not instance:
            initial = {
                'cataloger': self.request.user.id,
                'belongs_to': self.belongs_to
            }

        # Items are weird.  Need to add the user to the kwargs manually for the security app to be able to alter the
        # available level choices.
        kwargs.update({
            'instance': instance,
            'initial': initial,
            'user': self.request.user
        })

        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES
            })

        return ItemForm(**kwargs)

    def _prepare_frm_dublin_core(self):
        kwargs = {'prefix': 'frm_dublin_core_px'}

        instance = None
        if hasattr(self, 'object'):  # update view will have this, createview will not.
            try:
                instance = self.object.dublin_core
            except DublinCore.DoesNotExist:
                pass

        kwargs.update({'instance': instance, })

        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES
            })

        return DublinCoreForm(**kwargs)

    def _prepare_frm_holdings(self):
        kwargs = {'prefix': 'frm_holdings_px'}

        instance = None
        if hasattr(self, 'object'):  # update view will have this, createview will not.
            try:
                instance = self.object.holdings
            except Holdings.DoesNotExist:
                pass

        kwargs.update({'instance': instance, })

        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES
            })

        return HoldingsForm(**kwargs)

    def _prepare_frm_review(self):
        kwargs = {'prefix': 'frm_review_px'}

        instance = None
        if hasattr(self, 'object'):  # update view will have this, createview will not.
            try:
                instance = self.object.review
            except Review.DoesNotExist:
                pass

        kwargs.update({'instance': instance, })

        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES
            })

        return ReviewForm(**kwargs)

    def _prepare_frm_researcher_notes(self):
        kwargs = {'prefix': 'frm_researcher_notes_px'}

        instance = None
        if hasattr(self, 'object'):  # update view will have this, createview will not.
            try:
                instance = self.object.researcher_notes
            except ResearcherNotes.DoesNotExist:
                pass

        kwargs.update({'instance': instance, })

        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES
            })

        return ResearcherNotesForm(**kwargs)

    def _prepare_frmset_assetmodel(self):
        kwargs = {
            'prefix': 'frmset_assetmodel_px',
        }
        form_factory_kwargs = {
            'form': self.default_asset_modelform,
            'can_delete': True,
        }

        if hasattr(self, 'object'):  # update view will have this, createview will not.
            kwargs.update({'queryset': self.object.files.all()})
        else:
            kwargs.update({'queryset': self.default_asset_model.objects.none()})

        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES
            })

        AssetModelFormSet = modelformset_factory(self.default_asset_model, **form_factory_kwargs)

        return AssetModelFormSet(**kwargs)

    def _prepare_frm_confidentiality(self):
        kwargs = {'prefix': 'frm_confidentiality_px'}

        instance = None
        if hasattr(self, 'object'):  # update view will have this, createview will not.
            try:
                instance = self.object.confidentiality
            except Confidentiality.DoesNotExist:
                pass

        kwargs.update({'instance': instance, })

        if self.request.method == 'POST':
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES
            })

        return ConfidentialityForm(**kwargs)

    def get_form_context_kwargs(self):
        """
        Use in get() and post() to gather up the forms.
        Override super for finer grained control.
        :return:
        """

        kwargs = {
            'frm_item': self._prepare_frm_item(),
            'frm_dublin_core': self._prepare_frm_dublin_core(),
            'frm_holdings': self._prepare_frm_holdings(),
            'frm_review': self._prepare_frm_review(),
            'frm_researcher_notes': self._prepare_frm_researcher_notes(),
            'frm_confidentiality': self._prepare_frm_confidentiality(),
            'frmset_assetmodel': self._prepare_frmset_assetmodel()
        }

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ItemEditViewAbstract, self).get_context_data(**kwargs)
        context.update(**self.get_form_context_kwargs())
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        frm_item = self._prepare_frm_item()
        frm_dublin_core = self._prepare_frm_dublin_core()
        frm_holdings = self._prepare_frm_holdings()
        frm_review = self._prepare_frm_review()
        frm_researcher_notes = self._prepare_frm_researcher_notes()
        frm_confidentiality = self._prepare_frm_confidentiality()
        frmset_assetmodel = self._prepare_frmset_assetmodel()

        forms_are_valid = True

        # use is_bound to make sure the form has data.
        if not (frm_item.is_bound and frm_item.is_valid()):
            forms_are_valid = False

        if not frm_dublin_core.is_valid():
            forms_are_valid = False

        if not frm_holdings.is_valid():
            forms_are_valid = False

        if not frm_review.is_valid():
            forms_are_valid = False

        if not frm_researcher_notes.is_valid():
            forms_are_valid = False

        if not frm_confidentiality.is_valid():
            forms_are_valid = False

        if not frmset_assetmodel.is_valid():
            forms_are_valid = False

        if not forms_are_valid:
            return self.render_to_response(self.get_form_context_kwargs())

        else:

            # save everything and redirect
            item = frm_item.save(commit=False)
            self.item = item # ooh that's ugly. Did it for the success url biznass.

            # dublin_core and confidentiality - we want these created every time regardless of
            # whether user has input data or not.
            dublin_core = frm_dublin_core.save()
            item.dublin_core = dublin_core

            confidentiality = frm_confidentiality.save()
            item.confidentiality = confidentiality

            # if not item.cataloger:
            #     item.cataloger = UserPersonProxy(self.request.user.id)

            # First instantiate the one-to-one fields with the existing instances or None
            holdings = item.holdings or None
            review = item.review or None
            researcher_notes = item.researcher_notes or None

            if frm_holdings.has_changed():
                holdings = frm_holdings.save()
            if frm_review.has_changed():
                review = frm_review.save()
            if frm_researcher_notes.has_changed():
                researcher_notes = frm_researcher_notes.save()

            # Assign the one-to-one models to the item here so that they are
            # always present even when the form doesn't change.
            # For some reason when you don't assign holdings, review, and researcher_notes they disappear!
            item.holdings = holdings
            item.review = review
            item.researcher_notes = researcher_notes

            item.save()
            frm_item.save_m2m()  # to save tags.

            # due to m2m with custom through model, files must be saved last:
            # NOTE: existing assets won't be returned by .save()
            for assetmodel in frmset_assetmodel.save():
                ItemAssetRelation.objects.create(
                    item=item,
                    secureasset=assetmodel,
                )

            # Because the item form was saved with commit=False we must now create a SecurityLevel instance.
            frm_item.create_security_level_for_object(item)

            return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('library:item-detail', current_app=self.request.resolver_match.namespace, args=[self.item.id, ])


class ItemCreateView(EditObjectMixin, ItemEditViewAbstract):
    page_help_name = 'library:item-create'
    edit_object_cancel_url = reverse_lazy('library:item-list')

    @method_decorator(permission_required('library.add_item', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ItemCreateView, self).dispatch(request, *args, **kwargs)


class ItemUpdateView(UserHasObjectSecurityClearanceMixin, SingleObjectMixin, EditObjectMixin, ItemEditViewAbstract):
    """
    Subclasses the custom ItemEditViewAbstract and overrides the stuff that populates the
    form with an existing Item.
    """
    page_help_name = 'library:item-update'
    model = Item
    raise_exception = True

    def get_form_kwargs(self):
        return super().get_form_kwargs()

    def get_edit_object_cancel_url(self):
        return reverse('library:item-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('library:item-delete', args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super(ItemUpdateView, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ItemUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ItemUpdateView, self).post(request, *args, **kwargs)

    @method_decorator(permission_required('library.change_item', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ItemUpdateView, self).dispatch(request, *args, **kwargs)


class ItemDeleteView(PermissionRequiredMixin, UserHasObjectSecurityClearanceMixin, NavContextMixin, HelpContextMixin, DeleteView):
    model = Item
    success_url = reverse_lazy('library:item-list')
    page_help_name = 'library:item-delete'
    nav_url = reverse_lazy('heritage:dashboard')
    permission_required = 'library.delete_item'
    raise_exception = True

    def get_cancel_url(self):
        return reverse('library:item-detail', args=[self.object.id])


class ItemDetailView(LoginRequiredMixin, UserHasObjectSecurityClearanceMixin, NavContextMixin, HelpContextMixin, DetailView):
    model = Item
    template_name = 'library/item_detail.html'
    page_help_name = 'library:item-detail'
    nav_url = reverse_lazy('heritage:dashboard')
    raise_exception = True


class ItemDetailPrintView(ItemDetailView):
    def get_context_data(self, **kwargs):
        context = super(ItemDetailPrintView, self).get_context_data(**kwargs)
        context['is_print_view'] = True
        return context


class CollectionTagListView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, ListView):
    model = CollectionTag
    page_help_name = 'library:collectiontag-list'

    nav_url = reverse_lazy('heritage:dashboard')

    def get_context_data(self, **kwargs):
        context = super(CollectionTagListView, self).get_context_data(**kwargs)
        context['ajax_url'] = drf_reverse('library:api:collectiontag-list')

        context['fields'] = [
            ['name',
             {
                 'verbose_name': 'Name',
                 'type': 'link',
                 'url_field': 'url'
             }],
            ['description', 'Description'],
            ['items_count', 'Items']
        ]

        context['sort_options'] = [
            ['name', 'Name']
        ]
        context['filters'] = []

        return context


class CollectionTagDetailView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, LibraryViewMixin, DetailView):
    model = CollectionTag
    page_help_name = 'library:collectiontag-detail'
    nav_url = reverse_lazy('heritage:dashboard')

    def get_context_data(self, **kwargs):
        context = super(CollectionTagDetailView, self).get_context_data(**kwargs)
        context.update(get_item_list_context(self.request))

        # so far all we want
        context.update(**get_item_list_context(self.request))
        context['ajax_url'] = "{}?collection={}".format(drf_reverse('library:api:item-list'), self.object.pk)

        return context


class CollectionTagCreateView(PermissionRequiredMixin, EditObjectMixin, NavContextMixin, HelpContextMixin, LibraryFormViewMixin, CreateView):
    model = CollectionTag
    page_help_name = 'library:collectiontag-create'
    nav_url = reverse_lazy('heritage:dashboard')
    form_class = CollectionTagForm
    permission_required = 'library.add_collectiontag'
    edit_object_cancel_url = 'library:collectiontag-list'

    def get_success_url(self):
        return reverse('library:collectiontag-detail', args=[self.object.id, ])


class CollectionTagUpdateView(PermissionRequiredMixin, EditObjectMixin, NavContextMixin, HelpContextMixin, LibraryFormViewMixin, UpdateView):
    model = CollectionTag
    page_help_name = 'library:collectiontag-update'
    nav_url = reverse_lazy('heritage:dashboard')
    form_class = CollectionTagForm
    permission_required = 'library.change_collectiontag'

    def get_edit_object_cancel_url(self):
        return reverse('library:collectiontag-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('library:collectiontag-delete', args=[self.object.id])

    def get_success_url(self):
        return reverse('library:collectiontag-detail', args=[self.object.id, ])


class CollectionTagDeleteView(PermissionRequiredMixin, NavContextMixin, HelpContextMixin, DeleteView):
    model = CollectionTag
    success_url = reverse_lazy('library:collectiontag-list')
    page_help_name = 'library:collectiontag-delete'
    nav_url = reverse_lazy('heritage:dashboard')
    permission_required = 'library.delete_collectiontag'

    def get_cancel_url(self):
        return reverse('library:collectiontag-detail', args=[self.object.id])


class CaseBriefCreateView(PermissionRequiredMixin, EditObjectMixin, NavContextMixin, HelpContextMixin, LibraryFormViewMixin, CreateView):
    model = CaseBrief
    page_help_name = 'library:casebrief-create'
    nav_url = reverse_lazy('heritage:dashboard')
    form_class = CaseBriefForm
    permission_required = 'library.add_casebrief'
    edit_object_cancel_url = reverse_lazy("library:casebrief-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'].update({'cataloger': self.request.user.id})
        return kwargs

    def get_success_url(self):
        return reverse('library:casebrief-detail', args=[self.object.id, ])


class CaseBriefUpdateView(PermissionRequiredMixin, EditObjectMixin, NavContextMixin, HelpContextMixin, LibraryFormViewMixin, UpdateView):
    model = CaseBrief
    page_help_name = 'library:casebrief-update'
    nav_url = reverse_lazy('heritage:dashboard')
    form_class = CaseBriefForm
    permission_required = 'library.change_casebrief'
    edit_object_delete_perm = 'library.delete_casebrief'

    def get_edit_object_cancel_url(self):
        return reverse('library:casebrief-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('library:casebrief-delete', args=[self.object.id])

    def get_success_url(self):
        return reverse('library:casebrief-detail', args=[self.object.id, ])


class CaseBriefDeleteView(PermissionRequiredMixin, NavContextMixin, HelpContextMixin, DeleteView):
    model = CaseBrief
    success_url = reverse_lazy('library:casebrief-list')
    page_help_name = 'library:casebrief-delete'
    nav_url = reverse_lazy('heritage:dashboard')
    permission_required = 'library.delete_casebrief'

    def get_cancel_url(self):
        return reverse('library:casebrief-detail', args=[self.object.id])


class CaseBriefDetailView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, DetailView):
    model = CaseBrief
    page_help_name = 'library:casebrief-detail'
    nav_url = reverse_lazy('heritage:dashboard')


class CaseBriefDetailPrintView(CaseBriefDetailView):
    def get_context_data(self, **kwargs):
        context = super(CaseBriefDetailPrintView, self).get_context_data(**kwargs)
        context['is_print_view'] = True
        return context


class CaseBriefListView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, ListView):
    model = CaseBrief
    page_help_name = 'library:casebrief-list'

    nav_url = reverse_lazy('heritage:dashboard')

    def get_context_data(self, **kwargs):
        context = super(CaseBriefListView, self).get_context_data(**kwargs)
        context['ajax_url'] = drf_reverse('library:api:casebrief-list')

        context['fields'] = [
            ['prefixed_id', 'Case Brief ID'],
            ['story_title',
             {
                 'verbose_name': 'Story Title',
                 'type': 'link',
                 'url_field': 'url'
             }],
            # ['story_title', 'Story Title'],
            ['created', 'Created'],
            ['modified', 'Modified'],
        ]

        context['sort_options'] = [
            ['story_title', 'Story Title'],
            ['created', 'Date Created'],
            ['modified', 'Date Modified'],
        ]
        context['filters'] = [
            {
                'name': 'keyword',
                'verbose_name': 'Keywords',
                'id': 'keyword-filter',
                'options': list(
                    map(lambda x: [x.id, x.name],
                        CaseBriefTag.objects.all()
                        )
                ),
                'default_value': [],
                'initial_value': self.request.GET.getlist('keyword', 'undefined'),
                'component': "select",
                'labelClasses': "active",
                'select_type': 'select2',
                'is_multiple': "true"
            },
            {
                'name': 'tag',
                'verbose_name': 'Tags',
                'id': 'tag-filter',
                'options': list(
                    map(lambda x: [x.id, x.name],
                        Tag.objects.all()
                        )
                ),
                'default_value': [],
                'initial_value': self.request.GET.getlist('keyword', 'undefined'),
                'component': "select",
                'labelClasses': "active",
                'select_type': 'select2',
                'is_multiple': "true"
            },
        ]

        return context


class SynthesisCreateView(PermissionRequiredMixin, EditObjectMixin, NavContextMixin, HelpContextMixin, LibraryFormViewMixin, CreateView):
    model = Synthesis
    page_help_name = 'library:synthesis-create'
    nav_url = reverse_lazy('heritage:dashboard')
    form_class = SynthesisForm
    permission_required = 'library.add_synthesis'
    synthesis_item_formset = inlineformset_factory(Synthesis, SynthesisItem, form=SynthesisItemForm, can_delete=True, extra=1)
    edit_object_cancel_url = reverse_lazy('library:synthesis-list')

    def get_context_data(self, **kwargs):
        context = super(SynthesisCreateView, self).get_context_data(**kwargs)

        if self.request.method == 'POST':
            context['synthesis_item_formset'] = self.synthesis_item_formset(self.request.POST, self.request.FILES)
        else:
            # NOTE: The initial can't be set on the empty form, so in the form_valid method we make sure that property
            # is correctly set.
            context['synthesis_item_formset'] = self.synthesis_item_formset(initial=[{'belongs_to': self.belongs_to}])

        return context

    def form_valid(self, form):
        """
        
        :param form: 
        :return: 
        """
        response = super(SynthesisCreateView, self).form_valid(form)
        formset = self.synthesis_item_formset(self.request.POST, self.request.FILES, instance=self.object)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.belongs_to = self.belongs_to
                instance.save()
        return response

    def get_success_url(self):
        return reverse('library:synthesis-detail', args=[self.object.id, ])


class SynthesisUpdateView(PermissionRequiredMixin, EditObjectMixin, NavContextMixin, HelpContextMixin, LibraryFormViewMixin, UpdateView):
    model = Synthesis
    page_help_name = 'library:synthesis-update'
    nav_url = reverse_lazy('heritage:dashboard')
    form_class = SynthesisForm
    permission_required = 'library.change_synthesis'
    edit_object_delete_perm = 'library.delete_synthesis'
    synthesis_item_formset = inlineformset_factory(Synthesis, SynthesisItem, form=SynthesisItemForm, can_delete=True, extra=1)

    def get_edit_object_cancel_url(self):
        return reverse("library:synthesis-detail", args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse("library:synthesis-delete", args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.method == 'POST':
            context['synthesis_item_formset'] = self.synthesis_item_formset(self.request.POST)
        else:
            context['synthesis_item_formset'] = self.synthesis_item_formset(instance=self.object)

        return context

    def form_valid(self, form):
        formset = self.synthesis_item_formset(self.request.POST, self.request.FILES, instance=self.object)
        if formset.is_valid():
            formset.save()
            for obj in formset.deleted_objects:
                if obj.id:
                    obj.delete()
        else:
            return self.form_invalid(form)

        return super(SynthesisUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('library:synthesis-detail', args=[self.object.id, ])


class SynthesisDeleteView(PermissionRequiredMixin, NavContextMixin, HelpContextMixin, DeleteView):
    model = Synthesis
    success_url = reverse_lazy('library:synthesis-list')
    page_help_name = 'library:synthesis-delete'
    nav_url = reverse_lazy('heritage:dashboard')
    permission_required = 'library.delete_synthesis'

    def get_cancel_url(self):
        return reverse('library:synthesis-detail', args=[self.object.id])


class SynthesisDetailView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, DetailView):
    model = Synthesis
    page_help_name = 'library:synthesis-detail'
    nav_url = reverse_lazy('heritage:dashboard')


class SynthesisDetailPrintView(SynthesisDetailView):
    def get_context_data(self, **kwargs):
        context = super(SynthesisDetailPrintView, self).get_context_data(**kwargs)
        context['is_print_view'] = True
        return context


class SynthesisListView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, LibraryListViewMixin, ListView):
    model = Synthesis
    page_help_name = 'library:synthesis-list'

    nav_url = reverse_lazy('heritage:dashboard')

    def get_context_data(self, **kwargs):
        context = super(SynthesisListView, self).get_context_data(**kwargs)
        context['ajax_url'] = drf_reverse('library:api:synthesis-list')

        context['fields'] = [
            ['prefixed_id', 'Synthesis ID'],
            ['name',
             {
                 'verbose_name': 'Name',
                 'type': 'link',
                 'url_field': 'url'
             }],
            # ['story_title', 'Story Title'],
            ['created', 'Created'],
            ['modified', 'Modified'],
        ]

        context['sort_options'] = [
            ['name', 'Name'],
            ['created', 'Date Created'],
            ['modified', 'Date Modified'],
        ]
        context['filters'] = []

        return context


class PersonMentionedTagListView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, ListView):
    model = PersonMentionedTag
    page_help_name = 'library:personmentionedtag-list'

    nav_url = reverse_lazy('heritage:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ajax_url'] = reverse('library:api:personmentionedtag-list')

        context['fields'] = [
            ['name',
             {
                 'verbose_name': 'Name',
                 'type': 'link',
                 'url_field': 'url'
             }],
            ['items_count', 'Items']
        ]

        context['sort_options'] = [
            ['name', 'Name']
        ]
        context['filters'] = []

        return context


class PersonMentionedTagDetailView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, DetailView):
    model = PersonMentionedTag
    page_help_name = 'library:personmentionedtag-detail'
    nav_url = reverse_lazy('heritage:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_things'] = PersonMentionedTaggedItem.objects.filter(tag=self.object)
        return context


class PersonMentionedTagUpdateView(PermissionRequiredMixin, EditObjectMixin, NavContextMixin, HelpContextMixin, UpdateView):
    model = PersonMentionedTag
    page_help_name = 'library:personmentionedtag-update'
    nav_url = reverse_lazy('heritage:dashboard')
    form_class = PersonMentionedTagForm
    permission_required = 'library.change_personmentionedtag'
    edit_object_delete_perm = 'library.delete_personmentionedtag'

    def get_edit_object_cancel_url(self):
        return reverse('library:personmentionedtag-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse('library:personmentionedtag-delete', args=[self.object.id])

    def get_success_url(self):
        return reverse('library:personmentionedtag-detail', args=[self.object.id, ])


class PersonMentionedTagDeleteView(PermissionRequiredMixin, NavContextMixin, HelpContextMixin, DeleteView):
    model = PersonMentionedTag
    success_url = reverse_lazy('library:personmentionedtag-list')
    page_help_name = 'library:personmentionedtag-delete'
    nav_url = reverse_lazy('heritage:dashboard')
    permission_required = 'library.delete_personmentionedtag'

    def get_cancel_url(self):
        return reverse('library:personmentionedtag-detail', args=[self.object.id])


class LibrarySearchView(LoginRequiredMixin, NavContextMixin, HelpContextMixin, SearchView):
    '''
    There is a glaring problem with this view that I don't have time to address:
        - When a search is called, this view (or something below it) is calling
            the same search on solr 4 times in a row. May be the paginator, dunno.
            Watch the debug window for calls to solr.
    '''
    template_name = 'library/search_form.html'
    # load_all = False
    form_class = LibrarySearchForm
    queryset = CustomSearchQuerySet()  # Comment this out to go back to default --> Make sure to add () so it instantiates. Pain if not.
    page_help_name = 'library:search'
    nav_url = reverse_lazy('heritage:dashboard')
    facet_fields = ['django_ct', 'item_type', 'collections', 'tags', 'cataloger', 'reviewer', 'date']
    models = [Item, CollectionTag, CaseBrief, Synthesis, SynthesisItem, HeritageAsset, Place]

    def get_object_list_subtexts(self, context):
        # Paginated the queryset so we can process the text blocks of only
        # the current page:
        paginated = self.paginate_queryset(self.get_queryset(), GeneralSetting.objects.get('library__default_search_results_per_page', 20))
        paginated_queryset = paginated[2]  # Seems to be the paginated query set.
        return search_utils.get_subtexts(paginated_queryset)

    def get_queryset(self):
        '''
        When you subclass this view, be sure to specify the model
        you want to query, otherwise it will query everything:
            eg. sqs = super().get_queryset().models(HeritageAsset)
        :return:
        '''

        # TODO: Do something here to filter OUT asset types that require permission to view
        sqs = super().get_queryset()

        # Limit the query to a limited number of provided models...
        if self.models:
            sqs = sqs.models(*self.models)

        # If wanted, we can return nothing if user not authorized:
        # if not self.request.user.has_perm('assets.search_secureasset'):
        #     return queryset.none()
        # else:
        #     return queryset

        # Facets magic!
        for field in self.facet_fields:
            sqs = sqs.facet(field, sort='count')

        return sqs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object_list_subtexts'] = self.get_object_list_subtexts(context)

        # Tell the template about the available facet fields.
        context.update({'facet_fields': self.facet_fields})

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

        # Facets!
        # TODO this doesn't limit the displayed facet counts by the current search.
        # We can show whatever values we want in the form, but we still have to provide a list of valid choices.
        sqs = self.get_queryset()

        '''
        TODO This is a temporary hack (tm)  This is bad!  It means we're hitting solr twice just so that we can present
             facets with accurate counts for the current search...
        '''
        if self.request.POST.get('q', None) is not None:
            q = self.request.POST.get('q')

            # Run the search and OR the boosted name field onto the query to promote results:
            sqs = sqs.filter(SQ(text=Raw('({})'.format(q))) | SQ(name=Raw('({})'.format(q))))

        facet_counts = sqs.facet_counts()
        kwargs.update({'facets': facet_counts})

        return kwargs

    def form_valid(self, form):
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


##################################################################################################
# Rest API:
##################################################################################################


class ItemFilterSet(filters.FilterSet):
    """
    ItemFilterSet --- see development.views.DevelopmentProjectFilterSet for a tidy example of what can be done.
    """
    tag = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(), method='filter_tags')
    collection = django_filters.ModelMultipleChoiceFilter(queryset=CollectionTag.objects.all(), method='filter_collections')
    personmentioned = django_filters.ModelMultipleChoiceFilter(queryset=PersonMentionedTag.objects.all(), method='filter_personmentioned')
    plants = django_filters.ModelMultipleChoiceFilter(queryset=PlantTag.objects.all(), method='filter_plants')
    animals = django_filters.ModelMultipleChoiceFilter(queryset=AnimalTag.objects.all(), method='filter_animals')

    date_on = django_filters.DateFilter(name='dublin_core__date', lookup_type='exact')
    date_start = django_filters.DateFilter(name='dublin_core__date', lookup_type='gte')
    date_end = django_filters.DateFilter(name='dublin_core__date', lookup_type='lte')

    spreadsheet_id = django_filters.NumberFilter(name='researcher_notes__spreadsheet_id')

    item_type = django_filters.ModelMultipleChoiceFilter(queryset=ItemType.objects.all(), method='filter_item_types')

    class Meta:
        model = Item
        fields = ['id', 'name', 'item_type', 'tag', 'collection', 'date_on', 'date_start', 'date_end']

    def filter_tags(self, queryset, _, value):
        if value:
            queryset = queryset.filter(tags__in=value)
        return queryset

    def filter_collections(self, queryset, _, value):
        if value:
            queryset = queryset.filter(collections__in=value)
        return queryset

    def filter_personmentioned(self, queryset, _, value):
        if value:
            queryset = queryset.filter(review__people_mentioned__in=value)
        return queryset

    def filter_plants(self, queryset, _, value):
        if value:
            queryset = queryset.filter(review__plants__in=value)
        return queryset

    def filter_animals(self, queryset, _, value):
        if value:
            queryset = queryset.filter(review__animals__in=value)
        return queryset

    def filter_item_types(self, queryset, _, value):
        if value:
            queryset = queryset.filter(dublin_core__type__in=value)
        return queryset


class ItemViewSet(UserHasSecurityLevelQuerySetFilterMixin, LibraryListViewMixin, viewsets.ModelViewSet):
    queryset = Item.objects.all()  # Because I call super() in get_queryset, we still need this.
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ItemSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = ItemFilterSet
    # filter_fields = ('id', 'name')
    search_fields = ('id', 'name', 'prefixed_id_q', 'cataloger__username', 'cataloger__first_name', 'cataloger__last_name',
                     'reviewer__username', 'reviewer__first_name', 'reviewer__last_name', 'tags__name',
                     'collections__name', 'files__name', 'holdings__digital_file_name_path', 'holdings__digital_file_name')
    ordering_fields = ('id', 'name', 'dublin_core__date', 'created_date_null')
    ordering = ('-id',)

    def get_queryset(self):
        # Calling super instead of just using a starter queryset, because I want to
        # be able to pass this queryset to a mixin.
        queryset = super().get_queryset()

        queryset = queryset.annotate(created_date_null=Case(
            When(dublin_core__date__isnull=True, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ))

        return queryset


class CollectionTagViewSet(viewsets.ModelViewSet):
    queryset = CollectionTag.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CollectionTagSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('id', 'description', 'name')
    ordering_fields = ('name',)


class CaseBriefFilterSet(filters.FilterSet):
    """
    ItemFilterSet --- see development.views.DevelopmentProjectFilterSet for a tidy example of what can be done.
    """
    tag = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(), method='filter_tags')
    keyword = django_filters.ModelMultipleChoiceFilter(queryset=CaseBriefTag.objects.all(), method='filter_keywords')

    class Meta:
        model = CaseBrief
        fields = ['id', 'story_title', 'tag', 'keyword']

    def filter_tags(self, queryset, _, value):
        if value:
            queryset = queryset.filter(tags__in=value)
        return queryset

    def filter_keywords(self, queryset, _, value):
        if value:
            queryset = queryset.filter(keywords__in=value)
        return queryset


class CaseBriefViewSet(viewsets.ModelViewSet):
    queryset = CaseBrief.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CaseBriefSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = CaseBriefFilterSet
    search_fields = ('id', 'story_title', 'prefixed_id_q')
    ordering_fields = ('-modified',)


class SynthesisViewSet(viewsets.ModelViewSet):
    queryset = Synthesis.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SynthesisSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filter_class = CaseBriefFilterSet
    search_fields = ('id', 'name', 'prefixed_id_q', )
    ordering_fields = ('-modified',)


class PersonMentionedTagViewSet(viewsets.ModelViewSet):
    queryset = PersonMentionedTag.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PersonMentionedTagSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('id', 'description', 'name')
    ordering_fields = ('-item_count',)

