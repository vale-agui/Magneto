# Generated by Django 5.2 on 2025-04-05 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CredencialAPI_google',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('refresh_token', models.TextField()),
                ('access_token', models.TextField(blank=True, null=True)),
                ('expires_in', models.IntegerField(blank=True, null=True)),
                ('token_type', models.CharField(blank=True, max_length=50, null=True)),
                ('scope', models.CharField(blank=True, max_length=300, null=True)),
                ('creado', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
