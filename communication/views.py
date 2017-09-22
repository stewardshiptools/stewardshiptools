from pathlib import Path
import magic
import pickle
import logging

from django.shortcuts import render, redirect
from django.core.cache import cache
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.conf import settings

from rest_framework import viewsets, filters, generics
from rest_framework.decorators import list_route
from rest_framework.reverse import reverse, reverse_lazy
import rest_framework.renderers
from rest_framework.response import Response
from oauth2client.client import OAuth2WebServerFlow

from communication.models import Communication, CommunicationRelation, CommunicationFileRelation, HarvestCodePrefix, MailAccount, \
    GmailCredential, Message, MessageAttachment
from communication.serializers import CommunicationRelationSerializer
from communication.forms import CommunicationForm, HarvestCodePrefixForm
import communication

from help.mixins import HelpContextMixin
from cedar.mixins import EditObjectMixin
from cedar.utils.misc_utils import get_back_url
from cedar_settings.models import GeneralSetting

import communication.tasks  # noqa

from djcelery.views import is_task_successful, task_status

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CommunicationDashboardView(HelpContextMixin, TemplateView):
    template_name = 'communication/dashboard.html'
    page_help_name = 'communication:dashboard'

    def get_context_data(self, **kwargs):
        context = super(CommunicationDashboardView, self).get_context_data(**kwargs)
        context['communications_stats'] = communication.utils.comm_utils.communications_stats()
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CommunicationDashboardView, self).dispatch(request, *args, **kwargs)


class CommunicationListView(ListView):
    model = Communication

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CommunicationListView, self).dispatch(request, *args, **kwargs)


class CommunicationCreateView(CreateView):
    form_class = CommunicationForm
    model = Communication


class CommunicationUpdateView(UpdateView):
    model = Communication
    fields = '__all__'


