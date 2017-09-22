import json
from django.db import models
from model_utils.managers import InheritanceManager
from django_hstore import hstore
from django.contrib.contenttypes.models import ContentType
from colorful.fields import RGBColorField

from geoinfo.models import GISLayerMaster

import maps


class LeafletMap(models.Model):
    name = models.CharField(max_length=100,
                            help_text="The name that will be shown to users.")
    machine_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Must be unique and comprised of letters, numbers, dashes, and underscores"
    )
    description = models.TextField(blank=True, null=True)
    base_layers = models.ManyToManyField(
        'LeafletBaseLayer',
        help_text="Choose the base layers that will be available."
    )
    default_base_layer = models.ForeignKey(
        'LeafletBaseLayer',
        related_name="default_base_layer",
        help_text="Which layer will be displayed by default? (Choose from those selected above.)"
    )
    available_overlay_layers = models.ManyToManyField(
        'LeafletOverlayLayer',
        related_name='available_overlay_layers',
        help_text="Choose the overlay layers that will be available (Displayed in the selector.)",
        blank=True
    )
    visible_overlay_layers = models.ManyToManyField(
        'LeafletOverlayLayer',
        related_name='visible_overlay_layers',
        help_text="Choose the overlay layers that will be displayed (Choose from those selected above.)",
        blank=True
    )
    default_center_lon = models.FloatField(default=-128)
    default_center_lat = models.FloatField(default=54.9)
    default_initial_zoom = models.PositiveSmallIntegerField(default=4)
    layer_control_collapsed = models.BooleanField(default=False)

    other_settings = hstore.DictionaryField(blank=True, null=True)

    objects = hstore.HStoreManager()

    def __str__(self):
        return self.name


class LeafletLayer(models.Model):
    name = models.CharField(max_length=100,
                            help_text="The name that will be shown to the user in layers switches, etc.")
    machine_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Must be unique and comprised of letters, numbers, dashes, and underscores"
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class LeafletBaseLayer(LeafletLayer):
    objects = InheritanceManager()

    def __str__(self):
        return self.name


class LeafletOverlayLayer(LeafletLayer):
    objects = InheritanceManager()

    def __str__(self):
        return self.name


class LeafletTileLayer(LeafletBaseLayer):
    url_template = models.CharField(
        max_length=1000,
        help_text="A string of the following form: 'http://{s}.somedomain.com/blabla/{z}/{x}/{y}.png'"
    )  # Quite a large limit but still well under max url lengths.
    attribution = models.CharField(max_length=500, blank=True, null=True)
    max_zoom = models.PositiveSmallIntegerField(blank=True, null=True)
    sub_domains = models.CharField(
        max_length=200,
        default='abc',
        help_text='Subdomains of the tile service. Can be passed in the form of one string (where each letter is a'
                  'subdomain name) or a comma separated list of strings.'
    )

    other_settings = hstore.DictionaryField(blank=True, null=True)

    objects = hstore.HStoreManager()

    def __str__(self):
        return self.name


class LeafletOverlayGeoinfoLayer(LeafletOverlayLayer):
    geoinfo_layer = models.ForeignKey(GISLayerMaster)

    def __str__(self):
        return self.name


class StyleAbstract(models.Model):
    style_name = models.CharField(max_length=50, blank=True, null=True)

    @property
    def leaflet_layer_type(self):
        return "undefined"

    def __str__(self):
        return "{} style {} {}".format(self.leaflet_layer_type, self.id, self.style_name or '')

    class Meta:
        abstract = True


class StylePathAbstract(StyleAbstract, models.Model):
    """
    Provides a selection of leaflet-compatible style fields
    Borrowed from AV's private repo
    """
    stroke = models.BooleanField(default=True, help_text="Whether to draw stroke along the path. "
                                                         "Set it to false to disable borders on polygons or circles.")
    color = RGBColorField(default='#1776ff', help_text="Stroke color")
    weight = models.FloatField(default=1, help_text="Stroke width in pixels")
    opacity = models.FloatField(default=1.0, help_text="Stroke opacity")

    class Meta:
        abstract = True


class StylePolylineAbstract(StylePathAbstract, models.Model):
    smoothFactor = models.FloatField(default=1.0, help_text='How much to simplify the polyline on each zoom level. '
                                                            'More means better performance and smoother look, and less '
                                                            'means more accurate representation. Applies to polygon and polyline')

    class Meta:
        abstract = True


