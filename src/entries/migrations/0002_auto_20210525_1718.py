# Generated by Django 3.2 on 2021-05-25 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='record',
            name='text',
            field=models.TextField(blank=True, max_length=9999, null=True),
        ),
    ]