# Generated by Django 2.1.3 on 2018-11-22 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchingsite', '0009_auto_20181121_0645'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='location',
            field=models.DateField(null=True),
        ),
    ]