class StylePolygon(StylePolylineAbstract, models.Model):
    """
    Represents a Polygon layer style
    """

    fill = models.BooleanField(default=True, help_text="Whether to fill the path with color. "
                                                       "Set it to false to disable filling on polygons or circles.")
    fillColor = RGBColorField(blank=True, null=True, help_text="Fill color. Defaults to the value of the color option")
    fillOpacity = models.FloatField(default=0.2, help_text="Fill opacity.")

    @property
    def leaflet_layer_type(self):
        return "polygon"

    class Meta:
        verbose_name = "Polygon Style"

    @property
    def json(self):
        return maps.serializers.StylePolygonModelSerializer(self).data


class StylePolyline(StylePolylineAbstract, models.Model):
    """
    Represents a Polyline layer style
    """

    @property
    def leaflet_layer_type(self):
        return "polyline"

    class Meta:
        verbose_name = "Line Style"

    @property
    def json(self):
        return maps.serializers.StylePolylineModelSerializer(self).data


class StyleCircle(StylePathAbstract, models.Model):
    """
    Can represent a Circle or a CircleMarker layer style, they're pretty much the same except
    for the units that define the radius
    """
    layer_type_choices = (
        ('circleMarker', 'CircleMarker'),
        ('circle', 'Circle'),
    )

    layer_type = models.CharField(max_length=20, choices=layer_type_choices, default='circleMarker')
    radius = models.FloatField(default=10, blank=True, null=True, help_text="CircleMarker Radius: units in PIXELS. "
                                                                            "Circle Radius: units is METERS.")

    class Meta:
        verbose_name = "Circle Style"

    @property
    def leaflet_layer_type(self):
        return self.layer_type

    @property
    def json(self):
        return maps.serializers.StyleCircleModelSerializer(self).data


class StyleMarker(StyleAbstract, models.Model):
    """
    Represents a Marker layer style
    Roll with this guy's tweak to the leaflet awesome lib:
        https://github.com/bhaskarvk/Leaflet.awesome-markers
    """
    marker_color_choices = (
        ('red', 'red'),
        ('darkred', 'darkred'),
        ('lightred', 'lightred'),
        ('orange', 'orange'),
        ('beige', 'beige'),
        ('green', 'green'),
        ('darkgreen', 'darkgreen'),
        ('lightgreen', 'lightgreen'),
        ('blue', 'blue'),
        ('darkblue', 'darkblue'),
        ('lightblue', 'lightblue'),
        ('purple', 'purple'),
        ('darkpurple', 'darkpurple'),
        ('pink', 'pink'),
        ('cadetblue', 'cadetblue'),
        ('white', 'white'),
        ('gray', 'gray'),
        ('lightgray', 'lightgray'),
        ('black', 'black'),
    )

    identifier = models.CharField(max_length=300, help_text="The identifier used by the font library for this icon."
                                                            "If using Font-Awesome, refer to the font-awesome documentation.")
    markerColor = models.CharField(max_length=30, choices=marker_color_choices)
    iconColor = RGBColorField(default='#819CFF', help_text="Stroke color")
    square = models.BooleanField(default=False, help_text="Defaults to False (ie rounded), True makes it a square-ish icon.")
    prefix = models.CharField(max_length=20, default='fa', help_text="Icon library set prefix. 'fa' for font-awesome or 'glyphicon' for bootstrap 3.")

    @property
    def leaflet_layer_type(self):
        return "fa-marker"

    @property
    def className(self):
        if self.square:
            return 'awesome-marker awesome-marker-square'
        else:
            return 'awesome-marker'

    class Meta:
        verbose_name = "Marker Style"

    @property
    def json(self):
        return maps.serializers.StyleMarkerModelSerializer(self).data
    

class CompositeStyle(StyleAbstract, models.Model):
    # polygon_style = models.ForeignKey('StylePolygon', null=True, blank=True)
    polyline_style = models.ForeignKey('StylePolyline', null=True, blank=True)
    marker_style = models.ForeignKey('StyleMarker', null=True, blank=True)

    # circle_style = models.ForeignKey('StyleCircle', null=True, blank=True)

    class Meta:
        verbose_name = "Composite Style"

    @property
    def leaflet_layer_type(self):
        return 'composite'

    def __str__(self):
        styles = []
        # if self.polygon_style:
        #     styles.append(str(self.polygon_style))
        # if self.polyline_style:
        #     styles.append(str(self.polygon_style))
        # if self.marker_style or self.circle_style:
        #     styles.append(str(self.marker_style or self.circle_style))

        if self.polyline_style:
            styles.append(str(self.polyline_style))
        if self.marker_style:
            styles.append(str(self.marker_style))

        return "{} style {} {}. {}".format(self.leaflet_layer_type, self.id, self.style_name or '', ", ".join(styles))

    @property
    def json(self):
        # todo hack alert: couldn't make this stop returning OrderedDicts instead of proper json
        return json.dumps(maps.serializers.CompositeStyleModelSerializer(self).data)
