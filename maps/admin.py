from django.contrib import admin

from .models import LeafletMap, LeafletTileLayer, LeafletOverlayGeoinfoLayer, StyleCircle, StyleMarker, StylePolyline, \
    StylePolygon, CompositeStyle



def clone_map_object(modeladmin, request, queryset):
    for obj in queryset:
        # First remove the current pk
        obj.pk = None

        # Don't need to set this for maps
        if obj.__class__.__name__ != LeafletMap:
            obj.id = None

        # Identify a temporary unique machine_name
        i = 0
        copy_machine_name = "%s_%d" % (obj.machine_name, i)

        while LeafletTileLayer.objects.filter(machine_name=copy_machine_name).exists():
            i += 1
        # Give the copy its new unique machine_name and a new name to flag it as a copy.
        obj.machine_name = copy_machine_name
        obj.name = "Copy of %s" % obj.name
        obj.save()

    if queryset.count() == 1:
        message_bit = "1 layer was"
    else:
        message_bit = "%d layers were" % queryset.count()

    modeladmin.message_user(request, "%s successfully copied.  Please edit them and change the name, machine_name and "
                                     "other fields." % message_bit)

clone_map_object.short_description = "Clone selected map objects"


@admin.register(LeafletMap)
class LeafletMapAdmin(admin.ModelAdmin):
    list_display = ['name', 'machine_name', 'description']
    actions = [clone_map_object]
    clone_map_object.short_description = "Clone selected leaflet maps"


@admin.register(LeafletTileLayer)
class LeafletTileLayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'machine_name', 'description']

    actions = [clone_map_object]
    clone_map_object.short_description = "Clone selected leaflet tile layers"


@admin.register(LeafletOverlayGeoinfoLayer)
class LeafletOverlayGeoinfoLayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'geoinfo_layer', 'machine_name', 'description']

    actions = [clone_map_object]
    clone_map_object.short_description = "Clone selected leaflet geoinfo layers"


@admin.register(StyleCircle)
class StyleCircleLayerAdmin(admin.ModelAdmin):
    pass


@admin.register(StyleMarker)
class StyleMarkerLayerAdmin(admin.ModelAdmin):
    pass


@admin.register(StylePolyline)
class StylePolylineLayerAdmin(admin.ModelAdmin):
    pass


@admin.register(StylePolygon)
class StylePolygonLayerAdmin(admin.ModelAdmin):
    pass


@admin.register(CompositeStyle)
class CompositeStyleLayerAdmin(admin.ModelAdmin):
    pass
