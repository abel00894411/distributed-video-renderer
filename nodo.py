import socket
import threading
import base64

#dependencies to convert image to video
import cv2
import os
import json


print("Nodo iniciado")
serverIp = '127.0.0.1'
port = 5000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((serverIp, port))


def recibirJson():
    try:
        message = ''
        while True:
            print('recibiendo mensaje...')
            message = message + server_socket.recv(10000).decode()
            if message.endswith('}'):
                break
        print(message)
        jsonReceive = json.loads(message)
        return jsonReceive
    except Exception as e:
        print(f"Error receiving message: {e}")
        return []


def create_video_from_images(arrayNames,image_folder, video_name, fps, idSet):

    try:

        # Definir el codec y crear el objeto VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec para .mp4
        height, width, layers = 0,0,0
        video = 0
        i=0
        for name in arrayNames:
            pathFile = os.path.join(image_folder, name)
            if not os.path.isfile(pathFile):
                print(f"La imagen {name} no existe.")

                # REGRESAR UN MENSAJE CON CÓDIGO F (FALLO)
                server_socket.send(json.dumps({
                    'id': idSet,
                    'codigo': 'F'
                }).encode())

                return False
            image = cv2.imread(pathFile)
            if i==0:
                # este if es solo para que lo haga una vez ya que no tiene caso hacerlo mas de una vez 
                # porque todas las imagenes tienen el mismo tamaño
                # Leer la primera imagen para obtener el tamaño del video
                # frame = cv2.imread(os.path.join(image_folder,))
                height, width, layers = image.shape
                video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))
            video.write(image)
            print(f"Frame {i} agregado al video")
            i+=1
        # Liberar el objeto VideoWriter
        video.release()
    
    except Exception as e:
        print(f"Error creando el video: {e}")
        server_socket.send(json.dumps({
            'id': idSet,
            'codigo': 'F'
        }).encode())
        return False
    return True


def sendVideo(video_name, idSet):
    # Señal para que el servidor sepa que está a punto de recibir datos de video
    server_socket.send(json.dumps({
        'id': idSet,
        'codigo': 'V'
    }).encode())

    with open(video_name, 'rb') as f:

        diccionario = {
            'id': idSet,
            'codigo': 'R',
            'datos':  base64.b64encode(f.read()).decode('utf-8')
        }
        
        server_socket.send(json.dumps(diccionario).encode())
     
    print("Video enviado - metodo send")

def work():
    while True:
        set_json = recibirJson()
        if len(set_json) > 0:
            
            img = set_json['images']
            id = set_json['id']
            videoPath = f'nodo/set_{id}.mp4'
            isVideoCreated = create_video_from_images(img, 'CAM_FRONT', videoPath, 20, id)
            if isVideoCreated:
                sendVideo(videoPath, id)
        

work()