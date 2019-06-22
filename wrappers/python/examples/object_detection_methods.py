#!/usr/bin/python
## Ridiculou 6 Co. 2019

## This sript hanles identifying objects and avoiding them

import pyrealsense2 as rs
import numpy as np
import cv2

# Calculate the midpoint of the object for distance calculation
def get_midpoint(x,y,w,h):
    mid_x = x+ (w/2)
    mid_y = y+ (h/2)
    return (mid_x, mid_y)

# Removes object detection frame around the video stream
def isItself(w,h):
    if 843 <= w <= 848 and 473 <= h <= 480:
        return True
    return False

# After layers of altering the image, detects obstacles
def detect_objects(aligned_depth_frame, color_video):
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

    distance = 0.0
    # Looping through contours
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Ignores drawing around the video window and too small of objects
        if not isItself(w,h) and w > 100 and h > 100:

            # Get the midpoint of the object and calculate the distance
            mid_x, mid_y = get_midpoint(x,y,w,h)
            distance = round(aligned_depth_frame.get_distance(mid_x, mid_y)*3.28, 1)
            #TODO when distance is X ft away trigger the kickoff dodge maneuver
            distance_away =  str(distance) + ' ft away'
            # Size check removes noise
            size = cv2.contourArea(cnt)

            # Filters out unwanted objects
            if size > 300 and distance < 6.5 and distance != 0.0:
                #print(str(w) + "  " + str(h) + "  " + distance_away)
                cv2.putText(color_video, distance_away, (x, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                if distance < 2.5:
                    # red if too close
                    cv2.rectangle(color_video,(x,y),(x+w,y+h),(0,0,255),2)
                else:
                    # yellow identifies obstacle
                    cv2.rectangle(color_video,(x,y),(x+w,y+h),(0,255,255),2)
