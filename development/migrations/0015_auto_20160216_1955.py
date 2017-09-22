# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0014_auto_20160216_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentproject',
            name='cedar_assessor',
            field=models.ManyToManyField(related_name='cedar_assessor', to='crm.Person', blank=True, verbose_name='Nation assessor'),
        ),
        migrations.AlterField(
            model_name='developmentproject',
            name='company_contact',
            field=models.ManyToManyField(related_name='company_contact', to='crm.Person', blank=True),
        ),
        migrations.AlterField(
            model_name='developmentproject',
            name='government_contact',
            field=models.ManyToManyField(related_name='government_contact', to='crm.Person', blank=True),
        ),
    ]
