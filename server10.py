import cv2
import _pickle as cPickle
import socket
import struct

TCP_IP = '125.138.99.152'
TCP_PORT = 21537
video_file = 'ML_model/data/railway_demo.mp4'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # establishing a tcp connection
sock.connect((TCP_IP,TCP_PORT))

while True:
    # client_socket, client_address = sock.accept() # wait for client
    client_socket = sock # wait for client
    # print(f'connection established with {str(client_address)}')
    cap = cv2.VideoCapture(video_file)
    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    while True:
        flag, frame = cap.read()
        if flag:
            frame = cPickle.dumps(frame)
            size = len(frame)
            p = struct.pack('I', size)
            frame = p + frame
            client_socket.sendall(frame)
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            size = 10
            p = struct.pack("I", size)
            client_socket.send(p)
            client_socket.send('')
            break   
        else:
        	cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame-1)
         
