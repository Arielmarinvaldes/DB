from tkinter import *
import subprocess as sub
import pyttsx3
import pywhatkit
import speech_recognition as sr
import json
import requests
import pymongo
from pymongo import MongoClient
from funtions import Class as cl


# Crear ventana principal
main_window = Tk()
main_window.title("GUI")
main_window.geometry("500x400")
main_window.resizable(0, 0)
main_window.configure(bg='#FF9EA0')

Label_title = Label(main_window, text="Proyecto 2 por Ariel Marín", bg="#FF9EA0",
                    fg="black", font=('Arial', 12, 'bold'))
Label_title.pack(pady=5)

cm = """
Por favor siga los pasos

1- crea la estructura de la DB
2- Incerte las canciones de los artista
3- cree un usuario
4- mostrar sugerencias
5- finalizar el programa
"""
canvas_comandos = Canvas(bg="#666F80", height=100, width=200)
canvas_comandos.place(x=1, y=50)
canvas_comandos.create_text(90, 50, fill="#FFFFFF", text=cm, font='Arial 5')

canvas_dos = Canvas(bg="#C3C8D3", height=300, width=200)
canvas_dos.place(x=295, y=50)
canvas_dos.create_text(90, 50, fill="#434343", font='Arial 5')

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 145)


def talk(text):
    engine.say(text)
    engine.runAndWait()


def termina():
    talk("Fin del programa")
    main_window.destroy()


def abrir_ventana_agregar_artista():
    # Crear ventana emergente para agregar artista
    ventana_agregar_artista = Toplevel()
    ventana_agregar_artista.title("Agregar Artista")
    ventana_agregar_artista.geometry("300x150")
    ventana_agregar_artista.configure(background="#666F80")
    ventana_agregar_artista.resizable(0, 0)
    main_window.eval(f'tk::PlaceWindow {str(ventana_agregar_artista)} center')


    # Crear etiqueta y entrada para ingresar el nombre del artista
    name_label = Label(ventana_agregar_artista, text="Nombre del Artista", fg="White",
                       bg="#666F80", font=('Arial', 7, 'bold'))
    name_label.pack(pady=5)

    Label(ventana_agregar_artista, text="Incert User", fg="White", bg="#666F80", font=('Arial', 10, 'bold'))
    nombre_artista_entry = Entry(ventana_agregar_artista)
    nombre_artista_entry.pack(pady=1)
    # Función para actualizar la URL principal de la solicitud de datos
    def actualizar_url_principal():
        try:
            nombre_artista = nombre_artista_entry.get()
            url_principal = f"https://itunes.apple.com/search?term={nombre_artista}&limit=5"
            cl.Cancion.agregar_canciones_bd(url_principal)
            
        except KeyError:
            talk("Error    No se pudo agregar ese artista")

    # Crear botón para actualizar la URL principal y agregar las canciones a la base de datos
    save_button = Button(ventana_agregar_artista, text="Guardar", bg='#FF9EA0',
                        fg="black", width=7, height=1, command=actualizar_url_principal)
    save_button.pack(pady=4)


button_paso_uno = Button(main_window, text="1", command=cl.extructurandoData_Base)
button_paso_uno.place(x=10, y=170)

button_paso_dos = Button(main_window, text="2", command=abrir_ventana_agregar_artista)
button_paso_dos.place(x=50, y=170)

button_paso_tres = Button(main_window, text="3", command=cl.validacion_user)
button_paso_tres.place(x=90, y=170)

button_paso_cuatro = Button(main_window, text="4", command=cl.sug_songs)
button_paso_cuatro.place(x=130, y=170)

button_paso_cinco = Button(main_window, text="5", command=termina)
button_paso_cinco.place(x=170, y=170)



main_window.mainloop()
