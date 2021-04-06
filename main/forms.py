#encoding:utf-8
from django import forms
from main.models import Etiqueta
   
class BusquedaPorEtiquetaForm(forms.Form):
    lista=[(e.nombre, e.nombre) for e in Etiqueta.objects.all()]
    etiqueta = forms.ChoiceField(label="Seleccione la Etiqueta", choices=lista)

class BusquedaPorTituloODescripcion(forms.Form):
    busqueda = forms.CharField(label="Introduzca su búsqueda")

class BusquedaPorFechaForm(forms.Form):
    fecha = forms.DateField(label="Fecha (Formato dd/mm/yyyy)", widget=forms.DateInput(format='%d/%m/%Y'), required=True)

class BusquedaPorTituloDescripcionFechaForm(forms.Form):
    busqueda = forms.CharField(label="Introduzca su búsqueda")
    fecha_comienzo = forms.DateField(label="Fecha de inicio (Formato dd/mm/yyyy)", widget=forms.DateInput(format='%d/%m/%Y'), required=True)
    fecha_final = forms.DateField(label="Fecha de fin (Formato dd/mm/yyyy)", widget=forms.DateInput(format='%d/%m/%Y'), required=True)