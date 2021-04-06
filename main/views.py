#encoding:utf-8
from main.models import Mod, Etiqueta
from main.forms import BusquedaPorFechaForm, BusquedaPorEtiquetaForm, BusquedaPorTituloODescripcion, BusquedaPorTituloDescripcionFechaForm
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import logout as do_logout
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as do_login
from django.contrib.auth.decorators import login_required

from bs4 import BeautifulSoup
import urllib.request
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, DATETIME, KEYWORD, NUMERIC
import re, os, shutil
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from whoosh.query import Query, Term, Or, And
import lxml
from datetime import datetime, date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import itertools
import functools


#función auxiliar que hace scraping en la web y carga los datos en la base datos
def populateDB():
    #variables para contar el número de registros que vamos a almacenar
    num_mods = 0
    num_etiquetas = 0
       
    #borramos todas las tablas de la BD
    Mod.objects.all().delete()
    Etiqueta.objects.all().delete()

    #Preparamos el esquema del índice
    schem = Schema(titulo=TEXT(stored=True), descripcion=TEXT(stored=True), fecha_actualizacion=DATETIME(stored=True), etiquetas=TEXT(stored=True), imagen=TEXT(stored=True), fecha_publicacion=DATETIME(stored=True), tamanyo = NUMERIC(stored=True), puntuacion = NUMERIC(stored=True), num_valoraciones = NUMERIC(stored=True), suscriptores = NUMERIC(stored=True))
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    ix = create_in("Index", schema=schem)

    #Nombre, Etiquetas, Descripción, Fecha publicación, Fecha actualización, Tamaño, Puntuación, NúmeroValoraciones, LinkCreador, Suscriptores, Imagen

    f = urllib.request.urlopen("https://steamcommunity.com/workshop/browse/?appid=440900&searchtext=&childpublishedfileid=0&browsesort=totaluniquesubscribers&section=readytouseitems&actualsort=totaluniquesubscribers&p=1")
    s = BeautifulSoup(f, "lxml")

    num_pags = int(s.find("div", class_="workshopBrowsePagingControls").find_all("a")[2].text)
    for i in range(1,num_pags+1):
        print("Página " + str(i))
        f = urllib.request.urlopen("https://steamcommunity.com/workshop/browse/?appid=440900&searchtext=&childpublishedfileid=0&browsesort=totaluniquesubscribers&section=readytouseitems&actualsort=totaluniquesubscribers&p="+str(i))
        s = BeautifulSoup(f, "lxml")
        lista_mods = s.find("div", class_="responsive_page_content").find("div", class_="workshopBrowseItems").find_all("div", class_="workshopItem")
        lista_link_mods = []
        writer = ix.writer()
        for mod in lista_mods:
            link = mod.find("a")["href"]
            imagen = mod.find("img", class_="workshopItemPreviewImage")["src"]
            lista_link_mods.append((link, imagen))
        
        for link in lista_link_mods:
            
            print(link[0])
            #Posible solución a errores 502 Bad Gateway y a errores de None Type por no abrir los html correctamente
            #Se emula un navegador por defecto, en este caso, Mozilla en su versión 5.0
            req = urllib.request.Request(link[0], headers={'User-Agent': 'Mozilla/5.0'})
            f = urllib.request.urlopen(req).read()
            #f = urllib.request.urlopen(link[0])
            s = BeautifulSoup(f, "lxml")
    #Nombre, Etiquetas, Descripción, Fecha publicación, Fecha actualización, Tamaño, Puntuación, NúmeroValoraciones, LinkCreador, Suscriptores, Imagen

            titulo = s.find("div", class_="workshopItemTitle").text
            descripcion_soup = s.find("div", class_="workshopItemDescription")
            descripcion = str(descripcion_soup)
            #desc_index = descripcion_soup.text
            div_stats = s.find("div", class_="detailsStatsContainerRight").find_all("div")
            tamanyo = float("".join(div_stats[0].stripped_strings).split(sep=" MB")[0].replace(",", ""))
            fecha_separada = "".join(div_stats[1].stripped_strings).split(sep=" ")
            if len(fecha_separada) == 4:
                fecha_publicacion = datetime.strptime(fecha_separada[0] + " " + fecha_separada[1] + ", " + str(datetime.today().year) + " @ " + fecha_separada[3], "%d %b, %Y @ %I:%M%p")
            else:
                fecha_publicacion = datetime.strptime("".join(div_stats[1].stripped_strings), "%d %b, %Y @ %I:%M%p")
            try:
                fecha_separada = "".join(div_stats[2].stripped_strings).split(sep=" ")
                if len(fecha_separada) == 4:
                    fecha_actualizacion = datetime.strptime(fecha_separada[0] + " " + fecha_separada[1] + ", " + str(datetime.today().year) + " @ " + fecha_separada[3], "%d %b, %Y @ %I:%M%p")
                else:
                    fecha_actualizacion = datetime.strptime("".join(div_stats[1].stripped_strings), "%d %b, %Y @ %I:%M%p")
            except:
                fecha_actualizacion = None

            imagen_puntuacion = s.find("div", class_="fileRatingDetails").img["src"].split(sep="large")
            if imagen_puntuacion[0].find('5') != -1:
                puntuacion = 5
            elif imagen_puntuacion[0].find('4')!= -1:
                puntuacion = 4
            elif imagen_puntuacion[0].find('3')!= -1:
                puntuacion = 3
            elif imagen_puntuacion[0].find('2')!= -1:
                puntuacion = 2
            elif imagen_puntuacion[0].find('1')!= -1:
                puntuacion = 1
            elif imagen_puntuacion[0].find('0')!= -1:
                puntuacion = 0
            else:
                puntuacion = None

            try:
                num_valoraciones = int("".join(s.find("div", class_="numRatings").stripped_strings).split(sep=" ratings")[0].replace(",", ""))
            except:
                num_valoraciones = None
            link_creador = s.find("div", class_="breadcrumbs").find_all("a")[2]["href"]

            imagen = link[1]

            num_suscriptores =int("".join(s.find("table", class_="stats_table").find_all("tr")[1].find_all("td")[0].stripped_strings).replace(",",""))

            etiquetas_soup = s.find_all("div", class_="workshopTags")
            etiquetas = []
            for etiqueta in etiquetas_soup:
                aux = "".join(etiqueta.stripped_strings).split(sep=":")[0]
                etiquetas.append(aux)

            if len(etiquetas)>=1:
                etiquetas_index = ", ".join(etiquetas)
            else:
                etiquetas_index = "" 
            #almacenamos en la BD

            lista_etiquetas_obj = []
            for etiqueta in etiquetas:
                etiqueta_obj, creado = Etiqueta.objects.get_or_create(nombre=etiqueta)
                lista_etiquetas_obj.append(etiqueta_obj)
                if creado:
                    num_etiquetas = num_etiquetas + 1

            m = Mod.objects.create(titulo = titulo, descripcion = descripcion,
                                    fechaPublicacion = fecha_publicacion,
                                    fechaActualizacion = fecha_actualizacion,                               
                                    tamanyo = tamanyo,
                                    puntuacion = puntuacion,
                                    numeroValoraciones = num_valoraciones,
                                    linkCreador = link_creador,
                                    suscriptores = num_suscriptores,
                                    imagen = imagen)
            #añadimos la lista de etiquetas
            for e in lista_etiquetas_obj:
                m.etiquetas.add(e)
            
            writer.add_document(titulo= titulo, descripcion= descripcion, fecha_actualizacion=fecha_actualizacion, etiquetas=etiquetas_index, imagen=imagen, fecha_publicacion=fecha_publicacion, tamanyo=tamanyo, puntuacion= puntuacion, num_valoraciones = num_valoraciones, suscriptores = num_suscriptores)    
            num_mods = num_mods + 1
        writer.commit()
    return ((num_mods, num_etiquetas))

