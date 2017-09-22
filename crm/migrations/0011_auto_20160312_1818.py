# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0010_person_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='user',
        ),
        migrations.AddField(
            model_name='person',
            name='user_account',
            field=models.OneToOneField(blank=True, help_text='The internal user account for this person.', to=settings.AUTH_USER_MODEL, null=True,
                                       verbose_name='User account', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
