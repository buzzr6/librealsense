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

## Xubuntu 16.04 64-bit LibrealSense Downloads Doc:

1. Had to “unlock the front end” to use the sudo apt-get commands to download stuff
* sudo rm /var/cache/apt/archives/lock
* sudo rm /var/lib/dpkg/lock
* sudo rm /var/lib/apt/lists/lock

2. sudo apt-get install git
3. sudo apt-get install vim
4. Installed gedit (for Grisam :)
5. Git Cloned QR Code repo
6. I now have librealsense repo, lets see how to install and build everything
7. sudo apt install python-pip
8. pip install pyrealsense2 (dont need to do it) need to build out in the librealsense/build/wrappers/python after running the generl cmake with the python flag, that builds the pyrealsense 2, then update PYTHONPATH to be where the pyrealsense is
9. sudo apt-get update && sudo apt-get upgrade
Okay that took forever lol
10. Downloading OpenCV from the opencv page
Download before downloading python stuff
11. sudo apt install cmake
12. sudo apt-get install pkg-config
13. sudo apt-get install libusb-1.0-0-dev
14. sudo apt-get install libx11-dev
15. sudo apt-get install xorg-dev libglu1-mesa-dev
16. sudo apt-get install build-essential libgtk-3-dev
17. All that I was able to run the cmake command to build the python examples
18. sudo pip install numpy
19. Complete OpenCv build in the opencv git folder before tyring to build the opencv examples in the librealsense git folder
20. pip install opencv-python or sudo apt install python-opencv


### Now, the LibrealSense2 Build
1. Following this https://github.com/buzzr6/librealsense/blob/QRCode/doc/distribution_linux.md
2. sudo apt-get install libzbar0
3. pip install pyzbar
