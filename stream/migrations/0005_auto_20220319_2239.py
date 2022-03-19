# Generated by Django 2.2.26 on 2022-03-19 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stream', '0004_auto_20220317_1516'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='likes',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='picture',
            field=models.ImageField(blank=True, upload_to='profile_images/'),
        ),
    ]