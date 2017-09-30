# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppliedManagementScripts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_path', models.CharField(max_length=500)),
                ('file_hash', models.CharField(max_length=100)),
                ('applied_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
