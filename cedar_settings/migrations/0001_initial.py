# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralSetting',
            fields=[
                ('name', models.CharField(unique=True, primary_key=True, max_length=200, serialize=False)),
                ('data_type', models.CharField(default='text', choices=[('text', 'Text'), ('int', 'Integer'), ('float', 'Float'), ('boolean', 'Boolean'), ('reference', 'Reference')], max_length=200)),
                ('text_value', models.TextField(blank=True, null=True)),
                ('int_value', models.IntegerField(blank=True, null=True)),
                ('float_value', models.FloatField(blank=True, null=True)),
                ('boolean_value', models.BooleanField(default=False)),
                ('reference_id', models.PositiveIntegerField(blank=True, null=True)),
                ('reference_ct', models.ForeignKey(to='contenttypes.ContentType', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