#carga los datos desde la web en la BD
@login_required(login_url='/users/login')
def carga(request):
 
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_mods, num_etiquetas = populateDB()
            mensaje="Se han almacenado: " + str(num_mods) +" mods y " + str(num_etiquetas) +" etiquetas"
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
    
           
    return render(request, 'confirmacion.html')


#muestra el número de películas que hay en la BD
def inicio(request):
    num_mods=Mod.objects.all().count()
    return render(request,'inicio.html', {'num_mods':num_mods})

#muestra un listado con los datos de las películas (título, título original, país, director, géneros y fecha de estreno)
def lista_mods(request):
    #mods=Mod.objects.all()
    mods_list = Mod.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(mods_list, 13)
    try:
        mods = paginator.page(page)
    except PageNotAnInteger:
        mods = paginator.page(1)
    except EmptyPage:
        mods = paginator.page(paginator.num_pages)

    return render(request,'mods.html', {'mods':mods})

def buscar_modsporfecha(request):
    formulario = BusquedaPorFechaForm()
    mods = []    
    if request.method=='POST':
        formulario = BusquedaPorFechaForm(request.POST)      
        if formulario.is_valid():
            ix=open_dir("Index")      
            with ix.searcher() as searcher:
                fecha= str(formulario.cleaned_data['fecha']).replace("-", "")
                rango_fecha = '[' + fecha + ' TO '+ date.today().strftime("%Y%m%d") +']'
                query = MultifieldParser(["fecha_actualizacion", "fecha_publicacion"], ix.schema).parse(rango_fecha)
                result = searcher.search(query, limit=None)
                for r in result:
                    try:
                        aux = {"titulo": r['titulo'], "descripcion":r['descripcion'], "etiquetas": r["etiquetas"], "fecha_actualizacion": r['fecha_actualizacion'], "fecha_publicacion": r['fecha_publicacion'], "imagen": r['imagen'], "tamanyo":r['tamanyo'], "suscriptores": r['suscriptores']}
                    except:
                        aux = {"titulo": r['titulo'],"descripcion":r['descripcion'], "etiquetas": r["etiquetas"], "fecha_actualizacion": None, "fecha_publicacion": r['fecha_publicacion'], "imagen": r['imagen'], "tamanyo":r['tamanyo'], "suscriptores": r['suscriptores']}
                    mods.append(aux)
    return render(request, 'modsbusquedaporfecha.html', {'formulario':formulario, 'mods':mods, "counter": functools.partial(next, itertools.count())})

