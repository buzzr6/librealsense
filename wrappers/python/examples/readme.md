# R6 Scripts:

The current scripts under development.
1. `barcode_rec_runnable.py` is the exectuable script that runs barcode detection and has the ability to switch over to object detection once the payload is "picked up"
2. `object_detection_methods.py` contains all the methods needed for another class to leverage object detection
3. `object_detection_runnable.py` is the executable script that runs solely object detection (not as up to date as methods class)
4. `object_barcode_detection.py` this is the **MAIN** script that leverages both barcode and object detection
    * It starts out by examining the frame for a barcode image, if it does not find one it resumes obstacle avoidance and object detection
    * Once the vehicle detects a barcode, it switches over to the barcode script where it handles picking up the payload, once it deemed the payload secured it will switch back to the **MAIN** script
    * This implementation eliminates the need for an object detection script to "ignore" a barcode and not mistake it as an obstacle
        * We wouldnt be able to detect a barcode if there was a obstacle in front of it so its a safe case
    * **To Kill the script (stop it while running) you need to kill the process through the task manager, it will not stop if you hit Ctrl+C in the terminal or close the OpenCV window**

**Currently I updated the scripts to use the local paths that are on the UP board, if youre running this on your personal computer make sure to update those paths locally and NOT commit them**

## Crontab Instructions

On bootup of the UP board, the crontab executes specific scripts for the mission.  Currently I have the object detection script kicking off and clearing the payload.txt file.  What **needs** to be added is the connection to the ground station (if necessary) and execute any other scripts relating to IED detection. Or the RTSP server to stream video.

To view the cronjob and edit it
1. cd
2. crontab -e
    *  this brings the user into the cron editor
3. Make appropriate edits and view documentation link if necessary
4. To save and exit do "Crtl+X" then "y" then hit enter

## Xubuntu 16.04 64-bit LibrealSense Downloads Doc (adjusted for odroid install):

Had to “unlock the front end” to use the sudo apt-get commands to download stuff (on kernel 4.9)
* sudo rm /var/cache/apt/archives/lock
* sudo rm /var/lib/dpkg/lock
* sudo rm /var/lib/apt/lists/lock

sudo apt-get install git vim

**Auto login:**<br>
sudo vim /usr/share/lightdm/lightdm.conf.d/60-lightdm-gtk-greeter.conf<br>
[SeatDefaults]<br>
greeter-session=lightdm-gtk-greeter<br>
autologin-user=odroid

Remove keyring Accessories > Passwords and Keys > right Click on Login

**Mouse issue:**</br>
sudo vim /etc/modules
add these lines
-r usbhid <br>
usbhid mousepoll=1

**Git Cloned QR Code repo:**<br>
I now have librealsense repo, lets see how to install and build everything

**Download before downloading python stuff:**<br>
sudo apt install cmake<br>
sudo apt-get install libx11-dev<br>
sudo apt-get install libglfw3-dev<br>
sudo apt-get install libssl-dev libusb-1.0-0-dev pkg-config libgtk-3-dev 

**Odroid specific commands:**<br>
./scripts/patch-realsense-ubuntu-odroid.sh./scripts/setup_udev_rules.sh<br>
Odroid: ./scripts/patch-realsense-ubuntu-odroid-xu4-4.14.sh<br>
sudo udevadm control --reload-rules && udevadm trigger<br>
sudo modprobe uvcvideo

Following this https://github.com/buzzr6/librealsense/blob/QRCode/doc/installation.md<br>
Disregard toolchain updates

**Downloading OpenCV from the opencv page**, https://github.com/buzzr6/librealsense/tree/master/wrappers/opencv , https://docs.opencv.org/trunk/d7/d9f/tutorial_linux_install.html

Complete OpenCv build in the opencv git folder before tyring to build the opencv examples in the librealsense git folder
pip install opencv-python or sudo apt install python-opencv

**Python Stuff:**<br>
https://github.com/buzzr6/librealsense/tree/master/wrappers/python<br>
sudo apt install python-pip<br>
sudo apt-get install python python-dev

Need to build out in the librealsense/build/wrappers/python after running the generl cmake with the python flag, that builds the pyrealsense 2<br>
Update .bashrc with this line after build **export PYTHONPATH=$PYTHONPATH:/usr/local/lib**

sudo apt-get update && sudo apt-get upgrade

Okay that took forever lol<br>
All that I was able to run the cmake command to build the python examples

sudo pip install numpy

### Now, the LibrealSense2 Build
1. Following this https://github.com/buzzr6/librealsense/blob/QRCode/doc/installation.md
2. sudo apt-get install libzbar0
3. pip install pyzbar
