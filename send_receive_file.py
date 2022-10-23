
def send_file_to_server(file_path, file_size, client):
            print('path of the file to be sent: ', file_path)
            import time            
            with open(filename, 'rb') as f:
                c = 0
                # starting the time counter
                start_time = time.time()

                while c <= file_size:
                    data = f.read(1024)
                    if not data:
                        break
                    
                    client.sendall(data)
                    c += len(data)
                
                # ending the time counter
                end_time = time.time()

            
            print(f'{file_path} sent to server')
            print(f"Time taken to send the file: {end_time - start_time}")

def receive_file(file_path, file_size, client):
    print('path of the file to be received: ', file_path)
    import time
    with open(file_path, 'wb') as f:
        # starting the time counter
        start_time = time.time()
        c = 0
        print(type(file_size))
        # print(file_size)
        # print(file_size.split()[0].split('\\')[0])
        
        # while c <= file_size:
        #     data = client.recv(1024)
        #     if not data:
        #         break
        #     f.write(data)
        #     c += len(data)
        #     if c % 1000000 == 0:
        #         print(c)
        
        # f.close()
        # ending the time counter
        end_time = time.time()
        
    
    print(f'File received from server, and saved to {file_path}')
    print(f"Time taken to receive the file: {end_time - start_time}")
    return f