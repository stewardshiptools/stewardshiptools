# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0013_role_description'),
        ('communication', '0002_auto_20160817_2332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fax',
            name='from_contact',
        ),
        migrations.RemoveField(
            model_name='fax',
            name='to_contact',
        ),
        migrations.RemoveField(
            model_name='message',
            name='from_contact',
        ),
        migrations.RemoveField(
            model_name='message',
            name='to_contact',
        ),
        migrations.RemoveField(
            model_name='phonecall',
            name='from_contact',
        ),
        migrations.RemoveField(
            model_name='phonecall',
            name='to_contact',
        ),
        migrations.AddField(
            model_name='fax',
            name='from_contacts',
            field=models.ManyToManyField(related_name='communication_fax_from_contacts', to='crm.Person'),
        ),
        migrations.AddField(
            model_name='fax',
            name='to_contacts',
            field=models.ManyToManyField(related_name='communication_fax_to_contacts', to='crm.Person'),
        ),
        migrations.AddField(
            model_name='message',
            name='from_contacts',
            field=models.ManyToManyField(related_name='communication_message_from_contacts', to='crm.Person'),
        ),
        migrations.AddField(
            model_name='message',
            name='to_contacts',
            field=models.ManyToManyField(related_name='communication_message_to_contacts', to='crm.Person'),
        ),
        migrations.AddField(
            model_name='phonecall',
            name='from_contacts',
            field=models.ManyToManyField(related_name='communication_phonecall_from_contacts', to='crm.Person'),
        ),
        migrations.AddField(
            model_name='phonecall',
            name='to_contacts',
            field=models.ManyToManyField(related_name='communication_phonecall_to_contacts', to='crm.Person'),
        ),
    ]
