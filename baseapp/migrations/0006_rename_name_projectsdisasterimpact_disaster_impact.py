# Generated by Django 4.0.4 on 2022-06-10 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('baseapp', '0005_rename_disaster_impact_projectsdisasterimpact_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectsdisasterimpact',
            old_name='name',
            new_name='disaster_impact',
        ),
    ]
