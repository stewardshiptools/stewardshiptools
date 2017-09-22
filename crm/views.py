from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from rest_framework import viewsets, filters
from rest_framework.reverse import reverse, reverse_lazy
from rest_framework import permissions

from .serializers import RoleSerializer, OrganizationSerializer, PersonSerializer

from .models import Role, Organization, Person

from .forms import PersonForm, OrganizationForm

from help.mixins import HelpContextMixin

from cedar.mixins import EditObjectMixin


class PersonListView(HelpContextMixin, ListView):
    model = Person
    template_name = 'crm/person_list.html'  # Ths doesn't actually need to be specified now.
    page_help_name = 'crm:person-list'

    def get_context_data(self, **kwargs):
        context = super(PersonListView, self).get_context_data(**kwargs)
        context['ajax_url'] = reverse('crm:api:person-list')
        return context


class PersonDetailView(HelpContextMixin, DetailView):
    model = Person
    page_help_name = 'crm:person-detail'

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)

        search_interviews_by_person_url = "{}?{}={}".format(reverse('heritage:api:interview-list'), 'personid', self.object.id)
        # search_interviews_by_person_url = "{}?{}={}".format(reverse('heritage:api:interview-list'), 'participants__id', self.object.id)
        context['interview_ajax_url'] = search_interviews_by_person_url

        #context['dev_project_ajax_url_filter_by_person'] = "personid={}".format(self.object.id)
        # search_dev_project_by_person_url = "{}?{}={}".format(reverse('development:api:project-list'), 'personid', self.object.id)
        #context['dev_project_ajax_url'] = reverse('development:api:project-list')
        context['dev_project_ajax_url'] = "{}?{}={}".format(reverse('development:api:project-list'), 'personid', self.object.id)

        return context


class PersonCreateView(EditObjectMixin, CreateView):
    model = Person
    form_class = PersonForm

    edit_object_cancel_url = reverse_lazy('crm:person-list')

    @method_decorator(permission_required('crm.add_person'))
    def dispatch(self, request, *args, **kwargs):
        return super(PersonCreateView, self).dispatch(request, *args, **kwargs)


class PersonUpdateView(EditObjectMixin, UpdateView):
    model = Person
    form_class = PersonForm

    edit_object_delete_perm = 'crm.delete_person'

    def get_edit_object_cancel_url(self):
        return reverse_lazy('crm:person-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse_lazy('crm:person-delete', args=[self.object.id])

    @method_decorator(permission_required('crm.change_person'))
    def dispatch(self, request, *args, **kwargs):
        return super(PersonUpdateView, self).dispatch(request, *args, **kwargs)


class PersonDeleteView(DeleteView):
    model = Person
    success_url = reverse_lazy('crm:person-list')

    @method_decorator(permission_required('crm.delete_person'))
    def dispatch(self, request, *args, **kwargs):
        return super(PersonDeleteView, self).dispatch(request, *args, **kwargs)


class OrganizationListView(HelpContextMixin, ListView):
    model = Organization
    page_help_name = 'crm:organization-list'

    def get_context_data(self, **kwargs):
        context = super(OrganizationListView, self).get_context_data(**kwargs)
        context['ajax_url'] = reverse('crm:api:organization-list')
        return context


class OrganizationDetailView(HelpContextMixin, DetailView):
    model = Organization
    page_help_name = 'crm:organization-detail'

    def get_context_data(self, **kwargs):
        context = super(OrganizationDetailView, self).get_context_data(**kwargs)
        # context['person_info_ajax_url'] = reverse('crm:api:person-list',
        #                                            args=[self.object.id, ],
        #                                            request=self.request)

        # Put in the extra "&" in case filtering is done in the page and exta queries are added automatically.
        person_info_ajax_url = "{}?{}={}&".format(reverse('crm:api:person-list'), 'organizations__id', self.object.id)
        context['person_info_ajax_url'] = person_info_ajax_url

        return context


class OrganizationCreateView(EditObjectMixin, HelpContextMixin, CreateView):
    model = Organization
    form_class = OrganizationForm
    page_help_name = 'crm:organization-create'
    edit_object_cancel_url = reverse_lazy('crm:organization-list')

    @method_decorator(permission_required('crm.add_organization'))
    def dispatch(self, request, *args, **kwargs):
        return super(OrganizationCreateView, self).dispatch(request, *args, **kwargs)


class OrganizationUpdateView(EditObjectMixin, HelpContextMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm
    page_help_name = 'crm:organization-update'

    edit_object_delete_perm = 'crm.delete_organization'

    def get_edit_object_cancel_url(self):
        return reverse_lazy('crm:organization-detail', args=[self.object.id])

    def get_edit_object_delete_url(self):
        return reverse_lazy('crm:organization-delete', args=[self.object.id])

    @method_decorator(permission_required('crm.change_organization'))
    def dispatch(self, request, *args, **kwargs):
        return super(OrganizationUpdateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(OrganizationUpdateView, self).get_form_kwargs()
        kwargs['persons'] = self.object.person_set.all()
        return kwargs


class OrganizationDeleteView(HelpContextMixin, DeleteView):
    model = Organization
    success_url = reverse_lazy('crm:organization-list')
    page_help_name = 'crm:organization-delete'

    @method_decorator(permission_required('crm.delete_organization'))
    def dispatch(self, request, *args, **kwargs):
        return super(OrganizationDeleteView, self).dispatch(request, *args, **kwargs)


############################################################################
# Rest API Viewsets

class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('name',)
    search_fields = ('name',)
    ordering_fields = '__all__'
    ordering = ('name',)


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_fields = ('gender', 'roles', 'organizations__id',)
    search_fields = ('name_first', 'name_last', 'name_suffix', 'initials', 'indigenous_name', 'roles__name',
                     'organizations__name')
    ordering_fields = '__all__'
    ordering = ('name_last',)

    def get_queryset(self):
        '''
        Adds 'ids' query paramter to url. Can be a csv list of person ids.
        :return:
        '''
        qs = super(PersonViewSet, self).get_queryset()
        ids = self.request.query_params.get('ids', None)    # ids should be csv string.
        if ids is not None:
            # make sure ids not just an empty list
            if ids:
                return qs.filter(id__in=ids.split(','))  # returned queryset filtered by ids
            else:
                # return empty queryset because ids param was supplied but no actual id values were given.
                return qs.none()
        # pass over qs if ids was not a supplied paramter
        else:
            return qs