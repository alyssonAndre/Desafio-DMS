# Generated by Django 5.0.7 on 2024-08-20 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0005_remove_userprofile_is_2fa_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_2fa_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
