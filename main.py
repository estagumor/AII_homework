# -*- coding: utf-8 -*-

import tkinter
from tkinter import messagebox
from tkinter.constants import END
import urllib.request
import re
import datetime
from bs4 import BeautifulSoup
from whoosh.fields import *
import os
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import Every

def convertStringToMonth(m):
    dictionary = {'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6, 'Julio':7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12}
    return dictionary.get(m)

peliculas = Schema(titulo=TEXT(stored=True),
    fecha=DATETIME(stored=True, sortable=True),
    directores=TEXT(),
    sinopsis=TEXT())

##########FUNCIONES
def cargarDatos():
    #WHOOSH
    if not os.path.exists("index"):
        os.mkdir("index")
    ix0 = create_in("index", peliculas)
    ix = open_dir("index")
    writer = ix.writer()

    contador = 0
    i = 1
    while i <= 2:
        pageUrl= urllib.request.urlopen('https://www.elseptimoarte.net/estrenos/' + str(i)).read()
        soup=BeautifulSoup(pageUrl,"html.parser")
        s = soup.find('ul', ['elements']) #Bloque principal
        li = s.find_all('li') #Contiene la url y algunos datos de cada pelicula 
        for l in li: #Recorremos cada pelicula
            link = l.find('a')
            #Titulo
            title = link['title']
            #Fecha
            parrafos = l.find_all('p')
            p = parrafos[1].text
            pattern = '([a-zA-Z]*)\s*([0-9]*)\,\s*([0-9]*)'
            information = re.findall(pattern, p)
            information = information[0]
            fecha = datetime.datetime(int(information[2]),convertStringToMonth(information[0]), int(information[1]))
            #Directores
            url = ('https://www.elseptimoarte.net' + link['href'])
            urlpelicula = urllib.request.urlopen(url).read()
            soupelicula = BeautifulSoup(urlpelicula, "html.parser")
            span = soupelicula.find_all('span', itemprop="director")
            directores = ""
            for sp in span:
                if(span[0] == sp):
                    directores = directores + sp.find('span', itemprop="name").text
                else:
                    directores = directores + "," + sp.find('span', itemprop="name").text
            #Sinopsis
            sinopsis = soupelicula.find('div', itemprop="description").text
            writer.add_document(titulo=title, fecha=fecha,
                    directores=directores, sinopsis=sinopsis)  
            contador = contador + 1 
        i = i + 1
    writer.commit(optimize=True)
    messagebox.showinfo( "Peliculas", "Peliculas guardadas correctamente. \nHay " + str(contador) + " registros")

def listarDatos():
    secundario = tkinter.Tk()
    secundario.title("Listado")#Cambia el titulo
    secundario.geometry("500x500") #Cambiamos geometría
    scrollbar = tkinter.Scrollbar(secundario) #Hacemos una scrollbar
    scrollbar.pack(side="right", fill="y")
    lista = tkinter.Listbox(secundario) #Se la asociamos al eje y de la lista
    lista.pack(side="left", fill="both", expand=True)
    lista.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=lista.yview) #le asociamos al scroll el eje y de la vista

    ix = open_dir("index") #Abre el index de antes
    with ix.searcher() as s:
        q = Every() #Devuelve todos los documents
        results = s.search(q, limit=None, sortedby="fecha")
        for resultado in results:
            lista.insert(END, "Titulo: " + resultado['titulo'])
            lista.insert(END, "Estreno: " + resultado['fecha'].strftime('%d-%m-%Y'))
            lista.insert(END, " ")
    secundario.mainloop()

def mostrarBusqueda(eleccion, contenido):
    secundario = tkinter.Tk()
    secundario.title("Resultado de la busqueda")#Cambia el titulo
    secundario.geometry("500x500") #Cambiamos geometría
    scrollbar = tkinter.Scrollbar(secundario, orient="vertical") #Hacemos una scrollbar
    lista = tkinter.Listbox(secundario, yscrollcommand=scrollbar.set) #Se la asociamos al eje y de la lista
    scrollbar.config(command=lista.yview()) #le asociamos al scroll el eje y de la vista
    scrollbar.pack(side="right", fill="y")
    lista.pack(side="left",fill="both", expand=True)

    bd = sqlite3.connect("BD.dat") #Conecta con sql3lite y especifica archivo de destino de los datos
    cursor =  bd.cursor() #Crea un cursor que es lo que utiliza la bd
    bd.text_factory = str #Configuración para convertir a UTF-8
    s = "%" + contenido + "%" 
    if eleccion == 'tema':
        cursor.execute("""select * from datos where titulo like ?""", (s,)) #Se convierte esta mierda en lista porque si no pasa chars
    elif eleccion == 'autor':
        cursor.execute("""select * from datos where autor like ?""", (s,))
    else:
        cursor.execute("""select * from datos where fecha like ?""", (s,))
        
    for resultado in cursor:
        lista.insert(END, "Título: " + resultado[1]) #Empezamos desde 1 porque el 0 es id
        lista.insert(END, "Link: " + resultado[2])
        lista.insert(END, "Autor: " + resultado[3])
        lista.insert(END, "Fecha y hora: " + resultado[4])
        lista.insert(END, " ")
    
    cursor.close()
    bd.close()
    secundario.mainloop()

def mostrarPorTema():
# CONTROL SHIFT 7
    busqueda = tkinter.Tk()
    busqueda.title('Busqueda')
    buscador = tkinter.Entry(busqueda)
    button = tkinter.Button(busqueda, command = (lambda : mostrarBusqueda('tema', buscador.get())))
    buscador.pack()
    button.pack()

    
def mostrarPorAutor():
    busqueda = tkinter.Tk()
    busqueda.title('Busqueda')
    buscador = tkinter.Entry(busqueda)
    button = tkinter.Button(busqueda, command = (lambda : mostrarBusqueda('autor', buscador.get())))
    buscador.pack()
    button.pack()
    
def mostrarPorFecha():
    busqueda = tkinter.Tk()
    busqueda.title('Busqueda')
    buscador = tkinter.Entry(busqueda)
    button = tkinter.Button(busqueda, command = (lambda : mostrarBusqueda('', buscador.get())))
    buscador.pack()
    button.pack()

##########INTERFAZ GRÁFICA
principal = tkinter.Tk() #Creamos el tk principal
principal.title("Menu")
principal.geometry("250x10")
menuPrincipal = tkinter.Menu(principal) #Le añadimos un menú

menuPrincipal.add_command(label="CARGAR", command=cargarDatos)
menuPrincipal.add_command(label="LISTAR", command=listarDatos)
menuPrincipal.add_command(label="BUSCAR", command=mostrarPorTema)

principal.config(menu=menuPrincipal) #Añade el menu al tk principal
principal.mainloop() #Echa las cosas a andar