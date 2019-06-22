#!/usr/bin/python
## Ridiculou 6 Co. 2019

## This script is responsible for identifying the payload and performing the
## commands to pick up the payload

import pyrealsense2 as rs
import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar
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

# Set "payload centering" values & the axes
center_x_low = video_width/2 - 75
center_x_high = video_width/2 + 75
x_axis = video_width/2
y_axis = video_height/2

# Get Alignment information
align_to = rs.stream.color
align = rs.align(align_to)

# Start streaming
profile = pipeline.start(config)
distance_away = "pending..."

# Skip first 5 frames for Auto-Exposure
for x in range(5):
  pipeline.wait_for_frames()

# Determines which quadrant the barcode is within
def barcode_location(x, color_video):
    if (x < center_x_high) * ( x > center_x_low):
        # Draw estimated center for rover approach, adjust with testing
        cv2.line(color_video,(center_x_low, video_height),(center_x_low, 0),(0,255,0),2)
        cv2.line(color_video,(center_x_high, video_height),(center_x_high, 0),(0,255,0),2)
        # TODO This means barcode is in center range, send command
        # to keep going straight
        return "center"
    if x < x_axis:
        cv2.putText(color_video, "Go Left", (10, video_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        # TODO send motor command to adjust to the left, short burst left
        return "left"
    if x > x_axis:
        cv2.putText(color_video, "Go Right", (video_width -90, video_height -10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        # TODO send motor command to adjust right, short burst right
        return "right"
    return "unknown"

# Calculate the midpoint of the object for distance calculation
def get_midpoint(x,y,w,h):
    mid_x = x+ (w/2)
    mid_y = y+ (h/2)
    return (mid_x, mid_y)

# Returns barcode information relating to embedded info & position points
def get_barcode_data(barcode):
    # The barcode data is a bytes object so if we want to draw it
    # on our output image we need to convert it to a string first
    barcode_data = barcode.data.decode("utf-8")
    barcode_type = barcode.type
    barcode_text = ("{} ({})".format(barcode_data, barcode_type))[:2]

    # Retrieve the dimensions of the box around the barcode to draw
    (x, y, w, h) = barcode.rect
    barcode_center_x, barcode_center_y = get_midpoint(x,y,w,h)

    return barcode_text, x, y, barcode_center_x, barcode_center_y

# Draws the rectangle around the identified barcode
def draw_barcode_rectangle(points, color_video):
    # If the points do not form a quad, find convex hull
    if len(points) > 4 :
      hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
      hull = list(map(tuple, np.squeeze(hull)))
    else :
      hull = points;

    # Number of points in the convex hull
    n = len(hull)

    # Draw the convext hull
    for j in range(0,n):
      cv2.line(color_video, hull[j], hull[ (j+1) % n], (0,255,0), 3)

# Analyzes the list of barcodes and draws its location over the video display
def analyze_barcode_objects(decodedObjects, aligned_depth_frame, color_video):
    for barcode in decodedObjects:
        points = barcode.polygon

        draw_barcode_rectangle(points, color_video)
        barcode_text, x, y, barcode_center_x, barcode_center_y = get_barcode_data(barcode)

        # Get the distance away from the payload
        distance = round(aligned_depth_frame.get_distance(barcode_center_x, barcode_center_y)*3.28, 1)

        # Ignore cases where the distance calculates 0.0ft,
        if distance != 0.0:
            # TODO this is where we would have a while loop checking for
            # the hall a fax (w.e) sensor detecting we picked it up
            if distance < 0.8: # when we are this close and we get a trigger that the forklift has it, then we'd switch back
                subprocess.Popen(["python", str(os.getcwd())+"/object_barcode_detection.py"])
                sys.exit()
            distance_away = str(distance) + ' ft away'

            # Draw the distance, barcode info and cirle around the barcode
            cv2.putText(color_video, distance_away, (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.putText(color_video, barcode_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.circle(color_video, (barcode_center_x, barcode_center_y), 6, (255, 0, 0), -1)
            #cv2.putText(color_video, distance_away, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 3)

        # Determine barcode location and adjust accordingly
        location = barcode_location(barcode_center_x, color_video)
        print("adjusting") #make sure we keep checking the location until pickup

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

        # Pass in each frame from the video into the library for analyzing
        decodedObjects = pyzbar.decode(color_video)
        analyze_barcode_objects(decodedObjects, aligned_depth_frame, color_video)

        cv2.imshow("Barcode Detection", color_video)
        k = cv2.waitKey(1) & 0xFF
        # press 'q' to exit script
        if k == ord('q'):
            break
        cv2.waitKey(1)

finally:
    # Stop streaming
    pipeline.stop()
