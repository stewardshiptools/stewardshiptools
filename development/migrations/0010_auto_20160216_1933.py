# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0004_auto_20160202_1146'),
        ('development', '0009_remove_developmentproject_cedar_project_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='cedar_assessor',
            field=models.ManyToManyField(to='crm.Person', related_name='cedar_assessor'),
        ),
        migrations.AddField(
            model_name='developmentproject',
            name='company_contact',
            field=models.ManyToManyField(to='crm.Person', related_name='company_contact'),
        ),
        migrations.AddField(
            model_name='developmentproject',
            name='government_contact',
            field=models.ManyToManyField(to='crm.Person', related_name='government_contact'),
        ),
    ]
