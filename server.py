import socket
import threading
import base64
import cv2
import os
import json
from moviepy.editor import VideoFileClip, concatenate_videoclips


# SETS
# A = Pendiente
# B = Procesando
# C = Fallo
# D = Contado

sets_totales = 0
sets_contados = 0

listImages = os.listdir('CAM_FRONT')

sets = {}
for i in range(0, len(listImages), 100):
    id= len(sets)+1
    set = {
        'id': id,
        'images': listImages[i:i+100],
        'estado': 'A'
    }

    sets[id] = set
    sets_totales += 1

def obtenerSetDisponible():
    for key, set in sets.items():
        if set['estado'] == 'A' or set['estado'] == 'C':
            set['estado'] = 'B'
            return set
    return None

def sendArraynames(client_socket, setAsignado):
    try:
        client_socket.send(json.dumps(setAsignado).encode())
    except Exception as e:
        print(f"Error sending message: {e}")
        # break

def cambiarEstadoSet(idSet, estado):
    for key in sets.keys():
        if sets[key]['id'] == idSet:
            sets[key]['estado'] = estado

def circuitBreaker(mensaje, socket, setId):
    codigo = mensaje['codigo']
    idSet = mensaje['id']

    if codigo == 'F':
        print(f'Fracaso al procesar set {idSet}')
        cambiarEstadoSet(idSet, 'C')
    
    elif codigo == 'V':
        recibirVideo(socket, setId)
    
    return codigo


def recibirVideo(server_socket, id):
    global sets_totales
    global sets_contados

    try:
        data = b''
    
        while True:
            chunk = server_socket.recv(10000)
            data += chunk

            
            try:
                # try to convert data to dictionary
                diccionario = json.loads(data.decode())

                # si esta completo el diccionaro se rompe el ciclo
                print('intentando escribir')
                with open('resultado/'+str(id)+'.mp4', 'wb') as f:
                    f.write(base64.b64decode(diccionario['datos']))
                    f.flush()
                break
            except Exception as e:
                # if unsuccessful, continue receiving data
                continue
        sets[id]['estado'] = 'D'
        sets_contados += 1

    except Exception as e:
        print(f"Error receiving message: {e}")
        cambiarEstadoSet(id, 'C')
        


def incorporarVideos():
    ruta_resultado = 'resultado/resultado.mp4'
    videos = []

    for key in sets.keys():
        ruta_set = f'nodo/set_{key}.mp4'
        video_set = VideoFileClip(ruta_set)
        videos.append(video_set)
        
        print(f'Incorporando set {key}\nRuta: {ruta_set}')
        
    video_resultado = concatenate_videoclips(videos)
    video_resultado.write_videofile(ruta_resultado, codec="libx264")



def handle_client(client_socket, addr):
    global sets_contados
    global sets_totales

    while True:
        setAsignado = obtenerSetDisponible()

        if sets_contados == sets_totales:
            break

        if not setAsignado:
            continue

        sendArraynames(client_socket, setAsignado)

        mensaje = client_socket.recv(1024).decode()
        dic = json.loads(mensaje)

        circuitBreaker(dic, client_socket, setAsignado['id'])

    incorporarVideos()


def start_server():
    server_socket = socket.socket(
            socket.AF_INET,     # Especifica la familia direcciones, como la IPV4
            socket.SOCK_STREAM  # Este argumento especifica que se usará TCP
    )
    server_socket.bind(('127.0.0.1', 5000))
    server_socket.listen(100)
    print("Server started. Waiting for connections...")

    while True:
        client_socket, client_address = server_socket.accept()

        print(f"Connection from {client_address} has been established!")
        client_thread = threading.Thread(
            target = handle_client, 
            args   = (client_socket, client_address)
        )
        client_thread.start()

start_server()

