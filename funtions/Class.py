import json
import pymongo
import requests
import random
import re
import os
import sys
import tkinter as tk
import subprocess as sub
import pyttsx3
import pywhatkit
import speech_recognition as sr
from tkinter import *
from tabulate import tabulate
from pymongo import MongoClient



engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 145)


def talk(text):
    engine.say(text)
    engine.runAndWait()

def conexion():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    return client

def conexion_verificacion():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    return client["MusicPlayList"]

class Cancion:
    def __init__(self, nombre, cantante, genero, album, url):
        self.nombre = nombre
        self.cantante = cantante
        self.genero = genero
        self.album = album
        self.url = url

    def agregar_canciones_bd(url):
        # Conexión a la base de datos
        client = conexion()
        db = client.MusicPlayList

        # Obtener datos de la URL
        response = requests.get(url)
        canciones_json = json.loads(response.text)['results']

        # Insertar cada canción en la base de datos
        for cancion_json in canciones_json:
            cancion = Cancion(
                cancion_json['trackName'],
                cancion_json['artistName'],
                cancion_json['primaryGenreName'],
                cancion_json['collectionName'],
                cancion_json['trackViewUrl']
            )
            db.canciones.insert_one(cancion.__dict__)

        talk("Canciones insertadas en la base de datos.")

class PlayList(object):

    def __init__(self, nombre, usuario, canciones):
        self.name = nombre
        self.user = usuario
        self.songs = canciones

    def __str__():
        client = conexion()
        db = client.MusicPlayList
        try:
            cursor = db.playlist.find({"username": usuario})
            playlist_str = ""
            for pl in cursor:
                for song in pl["canciones"]:
                    cancion = song["nombre"]
                    cantante = song["cantante"]
                    genero = song["genero"]
                    playlist_str += f"{cancion} de {cantante}\n"
                    print(f"{cancion}\n{cantante}\n{genero}\n")

            if playlist_str:
                talk(f"Las canciones de la playlist del usuario {usuario} son:")
                talk(playlist_str)
            # Obtener todas las playlists
            playlist = db.playlist.find_one({"username": usuario})

            if playlist:
                num_canciones = len(playlist["canciones"])
                talk(f"La playlist del usuario {usuario} tiene {num_canciones} canciones.")
            else:
                talk(f"El usuario {usuario} no tiene canciones añadidas")
        except NameError:
            talk("No puedes consultar canciones mientra no crees un usuario")    
            window_sug.destroy()

    def mostrar_sugerencias(self):
        # Una lista de canciones aletorias con (nombre, cantante, id)
        l = []
        client = conexion()
        db = client.MusicPlayList
        canciones = []
        for e in self.songs:
            cursor = db.canciones.find({"_id": e})
            if cursor:
                for j in cursor:
                    sog = j
                    canciones.append(sog)
        playlist = {
                "nombre":self.name,
                "username":self.user,
                "canciones":[canciones]
                }
        db.playlist.insert_one(playlist)
        for i in self.songs:
            cursor = db.canciones.find({"_id": i})
            if cursor:
                for m in cursor:
                    r = m["nombre"], m["cantante"]
                    l.append(r)     
        return l


def num_sug():
    global randon_songs
    client = conexion()
    db = client.MusicPlayList
    try:
        # Crear una lista vacía con el mismo número de elementos que randon_songs
        songs = [None] * len(randon_songs)

        # Iterar sobre los identificadores de canciones y agregar el diccionario a la posición correspondiente en la lista "songs"
        for index, song_id in enumerate(randon_songs):
            cursor = db.canciones.find({"_id": song_id})
            if cursor:
                for m in cursor:
                    k = {
                        "nombre": m["nombre"],
                        "cantante": m["cantante"],
                        "genero": m["genero"],
                        "album": m["album"],
                        "url": m["url"]
                    }
                    songs[index] = k
    except NameError:
        talk("No puedes añadir canciones mientras no existan sugerencias")
        window_sug.destroy()
    return songs


