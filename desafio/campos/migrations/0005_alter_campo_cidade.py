# Generated by Django 5.0.7 on 2024-08-07 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campos', '0004_campo_cidade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campo',
            name='cidade',
            field=models.CharField(default='', max_length=100),
        ),
    ]
