# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0005_remove_organization_fake_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='email',
            field=models.EmailField(verbose_name='Email', blank=True, null=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='organization',
            name='fax',
            field=phonenumber_field.modelfields.PhoneNumberField(verbose_name='Fax', blank=True, null=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='organization',
            name='mailing_address',
            field=models.TextField(verbose_name='Mailing address', blank=True, null=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='organization',
            name='notes',
            field=models.TextField(verbose_name='Notes', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='office_address',
            field=models.TextField(verbose_name='Office address', blank=True, null=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='organization',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(verbose_name='Phone', blank=True, null=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='organization',
            name='website',
            field=models.URLField(verbose_name='Website', blank=True, null=True),
        ),
    ]
