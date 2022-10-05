import socket

ser = socket.socket()
host = '0.0.0.0'
port = 999
ser.bind((host, port))
ser.listen(3)
while True:
    c, address = ser.accept()
    print(' : ' + c.recv(1024).decode())
    brk = True
    while True:
         mess = input('Enter message : ')
         if mess == 'exit':
             brk = False
         if not brk:
            break

         c.send(bytes(mess, 'utf-8'))
         print(' : ' + c.recv(1024).decode())
    if not brk:
        break



c.close()