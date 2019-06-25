#!/usr/bin/python
## Ridiculou 6 Co. 2019

## This script dynamically switches between detcting obstacles and identifying
## payload objects to pickup

from object_detection_methods import detect_objects
import pyrealsense2 as rs
import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar
from pyzbar.pyzbar import ZBarSymbol
import socket
import sys
import subprocess
import os

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
video_height = 480
video_width = 848
config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 90)
config.enable_stream(rs.stream.color, video_width, video_height, rs.format.bgr8, 60)

# Get Alignment information
align_to = rs.stream.color
align = rs.align(align_to)

# Start streaming
profile = pipeline.start(config)

# Skip first 5 frames for Auto-Exposure
for x in range(5):
  pipeline.wait_for_frames()

# Returns the embedded information in the barcode
def get_barcode_text(barcode):
    # The barcode data is a bytes object so if we want to draw it
    # on our output image we need to convert it to a string first
    barcode_data = barcode.data.decode("utf-8")
    barcode_type = barcode.type
    barcode_text = ("{} ({})".format(barcode_data, barcode_type))[:2]
    return barcode_text

try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame().as_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        if not color_frame and aligned_depth_frame:
            continue

        # Get the RGB video
        color_video = np.asanyarray(color_frame.get_data())
        # TODO send video frame (color_video) to the other script, test perfomance decrease
        #      figure out the format of color_video, could work as is

        # Barcode analyzation
        decodedObjects = pyzbar.decode(color_video, symbols=[ZBarSymbol.CODE128])
        if len(decodedObjects) > 0:
            for barcode in decodedObjects:
                # Read the barcode and check which payload it is ex) 'P1'
                barcode_text = get_barcode_text(barcode)
                exists = False

                # Open payload log to see if we have seen this ID before
                with open("/home/buzzr6/git/librealsense/wrappers/python/examples/payload.txt","r+") as file:

                    # Search through the file line by line to look for the ID
                    for line in file:
                        if line[:2] == barcode_text:
                            exists = True

                    if not exists:
                        # If this is the first time we see the object write the payload ID in
                        file.write(barcode_text + "\n")
                        file.close()

                        #TODO INSERT MOTOR COMMAND TO STOP ROVER HERE
                        #TODO INSERT LOWER FORKLIFT COMMAND HERE, write out to file which one we
                        #     picked so we can use the other one, after both are used, clear file for next two payloads
                        subprocess.Popen(["python", "/home/buzzr6/git/librealsense/wrappers/python/examples/barcode_rec_runnable.py"])
                        sys.exit()

        # Object analyzation/ handles obstacle avoidance
        detect_objects(aligned_depth_frame, color_video)

        cv2.imshow("Object Detection", color_video)
        k = cv2.waitKey(1) & 0xFF
        # press 'q' to exit script
        if k == ord('q'):
            break
        cv2.waitKey(1)

finally:
    # Stop streaming
    pipeline.stop()
