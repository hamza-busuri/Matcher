# Generated by Django 2.1.3 on 2018-11-18 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchingsite', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='hobbies',
            field=models.ManyToManyField(blank=True, to='matchingsite.Hobbies'),
        ),
    ]