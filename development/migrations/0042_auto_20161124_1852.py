# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0041_developmentproject_extra_info'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentproject',
            name='description',
            field=models.TextField(null=True, blank=True, help_text='Short description of project/permit.', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='developmentproject',
            name='location_description',
            field=models.TextField(null=True, blank=True, help_text="Short description of the project's location.", verbose_name='Location Description'),
        ),
        migrations.AlterField(
            model_name='developmentproject',
            name='rationale',
            field=models.TextField(null=True, blank=True, verbose_name='Rationale'),
        ),
    ]
