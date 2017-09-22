# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0003_auto_20160126_2050'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeafletBaseLayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='leaflettilelayer',
            name='description',
        ),
        migrations.RemoveField(
            model_name='leaflettilelayer',
            name='name',
        ),
        migrations.AlterField(
            model_name='leafletmap',
            name='base_layers',
            field=models.ManyToManyField(help_text='Choose the base layers that will be available.', to='maps.LeafletBaseLayer'),
        ),
        migrations.AlterField(
            model_name='leaflettilelayer',
            name='sub_domains',
            field=models.CharField(default='abc', help_text='Subdomains of the tile service. Can be passed in the form of one string (where each letter is asubdomain name) or a comma separated list of strings.', max_length=200),
        ),
        migrations.AlterField(
            model_name='leaflettilelayer',
            name='url_template',
            field=models.CharField(help_text="A string of the following form: 'http://{s}.somedomain.com/blabla/{z}/{x}/{y}.png'", max_length=1000),
        ),
        migrations.AddField(
            model_name='leafletmap',
            name='default_base_layer',
            field=models.ForeignKey(to='maps.LeafletBaseLayer', default=0, help_text='Which layer will be displayed by default?', related_name='default_base_layer'),
            preserve_default=False,
        ),
    ]
