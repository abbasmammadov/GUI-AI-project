import socket
from ML_model.detect import run, ROOT
import argparse
# def parse_opt(weights, source, datayaml):
#             parser = argparse.ArgumentParser()
#             parser.add_argument('--weights', nargs='+', type=str, default=str(weights), help='model path(s)')
#             parser.add_argument('--source', type=str, default=str(source), help='file/dir/URL/glob, 0 for webcam')
#             parser.add_argument('--data', type=str, default=str(datayaml), help='(optional) dataset.yaml path')
#             parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
#             parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
#             parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
#             parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
#             parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
#             parser.add_argument('--view-img', action='store_true', help='show results')
#             parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
#             parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
#             parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
#             parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
#             parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
#             parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
#             parser.add_argument('--augment', action='store_true', help='augmented inference')
#             parser.add_argument('--visualize', action='store_true', help='visualize features')
#             parser.add_argument('--update', action='store_true', help='update all models')
#             parser.add_argument('--project', default=(str(ROOT) + '/runs'), help='save results to project/name')
#             parser.add_argument('--name', default='exp', help='save results to project/name')
#             parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
#             parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
#             parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
#             parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
#             parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
#             parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
#             opt = parser.parse_args()
#             opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
#             return opt
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
 
    host = '0.0.0.0'
    port = 999

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    print("Server Started")
    while True:
        message, addr = s.recvfrom(1024)
        message = message.decode('utf-8')
        (weights, source, datayaml) = message.split(',')[:-1]
        
        print('####WEIGHTS####')
        print('####WEIGHTS####')
        print('####WEIGHTS####')
        print(weights)
        print('####WEIGHTS####')
        print('####WEIGHTS####')
        print('####WEIGHTS####')
        print("Message from: " + str(addr))
        # print("From connected user: " + message) -> because message is very long
        print('starting analysis')
        print('--------------------')
        # do whatever you want with the data, and then send it back
        # data = data.upper()
        opt = parse_opt(weights, source, datayaml)
        save_dir = str(run(**vars(opt)))
        print('analysis done')
        print("Sending: " + save_dir)
        s.sendto(save_dir.encode('utf-8'), addr)
    s.close()

if __name__=='__main__':
    Main()