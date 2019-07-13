#!/usr/bin/python
## Ridiculou 6 Co. 2019

## This script dynamically switches between detcting obstacles and identifying
## payload objects to pickup

from object_detection_methods import detect_objects
import numpy as np
import cv2
import pyzbar.pyzbar as pyzbar
from pyzbar.pyzbar import ZBarSymbol

video_width=640
video_height=480

# Set "payload centering" values & the axes
center_x_low = video_width/2 - 75
center_x_high = video_width/2 + 75
y_axis = video_width/2
x_axis = video_height/2

# Determines which quadrant the barcode is within
def barcode_location(x, color_video):
    if (x < center_x_high) * ( x > center_x_low):
        # Draw estimated center for rover approach, ADJUST TO CENTER THROUGH TESTING WITH FORKLIFT
        cv2.line(color_video,(center_x_low, video_height),(center_x_low, 0),(0,255,0),2)
        cv2.line(color_video,(center_x_high, video_height),(center_x_high, 0),(0,255,0),2)
        return "center"
    if x < y_axis:
        cv2.putText(color_video, "Go Left", (10, video_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return "left"
    if x > y_axis:
        cv2.putText(color_video, "Go Right", (video_width -90, video_height -10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
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
def analyze_barcode_objects(decodedObjects, color_video):
    for barcode in decodedObjects:
        points = barcode.polygon

        draw_barcode_rectangle(points, color_video)
        barcode_text, x, y, barcode_center_x, barcode_center_y = get_barcode_data(barcode)

        # Draw the distance, barcode info and cirle around the barcode, KEEP FOR TESTING
        cv2.putText(color_video, barcode_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.circle(color_video, (barcode_center_x, barcode_center_y), 6, (255, 0, 0), -1)

        # Determine barcode location and adjust accordingly until the pickup trigger above is executed
        location = barcode_location(barcode_center_x, color_video)

cap = cv2.VideoCapture(0)

try:
    while True:
        # Get Stream
        ret, color_video = cap.read()

        # Barcode analyzation
        decodedObjects = pyzbar.decode(color_video, symbols=[ZBarSymbol.CODE128])
        analyze_barcode_objects(decodedObjects, color_video)
        
        # Object analyzation/ handles obstacle avoidance
        detect_objects(color_video)

        cv2.imshow("Object Detection", color_video)
        k = cv2.waitKey(1) & 0xFF
        # press 'q' to exit script
        if k == ord('q'):
            break
        cv2.waitKey(1)

finally:
    # Stop streaming
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
