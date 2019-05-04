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

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 60)

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

        color_image = np.asanyarray(color_frame.get_data())
        decodedObjects = pyzbar.decode(color_image)
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
              cv2.line(color_image, hull[j], hull[ (j+1) % n], (0,255,0), 3)
            # print out data of link to terminal if necessary
            # print("Data", barcode.data)

    		# The barcode data is a bytes object so if we want to draw it
    		# on our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type

    		# Draw the barcode data and barcode type on the image
            (x, y, w, h) = barcode.rect
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(color_image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Create alignment primitive with color as its target stream:
        align = rs.align(rs.stream.color)
        frameset = align.process(frames)

        cv2.imshow("QR Detector Frame", color_image)

        # Create alignment primitive with color as its target stream:
        align = rs.align(rs.stream.color)
        frameset = align.process(frames)

        # Update color and depth frames:
        aligned_depth_frame = frameset.get_depth_frame()
        depth = np.asanyarray(aligned_depth_frame.get_data())

        # Get data scale from the device and convert to meters
        depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()
        depth = depth * depth_scale
        dist,_,_,_ = cv2.mean(depth)
        print("Detected an object ", dist, " away")
        # TODO print this on the image in the corner showing the distance away

        cv2.waitKey(1)

finally:

    # Stop streaming
    pipeline.stop()
