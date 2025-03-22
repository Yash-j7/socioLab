# Generated by Django 5.1.6 on 2025-03-09 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id_user', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('bio', models.TextField(blank=True, default='')),
                ('profileImg', models.ImageField(default='blank-profile-picture', upload_to='profile_images/')),
                ('location', models.CharField(blank=True, default='', max_length=100)),
            ],
        ),
    ]
