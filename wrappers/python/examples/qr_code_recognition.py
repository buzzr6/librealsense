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
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 60)

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

        # Create alignment primitive with color as its target stream:
        align = rs.align(rs.stream.color)
        aligned_frames = align.process(frames)

        # Update color and depth frames:
        aligned_depth_frame = aligned_frames.get_depth_frame()
        depth = np.asanyarray(aligned_depth_frame.get_data())

        # Get data scale from the device and convert to meters
        #depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()
        #depth = depth * depth_scale
        #dist,_,_,_ = cv2.mean(depth)
        #distance = str(round(dist, 3))
        #distance_away = distance + ' meters away'

        decodedObjects = pyzbar.decode(color_video)
        for barcode in decodedObjects:
            points = barcode.polygon

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
            xy_depth = round(depth_frame.get_distance(x, y), 4)
            print('DEPTH: ' + str(xy_depth) + "  |  X: " + str(round(x)) +  " Y: " + str(round(y)))
            # TODO based on the pixel coords we can determine if we need to go left or right
            # also can make sure QR is centered by knowing the pixels it should be in the range of to be centered
            if w != 0:
                distance = ((580 * 6)/w) + 1
                # We know we can detect a code further than this distance so any
                # number higher is due to error
                if distance > 50 :
                    distance_away = "-- inches away"
                else:
                    distance_away = str(distance) + ' inches away'
            # TODO use the x, y pixel coords to get distance away field calculation

            barcode_text = ("{} ({})".format(barcode_data, barcode_type))[:20] + '...'
            cv2.putText(color_video, distance_away, (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.putText(color_video, barcode_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            #cv2.putText(color_video, distance_away, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 3)

        cv2.imshow("QR Code Detection Demo", color_video)
        #s.sendall(pickle.dumps(color_frame))
        # TODO use distance var in payload situation
        cv2.waitKey(1)

finally:

    # Stop streaming
    pipeline.stop()
