# Generated by Django 5.1.6 on 2025-04-09 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campannias', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CredencialAPI_facebook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.TextField()),
                ('token_type', models.CharField(blank=True, max_length=50, null=True)),
                ('expires_in', models.IntegerField(blank=True, null=True)),
                ('scope', models.CharField(blank=True, max_length=300, null=True)),
                ('creado', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
