from os.path import join
from email.mime.image import MIMEImage

from django.conf import settings
from django.forms import ModelForm, ValidationError, ChoiceField
from django.forms.models import BaseInlineFormSet
from django.forms.models import inlineformset_factory
from django.contrib.auth.forms import ReadOnlyPasswordHashWidget, ReadOnlyPasswordHashField, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template import loader

from crm.models import Person
from crm.forms import PersonSettingsForm

from django.contrib.auth.models import User
from security.forms import SecurityLevelModelFormMixin
from security.models import SecurityLevel


class UserAdminForm(SecurityLevelModelFormMixin, ModelForm):
    """
    Override the user admin form so that we can force firstname, lastname
    to be required --- needed for pushing changes over to crm.Person.
    """
    password = ReadOnlyPasswordHashField(label=("Password"),
                                         help_text=("Raw passwords are not stored, so there is no way to see "
                                                    "this user's password, but you can change the password "
                                                    "using <a href=\"password/\">this form</a>."))

    # Need to minimally declare security_level here so that the user admin can see it.
    # The mixin will take care of details.
    security_level = ChoiceField()

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        # self.fields['password'].widget = ReadOnlyPasswordHashWidget()

    def get_security_level_default(self):
        level_range = [x[0] for x in SecurityLevel.level_choices]
        return max(level_range)  # Default users to the lowest security level.

    class Meta:
        model = User
        fields = '__all__'


class UserSettingsForm(ModelForm):
    """
    This is the form used by the user menu to update user
    profile settings. hides user password (for now).
    """
    def __init__(self, *args, **kwargs):
        super(UserSettingsForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ('first_name',
                  'last_name',
                  'email',)


class CedarPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')
            email_message.mixed_subtype = 'related'

            with open(join(settings.STATIC_ROOT, 'css/cedarbox_icon_gry.png'), 'rb') as fp:
                logo_img = MIMEImage(fp.read())
                logo_img.add_header('Content-ID', '<{}>'.format('cedarbox_icon_gry.png'))
                email_message.attach(logo_img)

        email_message.send()

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        # If domain_override hasn't been provided.  Let's override it ourself using the request.
        if domain_override is None and request is not None:
            domain_override = request.META['HTTP_HOST']

        return super(CedarPasswordResetForm, self).save(
            domain_override=domain_override,
            subject_template_name=subject_template_name,
            email_template_name=email_template_name,
            use_https=use_https, token_generator=token_generator,
            from_email=from_email, request=request, html_email_template_name=html_email_template_name
        )


UserSettingsFormset = inlineformset_factory(User,
                                            Person,
                                            form=PersonSettingsForm,
                                            extra=1
                                            )
