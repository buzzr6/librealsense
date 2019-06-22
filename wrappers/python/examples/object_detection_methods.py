#!/usr/bin/python
## Ridiculou 6 Co. 2019

## This sript hanles identifying objects and avoiding them

import pyrealsense2 as rs
import numpy as np
import cv2

video_height = 480
video_width = 848

# Set of values to determine where the object detected is on screen
center_x_low = video_width/2 - 75
center_x_high = video_width/2 + 75
y_axis = video_width/2
x_axis = video_height/2

# Maintained list of current objects in view (distance values)
object_dict = {}

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

# Acts on the closest object
def dodge(dict, color_video):
    # Find the closest object and determine if we need to act
    key_min = min(dict.keys(), key=(lambda k: dict[k]))
    if dict[key_min] > 5.5:
        return "safe"
    else:
        if (key_min < center_x_high) * ( key_min > center_x_low):
            cv2.line(color_video,(center_x_low, video_height),(center_x_low, 0),(0,255,0),2)
            cv2.line(color_video,(center_x_high, video_height),(center_x_high, 0),(0,255,0),2)
            # TODO INSERT MOTOR COMMAND HERE TO GO RIGHT OR LEFT
            return "center"
        # Obstacle is on the left
        if key_min < y_axis:
            cv2.putText(color_video, "Go Right", (10, video_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            # TODO INSERT MOTOR COMMAND HERE TO DRIVE RIGHT
            return "left"
        # Obstacle is on the right
        if key_min > y_axis:
            cv2.putText(color_video, "Go Left", (video_width -90, video_height -10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            # TODO INSERT MOTOR COMMAND HERE TO DRIVE LEFT
            return "right"
        return "unknown"

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

    # Clear list to only have currently recognized objects
    object_dict.clear()

    # Looping through contours
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Ignores drawing around the video window and too small of objects
        if not isItself(w,h) and w > 100 and h > 100:

            # Get the midpoint of the object and calculate the distance
            mid_x, mid_y = get_midpoint(x,y,w,h)
            distance = round(aligned_depth_frame.get_distance(mid_x, mid_y)*3.28, 1)
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
                object_dict[mid_x] = distance
    # If the dictionary is not empty look to dodge
    if object_dict:
        # Analyze if any objects are a threat and move accordingly
        dodge(object_dict, color_video)
