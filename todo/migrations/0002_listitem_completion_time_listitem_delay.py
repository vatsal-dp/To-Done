# Generated by Django 5.1.2 on 2024-10-29 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='listitem',
            name='completion_time',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='listitem',
            name='delay',
            field=models.IntegerField(default=0),
        ),
    ]
