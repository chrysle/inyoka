# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-11-17 18:07
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_forum_read_status(apps, schema_editor):
    users = apps.get_model('portal', 'User').objects

    for u in users.only('old_forum_read_status'):
        u.forum_read_status = u.old_forum_read_status.encode()
        u.save(update_fields=['forum_read_status'])


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0027_auto_20191027_1814'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='forum_read_status',
            new_name='old_forum_read_status'
        ),
        migrations.AddField(
            model_name='user',
            name='forum_read_status',
            field=models.BinaryField(blank=True, verbose_name='Read posts'),
        ),
        migrations.RunPython(migrate_forum_read_status),
        migrations.RemoveField(model_name='user', name='old_forum_read_status'),
    ]
