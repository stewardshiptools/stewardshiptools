# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('communication', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fax',
            name='from_contact',
            field=models.ManyToManyField(related_name='communication_fax_from_contact', to='crm.Person'),
        ),
        migrations.AlterField(
            model_name='fax',
            name='to_contact',
            field=models.ManyToManyField(related_name='communication_fax_to_contact', to='crm.Person'),
        ),
        migrations.AlterField(
            model_name='message',
            name='from_contact',
            field=models.ManyToManyField(related_name='communication_message_from_contact', to='crm.Person'),
        ),
        migrations.AlterField(
            model_name='message',
            name='to_contact',
            field=models.ManyToManyField(related_name='communication_message_to_contact', to='crm.Person'),
        ),
        migrations.AlterField(
            model_name='phonecall',
            name='from_contact',
            field=models.ManyToManyField(related_name='communication_phonecall_from_contact', to='crm.Person'),
        ),
        migrations.AlterField(
            model_name='phonecall',
            name='to_contact',
            field=models.ManyToManyField(related_name='communication_phonecall_to_contact', to='crm.Person'),
        ),
    ]
