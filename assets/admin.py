import os
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch

from .models import Asset, SecureAsset, AssetType, MetaDocumentSecureAsset, MetaDocumentAsset


class AssetTypeAdmin(admin.ModelAdmin):
    ordering = ('type_of_asset',)


class AssetAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Asset._meta.fields if field.name != "id"]
    readonly_fields = ('name', 'file_path', 'legacy_path')

    # exclude = ("file",)

    # Exclude the file on the change form:
    # Beware: doing this alters the form so that afterwards, when you
    # open an ADD form the file will be missing there too. So RE-Add the
    # file again on the add_view below.
    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.exclude = ('file',)
        return super(AssetAdmin, self).change_view(request, object_id, extra_context)

    # RE-include the file on the change form because it may have been
    # removed by the change_view form.
    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = None
        return super(AssetAdmin, self).add_view(request, form_url=form_url, extra_context=extra_context)

        # Use this function if we go with a custom model manager that
        # filters out unpublished stuff. Assumes model manager is called "admin_objects"

        # def get_queryset(self, request):
        #     # first see if the model has implemented the admin_objects
        #     # manager, if not, use the default object manager.
        #     try:
        #         qs = self.model.admin_objects.get_queryset()
        #     except:
        #         qs = self.model.objects.get_queryset()
        #
        #     # we need this from the superclass method
        #     ordering = self.ordering or ()  # otherwise we might try to *None, which is bad ;)
        #     if ordering:
        #         qs = qs.order_by(*ordering)
        #     return qs


class SecureAssetAdmin(admin.ModelAdmin):
    readonly_fields = ('name', "secure_link", 'legacy_path')

    # exclude = ("file",)

    def __init__(self, *args, **kwargs):
        super(SecureAssetAdmin, self).__init__(*args, **kwargs)
        self.list_display = self.get_list_display_fields()

    # Exclude the file on the change form:
    # Beware: doing this alters the form so that afterwards, when you
    # open an ADD form the file will be missing there too. So RE-Add the
    # file again on the add_view below.
    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.exclude = ('file',)
        return super(SecureAssetAdmin, self).change_view(request, object_id, extra_context)

    # RE-include the file on the change form because it may have been
    # removed by the change_view form.
    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = None
        return super(SecureAssetAdmin, self).add_view(request, form_url=form_url, extra_context=extra_context)

    # Set the NAME attribute in the save method only if the file itself has changed.
    def save_model(self, request, obj, form, change):
        if 'file' in form.changed_data:
            head, tail = os.path.split(obj.file.name)
            obj.name = tail
        obj.save()

    def secure_link(self, obj):
        try:
            return u"<a href='{}'>Download</a>".format(obj.url)
        except NoReverseMatch:
            return ""
    secure_link.allow_tags = True

    # Override the file attribute so we don't get a link that doesn't work:
    def file_path(self, obj):
        return obj.file.name

    # Use this method to build list_display instead of declaring at the top.
    # makes it overridable by child classes of this admin:
    def get_list_display_fields(self):
        list_display = [field.name for field in SecureAsset._meta.fields if field.name != "id"]
        list_display.append('secure_link')
        list_display.append('file_path')
        list_display.remove('file')
        list_display.remove('modified')  # This gets added anyways.. grr.
        return list_display


class SecureAssetAdminInline(admin.TabularInline):
    model = SecureAsset
    extra = 0
    fields = ['name', ]
    readonly_fields = ['name', 'secure_link']

    def secure_link(self, obj):
        try:
            return u"<a href='{}'>Download</a>".format(obj.url)
        except NoReverseMatch:
            return ""

    secure_link.allow_tags = True

    # def has_change_permission(self, request, obj=None):
    #     return False

# Register other models here.
admin.site.register(AssetType, AssetTypeAdmin)

# CB requested hiding these:
admin.site.register(SecureAsset, SecureAssetAdmin)
# admin.site.register(Asset, AssetAdmin)
admin.site.register(MetaDocumentSecureAsset)
admin.site.register(MetaDocumentAsset)