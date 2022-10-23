import paramiko

hostname = '125.138.99.152'
port = 7024
user = 'kaleb'
password = '1q2w3e4r'

try:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port, user, password)

    while True:
        try:
            cmd = input('Enter command: ')
            if cmd == 'exit': break
            stdin, stdout, stderr = client.exec_command(cmd)
        
        except KeyBoardInterrupt:
            print('Interrupted by user')
            break
    client.close()
except Exception as e:
    print(str(e))