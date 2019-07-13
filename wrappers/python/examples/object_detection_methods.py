#!/usr/bin/python
## Ridiculou 6 Co. 2019

## This sript hanles identifying objects and avoiding them

import numpy as np
import cv2


# Removes object detection frame around the video stream
def isItself(w,h):
    if 630 <= w <= 643 and 473 <= h <= 482:
        return True
    return False

# After layers of altering the image, detects obstacles
def detect_objects(color_video):
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
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Ignores drawing around the video window and too small of objects
        if not isItself(w,h) and w > 100 and h > 100:

            # Size check removes noise
            size = cv2.contourArea(cnt)

            # Filters out unwanted objects
            if size > 300 :
	        cv2.rectangle(color_video,(x,y),(x+w,y+h),(0,0,255),2)
