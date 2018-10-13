# Generated by Django 2.1.1 on 2018-10-13 02:22

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alarm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('origin_point', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='Coordenadas de origem da carona')),
                ('origin_radius', models.FloatField(default=5, validators=[django.core.validators.MaxValueValidator(10), django.core.validators.MinValueValidator(0.05)], verbose_name='Raio de pesquisa da origem em km')),
                ('destination_point', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='Coordenadas de destino da carona')),
                ('destination_radius', models.FloatField(default=5, validators=[django.core.validators.MaxValueValidator(20), django.core.validators.MinValueValidator(0.05)], verbose_name='Raio de pesquisa do destino em km')),
                ('price', models.PositiveSmallIntegerField(null=True, verbose_name='Preço da carona em reais')),
                ('auto_approve', models.BooleanField(null=True, verbose_name='Aprovação automática de passageiros')),
                ('datetime_lte', models.DateTimeField(null=True, verbose_name='Datetime máxima de saída da carona')),
                ('datetime_gte', models.DateTimeField(null=True, verbose_name='Datetime mínima de saída da carona')),
                ('min_seats', models.PositiveSmallIntegerField(null=True, validators=[django.core.validators.MaxValueValidator(10)], verbose_name='Mínimo número de assentos na carona')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alarms', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
