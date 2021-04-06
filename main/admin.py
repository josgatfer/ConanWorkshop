from django.contrib import admin
from main.models import Mod, Etiqueta

#registramos en el administrador de django los modelos 
admin.site.register(Mod)
admin.site.register(Etiqueta)
