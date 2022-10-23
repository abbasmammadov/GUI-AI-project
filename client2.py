import socket


def Main():
    host = '0.0.0.0'
    port = 999
    server = (host, port) # replace with server IP_addr
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        message = input("[enter q to quit] -> ")
        if message == 'q': break
        s.sendto(message.encode('utf-8'), server)
        data, _ = s.recvfrom(1024)
        data = data.decode('utf-8')
        print("Received from server: " + data)
    s.close()

if __name__=='__main__':
    Main()
