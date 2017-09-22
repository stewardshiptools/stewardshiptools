# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0013_role_description'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('communication', '0003_auto_20160817_2334'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunicationRelation',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('comm_type_oid', models.PositiveIntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='communication',
            name='comm_ct',
        ),
        migrations.RemoveField(
            model_name='communication',
            name='comm_oid',
        ),
        migrations.RemoveField(
            model_name='communication',
            name='rel_object_ct',
        ),
        migrations.RemoveField(
            model_name='communication',
            name='rel_object_oid',
        ),
        migrations.RemoveField(
            model_name='fax',
            name='date',
        ),
        migrations.RemoveField(
            model_name='fax',
            name='from_contacts',
        ),
        migrations.RemoveField(
            model_name='fax',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='fax',
            name='to_contacts',
        ),
        migrations.RemoveField(
            model_name='message',
            name='date',
        ),
        migrations.RemoveField(
            model_name='message',
            name='from_contacts',
        ),
        migrations.RemoveField(
            model_name='message',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='message',
            name='to_contacts',
        ),
        migrations.RemoveField(
            model_name='phonecall',
            name='date',
        ),
        migrations.RemoveField(
            model_name='phonecall',
            name='from_contacts',
        ),
        migrations.RemoveField(
            model_name='phonecall',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='phonecall',
            name='to_contacts',
        ),
        migrations.AddField(
            model_name='communication',
            name='date',
            field=models.DateTimeField(verbose_name='Date & time of communication.', default=datetime.datetime(2016, 8, 18, 12, 53, 48, 14646)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='communication',
            name='from_contact',
            field=models.ManyToManyField(related_name='from_contact', to='crm.Person'),
        ),
        migrations.AddField(
            model_name='communication',
            name='subject',
            field=models.CharField(max_length=400, default=datetime.datetime(2016, 8, 18, 12, 53, 55, 918130)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='communication',
            name='to_contact',
            field=models.ManyToManyField(related_name='to_contact', to='crm.Person'),
        ),
        migrations.AddField(
            model_name='communicationrelation',
            name='comm',
            field=models.ForeignKey(related_name='related_communication', to='communication.Communication'),
        ),
        migrations.AddField(
            model_name='communicationrelation',
            name='comm_type_ct',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
    ]
