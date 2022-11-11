# GUI-AI-project
Graphical User Interface for AI project


## Instructions for making inference on a server, whose data is on a removable USB drive

this text assumes your drive uses the letter z to map the removable disk

  * First delete any preused drives using this command
      `net use z: /delete`
      
  * inquire users to put information about the USB drive letter
  * Let's say our drive's name we use is e, and 192.168.xx.xx is the ip address of the company

  * then to make the USB a shared file over the network mentioned below, run
      `net use z: \\\\192.168.xx.xx\\e`

  * inquire users to provide their username and the remote server's address
  * Let's say your server information is username@server_address:port
  * first create a mount folder - named 'mount'
  * you need to have a sudo access

Next, move to the server's terminal, and execute the rest of the commands

if there is no mount folder, we should create a mount point using

  * `sudo mkdir /home/username/mount`

then to mount our usb drive into our server, we can execute this command

* `sudo mount.cifs //192.168.xx.xx/e /home/username/mount -o user=share,password=share`

if that returns a 'resource busy' error, first unmount it using this command -> `sudo umount -l /home/username/mount`

* Now all you need to do is execute the `detect.py` from the forked yolov5 repository (named as ML_model)
* change your directory to GUI-AI-project/, and change 'video_name' to the actual name of the video, and run

`python3 ML_model/detect.py --weights {checkpoint_path} --source {path_to_be_analyzed_video} --project /home/username/mount/`




