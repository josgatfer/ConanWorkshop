from django.urls import path
from django.contrib import admin
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.inicio),
    path('carga/',views.carga),
    path('mods/', views.lista_mods),
    path('buscarmodsporetiqueta/', views.buscar_modsporetiqueta),
    path('buscarmodsporfecha/', views.buscar_modsporfecha),
    path('buscarmodsportitulodescripcion/', views.buscar_modsportitulodescripcion),
    path('buscarmodsportitulodescripcionfecha/', views.buscar_mods_por_titulo_descripcion_fecha),
    path('users/', views.welcome),
    path('users/login/', views.login),
    path('users/logout/', views.logout),
    path('mods/mod/<int:id_mod>',views.detalle_mod)
    ]
