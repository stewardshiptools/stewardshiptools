# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0006_auto_20170307_1421'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='cataloger',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL, related_name='library_item_cataloger_related', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='item',
            name='confidentiality',
            field=models.OneToOneField(to='library.Confidentiality', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='item',
            name='content_type',
            field=models.ForeignKey(null=True, blank=True, to='contenttypes.ContentType', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='item',
            name='holdings',
            field=models.OneToOneField(to='library.Holdings', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='item',
            name='researcher_notes',
            field=models.OneToOneField(to='library.ResearcherNotes', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='item',
            name='review',
            field=models.OneToOneField(to='library.Review', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='item',
            name='reviewer',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL, related_name='library_item_reviewer_related', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
