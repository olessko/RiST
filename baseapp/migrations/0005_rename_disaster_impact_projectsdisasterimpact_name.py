# Generated by Django 4.0.4 on 2022-06-10 17:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseapp', '0004_projectsdisasterimpact'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectsdisasterimpact',
            old_name='disaster_impact',
            new_name='name',
        ),
    ]
