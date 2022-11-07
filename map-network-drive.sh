#! /bin/bash

# first removing an existing network drive -> chosen drive 
# our drive uses z to map the removable disk
echo -e "Please enter the name of the drive"
read drive
if exist z:\ (
    net use z: /delete
)
net use z: \\\\192.168.55.52\\$drive

echo -e "Enter your username"
read username
echo -e "Enter your server address, ex. 125.138.99.152"
read server
echo -e "Enter your port number"
read port

echo "we use the cifs-utils utility, if you don't have it, install it using <sudo apt install cifs-utils>"

# then create a mount folder - named 'mount'
# you need to have a sudo access, and change the localhost ip according to your setting

ssh -L 224:127.0.0.1:224 $username@$server -p $port sudo mount.cifs //192.168.55.52/$drive /home/$username/mount/

# if that returns a 'resource busy' error, first unmount it using this command -> sudo umount -l mount/

# now you can execute this command to run the yolov5 detection
# change your directory to GUI-AI-project/

echo -e "please enter the name of the video"
read video_name

# please change the details according to your server
ssh -L 224:127.0.0.1:224 $username@$server -p $port python3 ML_model/detect.py --weights ML_model/checkpoints/railway.pt --source mount/$video_name.mp4 --project mount/

