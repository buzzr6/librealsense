#!/usr/bin/python
## Ridiculou 6 Co. 2019

import pyrealsense2 as rs
import numpy as np
import cv2

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
video_height = 480
video_width = 848
config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 90)
config.enable_stream(rs.stream.color, video_width, video_height, rs.format.bgr8, 60)

# Calculate the midpoint of the object for distance calculation
def get_midpoint(x,y,w,h):
    mid_x = x+ (w/2)
    mid_y = y+ (h/2)
    return (mid_x, mid_y)

# Start streaming
profile = pipeline.start(config)

# Get Alignment information
align_to = rs.stream.color
align = rs.align(align_to)

# Skip first 5 frames for Auto-Exposure
for x in range(5):
  pipeline.wait_for_frames()

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

        color_video = np.asanyarray(color_frame.get_data())
        #depth_video = np.asanyarray(aligned_depth_frame.get_data())

        # Gaussian blur
        blurred = cv2.GaussianBlur(color_video, (5, 5), 0)
        # Convert to graysscale
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        # Autocalculate the thresholding level
        threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        # Threshold
        retval, bin = cv2.threshold(threshold, 100, 255, cv2.THRESH_BINARY)
        # Find contours
        contours, _ = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.imshow('Threshold View', threshold)

        # Looping through contours
        # TODO tweak these settings for optimal object detection
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 60 and h > 60:

                # Get the midpoint of the object and calculate the distance
                mid_x, mid_y = get_midpoint(x,y,w,h)
                distance = round(aligned_depth_frame.get_distance(mid_x, mid_y)*3.28, 1)
                distance_away =  str(distance) + ' ft away'
                
                # ADDED SIZE CRITERION TO REMOVE NOISES
                size = cv2.contourArea(cnt)
                if size > 500:
                    # CHANGED DRAWING CONTOURS WITH RECTANGLE
                    cv2.rectangle(color_video,(x,y),(x+w,y+h),(0,215,255),2)
                    cv2.putText(color_video, distance_away, (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        #depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_video, alpha=0.03), cv2.COLORMAP_JET)
        #cv2.imshow('Depth Detection', depth_colormap)
        cv2.imshow('Object Detection', color_video)
        cv2.waitKey(1)

finally:
        pipeline.stop()
