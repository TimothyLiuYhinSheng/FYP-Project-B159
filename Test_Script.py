from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType, alarmAlarmJsonFile
from time import sleep
import threading
import numpy as np
import re

# current coordinates
current_actual = None
algorithm_queue = None
enableStatus_robot = None
robotErrorState = False
globalLockValue = threading.Lock()

#Setting the parameters
load=0.1
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

if __name__ == '__main__':
    dashboard, move, feed = connect_robot()
    
    #Set the parameters
    dashboard.EnableRobot()
    dashboard.EnableRobot(load, centerX, centerY, centerZ) 
    
    #Set the acceleration
    dashboard.AccL(acceleration)  
        
    #Set the speed
    dashboard.SpeedL(speed)
    
    #Get the cartesian coordinate pose of the robot
    # User=1 #Index of user coordinate System
    # Tool=1 # Index of Tool Coordinate System
    # dashboard.GetPose(User, Tool)  
    coordinates = dashboard.GetPose()
    print(coordinates)
    print('coordinates printed')
    
    #Check robot mode
    robotmode = dashboard.RobotMode()
    print(f'Robot mode is:{robotmode}')
    
    #to run a script
    # name="test.lua"
    # dashboard.RunScript(name)  
    
    feed_thread = threading.Thread(target=GetFeed, args=(feed,))
    feed_thread.setDaemon(True)
    feed_thread.start()
    feed_thread1 = threading.Thread(target=ClearRobotError, args=(dashboard,))
    feed_thread1.setDaemon(True)
    feed_thread1.start()
    
    
    print("Loop Execution")
    point_a = [350, 0, 50, 0]
    point_b = [350, 100 , 0, 0]
    point_d = [350, -200, -50,0]
    point_origin = [350,0,0,0] 
    count=0
    while True:
        RunPoint(move,point_origin)
        sleep(1)
        #WaitArrive(point_origin)
        RunPoint(move, point_a)
        sleep(1)
        RunPoint(move, point_b)
        sleep(1)
       # WaitArrive(point_b)
        RunPoint(move,point_d)
        sleep(1)
        #WaitArrive(point_d)
        count+=1
        if count==3:
            break
        continue
        
    dashboard.DisableRobot()