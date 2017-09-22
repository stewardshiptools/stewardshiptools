# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import Max

'''
Migration 0023, 0024, and 0025 form 3 parts of custom migration
to remove asset inheritance on messageattachment model.
Needed a new ID pk field but it had to be added as null=True,
calculated (0024) and then set to PK and null=False (0025)
'''


def get_max_id(apps, schema_editor):
    from communication.models import MessageAttachment

    for row in MessageAttachment.objects.all():
        max = MessageAttachment.objects.all().aggregate(Max('id'))['id__max']
        max = 0 if max is None else max # make sure max is not None
        row.id = max + 1
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0023_auto_20161026_1503'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(get_max_id, reverse_code=migrations.RunPython.noop),
    ]
