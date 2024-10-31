# Generated by Django 5.1.2 on 2024-10-31 06:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='due_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='listitem',
            name='due_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='templateitem',
            name='due_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
