# Generated by Django 3.1.2 on 2020-12-29 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Etiqueta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=40, verbose_name='Etiqueta')),
            ],
        ),
        migrations.CreateModel(
            name='Mod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.TextField(verbose_name='Título')),
                ('descripcion', models.TextField(verbose_name='Descripción')),
                ('fechaPublicacion', models.DateTimeField(verbose_name='Fecha de Publicación')),
                ('fechaActualizacion', models.DateTimeField(default=None, null=True, verbose_name='Fecha de Actualización')),
                ('tamanyo', models.FloatField(verbose_name='Tamaño')),
                ('puntuacion', models.IntegerField(default=None, null=True, verbose_name='Puntuación')),
                ('numeroValoraciones', models.IntegerField(default=None, null=True, verbose_name='Número de Valoraciones')),
                ('linkCreador', models.URLField(verbose_name='Link del Creador')),
                ('suscriptores', models.IntegerField(verbose_name='Número de Suscriptores')),
                ('etiquetas', models.ManyToManyField(to='main.Etiqueta')),
            ],
        ),
        migrations.RemoveField(
            model_name='pelicula',
            name='director',
        ),
        migrations.RemoveField(
            model_name='pelicula',
            name='generos',
        ),
        migrations.RemoveField(
            model_name='pelicula',
            name='pais',
        ),
        migrations.DeleteModel(
            name='Director',
        ),
        migrations.DeleteModel(
            name='Genero',
        ),
        migrations.DeleteModel(
            name='Pais',
        ),
        migrations.DeleteModel(
            name='Pelicula',
        ),
    ]
