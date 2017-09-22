# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import library.models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0041_remove_item_content_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseBriefRelatedObjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('casebrief', models.ForeignKey(related_name='related_objects', to='library.CaseBrief')),
            ],
            bases=(library.models.GenericReferenceMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ItemRelatedObjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.ForeignKey(related_name='related_objects', to='library.Item')),
            ],
            bases=(library.models.GenericReferenceMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SynthesisRelatedObjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('synthesis', models.ForeignKey(related_name='related_objects', to='library.Synthesis')),
            ],
            bases=(library.models.GenericReferenceMixin, models.Model),
        ),
    ]
