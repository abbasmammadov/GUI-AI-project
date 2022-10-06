import socket

ser = socket.socket()
host = '0.0.0.0'
port = 999
ser.bind((host, port))
ser.listen(3)
end = False
while not end:
    c, address = ser.accept()
    print(' : ' + c.recv(1024).decode())
    while True:
         mess = input('Enter message : ')
         if mess == 'exit':
             end = True
         if end:
            break

         c.send(bytes(mess, 'utf-8'))
         print(' : ' + c.recv(1024).decode())


c.close()