def buscar_modsporetiqueta(request):
    formulario = BusquedaPorEtiquetaForm()
    mods = []  
    if request.method=='POST':
        formulario = BusquedaPorEtiquetaForm(request.POST)      
        if formulario.is_valid():
            ix=open_dir("Index")      
            with ix.searcher() as searcher:
                etiqueta = str(formulario.cleaned_data['etiqueta'])
                query = QueryParser("etiquetas", ix.schema).parse(etiqueta)
                result = searcher.search(query, limit=None)
                for r in result:
                    try:
                        aux = {"titulo": r['titulo'], "descripcion":r['descripcion'], "etiquetas": r["etiquetas"], "fecha_actualizacion": r['fecha_actualizacion'], "fecha_publicacion": r['fecha_publicacion'], "imagen": r['imagen'], "tamanyo":r['tamanyo'], "suscriptores": r['suscriptores']}
                    except:
                        aux = {"titulo": r['titulo'],"descripcion":r['descripcion'], "etiquetas": r["etiquetas"], "fecha_actualizacion": None, "fecha_publicacion": r['fecha_publicacion'], "imagen": r['imagen'], "tamanyo":r['tamanyo'], "suscriptores": r['suscriptores']}
                    mods.append(aux)
    return render(request, 'modsbusquedaporetiqueta.html', {'formulario':formulario, 'mods':mods, "counter": functools.partial(next, itertools.count())})

def buscar_modsportitulodescripcion(request):
    formulario = BusquedaPorTituloODescripcion()
    mod_list = []
    if request.method=='POST':
        formulario = BusquedaPorTituloODescripcion(request.POST)      
        if formulario.is_valid():
            ix=open_dir("Index")      
            with ix.searcher() as searcher:
                busqueda = str(formulario.cleaned_data['busqueda'])
                query = MultifieldParser(["titulo", "descripcion"], ix.schema).parse(busqueda)
                result = searcher.search(query, limit=None)
                
                for r in result:
                    try:
                        aux = {"titulo": r['titulo'], "descripcion":r['descripcion'], "etiquetas": r["etiquetas"], "fecha_actualizacion": r['fecha_actualizacion'], "fecha_publicacion": r['fecha_publicacion'], "imagen": r['imagen'], "tamanyo":r['tamanyo'], "suscriptores": r['suscriptores']}
                    except:
                        aux = {"titulo": r['titulo'],"descripcion":r['descripcion'], "etiquetas": r["etiquetas"], "fecha_actualizacion": None, "fecha_publicacion": r['fecha_publicacion'], "imagen": r['imagen'], "tamanyo":r['tamanyo'], "suscriptores": r['suscriptores']}
                    mod_list.append(aux)
    return render(request, 'modsbusquedaportitulodescripcion.html', {'formulario':formulario, 'mods':mod_list, "counter": functools.partial(next, itertools.count())})

