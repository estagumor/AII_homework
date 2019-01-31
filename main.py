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
from whoosh.query import *

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
            fecha = datetime.datetime(int(information[2]), convertStringToMonth(information[0]), int(information[1]))
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
    lista = tkinter.Listbox(secundario) 
    lista.pack(side="left", fill="both", expand=True)
    lista.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=lista.yview) #le asociamos al scroll el eje y de la vista

    ix = open_dir("index") #Abre el index de antes
    with ix.searcher() as s:
        q = Every() #Devuelve todos los documents
        results = s.search(q, limit=None, sortedby="fecha") #Ordenamos por fecha
        for resultado in results:
            lista.insert(END, "Titulo: " + resultado['titulo'])
            lista.insert(END, "Estreno: " + resultado['fecha'].strftime('%d-%m-%Y'))
            lista.insert(END, " ")
    secundario.mainloop()

def mostrarBusqueda(contenido):
    terciario = tkinter.Tk()
    terciario.title("Resultado de la busqueda")#Cambia el titulo
    terciario.geometry("500x500") #Cambiamos geometría
    scrollbar = tkinter.Scrollbar(terciario) #Hacemos una scrollbar
    scrollbar.pack(side="right", fill="y")
    lista = tkinter.Listbox(terciario) 
    lista.pack(side="left", fill="both", expand=True)
    lista.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=lista.yview) #le asociamos al scroll el eje y de la vista

    ix = open_dir("index") #Abre el index de antes
    with ix.searcher() as s: 
        qp = MultifieldParser(["titulo", "sinopsis"], peliculas)
        q = qp.parse(contenido)
        results = s.search(q, limit= None)
        print(results)
        for resultado in results:
            lista.insert(END, "Titulo: " + resultado['titulo'])
            lista.insert(END, "Estreno: " + resultado['fecha'].strftime('%d-%m-%Y'))
            lista.insert(END, " ")
    terciario.mainloop()

def buscar():
    busqueda = tkinter.Tk()
    busqueda.title('Búsqueda')
    label = tkinter.Label(busqueda, text= "Debe introducir los operadores en mayúsculas")
    buscador = tkinter.Entry(busqueda)
    button = tkinter.Button(busqueda, text="Buscar", command=(lambda: mostrarBusqueda(buscador.get())))
    label.pack()
    buscador.pack()
    button.pack()

##########INTERFAZ GRÁFICA
principal = tkinter.Tk() #Creamos el tk principal
principal.title("Menu")
principal.geometry("250x10")
menuPrincipal = tkinter.Menu(principal) #Le añadimos un menú

menuPrincipal.add_command(label="CARGAR", command=cargarDatos)
menuPrincipal.add_command(label="LISTAR", command=listarDatos)
menuPrincipal.add_command(label="BUSCAR", command=buscar)

principal.config(menu=menuPrincipal) #Añade el menu al tk principal
principal.mainloop() #Echa las cosas a andar