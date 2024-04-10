#Modules for Robot Movement
from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType, alarmAlarmJsonFile
from time import sleep
import threading
import numpy as np
import re

#Modules for ObjectDetection
import cv2 
import argparse
from ultralytics import YOLO
import supervision as sv
import numpy as np

from functions import *

def get_object_coordinates(cap,model,box_annotator):
    #Setting number of iterations to ensure that object remains stationary
    consecutive_frames = 0
    prev_x_center = 0
    prev_y_center = 0
    
    while True:
        ret, frame = cap.read()
    
        #enable the bounding box in the frame
        result = model(frame)[0]
        
        #Convert YOLOV8 detections to Supervision Bounding Box
        detections = sv.Detections.from_yolov8(result)
        
        #Label the bounding box with the class attached (from the weights), with the confidence
        labels = [
            f"{model.model.names[class_id]} {confidence:0.2f}"
            for _, confidence,class_id, _
            in detections
        ]
        
        frame = box_annotator.annotate(
            scene=frame, 
            detections= detections, 
            labels=labels
            )
       
        # Printing the coordinates of the Detection
        for i in range(len(detections.xyxy)):
            # Extract bounding box coordinates
            x1, y1, x2, y2 = detections.xyxy[i]
            
            # Calculate center coordinates
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            
            #Limit the scope of the detected object to certain ranges
            if not (200.0 < x_center < 700.0) or not (200.0 < y_center < 700.0):
                pass
            
            # Extract confidence and class_id
            confidence = detections.confidence[i]
            class_id = detections.class_id[i]

            # Print or store the coordinates
            print(f"Object detected at X: {x_center}, Y: {y_center}, Confidence: {confidence}, Class ID: {class_id}")
            
            # Check if values have not varied for 20 consecutive frames and confidence is above 0.6
            #setting the threshold is set to be 50
            if ( (abs(x_center - prev_x_center) <= 50) and (abs(y_center - prev_y_center) <= 50) and (confidence > 0.8)):
                consecutive_frames += 1
                if consecutive_frames >= 5:
                    # Return the values or do further processing
                    object_coordinates['x_point'] = x_center
                    object_coordinates['y_point'] = y_center
                    object_coordinates['final_confi'] = confidence
                    #return x_center, y_center, confidence
            else:
                consecutive_frames = 0  # Reset the count if values vary

            # Update previous values
            prev_x_center = x_center
            prev_y_center = y_center
        
        cv2.imshow('yolov8',frame)

        #press escape to exit the program
        if (cv2.waitKey(30)== 27):
            break
    
if __name__ == "__main__":
    dashboard, move, feed = connect_robot()
    
    #Set the parameters
    dashboard.EnableRobot()
    dashboard.EnableRobot(load, centerX, centerY, centerZ) 
    
    #Set the acceleration
    dashboard.AccL(acceleration)  
        
    #Set the speed
    dashboard.SpeedL(speed)
    
    #to run a script
    # name="test.lua"
    # dashboard.RunScript(name)  
    
    #Thread for Robot Movement
    feed_thread = threading.Thread(target=GetFeed, args=(feed,))
    feed_thread.setDaemon(True)
    feed_thread.start()
    #Thread 2 for RobotError
    feed_thread1 = threading.Thread(target=ClearRobotError, args=(dashboard,))
    feed_thread1.setDaemon(True)
    feed_thread1.start()
    
    
    #initialise camera
    cap, model, box_annotator = init_cam()
    
    # Initialize a dictionary to store the coordinates and confidence
    object_coordinates = {'x_point': "a" , 'y_point': "b", 'final_confi': "c"}
    
    #Thread for Object Detection
    object_detection_thread = threading.Thread(target=get_object_coordinates, args=(cap, model, box_annotator))
    object_detection_thread.setDaemon(True)
    object_detection_thread.start()
    
    #Move robot to Origin position
    point_origin = [0,-300,100,0] 
    RunPoint(move,point_origin)
    
    while True:
        
        x_point = object_coordinates['x_point']
        y_point = object_coordinates['y_point']
        final_confi = object_coordinates['final_confi']
        
        if (x_point == 'a') and (y_point == 'b') and (final_confi == 'c'):
            sleep(5)
            continue
        
        #Move Robot to Origin Position
        RunPoint(move,point_origin)
        
        print('Object Stationary: Initiating Movement')
        print(x_point,y_point,final_confi)
        
        #matching the coordinates of the y_point
        #y coordinate in webcam is the negative direction for robot
        final_x = round((x_point/1280) * 185 + 215)
        final_y = round((y_point/720) * 250 - 150)
        
        #Middle of screen (700,200) for webcam
        #Moving to Object
        RunPoint(move,[final_x,final_y,50,0])
        sleep(4)
        RunPoint(move,[final_x,final_y,-40,0])
        sleep(15)
        RunPoint(move,[final_x,final_y,50,0])
        sleep(1)
        #Move to Final Position
        RunPoint(move,[0,-300,100,0])
        sleep(5)
        
        object_coordinates['x_point'] = 'a'
        object_coordinates['y_point'] = 'b'
        object_coordinates['final_confi'] = 'c'
        
        
    dashboard.DisableRobot()