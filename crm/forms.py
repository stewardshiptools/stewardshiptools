import re

from django.forms.models import BaseInlineFormSet
from django.forms import ModelForm, DateField, DateInput, ModelMultipleChoiceField, CharField
import django.forms
from django.forms import ValidationError

from .models import Person, Organization, AlternateName


class PersonAdminInlineFormSet(BaseInlineFormSet):
    """
    See: http://stackoverflow.com/questions/5648563/django-forcing-admin-users-to-enter-at-least-one-item-in-tabularinline?lq=1
    """
    def __init__(self, *args, **kwargs):
        super(PersonAdminInlineFormSet, self).__init__(*args, **kwargs)
        # Set initial values: -- didn't suit my purposes, leave for future reference.
        # self.initial = [{'name_first': 'firstnameplaceholder', 'name_last': 'lastnameplaceholder'},]

        # REQUIRE at least one of these inlines to be submitted, uncomment the following
        # clean method:
        # def clean(self):
        #     """Check that at least one inline has been entered."""
        #     super(PersonAdminInlineFormSet, self).clean()
        #     if any(self.errors):
        #         return
        #     if not any(cleaned_data and not cleaned_data.get('DELETE', False)
        #         for cleaned_data in self.cleaned_data):
        #         raise ValidationError('Please enter the required crm information below.')


        # def save_new(self, form, commit=True):
        #     return super(PersonAdminInlineFormSet, self).save_new(form, commit=commit)
        #
        # def save_existing(self, form, instance, commit=True):
        #     request = self.request.user
        #     return form.save(commit=commit)
        #


class PersonSettingsForm(ModelForm):
    """
    The person settings form is used only for when a auth.User
    is updating their settings via the cedar8 interface. Some crm.Person fields
    are hidden and values a automatically taken from auth.User fields:
    """
    def clean(self):
        super(PersonSettingsForm, self).clean()

    class Meta:
        model = Person
        # fields = "__all__"
        exclude = ('name_first',
                   'name_last',
                   'email',)


class PersonForm(ModelForm):
    alternate_names = CharField(required=False, help_text="Enter a list of alternate names separated by commas.")

    class Meta:
        model = Person
        fields = (
            'name_first',
            'name_last',
            'name_suffix',
            'initials',
            'indigenous_name',
            'alternate_names',
            'date_of_birth',
            'gender',
            'mentor_name',
            'mentor_relationship',
            'email',
            'phone',
            'alt_phone',
            'address',
            'organizations',
            'roles',
            'bio',
            'notes',
            'clan_family',
            'pic'
        )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            initial_alternate_names = [x.name for x in AlternateName.objects.filter(person__pk=instance.pk)]

            kwargs.update(initial={
                'alternate_names': ', '.join(initial_alternate_names)
            })

        super(PersonForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        form = super(PersonForm, self).save(commit=commit)  # Save the Person as normal

        # Now... process the alternate_names field
        alternate_names = re.split(r'\s*,\s*', self.cleaned_data['alternate_names'])
        existing_names = AlternateName.objects.filter(person__pk=form.pk, name__in=alternate_names)

        # Delete names that no longer show up in the field.
        names_to_delete = AlternateName.objects.exclude(person__pk=form.pk, name__in=alternate_names)
        names_to_delete.delete()

        for name in alternate_names:
            # If a name doesn't already exist, create it.
            if not existing_names.filter(name=name).exists():
                AlternateName.objects.create(
                    person=form,
                    name=name
                )

        return form


class OrganizationForm(ModelForm):
    members = ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        required=False
    )
    website = django.forms.URLField(
        max_length=200,
        widget=django.forms.TextInput,
        required=False
    )

    def __init__(self, *args, **kwgargs):
        persons = kwgargs.pop('persons', None)
        super(OrganizationForm, self).__init__(*args, **kwgargs)

        if persons is None:
            self.fields['members'].queryset = Person.objects.all()
            self.fields['members'].initial = Person.objects.none()
        else:
            self.fields['members'].queryset = Person.objects.all()
            self.fields['members'].initial = persons

    def save(self, commit=True):
        saved = super(OrganizationForm, self).save(commit)

        # Wipe out the previous m2m relations:
        self.instance.person_set.clear()

        # Add persons to the org:
        self.instance.person_set.add(*self.cleaned_data['members'].values_list('id', flat=True))

        return saved

    class Meta:
        model = Organization
        fields = '__all__'
