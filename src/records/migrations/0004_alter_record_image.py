# Generated by Django 3.2 on 2021-06-07 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0003_rename_heading_record_header'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='image_entries/'),
        ),
    ]
