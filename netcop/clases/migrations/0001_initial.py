# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-26 14:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CIDR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('direccion', models.GenericIPAddressField(protocol='IPv4')),
                ('prefijo', models.PositiveSmallIntegerField(default=32)),
            ],
        ),
        migrations.CreateModel(
            name='ClaseCIDR',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grupo', models.CharField(choices=[('i', 'En la red local'), ('o', 'En Internet')], max_length=1)),
                ('cidr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clases.CIDR')),
            ],
        ),
        migrations.CreateModel(
            name='ClasePuerto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grupo', models.CharField(choices=[('i', 'En la red local'), ('o', 'En Internet')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='ClaseTrafico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=32)),
                ('descripcion', models.CharField(default='', max_length=160)),
                ('activa', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Puerto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.PositiveIntegerField()),
                ('protocolo', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='clasepuerto',
            name='clase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clases.ClaseTrafico'),
        ),
        migrations.AddField(
            model_name='clasepuerto',
            name='puerto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clases.Puerto'),
        ),
        migrations.AddField(
            model_name='clasecidr',
            name='clase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clases.ClaseTrafico'),
        ),
    ]