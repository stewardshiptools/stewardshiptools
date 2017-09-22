# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

'''
Migration 0023, 0024, and 0025 form 3 parts of custom migration
to remove asset inheritance on messageattachment model.
Needed a new ID pk field but it had to be added as null=True,
calculated (0024) and then set to PK and null=False (0025)
'''

# def nullify_fax_document_fks(apps, schema_editor):
#     from communication.models import Fax
#     Fax.objects.all().update(document=None)


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0022_auto_20161021_2200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='messageattachment',
            name='communicationasset_ptr',
        ),

        # Setting to null makes this reversable; the field gets dropped in a future mig. anyways.
        migrations.AddField(
            model_name='messageattachment',
            name='file',
            field=models.ForeignKey(to='communication.CommunicationFileRelation', null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='messageattachment',
            name='id',
            # field=models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', null=True, serialize=False),
            field=models.IntegerField(verbose_name='ID', null=True, serialize=False),
            preserve_default=False,
        ),
    ]
