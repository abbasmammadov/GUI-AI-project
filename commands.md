Instructions to execute code for mounting USB drive to a remote server

this text assumes your drive uses the letter z to map the removable disk

to delete any preused drives run
`net use z: /delete`

Let's say our drive's name we use is e,

to make the USB a shared file over the network mentioned below, run
`net use z: \\\\192.168.55.52\\e`

Let's say your server information is username@server_address:port
first create a mount folder - named 'mount'
you need to have a sudo access

Next, move to the server's terminal, and execute the rest of the commands

if there is no mount folder, we should create a mount point

`sudo mkdir /home/username/mount`

then to mount our usb drive into our server, we can execute this command, where 192.168.55.52 is the ip address of the company
`sudo mount.cifs //192.168.55.52/e /home/username/mount -o user=share,password=share`

if that returns a 'resource busy' error, first unmount it using this command -> `sudo umount -l /home/username/mount`


Now all you need to do is execute the detect.py from the yolov5 repository we have forked (named as ML_model)
change your directory to GUI-AI-project/, and change 'video_name' to the actual name of the video

`python3 ML_model/detect.py --weights ML_model/checkpoints/railway.pt --source /home/username/mount/video_name.mp4 --project /home/username/mount/`

