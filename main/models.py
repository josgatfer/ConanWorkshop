#encoding:utf-8
from django.db import models

#Nombre, Etiquetas, Descripción, Fecha publicación, Fecha actualización, Tamaño, Puntuación, NúmeroValoraciones, LinkCreador, Suscriptores, Imagen

class Etiqueta(models.Model):
    nombre = models.CharField(max_length=40, verbose_name="Etiqueta")
    def __str__(self):
        return self.nombre
    
class Mod(models.Model):
    titulo = models.TextField(verbose_name="Título")
    etiquetas = models.ManyToManyField(Etiqueta)
    descripcion = models.TextField(verbose_name="Descripción")
    fechaPublicacion = models.DateTimeField(verbose_name="Fecha de Publicación")
    fechaActualizacion = models.DateTimeField(default=None, null=True, verbose_name="Fecha de Actualización")
    tamanyo = models.FloatField(verbose_name="Tamaño")
    puntuacion = models.IntegerField(default=None, null=True, verbose_name="Puntuación")
    numeroValoraciones = models.IntegerField(default=None, null=True, verbose_name="Número de Valoraciones")
    linkCreador = models.URLField(verbose_name="Link del Creador")
    suscriptores = models.IntegerField(verbose_name="Número de Suscriptores")
    imagen = models.URLField(default = None, null = True, verbose_name="Imagen")

    def __str__(self):
        return self.titulo