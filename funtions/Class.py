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

        print("Canciones insertadas en la base de datos.")

def extructurarData_Base():
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
    

# def validacion_email(correo):
#     re = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
#     return re.match(re, correo) is not None


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
            print(lista)
        else:
            talk("Por favor ingrese un nombre válido (solo letras).")
            return

        if apellido.isalpha():
            lista.append(apellido.capitalize())
            print(lista)
        else:
            talk("Por favor ingrese un apellido válido (solo letras).")
            return

        if usuario.isalnum():
            lista.append(usuario)
            print(lista)
        else:
            talk("Por favor ingrese un nombre de ususario válido (sin signos de puntuación).")
            return

        if "@" in email and "." in email:
            lista.append(email)
            print(lista)
        else:
            talk("Por favor ingrese un correo electrónico válido.")
            return

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

    return lista
    

def procesar_usuario():
    datos_usuario = validacion_user
    if len(datos_usuario) == 4:
        nombre = datos_usuario[0]
        apellido = datos_usuario[1]
        usuario = datos_usuario[2]
        email = datos_usuario[3]
        crear_user(nombre, apellido, usuario, email)
    else:
        talk("Error en los datos del usuario")

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
        # Mensaje de confirmación
        message = f"Se ha creado la cuenta para {usuario} con éxito."
        messagebox.showinfo("Registro exitoso", message)
    else:
        talk(f"Ya existe un usuario ({usuario}) ")
        talk("Por favor inténte con otro username")

    # def valida_user_name(username):
    #     # validar que el nombre de usuario no contiene espacios
    #     if " " in username:
    #         talk("El nombre de usuario no puede contener espacios.")
    #         return ""
    #     return username

    # def validacion_email(email):
    #     # validar que el correo contiene un "@" y un "."
    #     if "@" not in email and "." not in email:
    #         talk("El correo electrónico no es válido.")
    #         return False
    #     return True


    # def validacion_email(email):
    #     # validar que el correo tenga formato válido usando una expresión regular
    #     regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    #     if not re.match(regex, email):
    #         talk("El correo electrónico no es válido.")
    #         return False
    #     return True
    window_user.mainloop()




