# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import model_utils.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0016_casebrieftag_casebrieftaggeditem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='casebrief',
            name='keywords',
        ),
        migrations.AddField(
            model_name='casebrief',
            name='created',
            field=model_utils.fields.AutoCreatedField(editable=False, default=django.utils.timezone.now, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='casebrief',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(editable=False, default=django.utils.timezone.now, verbose_name='modified'),
        ),
        migrations.AlterField(
            model_name='casebrief',
            name='decision',
            field=models.TextField(null=True, help_text='Describe what is decided or how the issue is finally addressed or resolved', blank=True, verbose_name='Decision / Resolution'),
        ),
    ]
