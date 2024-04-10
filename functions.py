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

# current coordinates
current_actual = None
algorithm_queue = None
enableStatus_robot = None
robotErrorState = False
globalLockValue = threading.Lock()

#Setting the parameters
load=0.2 #In terms of Kg
centerX=0.1
centerY=0.1
centerZ=0.1
acceleration = 75 #Range 1-100
speed = 75 #Range 1-100
      
def connect_robot():
    try:
        #Connection via TCP/IP LAN 2 Port
        ip = "192.168.2.6"
        #ip = "192.168.2.101"
        dashboard_p = 29999 #Receiving simple commands
        move_p = 30003 #feeds back the robot information. 
        feed_p = 30004 #Feeds back robot information every 8ms
        
        #Establishing Connection
        print("Establishing Connection")
        dashboard = DobotApiDashboard(ip, dashboard_p)
        move = DobotApiMove(ip, move_p)
        feed = DobotApi(ip, feed_p)
        print("Successful Connection!")
        return dashboard, move, feed
    except Exception as e:
        print("Failed Connection")
        raise e

#movement function
def RunPoint(move: DobotApiMove, point_list: list):
    move.MovL(point_list[0], point_list[1], point_list[2], point_list[3])

def GetFeed(feed: DobotApi):
    global current_actual
    global algorithm_queue
    global enableStatus_robot
    global robotErrorState
    hasRead = 0
    while True:
        data = bytes()
        while hasRead < 1440:
            temp = feed.socket_dobot.recv(1440 - hasRead)
            if len(temp) > 0:
                hasRead += len(temp)
                data += temp
        hasRead = 0
        feedInfo = np.frombuffer(data, dtype=MyType)
        if hex((feedInfo['test_value'][0])) == '0x123456789abcdef':
            globalLockValue.acquire()
            # Refresh Properties
            current_actual = feedInfo["tool_vector_actual"][0]
            algorithm_queue = feedInfo['isRunQueuedCmd'][0]
            enableStatus_robot=feedInfo['EnableStatus'][0]
            robotErrorState= feedInfo['ErrorStatus'][0]
            globalLockValue.release()
        sleep(0.001)
        
def WaitArrive(point_list):
    while True:
        is_arrive = True
        globalLockValue.acquire()
        if current_actual is not None:
            for index in range(4):
                if (abs(current_actual[index] - point_list[index]) > 1):
                    is_arrive = False
            if is_arrive :
                globalLockValue.release()
                return
        globalLockValue.release()  
        sleep(0.001)

def ClearRobotError(dashboard: DobotApiDashboard):
    global robotErrorState
    dataController,dataServo =alarmAlarmJsonFile()    # Read controller and servo alarm codes
    while True:
      globalLockValue.acquire()
      if robotErrorState:
                numbers = re.findall(r'-?\d+', dashboard.GetErrorID())
                numbers= [int(num) for num in numbers]
                if (numbers[0] == 0):
                  if (len(numbers)>1):
                    for i in numbers[1:]:
                      alarmState=False
                      if i==-2:
                          print("Machine alarm Machine collision ",i)
                          alarmState=True
                      if alarmState:
                          continue                
                      for item in dataController:
                        if  i==item["id"]:
                            print("Machine alarm Controller errorid",i,item["zh_CN"]["description"])
                            alarmState=True
                            break 
                      if alarmState:
                          continue
                      for item in dataServo:
                        if  i==item["id"]:
                            print("Machine alarm Servo errorid",i,item["zh_CN"]["description"])
                            break  
                       
                    choose = input("Entering 1 will clear the error and the machine will continue to run: ")     
                    if  int(choose)==1:
                        dashboard.ClearError()
                        sleep(0.01)
                        dashboard.Continue()

      else:  
         if int(enableStatus_robot[0])==1 and int(algorithm_queue[0])==0:
            dashboard.Continue()
      globalLockValue.release()
      sleep(5)
      
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live")
    parser.add_argument(
        "--webcam-resolution",
        default=[1280,720],
        nargs=2,
        type=int
    )
    args = parser.parse_args()
    return args

def init_cam():
    
    #Using the webcam's default resolution
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)    
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)    
    
    model = YOLO("best.pt")
    
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )
    return cap, model, box_annotator
    

