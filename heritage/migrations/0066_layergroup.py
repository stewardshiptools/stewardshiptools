# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0065_remove_heritagegislayer_session'),
    ]

    operations = [
        migrations.CreateModel(
            name='LayerGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(null=True, max_length=200, blank=True)),
                ('data', django_hstore.fields.DictionaryField(null=True, blank=True)),
                ('interview', models.ForeignKey(to='heritage.Interview')),
            ],
        ),
    ]
