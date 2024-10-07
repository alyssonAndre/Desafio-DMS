# Generated by Django 5.0.7 on 2024-08-09 15:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campos', '0012_reserva_bloqueado'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiaBloqueado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('campo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dias_bloqueados', to='campos.campo')),
            ],
        ),
    ]
