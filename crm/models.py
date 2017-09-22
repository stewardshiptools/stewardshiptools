from phonenumber_field.modelfields import PhoneNumberField
import datetime

from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from django_hstore.hstore import DictionaryField, HStoreManager

from cedar.fields import StrippedCharField

class Role(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Organization(models.Model):
    # name = models.CharField('Name', max_length=100, blank=False)
    name = StrippedCharField('Name', max_length=100, blank=False)
    # todo Are we happy with a single field for storing addresses? Break them out more?
    mailing_address = models.TextField('Mailing address', max_length=300, blank=True, null=True)
    office_address = models.TextField('Office address', max_length=300, blank=True, null=True)
    email = models.EmailField('Email', blank=True, null=True)
    website = models.URLField('Website', blank=True, null=True)
    phone = PhoneNumberField('Phone', blank=True, null=True)
    fax = PhoneNumberField('Fax', blank=True, null=True)
    notes = models.TextField('Notes', blank=True, null=True)

    extra_info = DictionaryField(blank=True, null=True)

    objects = HStoreManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('crm:organization-detail', args=[str(self.id)])

    class Meta:
        ordering = ('name',)


class Person(models.Model):
    user_account = models.OneToOneField(User, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="User account",
                                        help_text="The internal user account for this person.")
    year_choices = []
    for r in range(1890, (datetime.datetime.now().year + 1)):
            year_choices.append((r,r))

    gender_choices = (('Male', 'M'), ('Female', 'F'), ('Other', 'other'))

    name_first = StrippedCharField('First Name', max_length=100, blank=False)
    name_last = StrippedCharField('Last Name', max_length=100, blank=False)
    name_suffix = StrippedCharField('Suffix', max_length=10, blank=True, null=True)
    initials = StrippedCharField('Initials', max_length=10, blank=True, null=True)
    indigenous_name = StrippedCharField('Indigenous name', max_length=100, blank=True, null=True)
    year_of_birth = models.PositiveIntegerField(blank=True, null=True, choices=year_choices, default=datetime.datetime.now().year)
    date_of_birth = models.DateField("Date of Birth", blank=True, null=True)
    gender = models.CharField(max_length=50, choices=gender_choices, blank=True, null=True)
    mentor_name = StrippedCharField(max_length=250, blank=True, null=True)
    mentor_relationship = StrippedCharField(max_length=250, blank=True, null=True)
    email = models.EmailField('Email', blank=True)
    # todo Is this overkill? A simple string preferable? https://github.com/stefanfoulis/django-phonenumber-field.
    phone = PhoneNumberField('Phone', blank=True, null=True)
    alt_phone = PhoneNumberField('Alternate phone', blank=True)
    address = models.TextField("Address", max_length=250, blank=True, null=True)
    organizations = models.ManyToManyField(Organization, blank=True)
    roles = models.ManyToManyField(Role, blank=True)
    bio = models.TextField('Bio', blank=True)
    notes = models.TextField('Notes', blank=True)
    clan_family = StrippedCharField('Clan/Family', blank=True, null=True, max_length=100)
    pic = models.ImageField(blank=True, verbose_name="Profile photo")

    extra_info = DictionaryField(blank=True, null=True)

    objects = HStoreManager()

    def __str__(self):
        return self.name

    @property
    def name(self):
        if self.name_suffix:
            return "%s %s %s" % (self.name_first, self.name_last, self.name_suffix)
        return "%s %s" % (self.name_first, self.name_last)

    def get_absolute_url(self):
        return reverse('crm:person-detail', kwargs={"pk": self.pk})

    def roles_list(self):
        return ', '.join(map(lambda x: x.name, self.roles.all()))

    roles_list.short_description = 'Roles'


class AlternateName(models.Model):
    person = models.ForeignKey('Person')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)


class UserPersonProxy(User):
    """
    A cheap user proxy model that we can use to get crm.Person info (eg __str__)
    for Users when they are available and fall back to User when not.
    Created for use in a user select dropdown list so we can see the crm.Person
    profile name instead of the user name (in cases where a user has a crm.Person profile).
    
    Currently in use on library.models.Item
    
    USAGE: 
        # Get an instance in a view:
        UserPersonProxy(self.request.user.id)
            
    """
    class Meta:
        proxy = True

    def __str__(self):
        try:
            return str(self.person)
        except ObjectDoesNotExist:
            """
            Use the generic object does not exist to handle RelatedObjectDoesNotExist exception
            """
            return super(UserPersonProxy, self).__str__()

    @classmethod
    def get_from_user_object(cls, user):
        """
        returns a UserPersonProxy instance from a User instance
        :param user: 
        :return: 
        """
        return cls.objects.get(id=user.id)
