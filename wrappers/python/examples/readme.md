
# Sample Code for Intel® RealSense™ Python Wrapper

These Examples demonstrate how to use the python wrapper of the SDK.

## R6 Scripts:

I've created a couple scripts here.
1. `barcode_rec_methods.py` contains all the methods needed for another class to leverage barcode detection
2. `barcode_rec_runnable.py` is the exectuable script that runs barcode detection and has the ability to switch over to object detection once the payload is "picked up"
3. `object_detection_methods.py` contains all the methods needed for another class to leverage object detection
4. `object_detection_runnable.py` is the executable script that runs solely object detection
5. `object_barcode_detection.py` this is the **MAIN** script that leverages both barcode and object detection
* It starts out by examining the frame for a barcode image, if it does not find one it resumes obstacle avoidance and object detection
* Once the vehicle detects a barcode, it switches over to the barcode script where it handles picking up the payload, once it deemed the payload secured it will switch back to the MAIN script
* This implementation eliminates the need for an object detection script to "ignore" a barcode and not mistake it as an obstacle
* We wouldnt be able to detect a barcode if there was a obstacle in front of it so its a safe case

## List of Examples:

1. [Tutorial 1](./python-tutorial-1-depth.py) - Demonstrates how to start streaming depth frames from the camera and display the image in the console as an ASCII art.
2. [NumPy and OpenCV](./opencv_viewer_example.py) - Example of rendering depth and color images using the help of OpenCV and Numpy
3. [Stream Alignment](./align-depth2color.py) - Demonstrate a way of performing background removal by aligning depth images to color images and performing simple calculation to strip the background.
4. [RS400 Advanced Mode](./python-rs400-advanced-mode-example.py) - Example of the advanced mode interface for controlling different options of the D400 cameras
5. [Realsense Backend](./pybackend_example_1_general.py) - Example of controlling devices using the backend interface
6. [Read bag file](./read_bag_example.py) - Example on how to read bag file and use colorizer to show recorded depth stream in jet colormap.
7. [Box Dimensioner Multicam](./box_dimensioner_multicam/box_dimensioner_multicam_demo.py) - Simple demonstration for calculating the length, width and height of an object using multiple cameras.

## Pointcloud Visualization

1. [OpenCV software renderer](https://github.com/IntelRealSense/librealsense/blob/development/wrappers/python/examples/opencv_pointcloud_viewer.py)
2. [PyGlet pointcloud renderer](https://github.com/IntelRealSense/librealsense/blob/development/wrappers/python/examples/pyglet_pointcloud_viewer.py) - requires `pip install pyglet`

## Interactive Examples:

1. [Distance to Object](https://github.com/IntelRealSense/librealsense/blob/jupyter/notebooks/distance_to_object.ipynb) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/IntelRealSense/librealsense/jupyter?filepath=notebooks/distance_to_object.ipynb)
2. [Depth Filters](https://github.com/IntelRealSense/librealsense/blob/jupyter/notebooks/depth_filters.ipynb) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/IntelRealSense/librealsense/jupyter?filepath=notebooks/depth_filters.ipynb)
