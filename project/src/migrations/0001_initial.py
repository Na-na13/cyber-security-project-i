# Generated by Django 4.2 on 2023-07-14 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('messagetext', models.TextField()),
                ('sender', models.CharField(max_length=150)),
                ('receiver', models.CharField(max_length=150)),
            ],
            options={
                'db_table': 'messages',
            },
        ),
    ]
