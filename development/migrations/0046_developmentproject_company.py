# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0020_auto_20161207_2035'),
        ('development', '0045_developmentproject_final_decision'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='company',
            field=models.ForeignKey(to='crm.Organization', blank=True, null=True),
        ),
    ]
