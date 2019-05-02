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
pipeline.start(config)

font = cv2.FONT_HERSHEY_PLAIN

try:
    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        width = depth_frame.get_width();
        height = depth_frame.get_height();
        dist = depth_frame.get_distance(0, 0)
        #print (dist);

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
            print("Data", barcode.data)

    		# The barcode data is a bytes object so if we want to draw it
    		# on our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type

    		# Draw the barcode data and barcode type on the image
            (x, y, w, h) = barcode.rect
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(color_image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imshow("QR Detector Frame", color_image)

        # Convert images to numpy arrays
        #depth_image = np.asanyarray(depth_frame.get_data())
        #color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Stack both images horizontally
        # images = np.hstack((color_image, depth_colormap))

        # Show images
        #cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        #cv2.imshow('RealSense', color_image)
        cv2.waitKey(1)

finally:

    # Stop streaming
    pipeline.stop()