def añadir_cancion(posicion):
    try:
        client = conexion()
        db = client.MusicPlayList

        # Obtener el diccionario de canción correspondiente a la posición del botón
        cancion = num_sug()[posicion-1]

        cursor = db.playlist.find_one({"username": usuario})
        if cursor is None:
            # Si el usuario no tiene una lista de reproducción, crear una nueva con la canción seleccionada
            song_pl = {
                "nombre": nombre,
                "username": usuario,
                "canciones": [{
                    "nombre": cancion["nombre"],
                    "cantante": cancion["cantante"],
                    "genero": cancion["genero"],
                    "album": cancion["album"],
                    "url": cancion["url"]
                }]
            }
            db.playlist.insert_one(song_pl)
            talk("Lista de reproducción creada con éxito")

        else:
            db.playlist.update_one(
                {"username": usuario},
                {"$push": {
                    "canciones": {
                        "nombre": cancion["nombre"],
                        "cantante": cancion["cantante"],
                        "genero": cancion["genero"],
                        "album": cancion["album"],
                        "url": cancion["url"]
                    }
                }}
            )
            talk("Canción agregada con éxito")
    except IndexError:
        talk("No puedes añadir canciones que no existen")

def num_sug_all():
    client = conexion()
    db = client.MusicPlayList
        # Construir lista de diccionarios de canciones
    songs = []
    songs_d = []
    try:
        cursor = db.playlist.find_one({"username": usuario})
        if cursor is None:
            for i in randon_songs:
                cursor = db.canciones.find({"_id": i})
                if cursor:
                    for m in cursor:
                        k = {
                            "nombre": m["nombre"],
                            "cantante": m["cantante"],
                            "genero": m["genero"],
                            "album": m["album"],
                            "url": m["url"]
                        }
                        songs.append(k)
            # Construir lista de diccionarios de playlists
            playlist = [{
                "nombre": nombre,
                "username": usuario,
                "canciones": songs
            }]
            talk("La playlist se a creado con todas las canciones")
            # Insertar lista de playlists en la base de datos
            db.playlist.insert_many(playlist)
        else:
            for i in randon_songs:
                cursor = db.canciones.find({"_id": i})
                if cursor:
                    for m in cursor:
                        g = {
                            "nombre": m["nombre"],
                            "cantante": m["cantante"],
                            "genero": m["genero"],
                            "album": m["album"],
                            "url": m["url"]
                        }
                        songs_d.append(g)
            db.playlist.update_one(
                {"username": usuario},
                {"$push": {
                    "canciones": songs_d
                }}
            )
            talk("Se han añadido todas las canciones a tu playlist")
    except NameError:
        talk("No puedes añadir canciones mientras no existan sugerencias")
        window_sug.destroy()

