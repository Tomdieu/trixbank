# Generated by Django 5.0.3 on 2024-03-28 00:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersession',
            name='session',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='sessions.session'),
            preserve_default=False,
        ),
    ]