def buscar_mods_por_titulo_descripcion_fecha(request):
    formulario = BusquedaPorTituloDescripcionFechaForm()
    mods = []    
    if request.method=='POST':
        formulario = BusquedaPorTituloDescripcionFechaForm(request.POST)      
        if formulario.is_valid():
            ix=open_dir("Index")      
            with ix.searcher() as searcher:
                busqueda = str(formulario.cleaned_data['busqueda'])
                fecha_comienzo= str(formulario.cleaned_data['fecha_comienzo']).replace("-", "")
                fecha_final= str(formulario.cleaned_data['fecha_final']).replace("-", "")
                rango_fecha = '[' + fecha_comienzo + ' TO '+ fecha_final +']'
                # Se buscará la cadena introducida en el título o en la descripción y posteriormente se comprobará que el mod
                # esté actualizado/publicado entre las fechas introducidas
                aux = "(titulo:(" + busqueda + ") OR descripcion:(" + busqueda + ")) AND (fecha_actualizacion:" + rango_fecha + " OR fecha_publicacion:" + rango_fecha + ")"
                # En realidad no haría falta especificar ningún campo, estos son los campos en los que buscaría por defecto el parser
                # si no se especificaran los campos en la cadena pasada al parse. 
                # Pero los hemos definido en "aux", por lo que realizará la búsqueda tal y como se la hemos pedido
                query = MultifieldParser(["titulo", "descripcion"], ix.schema).parse(aux)
                result = searcher.search(query, limit=None)
                for r in result:
                    try:
                        aux = {"titulo": r['titulo'], "descripcion":r['descripcion'], "etiquetas": r["etiquetas"], "fecha_actualizacion": r['fecha_actualizacion'], "fecha_publicacion": r['fecha_publicacion'], "imagen": r['imagen'], "tamanyo":r['tamanyo'], "suscriptores": r['suscriptores']}
                    except:
                        aux = {"titulo": r['titulo'],"descripcion":r['descripcion'], "etiquetas": r["etiquetas"], "fecha_actualizacion": None, "fecha_publicacion": r['fecha_publicacion'], "imagen": r['imagen'], "tamanyo":r['tamanyo'], "suscriptores": r['suscriptores']}
                    mods.append(aux)
    return render(request, 'modsbusquedaportitulodescripcionfecha.html', {'formulario':formulario, 'mods':mods, "counter": functools.partial(next, itertools.count())})

def welcome(request):
    if request.user.is_authenticated:
        return render(request, "welcome.html")
        #Si no está loggeado se redirecciona a login
    return render(request, "login.html")

def login(request):
    formulario = AuthenticationForm()
    if request.method == "POST":
        # Añadimos los datos recibidos al formulario
        formulario = AuthenticationForm(data=request.POST)
        # Si el formulario es válido...
        if formulario.is_valid():
            # Recuperamos las credenciales validadas
            username = formulario.cleaned_data['username']
            password = formulario.cleaned_data['password']
            user = authenticate(username=username, password=password)

            # Si existe un usuario con ese nombre y contraseña
            if user is not None:
                # Hacemos el login manualmente
                do_login(request, user)
                # Y le redireccionamos a la portada
                return redirect('/users/')

    return render(request, "login.html", {'formulario': formulario})

def logout(request):
    do_logout(request)
    # Redireccionamos a la portada
    return redirect('/')

def detalle_mod(request, id_mod):
    dato = get_object_or_404(Mod, pk=id_mod)
    return render(request,'mod.html',{'mod':dato})