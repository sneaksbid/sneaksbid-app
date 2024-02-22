# Generated by Django 5.0.2 on 2024-02-20 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('price', models.FloatField()),
                ('stock_no', models.CharField(max_length=10)),
                ('description_short', models.CharField(max_length=50)),
                ('description_long', models.TextField()),
                ('image', models.ImageField(upload_to='')),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]