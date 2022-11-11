import socket
from ML_model.detect import run, ROOT
import argparse
import os
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
    # host = '0.
    # 0.0.0'
    port = 21537


    # 21536 ~ 21540
    # port = 999

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    decode_format = 'utf-8'
    buffer_size = 1024
    # server_foler = 
    # decode_format = 'ISO-8859-1'
    print("Server Started")
    while True:
        
        print("wait")
        # client = s
        print("new connection")

        client, address = s.accept()
        # we already loaded the checkpoint and the datayaml file, so it's just feeding it to the above function

        # first let's receive the name and the size of the video file
        file_name = client.recv(buffer_size).decode('utf-8')
        # file_size = client.recv(buffer_size).decode('utf-8')
        # print('received file_size is:', file_size, 'and its type is', type(file_size))
        print('path of the file which is received', file_name) # kalebmes06/Desktop/KAI/GUI-AI-PROJECT/ML_model/data/railway_demo.mp4
        # we have to only use the path after 'ML_model'. so let's cut everything before it
        if 'GUI-AI-project' in file_name:
            file_name = file_name.split('GUI-AI-project/')[1] # -> [ML_model, data, railway_demo.mp4] -> ML_model/data/railway_demo.mp4
            print('filename has been edited to ', file_name)
        # now let's receive the video file
        print('starting to read bytes of the video file')
        #data = client.recv(buffer_size) 
        # with open(file_name.split('.')[0] + '2.mp4', 'wb') as f:
        with open(file_name, 'wb') as f:
            c = 0
            # while c <= int(file_size):
            while True:
                #f.write(data)
                #print(f'data / buffer - {c}')   
                
                data = client.recv(buffer_size)
                if data == b"DONE":
                    print("DONE")
                    break
                f.write(data)
                c += buffer_size
                print('received:', c, 'byte')     
            f.close()
                # print(f'recieved {c} bytes')
                # c+=len(data)
        
        # msg = client.recv(buffer_size).decode('utf-8')
        # print('message from client:',msg)
        
        # client.close()
        print('done reading bytes of the video')
        
        print('video is now received')
        print('starting analysis')
        print('--------------------')
        # here we have to send a signal to the client so that we can initialize a status-bar
        # msg = 'initialize a status-bar'
        # client.send(msg.encode('utf-8'))
        # do whatever you want with the data, and then send it back
        # data = data.upper()
        # opt = parse_opt(target_source_path, weight_filepath, yaml_filepath)
        # weights = 'ML_model/checkpoints/yolov5_best.pt'
        # weights = 'ML_model/checkpoints/catenary.pt'
        weights = 'ML_model/checkpoints/railway.pt'
        # weights = 'ML_model/checkpoints/yolov5_best.pt'
        # weights = 'ML_model/checkpoints/yolov5_best.pt'
        # weights = 'ML_model/checkpoints/yolov5s6.pt'
        datayaml = 'ML_model/data/railway_compnents.yaml'
        # datayaml = 'ML_model/data/coco128.yaml'
        file_name = '/home/kaleb/GUI-AI-project/' + file_name
        print(file_name)
        # file_name = '/home/kaleb/GUI-AI-project/ML_model/data/railway_demo.mp4'
        opt = parse_opt(weights, file_name, datayaml)
        save_dir = str(run(**vars(opt)))
        print('analysis done')
        print("Sending: " + save_dir)
        if 'GUI-AI-project' in save_dir:
            save_dir = save_dir.split('GUI-AI-project/')[1] # -> [ML_model, runs, exp4] -> ML_model/data/railway_demo.mp4
            print('filename has been edited to ', save_dir)
        # sending result back to the client
        # s.sendto(save_dir.encode('utf-8'), addr)
        # sending result to server
        result_vid = save_dir + '/' + file_name.split('/')[-1] # including the name of the video
        result_vid_filesize = os.path.getsize(result_vid)
        # client, _ = s.accept()
        # let me first send result_vid filename and filesize
        client.send(result_vid.encode('utf-8'))
        # client.send(str(result_vid_filesize).encode('utf-8'))
        
        print('starting to send bytes of the result video')
        # with open(result_vid, 'rb') as f:
        #     # c = 0
        #     # while c <= result_vid_filesize:
        #     data = f.read()
        #     # print(data)
        #     client.sendall(data)
        
        with open(result_vid, 'rb') as f:
            c = 0
            data = f.read(buffer_size)
            while len(data):
                # print(len(data))
                # if len(data) == 0:
                #     break
                client.send(data)
                data = f.read(buffer_size)
                c+=len(data)
                print(f'sent {c} bytes')
        client.send(b"DONE")
        print('sent done message')
        f.close()
            # print(f'sent {c} bytes')
                # c+=len(data)
        # msg = 'result video has been nsent'
        # client.send(msg.encode('utf-8'))
        # print(f'Finished sending {result_vid} to the client')
        
        # send_file_to_server()
        to_close = input('Do you want to close the server? (y/n): ')
        if to_close.lower() == 'y':
            print('Server closed')
            client.close()
            break
        else:
            print('Server still running')
        print('server will keep running. to close press ctrl + C')
    s.close()

if __name__=='__main__':
    Main()