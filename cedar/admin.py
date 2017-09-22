from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


from .forms import UserAdminForm

from crm.admin import PersonAdminInline
from security.models import SecurityLevel


# Wow what a pain. In order to make first_name, last_name REQUIRED fields I
# has to rebuild the whole User admin page.
class CedarUserAdmin(UserAdmin):
    form = UserAdminForm

    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (None, {
            'fields': ('username', 'first_name', 'last_name', 'email', 'password', 'security_level')
        }),
        ('Status', {
            'fields': ('date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Groups and Permissions', {
            # 'classes': ('collapse',),
            'fields': ('groups', 'user_permissions',),
        }),
    )

    inlines = (PersonAdminInline,)

    def __init__(self, *args, **kwargs):
        super(CedarUserAdmin, self).__init__(*args, **kwargs)
        self.list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff', 'security_level')
        # self.fields['password'].widget = ReadOnlyPasswordHashWidget

    def security_level(self, obj):
        security_level = SecurityLevel.objects.get_for_object(obj)
        if security_level is not None:
            return security_level.level
        level_range = [x[0] for x in SecurityLevel.level_choices]
        return max(level_range)  # Default users to the lowest security level.
    security_level.short_description = "Security level"

    def get_fields(self, request, obj=None):
        return super(UserAdmin, self).get_fields(request, obj)

    # def save_formset(self, request, form, formset, change):
    #     instances = formset.save(commit=False)
    #     for instance in instances:
    #         # Instance == crm.Person instance.
    #         # Override the crm.Person first_name, last_name, email:
    #
    #         instance.save()
    #     formset.save_m2m()

    # Hide the crm.Person inline form when add user is doing the password form:
    def get_inline_instances(self, request, obj=None):
        # return super(UserAdminForm, self).get_inline_instances(self, request, obj=None)
        return obj and super(CedarUserAdmin, self).get_inline_instances(request, obj) or []

        # def get_inline_formsets(self, request, formsets, inline_instances,
        #                     obj=None):
        #     return super(CedarUserAdmin, self).get_inline_formsets(request, formsets, inline_instances, obj)


admin.site.unregister(User)
admin.site.register(User, CedarUserAdmin)

#######################################################
# HIDE DJANGO-FILER MGMT:
#   We are not actually using a django-filer field
#   when we go to build a new db, all references
#   to django-filer need to be removed.
#######################################################

from filer.models import File, Folder, FolderPermission

# UNREGISTER DJANGO FILER:
admin.site.unregister(File)
admin.site.unregister(Folder)
admin.site.unregister(FolderPermission)
