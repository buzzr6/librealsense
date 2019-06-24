
# Sample Code for Intel® RealSense™ Python Wrapper

These Examples demonstrate how to use the python wrapper of the SDK.

## R6 Scripts:

I've created a couple scripts here.
1. `barcode_rec_runnable.py` is the exectuable script that runs barcode detection and has the ability to switch over to object detection once the payload is "picked up"
2. `object_detection_methods.py` contains all the methods needed for another class to leverage object detection
3. `object_detection_runnable.py` is the executable script that runs solely object detection (not as up to date as method class)
4. `object_barcode_detection.py` this is the **MAIN** script that leverages both barcode and object detection
* It starts out by examining the frame for a barcode image, if it does not find one it resumes obstacle avoidance and object detection
* **To Kill the script (stop it while running) you need to kill the process through the task manager, it will not stop if you hit Ctrl+C in the terminal or close the OpenCV window**
* Once the vehicle detects a barcode, it switches over to the barcode script where it handles picking up the payload, once it deemed the payload secured it will switch back to the MAIN script
* This implementation eliminates the need for an object detection script to "ignore" a barcode and not mistake it as an obstacle
* We wouldnt be able to detect a barcode if there was a obstacle in front of it so its a safe case

## Crontab Instructions

On bootup of the UP board, the crontab kicks off which executes specific scripts for the mission.  Currently I have the object detection script kicking off and clearing the payload.txt file.  What **needs** to be added is the connection to the ground station (if necessary) and kick off any other scripts relating to IED detection. Or the RTSP server to stream video.

To view the cronjob and edit it
1. cd
2. crontab -e
* this brings the user into the cron editor
3. Make appropriate edits and view documentation link if necessary
4. To save and exit do "Crtl+X" then "y" then hit enter


**Currently I updated the scripts to use the local paths that are on the UP board, if youre running this on your personal computer make sure to update those paths locally and NOT commit them**