def interfaz_botones():

    # Verificar si la base de datos existe antes de continuar
    if "MusicPlayList" not in conexion_verificacion().client.list_database_names():
        talk("No puedes mostrar sugerencias sin crear la base de datos")
        return

    global window_sug, table_text
    window_sug = Toplevel()
    window_sug.title("I-USER")
    window_sug.geometry("400x530")
    window_sug.resizable(0, 0)
    window_sug.configure(background="#666F80")

    table_text = Text(window_sug, height=20, width=60, font=('Arial', 6, 'bold'))
    table_text.pack()

    generate_button = Button(window_sug, text="Generar sugerencias", bg='#FF9EA0', fg="black", command=mostrar_sugerencias)
    generate_button.pack()

    Label_title = Label(window_sug, text="Botones para agregar sugerencias de canciones", bg="#666F80",
                    fg="black", font=('Arial', 8, 'bold'))
    Label_title.pack(pady=5)

    button_uno = Button(window_sug, text="1", width=2, command=lambda: añadir_cancion(1))
    button_uno.place(x=3, y=380)

    button_dos = Button(window_sug, text="2", width=2, command=lambda: añadir_cancion(2))
    button_dos.place(x=43, y=380)

    button_tres = Button(window_sug, text="3", width=2, command=lambda: añadir_cancion(3))
    button_tres.place(x=83, y=380)

    button_cuatro = Button(window_sug, text="4", width=2, command=lambda: añadir_cancion(4))
    button_cuatro.place(x=123, y=380)

    button_cinco = Button(window_sug, text="5", width=2, command=lambda: añadir_cancion(5))
    button_cinco.place(x=163, y=380)

    button_seis = Button(window_sug, text="6", width=2, command=lambda: añadir_cancion(6))
    button_seis.place(x=203, y=380)

    button_siete = Button(window_sug, text="7", width=2, command=lambda: añadir_cancion(7))
    button_siete.place(x=243, y=380)

    button_ocho = Button(window_sug, text="8", width=2, command=lambda: añadir_cancion(8))
    button_ocho.place(x=283, y=380)

    button_nueve = Button(window_sug, text="9", width=2, command=lambda: añadir_cancion(9))
    button_nueve.place(x=323, y=380)

    button_diez = Button(window_sug, text="10", width=2, command=lambda: añadir_cancion(10))
    button_diez.place(x=365, y=380)

    button_once = Button(window_sug, text="11", width=2, command=lambda: añadir_cancion(11))
    button_once.place(x=3, y=430)

    button_doce = Button(window_sug, text="12", width=2, command=lambda: añadir_cancion(12))
    button_doce.place(x=43, y=430)

    button_trece = Button(window_sug, text="13", width=2, command=lambda: añadir_cancion(13))
    button_trece.place(x=83, y=430)

    button_catorce = Button(window_sug, text="14", width=2, command=lambda: añadir_cancion(14))
    button_catorce.place(x=123, y=430)

    button_quince = Button(window_sug, text="15", width=2, command=lambda: añadir_cancion(15))
    button_quince.place(x=163, y=430)

    button_dseis = Button(window_sug, text="16", width=2, command=lambda: añadir_cancion(16))
    button_dseis.place(x=203, y=430)

    button_dsiete = Button(window_sug, text="17", width=2, command=lambda: añadir_cancion(17))
    button_dsiete.place(x=243, y=430)

    button_docho = Button(window_sug, text="18", width=2, command=lambda: añadir_cancion(18))
    button_docho.place(x=283, y=430)

    button_dnueve = Button(window_sug, text="19", width=2, command=lambda: añadir_cancion(19))
    button_dnueve.place(x=323, y=430)

    button_veinte = Button(window_sug, text="20", width=2, command=lambda: añadir_cancion(20))
    button_veinte.place(x=365, y=430)

    button_todas = Button(window_sug, text="Añadir Todas", width=10, command=num_sug_all)
    button_todas.place(x=140, y=480)

    button_todas = Button(window_sug, text="Tus playlist", width=10, command=count_playlists)
    button_todas.place(x=5, y=480)

    button_todas = Button(window_sug, text="Tus canciones", width=11, command=PlayList.__str__)
    button_todas.place(x=275, y=480)

    window_sug.mainloop()

def mostrar_sugerencias():
    client = conexion()
    db = client.MusicPlayList
    try:
        cursor = db.usuario.find_one({"username": usuario})
        if cursor:
            global randon_songs
            randon_songs = lista_canciones()
            p = PlayList("PlayListGeneral", "admin", randon_songs)
            e = list(enumerate(p.mostrar_sugerencias(), start=1))
            table = tabulate(e, headers=['#', 'Nombre  -  Cantante'])
            table_text.insert(END, table)
        else:
            talk("No existe un usuario para generar sugerencias por favor cree un usuario")
    except NameError:
        talk("No existe un usuario para generar sugerencias por favor cree un usuario")
        window_sug.destroy()


def extructurandoData_Base():
    client = conexion()
    db = client.MusicPlayList
    lc = db.list_collection_names()
    if "usuario" not in lc:
        db.create_collection("usuario")
        talk("La Base de Datos MusicPlayList ha creado exitosamente")
        talk("Colección usuario se ha creada correctamente")
    else:
        talk("La colección usuario ya existe")
    if "playlist" not in lc:
        db.create_collection("playlist")
        talk("Colección playlist creada correctamente")
    else:
        talk("La colección playlist ya existe")
    if "canciones" not in lc:
        db.create_collection("canciones")
        talk("Colección canciones creada correctamente")
    else:
        talk("La colección canciones ya existe")
    

