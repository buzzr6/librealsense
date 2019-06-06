#!/usr/bin/python
## Ridiculou 6 Co. 2019

from barcode_rec_methods import analyze_barcode_objects
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

distance_away = "pending..."

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

        # Barcode analyzation
        decodedObjects = pyzbar.decode(color_video, symbols=[ZBarSymbol.CODE128])
        if len(decodedObjects) > 0:
            #TODO send command to stop rover, then execute script
            subprocess.Popen(["python", str(os.getcwd())+"/barcode_rec_runnable.py"])
            sys.exit()
        #analyze_barcode_objects(decodedObjects, aligned_depth_frame, color_video)

        # Object analyzation
        #if len(decodedObjects) == 0:
        detect_objects(aligned_depth_frame, color_video)

        cv2.imshow("Barcode Detection", color_video)
        k = cv2.waitKey(1) & 0xFF
        # press 'q' to exit script
        if k == ord('q'):
            break
        cv2.waitKey(1)

finally:
    # Stop streaming
    pipeline.stop()
