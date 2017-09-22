from django.contrib import admin

# Register your models here.
from .models import Person
from .models import Role
from .models import Organization
from .models import AlternateName

from .forms import PersonAdminInlineFormSet


class AlternateNameInline(admin.TabularInline):
    model = AlternateName


# http://stackoverflow.com/questions/163823/can-list-display-in-a-django-modeladmin-display-attributes-of-foreignkey-field?lq=1
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'roles_list', 'initials', 'username']
    list_filter = ['roles']
    search_fields = ('name_first', 'name_last', 'roles__name', 'initials', 'user_account__username')
    ordering = ('name_last', 'name_first')
    inlines = [AlternateNameInline]

    def name(self, obj):
        if obj.name_suffix:
            return "%s %s %s" % (obj.name_first, obj.name_last, obj.name_suffix)
        else:
            return "%s %s" % (obj.name_first, obj.name_last)

    def username(self, obj):
        if obj.user_account:
            return obj.user_account.username
        else:
            return ""

    name.admin_order_field = 'name_last'
    name.short_description = 'Name'

    username.admin_order_field = 'user_account'  # Allows column order sorting
    username.short_description = 'User Account'  # Renames column head


# The stacked inline is to be used on the user auth admin page.
class PersonAdminInline(admin.StackedInline):
    model = Person
    formset = PersonAdminInlineFormSet
    extra = 1
    max_num = 1
    verbose_name = "CRM Profile Details"
    can_delete = False

    # Exclude fields that will be set by the User admin form save:
    # exclude = ['name_first', 'name_last', 'email']


class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


admin.site.register(Person, PersonAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Organization)
