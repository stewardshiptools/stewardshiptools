# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0010_auto_20160216_1933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentproject',
            name='cedar_assessor',
            field=models.ManyToManyField(related_name='cedar_assessor', to='crm.Person', verbose_name='Nation assessor'),
        ),
    ]
