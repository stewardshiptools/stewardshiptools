# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0013_role_description'),
        ('development', '0020_auto_20160726_2138'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileNo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_number', models.CharField(max_length=200)),
                ('org_type', models.CharField(choices=[('government', 'Government'), ('proponent', 'Proponent')], max_length=30)),
                ('organization', models.ForeignKey(blank=True, null=True, to='crm.Organization')),
            ],
        ),
        migrations.AlterField(
            model_name='developmentproject',
            name='govt_project_code',
            field=models.CharField(verbose_name='This field is deprecated, use external file no instead.', max_length=80, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='developmentproject',
            name='external_file_no',
            field=models.ForeignKey(blank=True, null=True, to='development.FileNo'),
        ),
    ]
