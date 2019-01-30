#https://foros.derecho.com/foro/20-Derecho-Civil-General
# -*- coding: utf-8 -*-

import sqlite3
import tkinter
from tkinter.constants import END
import urllib.request
import re
import datetime
from bs4 import BeautifulSoup
from builtins import str

def convertStringToMonth(m):
    dictionary = {'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6, 'Julio':7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12}
    return dictionary.get(m)

##########FUNCIONES
def cargarDatos():
    #Utilizando BeautifulSoup, extrae para cada película: título, fecha de estreno
    #en España, director/s y sinopsis .
    bd = sqlite3.connect("BD.dat") #Conecta con sql3lite y especifica archivo de destino de los datos
    cursor =  bd.cursor() #Crea un cursor que es lo que utiliza la bd
    cursor.execute("""drop table if EXISTS datos""")
    cursor.execute("""create table datos (id integer primary key autoincrement, titulo text, fechaEstreno date, directores text, sinopsis text)""")
    i = 1
    while i <= 2:
        pageUrl= urllib.request.urlopen('https://www.elseptimoarte.net/estrenos/' + i).read()
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
            cursor.execute("""insert into datos (titulo, fechaEstreno, directores, sinopsis) values (?,?,?,?)""", (title, fecha, directores, sinopsis))
    bd.commit()
    cursor.close()
    bd.close()
    #Además crea esquemas e índices en Whoosh para almacenar dicha información TODO

def mostrarDatos():
    secundario = tkinter.Tk()
    secundario.title("Listado")#Cambia el titulo
    secundario.geometry("500x500") #Cambiamos geometría
    scrollbar = tkinter.Scrollbar(secundario, orient="vertical") #Hacemos una scrollbar
    lista = tkinter.Listbox(secundario, yscrollcommand=scrollbar.set) #Se la asociamos al eje y de la lista
    scrollbar.config(command=lista.yview()) #le asociamos al scroll el eje y de la vista
    scrollbar.pack(side="right", fill="y")
    lista.pack(side="left",fill="both", expand=True)

    bd = sqlite3.connect("BD.dat") #Conecta con sql3lite y especifica archivo de destino de los datos
    cursor =  bd.cursor() #Crea un cursor que es lo que utiliza la bd
    cursor.execute("""select * from datos""")
    for resultado in cursor:
        lista.insert(END, "Título: " + resultado[1]) #Empezamos desde 1 porque el 0 es id
        lista.insert(END, "Link: " + resultado[2])
        lista.insert(END, "Autor: " + resultado[3])
        lista.insert(END, "Fecha y hora: " + resultado[4])
        lista.insert(END, " ")
    cursor.close()
    bd.close()

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

def temasMasPopulares():
    return None
def temasMasActivos():
    return None


##########INTERFAZ GRÁFICA
# principal = tkinter.Tk() #Creamos el tk principal
# principal.title("Menú")
# principal.geometry("250x12")
# menuPrincipal = tkinter.Menu(principal) #Le añadimos un menú
# menuDatos = tkinter.Menu(menuPrincipal, tearoff=0) #Crea el primer desplegable
# menuMostrar = tkinter.Menu(menuPrincipal,tearoff=0)#Crea el segundo
# menuEstadisticas = tkinter.Menu(menuPrincipal,tearoff=0)#Crea el tercero

# #Primer desplegable
# menuDatos.add_command(label="Cargar", command=cargarDatos)
# menuDatos.add_command(label="Mostrar", command=mostrarDatos)
# menuDatos.add_command(label="Salir", command=quit) #Cierra el principal, cuidado con los corchetes
# menuPrincipal.add_cascade(label="Datos", menu=menuDatos)

# #Segundo desplegable
# menuMostrar.add_command(label="Tema", command=mostrarPorTema)
# menuMostrar.add_command(label="Autor", command=mostrarPorAutor)
# menuMostrar.add_command(label="Fecha", command=mostrarPorFecha)
# menuPrincipal.add_cascade(label="Buscar", menu=menuMostrar)

# #Tercer desplegable
# menuEstadisticas.add_command(label="Temas más populares", command=temasMasPopulares)
# menuEstadisticas.add_command(label="Temas más activos", command=temasMasActivos)
# menuPrincipal.add_cascade(label="Estadísticas", menu=menuEstadisticas)


# principal.config(menu=menuPrincipal) #Añade el menu al tk principal
# principal.mainloop() #Echa las cosas a andar