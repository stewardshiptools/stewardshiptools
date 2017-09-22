# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import colorful.fields


class Migration(migrations.Migration):
    dependencies = [
        ('maps', '0017_auto_20160922_1932'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompositeStyle',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
            options={
                'verbose_name': 'Composite Style',
            },
        ),
        migrations.CreateModel(
            name='StyleCircle',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('stroke',
                 models.BooleanField(help_text='Whether to draw stroke along the path. Set it to false to disable borders on polygons or circles.',
                                     default=True)),
                ('color', colorful.fields.RGBColorField(help_text='Stroke color', default='#1776ff')),
                ('weight', models.FloatField(help_text='Stroke width in pixels', default=1)),
                ('opacity', models.FloatField(help_text='Stroke opacity', default=1.0)),
                ('fill',
                 models.BooleanField(help_text='Whether to fill the path with color. Set it to false to disable filling on polygons or circles.',
                                     default=True)),
                (
                'fillColor', colorful.fields.RGBColorField(help_text='Fill color. Defaults to the value of the color option', null=True, blank=True)),
                ('fillOpacity', models.FloatField(help_text='Fill opacity.', default=0.2)),
                ('layer_type',
                 models.CharField(max_length=20, default='circleMarker', choices=[('circleMarker', 'CircleMarker'), ('circle', 'Circle')])),
                ('radius', models.FloatField(help_text='CircleMarker Radius: units in METERS. Circle Radius: units is PIXELS.', null=True, default=10,
                                             blank=True)),
            ],
            options={
                'verbose_name': 'Circle Style',
            },
        ),
        migrations.CreateModel(
            name='StyleMarker',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('identifier', models.CharField(max_length=300,
                                                help_text='The identifier used by the font library for this icon.If using Font-Awesome, refer to the font-awesome documentation.')),
                ('markerColor', models.CharField(max_length=30,
                                                 choices=[('red', 'red'), ('darkred', 'darkred'), ('lightred', 'lightred'), ('orange', 'orange'),
                                                          ('beige', 'beige'), ('green', 'green'), ('darkgreen', 'darkgreen'),
                                                          ('lightgreen', 'lightgreen'), ('blue', 'blue'), ('darkblue', 'darkblue'),
                                                          ('lightblue', 'lightblue'), ('purple', 'purple'), ('darkpurple', 'darkpurple'),
                                                          ('pink', 'pink'), ('cadetblue', 'cadetblue'), ('white', 'white'), ('gray', 'gray'),
                                                          ('lightgray', 'lightgray'), ('black', 'black')])),
                ('iconColor', colorful.fields.RGBColorField(help_text='Stroke color', default='#819CFF')),
                ('square', models.BooleanField(help_text='Defaults to False (ie rounded), True makes it a square-ish icon.', default=False)),
            ],
            options={
                'verbose_name': 'Marker Style',
            },
        ),
        migrations.CreateModel(
            name='StylePolygon',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('stroke',
                 models.BooleanField(help_text='Whether to draw stroke along the path. Set it to false to disable borders on polygons or circles.',
                                     default=True)),
                ('color', colorful.fields.RGBColorField(help_text='Stroke color', default='#1776ff')),
                ('weight', models.FloatField(help_text='Stroke width in pixels', default=1)),
                ('opacity', models.FloatField(help_text='Stroke opacity', default=1.0)),
                ('fill',
                 models.BooleanField(help_text='Whether to fill the path with color. Set it to false to disable filling on polygons or circles.',
                                     default=True)),
                (
                'fillColor', colorful.fields.RGBColorField(help_text='Fill color. Defaults to the value of the color option', null=True, blank=True)),
                ('fillOpacity', models.FloatField(help_text='Fill opacity.', default=0.2)),
                ('smoothFactor', models.FloatField(
                    help_text='How much to simplify the polyline on each zoom level. More means better performance and smoother look, and less means more accurate representation. Applies to polygon and polyline',
                    default=1.0)),
            ],
            options={
                'verbose_name': 'Polygon Style',
            },
        ),
        migrations.CreateModel(
            name='StylePolyline',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('stroke',
                 models.BooleanField(help_text='Whether to draw stroke along the path. Set it to false to disable borders on polygons or circles.',
                                     default=True)),
                ('color', colorful.fields.RGBColorField(help_text='Stroke color', default='#1776ff')),
                ('weight', models.FloatField(help_text='Stroke width in pixels', default=1)),
                ('opacity', models.FloatField(help_text='Stroke opacity', default=1.0)),
                ('fill',
                 models.BooleanField(help_text='Whether to fill the path with color. Set it to false to disable filling on polygons or circles.',
                                     default=True)),
                (
                'fillColor', colorful.fields.RGBColorField(help_text='Fill color. Defaults to the value of the color option', null=True, blank=True)),
                ('fillOpacity', models.FloatField(help_text='Fill opacity.', default=0.2)),
                ('smoothFactor', models.FloatField(
                    help_text='How much to simplify the polyline on each zoom level. More means better performance and smoother look, and less means more accurate representation. Applies to polygon and polyline',
                    default=1.0)),
            ],
            options={
                'verbose_name': 'Line Style',
            },
        ),
        migrations.AddField(
            model_name='compositestyle',
            name='circle_style',
            field=models.ForeignKey(to='maps.StyleCircle', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='compositestyle',
            name='marker_style',
            field=models.ForeignKey(to='maps.StyleMarker', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='compositestyle',
            name='polygon_style',
            field=models.ForeignKey(to='maps.StylePolygon', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='compositestyle',
            name='polyline_style',
            field=models.ForeignKey(to='maps.StylePolyline', blank=True, null=True),
        ),
    ]
