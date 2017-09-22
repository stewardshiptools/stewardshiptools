from datetime import datetime
from django.utils import timezone
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.forms import generic_inlineformset_factory

from communication.models import MailAccount, Mailbox, Communication, HarvestCodePrefix
import communication

from assets.forms import SecureAssetForm
from assets.models import AssetType


class MailAccountAdminForm(forms.ModelForm):
    class Meta:
        model = MailAccount
        fields = '__all__'
        widgets = {
            'password': forms.widgets.PasswordInput(render_value=True)
        }


class MailboxAdminForm(forms.ModelForm):
    class Meta:
        model = Mailbox
        fields = ('mail_account', 'folder_name', 'active', 'incoming')
        widgets = {
            'password': forms.widgets.PasswordInput(render_value=True)
        }


class HarvestCodePrefixForm(forms.ModelForm):
    '''
    This is broken and being left as-is for now.
    '''

    def __init__(self, *args, **kwargs):
        super(HarvestCodePrefixForm, self).__init__(*args, **kwargs)
        self.fields['mailboxes'].required = False

        if kwargs.get('instance', None) is None:
            self.fields['active'].initial = True


    def clean_mailboxes(self):
        '''
        Sets related mailboxes to ALL mailboxes
        :return:
        '''
        return Mailbox.objects.all()

    # def clean(self):
    #     cleaned_data = super(HarvestCodePrefixForm, self).clean()
    #     mb = cleaned_data.get('mailboxes')
    #     return cleaned_data

    class Meta:
        model = HarvestCodePrefix
        fields = '__all__'


class CommunicationAssetForm(SecureAssetForm):

    def __init__(self, *args, **kwargs):
        super(CommunicationAssetForm, self).__init__(*args, **kwargs)

        self.fields['asset_type'].widget = forms.HiddenInput()
        self.fields['asset_type'].initial = AssetType.objects.get(type_of_asset='Document')

        self.fields['comment'].widget = forms.HiddenInput()

    class Meta(SecureAssetForm.Meta):
        model = communication.models.CommunicationAsset


class CommunicationForm(forms.ModelForm):
    '''
    Splits the datetime field into two fields managed by separate materialized widgets:
        time_picker, date_picker.
    So far this should only be used as an inline for each of the various communication type model forms
    '''
    time_picker = forms.TimeField(
        label='Time',
        initial=timezone.localtime(timezone.now()).time().strftime('%I:%M%p'),
        input_formats=[
            '%H:%M:%S',  # '14:30:59'
            '%H:%M',  # '14:30',
            '%I:%M%p',  # '5:30 AM',
        ]
    )
    date_picker = forms.DateField(
        label='Date',
        initial=timezone.now().date()
    )

    def __init__(self, *args, **kwargs):
        super(CommunicationForm, self).__init__(*args, **kwargs)

        # set date field to not required, we will set it's value in the clean via the time/date picker values.
        self.fields['date'].required = False

    def clean_date(self):
        date = self.cleaned_data.get("date_picker")
        time = self.cleaned_data.get("time_picker")
        try:
            date_and_time = datetime.combine(date, time)
            return date_and_time
        except TypeError as err:
            raise forms.ValidationError("Failed to validate datetime:", str(err))

    class Meta:
        model = Communication
        fields = ('subject', 'time_picker', 'date_picker', 'date', 'from_contacts', 'to_contacts', 'comm_type_ct', 'comm_type_oid')


class CommunicationTypeAbstractForm(forms.ModelForm):
    '''
    Used as a super class for creating communication type instances (PhoneCall, Fax, etc.)
    Form expects two kwargs that set the related object (eg Dev't Project):
        related_ct_id -- the content type of the related object
        related_oid -- the ID of the related object.

    This should have been a mixin, but... problems.
    '''

    def __init__(self, *args, **kwargs):
        self.related_ct_id = kwargs.pop('related_ct_id', None)
        self.related_oid = kwargs.pop('related_oid', None)

        if self.related_ct_id is None:
            raise TypeError('related_ct_id is a required kwarg of CommunicationTypeAbstractForm')
        elif self.related_oid is None:
            raise TypeError('related_oid is a required kwarg of CommunicationTypeAbstractForm')

        super(CommunicationTypeAbstractForm, self).__init__(*args, **kwargs)


class PhoneCallForm(CommunicationTypeAbstractForm):
    class Meta:
        model = communication.models.PhoneCall
        fields = ('duration', 'from_number', 'to_number', 'notes')


class FaxForm(CommunicationTypeAbstractForm):
    class Meta:
        model = communication.models.Fax
        fields = ('from_number', 'to_number', 'document')


class LetterForm(CommunicationTypeAbstractForm):
    class Meta:
        model = communication.models.Letter
        fields = ('document',)


CommunicationGenericFormset = generic_inlineformset_factory(
    communication.models.Communication,
    form=CommunicationForm,
    ct_field='comm_type_ct',
    fk_field='comm_type_oid',
    extra=1,
    max_num=1,
    validate_max=True,
    can_delete=False,

)