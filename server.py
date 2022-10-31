import socket
from ML_model.detect import run, ROOT
import argparse
from send_receive_file import send_file_to_server, receive_file
import sys
from tqdm import tqdm
import os
import torch
def parse_opt(weights, source, datayaml):
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default=weights, help='model path or triton URL')
    parser.add_argument('--source', type=str, default=source, help='file/dir/URL/glob/screen/0(webcam)')
    parser.add_argument('--data', type=str, default=datayaml, help='(optional) dataset.yaml path')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='show results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default=ROOT / 'runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    parser.add_argument('--vid-stride', type=int, default=1, help='video frame-rate stride')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    
    return opt
def Main():
 
    # host = '192.168.55.224'
    host = ''
    # host = '0.0.0.0'
    port = 21537


    # 21536 ~ 21540
    # port = 999

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    decode_format = 'utf-8'
    # server_foler = 
    # decode_format = 'ISO-8859-1'
    print("Server Started")
    while True:
        print("wait")
        client, address = s.accept()
        print("new connection")

        # receiving folder name
        # folder_name = client.recv(1024).decode(decode_format)
        # print(folder_name)
        
        # creating folder path
        # server_folder_path = os.path.join('ML_model', 'data', folder_name)

        # if not os.path.exists(server_folder_path):
        #     os.makedirs(server_folder_path)
        #     client.send(f'Folder {folder_name} is created'.encode(decode_format))
        
        # else:
        #     client.send(f'Folder {folder_name} already exists'.encode(decode_format))
        # # receive files from server 
        # only the video is being transferred.
        while True:
            msg = client.recv(1024).decode(decode_format)
            print('this is message')
            print('type of the message', type(msg))
            
            print(msg)
            
            print('yes are are connected:))')
            break
            cmd, data = msg.split('::')
            # print(cmd, data)
            if cmd == 'FILENAME':
               

                # we received the file name
                print(f'[CLIENT] Received the filename: {data}')

                file_path = os.path.join(server_folder_path, data)
                print('the file will be saved here:', file_path)
                # if file_path.endswith('.pt'):
                #     # download from githubusercontent
                #     # if not os.path.exists(file_path):

                #     # torch.hub.download_url_to_file('https://raw.githubusercontent.com/kalebmes/GUI-AI-project/blob/main/ML_model/checkpoints/yolov5_best.pt', file_path)
                #     print('got our checkpoints')
                #     client.send('FileName receieved'.encode(decode_format))
                
                f = open(file_path, 'w')
                client.send('Filename received'.encode(decode_format))
            
            elif cmd == 'DATA':
                # if file_path.endswith('.pt'):
                    
                print(f'[CLIENT] receiving the file data')
                print(file_path)
                print(file_path.endswith('.yaml'))
                # print(data.split('b')[1:])
                # print(data)
                # if file_path.endswith('.txt'):
                #     print('now we got checkpoints to read')
                #     print(data)
                #     # to decode it in the server side, we can use the following command
                #     import base64
                #     # with open(file_path.split('.')[0] + '.txt', 'r') as f:
                #         # file_data = f.read()
                #         # file_data = f.read()
                #     file_data = base64.b64decode(data)
                #     print('new path: ', file_path.split('.')[0] + '.pt')
                #     with open(file_path.split('.')[0] + '.pt', 'wb') as f:
                #         f.write(file_data)
                #         print('check point is written')
                #         # 
                if file_path.endswith('.yaml'):
                    
                    data = eval(''.join(data.split('b')[1:]))
                    # data = eval(data)
                    import yaml
                    parsed_yaml = yaml.dump(data)
                    # print(parsed_yaml)
                    # f.write(data) 
                    print('writing yaml file is done :))')
                    client.send('yaml file writing is done'.encode('utf-8'))

                # if file_path.endswith('.pt'):
                #     print('now we got checkpoints to read')
                #     print(data)
                #     # to decode it in the server side, we can use the following command
                #     import base64
                #     # with open(file_path.split('.')[0] + '.txt', 'r') as f:
                #         # file_data = f.read()
                #         # file_data = f.read()
                #     file_data = base64.b64decode(data)
                #     print('new path: ', file_path.split('.')[0] + '.pt')
                #     with open(file_path.split('.')[0] + '.pt', 'wb') as f:
                #         f.write(file_data)
                #         print('check point is written')
                #         # 
                #     # then we can use the .pt file as usual
                #     # f.write(data)
                # if file_path.endswith('.pt'):
                #     # client.send('checkpoints turn'.encode('utf-8'))
                #    continue
                elif file_path.endswith('.mp4'):
                    print('[CLIENT] receiving the data')
                    print(file_path)
                    with open(file_path, 'wb') as f:
                        c = 0
                        while c <= os.path.getsize(file_path):
                            file_data = client.recv(1024)
                            if not file_data:
                                break
                            f.write(file_data)
                            c+=len(file_data)
                    
                    video_path = file_path
                    break
                    # client.send('Filename received'.encode('utf-8'))
                
                

                # f.write(str(data))
                
                # client.send('File data received'.encode(decode_format))

            elif cmd == 'FINISH':

                f.close()
                print(f'[CLIENT] {data}')
                break
        client.close()
        transferred_files = [os.path.join(server_folder_path, file) for file in os.listdir(server_folder_path)]
        print('these are the files which are transferred okay :))')
        print(transferred_files)
        # source_directory = transferred_files[0]
        # checkpoint_directory = transferred_files[2]
        # yaml_directory = transferred_files[1]


        # source_filename, source_size, weights, weight_filesize, datayaml, yaml_filesize = client.recv(1024).decode(decode_format2).split('_')
        # # source_filesize = int.from_bytes(client.recv(1024), 'big', signed=False)
        # target_source_path = source_directory + '/' + source_filename.split('/')[-1]
        # weight_filepath = checkpoint_directory + '/' + weights.split('/')[-1]
        # yaml_filepath = source_directory + '/' + datayaml.split('/')[-1]
        
        # print(f'names and sizes have been received from the client')
        # client.send(f'Received names and sizes from client').encode(decode_format)
        # # source = receive_file(source_directory + "/" + source_filename, source_filesize, client)
        # # file_path_dict = {target_source_path, weight_filepath, yaml_filepath}
        # # for target_path in target_paths:
        # file_nname = target_path.split('/')[-1]
        # bar = tqdm(range(source_size), f'receiving {file_nnmae}', unit='B', unit_scale=True, unit_divisor=1024)
        # with open(target_source_path, 'wb') as f:
        #     c = 0
        #     while c < int(source_size):
        #         data = client.recv(1024)#.decode(decode_format)
        #         if not data:
        #             break
                
        #         f.write(data)
        #         client.send('Video received'.encode(decode_format))
        #         c += len(data)
        #         bar.update(len(data))
        # # client.close()
        # s.close()

        # weight_filename = client.recv(1024).decode(decode_format2).split('/')[-1]
        # weight_filesize = int.from_bytes(client.recv(1024), 'big', signed=False)
        # print(checkpoint_directory + "/" + weight_filename)
        # weights = receive_file(checkpoint_directory + "/" + weight_filename, weight_filesize, client)

        # yaml_filename = client.recv(1024).decode(decode_format2).split('/')[-1]
        # yaml_filesize = int.from_bytes(client.recv(1024), 'big', signed=False)
        # datayaml = receive_file(source_directory + "/" + yaml_filename, yaml_filesize, client)

        # message, addr = client.recvfrom(1024)
        # message = message.decode('utf-8')
        # (weights, source, datayaml) = message.split(',')[:-1]
        # print("Message from: " + str(addr))
        # print("From connected user: " + message) -> because message is very long
        print('starting analysis')
        print('--------------------')
        # do whatever you want with the data, and then send it back
        # data = data.upper()
        # opt = parse_opt(target_source_path, weight_filepath, yaml_filepath)
        weights = 'ML_model/data/client/yolov5_best.pt'
        transferred_files.append(weights)
        source, datayaml = transferred_files[1], transferred_files[0]
        opt = parse_opt(weights, source, datayaml)
        save_dir = str(run(**vars(opt)))
        print('analysis done')
        print("Sending: " + save_dir)

        # sending result back to server
        # s.sendto(save_dir.encode('utf-8'), addr)
        # sending result to server
        result_vid = save_dir + '/' + source_directory.split('/')[-1]
        # send_file_to_server(result_vid, os.path.getsize(result_vid))
        # bar = tqdm(range(source_size), f'sending {result_vid}', unit='B', unit_scale=True, unit_divisor=1024)

        # with open(result_vid, 'r') as f:
        #     while True:
        #         data = f.read(1024)
        #         if not data:
        #             break
        #         s.send(data.encode(encode_format))
        #         msg = client.recv(1024).decode(encode_format)

        #         bar.update(len(data))
        # now let's send the result video to the client
        print(f'[SERVER] Sending {result_vid} to the client')
        msg = f'FILENAME:{result_vid}'
        client.send(msg.encode(encode_format))

        msg = client.recv(1024).decode()
        print(f'Finished transferring files to the client')
        # client.close()


        # send_file_to_server()
    #     to_close = input('Do you want to close the server? (y/n): ')
    #     if to_close.lower() == 'y':
    #         print('Server closed')
    #         break
    #     else:
    #         print('Server still running')
    # s.close()

if __name__=='__main__':
    Main()