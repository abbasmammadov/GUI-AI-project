import socket

soc = socket.socket()
host = '0.0.0.0'
port = 999
soc.connect((host, port))
while True:

    mess = input('Enter message : ')
    if mess == 'exit':
        break
        

    soc.send(bytes(mess, 'utf-8'))

    print(soc.recv(1024).decode())

soc.close()