class CommunicationDeleteView(DeleteView):
    model = Communication

    def get_context_data(self, **kwargs):
        context = super(CommunicationDeleteView, self).get_context_data(**kwargs)
        context['communication_relations'] = CommunicationRelation.objects.filter(comm=self.object)

        # Gather list of assets that will be deleted. These come from the CommsFileRelations model
        # Assets related to Messages are funny in that they are related to MessageAttachments that
        # are related to Messages.

        # Check if this is a Message, if so, gather the MessageAttachment asset relations.
        if isinstance(self.object.comm_type, Message):
            cfr_qs = CommunicationFileRelation.objects.filter(
                    comm_type_oid__in=self.object.comm_type.attachments.values_list('id', flat=True),
                    comm_type_ct=ContentType.objects.get_for_model(MessageAttachment))
        else:
            cfr_qs = CommunicationFileRelation.objects.filter(
                    comm_type_oid=self.object.comm_type.id,
                    comm_type_ct=self.object.comm_type_ct)

        context['related_assets'] = [cfr.asset for cfr in cfr_qs]
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('communication.delete_communication'):
            raise PermissionDenied
        return super(CommunicationDeleteView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        '''
        Try to set the success url here. Tricky thing to do. Needs to be done before
         the actual comm object is deleted.
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        try:
            communication_object = Communication.objects.get(id=kwargs.get('pk', None))

            # get success link back to Dev Prj, Her Prj, etc.:
            first_relation = CommunicationRelation.objects.filter(comm=communication_object).first()
            self.success_url = first_relation.related_object.get_absolute_url() + \
                               GeneralSetting.objects.get('communication__comm_items_panel_html_id')
        except AttributeError:
            self.success_url = reverse('communication:communication-list') + \
                               GeneralSetting.objects.get('communication__comm_items_panel_html_id')

        if isinstance(communication_object.comm_type, Message):
            logger.info("Delete message requested - remove all secure assets and wipe the message. message id {}".format(communication_object.comm_type.id))

            # wipe the message
            communication_object.comm_type.wipe()

            # get the communication object (not the comm type):
            communication_ct = ContentType.objects.get_for_model(communication_object)

            # remove file relations:
            for cfr in CommunicationFileRelation.objects.filter(
                    comm_type_oid=communication_object.id,
                    comm_type_ct=communication_ct):
                cfr.asset.delete()
                cfr.delete()

            # finally delete the communication:
            communication_object.delete()

            return HttpResponseRedirect(self.success_url)

        else:
            return super(CommunicationDeleteView, self).delete(request, *args, **kwargs)


class CommunicationDetailView(DetailView):
    model = Communication


class CommunicationCreateViewAbstract(EditObjectMixin, CreateView):
    '''
    This is the parent class that should be used for creating child communication type
    createviews. Do not use this class on a Communication instance directly.
    Child classes (eg. PhoneCallCreateView) must implement the following class properties:
        form_class = implemented_by_child class
        template = implemented_by_child class
        model = implemented_by_child class

    '''

    # will be populated with 'inline_communication_formset' in init by default.
    # declare your subclasses's inline formsets here:
    inline_formset_classes = {}

    # add any additional non-inline form classes here (eg. Fax document field)
    noninline_form_classes = {}

    def get_edit_object_cancel_url(self):
        return get_back_url(self.request)

    def __init__(self):
        # create the formset_classes dict and set the inline comm formset key:
        if not self.inline_formset_classes:
            self.inline_formset_classes = {}

        if not 'inline_communication_formset' in self.inline_formset_classes:
            self.inline_formset_classes.update({
                'inline_communication_formset': communication.forms.CommunicationGenericFormset
            })

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        formsets = self._get_formsets(request)

        context_kwargs = {'form': form}
        context_kwargs.update(formsets)
        context = self.get_context_data(**context_kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        # Check the validity of the formsets:
        all_formsets_valid = True
        formsets = self._get_formsets(request)
        for formset_classname in formsets:
            # Set to false if any of the formsets are invalid:
            all_formsets_valid = all_formsets_valid & formsets[formset_classname].is_valid()

        # Check validity of main form:
        if form.is_valid() and all_formsets_valid:
            return self.form_valid(form, formsets)
        else:
            return self.form_invalid(form, formsets)

    # Add related_object's contenttype things to the form's kwargs:
    def get_form_kwargs(self):
        '''
        Adds instance variables tracking the object that this communication
        will be related to: related_object (the actual instance), and the
        related objects contenttype (it had to be done here so why not hold it
        in a var and save a db query).
        :return:
        '''
        kwargs = super(CommunicationCreateViewAbstract, self).get_form_kwargs()
        kwargs['related_ct_id'] = self.kwargs.get('related_ct_id', None)
        kwargs['related_oid'] = self.kwargs.get('related_oid', None)

        # Get the related object from url params and store it:
        self.related_object_ct = ContentType.objects.get_for_id(kwargs['related_ct_id'])
        self.related_object = self.related_object_ct.get_object_for_this_type(pk=kwargs['related_oid'])

        return kwargs

    def _get_formsets(self, request):
        # Copy the formsets dict so we can reuse and initialize:
        inline_formsets = self.inline_formset_classes.copy()
        noninline_forms = self.noninline_form_classes.copy()

        if not request.POST:
            for formset_classname in inline_formsets:
                inline_formsets[formset_classname] = inline_formsets[formset_classname](instance=self.model())
            for form_classname in noninline_forms:
                noninline_forms[form_classname] = noninline_forms[form_classname]()

        else:
            for formset_classname in inline_formsets:
                inline_formsets[formset_classname] = inline_formsets[formset_classname](request.POST, request.FILES)
            for form_classname in noninline_forms:
                noninline_forms[form_classname] = noninline_forms[form_classname](request.POST, request.FILES)

        # merge the dicts and return:
        inline_formsets.update(noninline_forms)
        return inline_formsets

    def _process_valid_forms(self, form, formsets):
        '''
            Called by form_valid if ALL forms are valid. Creates a Comm Type instance along with
            the associated Communication instance (inline_communication_formset).

            Extend this method (and always call super first!) if/when there is additional processing
            required for other additional inline forms (eg fax document). Reference self.object
            to get the communication type instance (phone, fax, etc.)
        :param form:
        :param formsets:
        :return:
        '''
        """

        """

        # This saves the communication type object (Phone, Fax, ...)
        # Don't commit until we check the validation of the comm instance
        self.object = form.save(commit=False)

        # This saves the communication instance:
        inline_communication_formset = formsets['inline_communication_formset']
        inline_communication_formset.instance = self.object

        # Save the inline_communication_formset: the formset returns a list, but we only ever
        # want one comm instance, so take the first element:
        # commit the communication object save:
        self.object.save()
        comm_instance = inline_communication_formset.save()[0]

        # Now create the CommunicationRelation which connects the Communication instance
        # to another related database object (eg Development Project). Use the related_object
        # instance we get from get_form_kwargs:
        cr_instance, created = CommunicationRelation.objects.get_or_create(
            comm=comm_instance,
            related_object_ct=self.related_object_ct,
            related_object_oid=self.related_object.id
        )
        if cr_instance:
            logger.debug("created new CommunicationRelation instance")

    def form_valid(self, form, formsets):
        '''
        Call if all form and formsets are valid. Invokes _process_valid_forms method
        and then redirects to success_url.
        :param form:
        :param formsets:
        :return:
        '''
        self._process_valid_forms(form, formsets)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formsets):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        context_kwargs = {'form': form}
        context_kwargs.update(formsets)
        context = self.get_context_data(**context_kwargs)
        return self.render_to_response(context)

    def get_success_url(self):
        try:
            return self.related_object.get_absolute_url() + \
                               GeneralSetting.objects.get('communication__comm_items_panel_html_id')
        except AttributeError as err:
            raise AttributeError("Communication create view requires the related object to have an absolute URL defined.")

            # return reverse('communication:communication-list')


class CommunicationTypeDetailViewMixin(DetailView):

    def get_context_data(self, **kwargs):
        context = super(CommunicationTypeDetailViewMixin, self).get_context_data(**kwargs)
        context['communication_relations'] = CommunicationRelation.objects.filter(comm=self.object.communication.first())
        context['from_contact_url'] = "{url}?{param}={value}".format(
            url=reverse('crm:api:person-list'),
            param='ids',
            value=','.join([str(id) for id in self.object.communication.first().from_contacts.values_list('id', flat=True)])
        )
        context['to_contact_url'] = "{url}?{param}={value}".format(
            url=reverse('crm:api:person-list'),
            param='ids',
            value=','.join([str(id) for id in self.object.communication.first().to_contacts.values_list('id', flat=True)])
        )
        return context


class MessageDetailView(CommunicationTypeDetailViewMixin, DetailView):
    model = communication.models.Message


class PhoneCallCreateView(CommunicationCreateViewAbstract):
    form_class = communication.forms.PhoneCallForm
    template = 'phonecall_form.html'
    model = communication.models.PhoneCall


class PhoneCallDetailView(CommunicationTypeDetailViewMixin, DetailView):
    model = communication.models.PhoneCall


class FaxCreateView(CommunicationCreateViewAbstract):
    form_class = communication.forms.FaxForm
    template = 'fax_form.html'
    model = communication.models.Fax

    noninline_form_classes = {
        'document_form': communication.forms.CommunicationAssetForm
    }

    def _process_valid_forms(self, form, formsets):
        '''
        Add extra processing for the fax document instance.
        :param form: the instantiated main form.
        :param formsets: dict of instantiated forms
        :return:
        '''
        super(FaxCreateView, self)._process_valid_forms(form, formsets)

        # Handle the document form.
        # Pull relevant bits out of CommunicationAsset form and reassign
        # to the instantiated related object asset.
        # Discard CommunicationAsset instance.

        asset = self.related_object.get_asset_class()

        # save temp doc instance:
        doc = formsets['document_form'].save(commit=False)
        doc.delete_file_with_record = False
        doc.save()

        # transfer info to new asset instance
        asset.name = doc.name
        asset.asset_type = doc.asset_type
        asset.comment = doc.comment
        asset.file = doc.file
        asset.save()

        # dump temp doc instance
        doc.delete()

        # store record of asset in the relation table
        cfr = communication.models.CommunicationFileRelation.objects.create(
            asset=asset,
            comm_type=self.object
        )
        # print ('cfr:', str(cfr), ' id:', cfr.id)

        self.object.document = cfr
        self.object.save()


class FaxDetailView(CommunicationTypeDetailViewMixin, DetailView):
    model = communication.models.Fax


class LetterCreateView(CommunicationCreateViewAbstract):
    form_class = communication.forms.LetterForm
    template = 'letter_form.html'
    model = communication.models.Letter

    noninline_form_classes = {
        'document_form': communication.forms.CommunicationAssetForm
    }

    def _process_valid_forms(self, form, formsets):
        '''
        Add extra processing for the fax document instance.
        :param form: the instantiated main form.
        :param formsets: dict of instantiated forms
        :return:
        '''
        super(LetterCreateView, self)._process_valid_forms(form, formsets)

        # Handle the document form.
        # Pull relevant bits out of CommunicationAsset form and reassign
        # to the instantiated related object asset.
        # Discard CommunicationAsset instance.

        asset = self.related_object.get_asset_class()

        # save temp doc instance:
        doc = formsets['document_form'].save(commit=False)
        doc.delete_file_with_record = False
        doc.save()

        # transfer info to new asset instance
        asset.name = doc.name
        asset.asset_type = doc.asset_type
        asset.comment = doc.comment
        asset.file = doc.file
        asset.save()

        # dump temp doc instance
        doc.delete()

        # store record of asset in the relation table
        cfr = communication.models.CommunicationFileRelation.objects.create(
            asset=asset,
            comm_type=self.object
        )
        # print ('cfr:', str(cfr), ' id:', cfr.id)

        self.object.document = cfr
        self.object.save()


class LetterDetailView(CommunicationTypeDetailViewMixin, DetailView):
    model = communication.models.Letter


class HarvestCodePrefixCreateView(CreateView):
    '''
    This is broken and being left as-is for now.
    '''
    model = HarvestCodePrefix
    form_class = HarvestCodePrefixForm

    def get_success_url(self):
        return reverse('communication:prefix-list')


class HarvestCodePrefixListView(ListView):
    model = HarvestCodePrefix


class MailHarvestManageView(TemplateView):
    template_name = 'communication/mailharvest_manage.html'

    def get_context_data(self, **kwargs):
        context = super(MailHarvestManageView, self).get_context_data(**kwargs)
        context['mail_accounts'] = communication.models.MailAccount.objects.all()

        logfile_path = settings.LOGGING['handlers']['handler_for_communication']['filename']
        log_file = Path(logfile_path)
        context['logfile_name'] = log_file.name
        context['logfile_path'] = logfile_path
        context['logfile_download_link'] = reverse('communication:log-download')

        return context


class MailHarvestRunMailAccountView(DetailView):
    # template_name = 'communication/mailharvest_manage.html'
    model = communication.models.MailAccount

    def get(self, request, *args, **kwargs):
        response = super(MailHarvestRunMailAccountView, self).get(request, *args, **kwargs)
        if not request.user.has_perm('communication.harvest_mailbox'):
            raise PermissionDenied  # Exception parameter text becomes available in django 1.9

        self.object.harvest_mail()

        return HttpResponseRedirect(reverse('communication:mailharvest-manage'))

    # @permission_required('communication.harvest_mailbox', raise_exception=True)
    # def dispatch(self, request, *args, **kwargs):
    #     response = super(MailHarvestRunMailAccountView, self).dispatch(request, *args, **kwargs)
    #     self.object.harvest_mail()
    #     return HttpResponseRedirect(reverse('communication:mailharvest-manage'))


@login_required()
def check_mail_account_harvest_status(request, mail_account_id):
    """ A helper view to inform via ajax whether a mail account is currently harvesting, has never harvested, or
    report the last date that it harvested.
    DEPRECATED in favour of check_task_mail_account_status() and check_task_mail_account_status_all()

    :param request:
    :param mail_account_id:
    :return:
    """
    mail_account = MailAccount.objects.get(id=mail_account_id)
    result = communication.utils.comm_utils.harvest_mail_account_status(mail_account)


@login_required()
def check_task_mail_account_status(request, mail_account_id):
    """ A helper view to inform via ajax whether a mail account is currently running.

    :param request:
    :param mail_account_id:
    :return:
    """
    lock_id = "lock:{}:{}".format('communication.tasks.harvest_mail_account', mail_account_id)
    task_id = cache.get(lock_id)
    # logger.debug("mail account lock id:{}  task id:{}".format(lock_id, task_id))
    return task_status(None, task_id)


@login_required()
def check_task_mail_account_status_all(request):
    """ A helper view to inform via ajax whether the all accounts mail harvest task is currently running.

    :param request:
    :return:
    """
    lock_id = "lock:{}".format('communication.tasks.harvest_mail')
    task_id = cache.get(lock_id)
    # logger.debug("all lock id:{}  task id:{}".format(lock_id, task_id))
    return task_status(None, task_id)



@login_required()
@permission_required('communication.add_mailaccount', raise_exception=True)
def initiate_gmail_auth(request):
    flow_args = {
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'scope': settings.GOOGLE_OAUTH2_SCOPES,
        'redirect_uri': communication.utils.comm_utils.get_google_oauth2_private_redirect_url(request),
    }
    if settings.GOOGLE_OAUTH2_PRIVATE_REDIRECT:
        flow_args['device_id'] = "asdfkasdfasdfasdfasdf"  # Random warblegarble
        flow_args['device_name'] = "Some cedar8 device"

    flow = OAuth2WebServerFlow(**flow_args)

    auth_uri = flow.step1_get_authorize_url()

    # Store the flow as a pickled string in cache keyed by the session_key
    cache.set("google_oauth2_flow_%s" % request.session.session_key, pickle.dumps(flow), 3600)
    
    return HttpResponseRedirect(auth_uri)


@login_required()
@permission_required('communication.add_mailaccount', raise_exception=True)
def authorize_gmail(request):
    # Fetch the pickle from cache.
    flow_pickle = cache.get("google_oauth2_flow_%s" % request.session.session_key, None)
    cache.delete("google_oauth2_flow_%s" % request.session.session_key)
    if flow_pickle is None:
        return redirect('communication:dashboard')

    
    flow = pickle.loads(flow_pickle)
    auth_code = request.GET.get('code', None)
    if auth_code is None:
        return redirect('communication:dashboard')

    logger.info("Successfully fetched auth code from google.  Attempting to exchange it for a refresh key...")

    # This breaks completely on production servers for some reason...
    # I have no idea why... and it inferiates me, but adding a print and pointless redirect here fixes this...
    #print('Pointless print that somehow helps make the auth_exchange work....')
    #redirect('communication:dashboard')
    credentials = flow.step2_exchange(auth_code)

    logger.info("Exchange completed.  Attempting to build mail account from credentials...")
    
    email = credentials.id_token['email']

    mail_account, created = MailAccount.objects.get_or_create(
        email_address=email,
        username=email,
        server_address='imap.gmail.com',
        protocol='gmail',
        ssl=True
    )

    logger.info("Mail account created.  Now creating credentials store for refresh key.")

    credentials_instance, created = GmailCredential.objects.get_or_create(
        mail_account=mail_account,
    )

    credentials_instance.credential = credentials
    credentials_instance.save()

    logger.info("Success!  Mail account configured for %s. Redirecting to success message." % email)

    return redirect('communication:authorize_gmail_success', credentials_id=credentials_instance.id)


@login_required()
@permission_required('communication.add_mailaccount', raise_exception=True)
def authorize_gmail_success(request, credentials_id):
    credentials_instance = GmailCredential.objects.get(id=credentials_id)
    credentials = credentials_instance.credential

    context = {
        'email': credentials.id_token['email']
    }

    return render(request=request, template_name='communication/authorize_gmail_success.html', context=context)


@login_required()
def serve_communication_log_file(request):
    #  TODO: Switch to newer CBV asset serve view.
    full_path = settings.LOGGING['handlers']['handler_for_communication']['filename']
    log_file = Path(full_path)

    if not log_file.is_file():
        raise FileNotFoundError("No log file found at the path: %s" % full_path)

    content_type = magic.from_file(full_path, mime=True)
    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(log_file.name)
    response['X-Sendfile'] = smart_str(full_path)

    return response


############################################################################
# Rest API Viewsets


class CommunicationViewSet(viewsets.ReadOnlyModelViewSet):
    '''
    When requested, this Viewset will return rendered html for the returned Communication instances.
    '''
    # queryset = Communication.objects.all()
    queryset = CommunicationRelation.objects.all()
    template_name = 'communication/communication_items.html'
    renderer_classes = (
        rest_framework.renderers.TemplateHTMLRenderer,  # having multiple renderers is not working as expected, comment-out
        # the html renderer if you need the browsable api.
        rest_framework.renderers.BrowsableAPIRenderer,
        rest_framework.renderers.JSONRenderer)

    # serializer_class = CommunicationSerializer
    serializer_class = CommunicationRelationSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('related_object_oid', 'related_object_ct')
    search_fields = ('comm__subject',)
    ordering_fields = ('comm__date',)
    ordering = ('-comm__date',)

    def get_queryset(self):
        '''
        Overrides get_queryset to allow filtering on comm__comm_type__model attribute.
        Looks for a url parameter "comm_type_model".
        :return:
        '''
        queryset = super(CommunicationViewSet, self).get_queryset()
        comm_type_model = self.request.query_params.get('comm_type_model', None)
        if comm_type_model:
            queryset = queryset.filter(comm__comm_type_ct__model=comm_type_model)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(CommunicationViewSet, self).list(request, *args, **kwargs)
        if request.accepted_renderer.format == 'html':
            # Get data: check if in "results" format, data set to list if so.
            if 'results' in response.data:
                response.data['results'] = list(response.data['results'])

            response = Response({'data': response.data}, template_name=self.template_name)

        return response
