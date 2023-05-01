import json
import pymongo
import requests
import random
import re
import os
import sys
from tkinter import *
import subprocess as sub
import pyttsx3
import pywhatkit
import speech_recognition as sr
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

    def mostrar_sugerencias(self):
        # Una lista de canciones aletorias con (nombre, cantante, id)
        
        # window_sug = Toplevel()
        # window_sug.title("I-USER")
        # window_sug.geometry("300x350")
        # window_sug.resizable(0, 0)
        # window_sug.configure(background="#666F80")
        l = []
        client = conexion()
        db = client.MusicPlayList
        for i in self.songs:
            cursor = db.canciones.find({"_id": i})
            if cursor:
                for j in cursor:
                    t = j["nombre"], j["cantante"]
                    l.append(t)
                    print(l)
        return l

    def crearplaylist (self):
        client = conexion()
        db = client.MusicPlayList
        playlist = ([{
            "nombre":self.name,
            "username":self.user,
            "canciones":[self.songs]
            }])
        db.playlist.insert_many(playlist)

def sugerencias():
    randon_songs = cl.lista_canciones()
    p = cl.PlayList("PlayListGeneral", "admin", randon_songs)

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
    window_user = Toplevel()
    window_user.title("I-USER")
    window_user.geometry("300x350")
    window_user.resizable(0, 0)
    window_user.configure(background="#666F80")

    lista = []

    def guardar():
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
            print(lista)
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


# def lista_canciones(cant = 20):
#     # Una lista de 20 las canciones aleatorias
#     lista = []
#     client = conexion()
#     db = client.MusicPlayList
#     cursor = db.canciones.find()
#     for song in cursor:
#         lista.append(song["_id"])
#     lista = random.sample(lista, cant)
#     return lista

def lista_canciones(cant=20):
    # Una lista de 20 canciones aleatorias
    lista = []
    client = conexion()
    db = client.MusicPlayList
    cursor = db.canciones.aggregate([{"$sample": {"size": cant}}])
    for song in cursor:
        lista.append(song["_id"])
        print(lista)
    return lista