def validacion_user():

    # Verificar si la base de datos existe antes de continuar
    if "MusicPlayList" not in conexion_verificacion().client.list_database_names():
        talk("No puedes agregar un usuario sin crear la base de datos")
        return

    window_user = Toplevel()
    window_user.title("I-USER")
    window_user.geometry("300x350")
    window_user.resizable(0, 0)
    window_user.configure(background="#666F80")

    lista = []

    def guardar():
        global nombre, usuario
        nonlocal nombre_entry, apellido_entry, usuario_entry, email_entry, lista
        
        nombre = nombre_entry.get()
        apellido = apellido_entry.get()
        usuario = usuario_entry.get()
        email = email_entry.get()
        
        if nombre.isalpha():
            lista.append(nombre.capitalize())
        else:
            talk("Por favor ingrese un nombre válido (solo letras).")
            return

        if apellido.isalpha():
            lista.append(apellido.capitalize())
        else:
            talk("Por favor ingrese un apellido válido (solo letras).")
            return

        if usuario.isalnum():
            lista.append(usuario)

        else:
            talk("Por favor ingrese un nombre de ususario válido (sin signos de puntuación).")
            return

        if "@" in email and "." in email:
            lista.append(email)
        else:
            talk("Por favor ingrese un correo electrónico válido.")
            return

        if len(lista) == 4:
            nombre = lista[0]
            apellido = lista[1]
            usuario = lista[2]
            email = lista[3]
            crear_user(nombre, apellido, usuario, email)
        else:
            talk("Error en los datos del usuario")
        window_user.destroy()


    title_label = Label(window_user, text="Incert Nombre",
                        fg="White", bg="#666F80", font=('Arial', 10, 'bold'))
    title_label.pack(pady=3)

    nombre_entry = Entry(window_user)
    nombre_entry.pack(pady=1)
    nombre_entry.focus()
    talk("Por favor introduzca un nombre válido (Solo Letras)")

    title_label = Label(window_user, text="Incert Apellido",
                        fg="White", bg="#666F80", font=('Arial', 10, 'bold'))
    title_label.pack(pady=3)

    apellido_entry = Entry(window_user)
    apellido_entry.pack(pady=1)
    talk("Por favor introduzca un apellido válido (Solo Letras)")

    title_label = Label(window_user, text="Incert Usuario",
                        fg="White", bg="#666F80", font=('Arial', 10, 'bold'))
    title_label.pack(pady=3)

    usuario_entry = Entry(window_user)
    usuario_entry.pack(pady=1)
    talk("Por favor usuario válido (Sin signos de puntuación)")

    title_label = Label(window_user, text="Incert email",
                        fg="White", bg="#666F80", font=('Arial', 10, 'bold'))
    title_label.pack(pady=3)

    email_entry = Entry(window_user)
    email_entry.pack(pady=1)
    talk("Por favor introduzca un correo válido")

    save_button = Button(window_user, text="Guardar", bg='#FF9EA0',
                         fg="black", width=7, height=1, command=guardar)
    save_button.pack(pady=4)

    window_user.bind('<Return>', lambda event: guardar())


def crear_user(nombre, apellido, usuario, email):
    client = conexion()
    db = client.MusicPlayList
    cursor = db.usuario.find_one({"username":usuario})
    if cursor is None:
        user = ([{
            "nombre":nombre,
            "apellido":apellido,
            "username":usuario,
            "email":email
        }])
        db.usuario.insert_many(user)
        talk("Usuario creado con éxito")
    else:
        talk(f"Ya existe un usuario{usuario}")
        talk("Por favor inténte con otro usuario")


def lista_canciones(cant=20):
    # Una lista de 20 canciones aleatorias
    lista = []
    client = conexion()
    db = client.MusicPlayList
    cursor = db.canciones.aggregate([{"$sample": {"size": cant}}])
    for song in cursor:
        lista.append(song["_id"])
    return lista


def count_playlists():
    client = conexion()
    db = client.MusicPlayList
    try:
        count = db.playlist.count_documents({"username": usuario})
        if count > 0:
            talk(f"Hay {count} playlist del usuario {usuario}")
        else:
            talk(f"No se encontraron playlist del usuario {usuario},   añada canciones para crear una playlist")
    except NameError:
        talk("No puedes consultar playlist mientra no crees un usuario")
        window_sug.destroy()
