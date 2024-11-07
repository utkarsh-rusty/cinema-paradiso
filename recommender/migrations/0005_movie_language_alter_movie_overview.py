# Generated by Django 5.1.1 on 2024-10-31 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0004_alter_movie_runtime'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='language',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='overview',
            field=models.TextField(blank=True, null=True),
        ),
    ]