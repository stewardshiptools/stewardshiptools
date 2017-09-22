from django.contrib import admin
from django.db.models import Max
from assets.admin import SecureAssetAdmin
from mptt.admin import MPTTModelAdmin

from .models import DevelopmentProject, ConsultationStage, DevelopmentProjectAsset, DevelopmentGISLayer, FileNo, \
    FilingCode, DevelopmentProjectAction

# from geoinfo.forms import GISLayerAdminForm
from .forms import DevelopmentProjectGISLayerForm, DevelopmentProjectForm


# Not used due to weirdness with draw widget.
class DevelopmentGISLayerInline(admin.StackedInline):
    model = DevelopmentGISLayer
    form = DevelopmentProjectGISLayerForm
    extra = 0


# @admin.register(DevelopmentProject)
# class DevelopmentProjectAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in DevelopmentProject._meta.fields if field.name != 'id']
#
#     # inlines = [DevelopmentGISLayerInline]
#
#     def get_form(self, request, obj=None, **kwargs):
#         form = super(DevelopmentProjectAdmin, self).get_form(request, obj, **kwargs)
#
#         # cedar_project_code will disappear if modifying the form (readonly!)
#         # ---NOTE: this doesn't actually do anything does it?
#
#         if 'cedar_project_code' in form.base_fields.keys():
#             form.base_fields['cedar_project_code'].initial = DevelopmentProject.suggest_new_project_code()
#
#         return form


@admin.register(ConsultationStage)
class ConsultationStageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ConsultationStage._meta.fields if field.name != "id"]


@admin.register(DevelopmentGISLayer)
class DevelopmentGISLayerAdmin(admin.ModelAdmin):
    readonly_fields = ('project',)

    # The DevelopmentProjectGISLayerForm has some validation that is needed
    # but it needs to know the Dev't Project ID BEFORE instantiation. This
    # creates a problem for the createview in the admin pages. Going with
    # default admin form for now.
    # form = DevelopmentProjectGISLayerForm

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()


@admin.register(DevelopmentProject)
class DevelopmentProjectAdmin(admin.ModelAdmin):
    form = DevelopmentProjectForm
    list_filter = (
        'status',
        'final_decision',
    )


@admin.register(FilingCode)
class FilingCodeAdmin(MPTTModelAdmin):
    pass


@admin.register(FileNo)
class FilingCodeAdmin(admin.ModelAdmin):
    list_display = (
        'file_number',
        'organization',
        'project'
    )
    list_filter = (
        'organization',
    )
    search_fields = [
        'file_number',
        'organization__name',
        'project__cedar_project_name'
    ]

@admin.register(DevelopmentProjectAction)
class DevelopmentProjectActionAdmin(admin.ModelAdmin):
    list_display = ['label', 'date', 'project']


# admin.site.register(DevelopmentProjectAsset, DevelopmentProjectAssetAdmin)
#admin.site.register(DevelopmentProject)
# admin.site.register(FileNo)
