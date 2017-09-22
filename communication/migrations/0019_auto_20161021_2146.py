# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def nullify_fax_document_fks(apps, schema_editor):
    from communication.models import Fax
    Fax.objects.all().update(document=None)


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('communication', '0018_auto_20161019_0034'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunicationFileRelation',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('asset_oid', models.PositiveIntegerField()),
                ('asset_ct', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.AlterModelOptions(
            name='mailbox',
            options={'permissions': (('harvest_mailbox', 'Can run mailharvest on mailbox'),), 'verbose_name_plural': 'Mailboxes'},
        ),

        # remove FK pointers to docs, or this all breaks.
        migrations.RunPython(nullify_fax_document_fks, reverse_code=migrations.RunPython.noop),

        migrations.AlterField(
            model_name='fax',
            name='document',
            field=models.ForeignKey(blank=True, null=True, to='communication.CommunicationFileRelation'),
        ),
    ]
