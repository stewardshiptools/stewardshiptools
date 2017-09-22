from django.contrib import admin

from .forms import GISLayerAdminForm

from .models import GISLayer, GISFeaturePoint, GISFeatureLine, GISFeaturePolygon, SpatialReport, SpatialReportItem
from .models import DBView


@admin.register(SpatialReportItem)
class SpatialReportItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'report']


class SpatialReportItemInline(admin.StackedInline):
    model = SpatialReportItem
    extra = 0


@admin.register(SpatialReport)
class SpatialReportAdmin(admin.ModelAdmin):
    inlines = [SpatialReportItemInline]


@admin.register(GISLayer)
class GISLayerAdmin(admin.ModelAdmin):
    form = GISLayerAdminForm

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()


admin.site.register(GISFeaturePoint)
admin.site.register(GISFeatureLine)
admin.site.register(GISFeaturePolygon)

admin.site.register(DBView)
