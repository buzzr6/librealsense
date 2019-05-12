#!/usr/bin/python
## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar
import socket

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
video_height = 540
video_width = 960
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, video_width, video_height, rs.format.bgr8, 60)

center_x_low = video_width/2 - 75
center_x_high = video_width/2 + 75
x_axis = video_width/2
y_axis = video_height/2

def barcode_location(x, y):
    if (x < center_x_high) * ( x > center_x_low):
        return "middle"
    if x < video_width/2:
        if y < video_height/2:
            return "top left"
    if x < video_width/2:
        if y > video_height/2:
            return "bottom left"
    if x > video_width/2:
        if y < video_height/2:
            return "top right"
    if x > video_width/2:
        if y > video_height/2:
            return "bottom right"
    return "unknown or center"

#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect(('192.168.8.1', 8554))

distance_away = "pending..."

# Start streaming
profile = pipeline.start(config)

# Skip first 5 frames for Auto-Exposure
for x in range(5):
  pipeline.wait_for_frames()

try:

    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        color_video = np.asanyarray(color_frame.get_data())

        decodedObjects = pyzbar.decode(color_video)
        for barcode in decodedObjects:
            points = barcode.polygon

            # Draw a center vertical and horizontal lines
            #cv2.line(color_video,(x_axis, video_height),(x_axis, 0),(255,0,0),1)
            #cv2.line(color_video,(0, y_axis),(video_width, y_axis),(255,0,0),1)

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

    		# The barcode data is a bytes object so if we want to draw it
    		# on our output image we need to convert it to a string first
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

    		# Draw the barcode data and the distance on the video
            (x, y, w, h) = barcode.rect
            rect_center_x = (x + (x+w))/2
            rect_center_y = (y + (y+h))/2
            #xy_depth = round(depth_frame.get_distance(x, y), 3)
            print('X: ' + str(round(rect_center_x)) +  "   Y: " + str(round(rect_center_y)))

            if w != 0:
                distance = round(((489 * 5.25)/w) -3, 1)  # the -3 compensates for the angle
                # We know we can detect a code further than this distance so any
                # number higher is due to error
                if distance > 90 :
                    distance_away = "-- inches away"
                else:
                    distance_away = str(distance) + ' inches away'

            barcode_text = ("{} ({})".format(barcode_data, barcode_type))[:2]
            cv2.putText(color_video, distance_away, (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.putText(color_video, barcode_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.circle(color_video, (rect_center_x, rect_center_y), 7, (255, 0, 0), -1)
            #cv2.putText(color_video, distance_away, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 3)

            if barcode_location(rect_center_x ,rect_center_y) == "middle":
                # Draw estimated center for rover approach
                cv2.line(color_video,(center_x_low, video_height),(center_x_low, 0),(0,255,0),2)
                cv2.line(color_video,(center_x_high, video_height),(center_x_high, 0),(0,255,0),2)
                # TODO This means barcode is inc enter range, send command
                # to keep going straight

        cv2.imshow("QR Code Detection Demo", color_video)
        #s.sendall(pickle.dumps(color_video))
        cv2.waitKey(1)


finally:

    # Stop streaming
    pipeline.stop()
