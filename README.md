---
typora-root-url: ./picture
---

dobot   TCP-IP-4Axis-Python-CMD   二次开发api接口 （ [TCP-IP-MG400-Python English README](https://github.com/Dobot-Arm/TCP-IP-4Axis-Python.git) ）


# Additional Notes
The final Script can be found in 
Final_Script.py

There are multiple testing scripts (for future development)
1. ObjectDetection (Testing Script)
2. PythonExample
3. Movement
4. Camsize (Testing Script)

Video of Working model can be found here:
https://www.youtube.com/watch?v=ZkObqneRZOo

# 1 Introduction

TCP-IP-4Axis-Python is a software development kit designed for dobot company's Python package based on TCP/IP protocol. It is developed based on Python language, follows the dobot-TCP-IP control communication protocol, connects to the machine terminal through Tcp socket, and provides users with an easy-to-use API interface. Through TCP-IP-4Axis-Python, users can quickly connect to the dobot machine and conduct secondary development to control and use the machine.



## Prerequisites

* The computer can be connected to the network port of the controller with a network cable, and then set a fixed IP to be in the same network segment as the controller IP. The controller can also be connected wirelessly.

  When connected to wired connection, connect to LAN1: ip is 192.168.1.6, when connected to wired connection, connect to LAN2: ip is 192.168.2.6, wireless connection: ip is 192.168.9.1

* Try to ping the controller IP and make sure it is on the same network segment.

* Install the Python environment. For Python environment installation, please refer to [Python Installation Guide](https://docs.python.org/zh-cn/3/using/index.html)

  Python environment configuration numpy: pip install numpy

* This API interface and Demo are suitable for controller versions V1.5.6.0 and above of the MG400/M1Pro series




## Version and Release Records

### Current version v1.0.0.0

| Version | Modification date |
| :------: | :--------: |
| v1.0.0.0 | 2023-10-20 |



# 2. Technical support

If you encounter any problems or suggestions during use, you can obtain dobot technical support through the following methods:

* Send an email to futingxing@dobot-robots.com and describe the problems and usage scenarios you encountered in detail
* Send an email to wuyongfeng@dobot-robots.com and describe in detail the problems you encountered and usage scenarios




# 3.TCP-IP-4Axis-Python control protocol

Since TCP/IP-based communication has the characteristics of low cost, high reliability, strong practicability, and high performance; many industrial automation projects have widespread demand for supporting TCP/IP protocol-controlled robots, so the MG400/M1Pro robot will be designed using the TCP/IP protocol. Based on the /TCP-IP-Protocol.git)**



# 4. Get TCP-IP-4Axis-Python

1. Download or clone the dobot TCP-IP-4Axis-Python-CMD secondary development api program from GitHub

   ```bash
   `git clone https://github.com/Dobot-Arm/TCP-IP-4Axis-Python.git
   ```

2. Refer to the corresponding README.md document for use;

   
# 5. Description and usage of file class

1. main.py: main program execution entry.

2. dobot_api.py: encapsulates the robot interface. The specific Api instruction usage is based on the robot TCP/IP remote control solution (https://github.com/Dobot-Arm/TCP-IP-Protocol) for reference and use.

3. files: stores alarm ID related information, `alarm_controller.json` warning alarm configuration file, `alarm_servo.json` servo alarm configuration file

4. PythonExample.py: Contains usage and code examples of some api interface instructions for reference

Class description in dobot_api directory:

| Class | Define |
| ------------------ | ---------------------------------- --------------- |
| DobotApi | An interface class based on tcp communication, encapsulating the basic business of communication |
| DobotApiDashboard | Inherited from DobotClient and implements specific basic robot functions |
| DobotApiMove | Inherited from DobotClient, implements specific robot movement functions |
| MyType | Data type object, status list of feedback robot |
| alarm_controller | Warning alarm configuration information |
| alarm_servo | Servo alarm configuration information |

**DobotApi**

 The interface class based on TCP communication provides functions such as TCP connection to the machine, closing, obtaining IP, port, etc., and encapsulates the basic business of communication.


```python
class DobotApi:
    def __init__(self, ip, port, *args):
    ""
    if self.port == 29999 or self.port == 30003 or self.port == 30004:
            try:
                self.socket_dobot = socket.socket()
                self.socket_dobot.connect((self.ip, self.port))
    ""        
```


**DobotApiDashboard**

   Inherited from DobotClient, it can send some setting-related control instructions to the robot. Implemented specific basic robot functions.

```c++

class DobotApiDashboard(DobotApi):
    """
    Define class dobot_api_dashboard to establish a connection to Dobot
    """
    def EnableRobot(self,*dynParams):
      """
```

**DobotApiMove**  

Inherited from DobotClient, it can send some motion-related motion instructions to the robot, realizing specific robot motion functions.

```python
class DobotApiMove(DobotApi):
    """
    Define class dobot_api_move to establish a connection to Dobot
    """
    def MovJ(self, x, y, z, r,*dynParams):

```

**MyType**

Data type object that can feed back the status information of the robot.


```c++
MyType=np.dtype([('len', np.int16, ), 
                ('Reserve', np.int16, (3,) ),
```



Create control port objects, motion port objects, feedback port objects respectively, and perform Tcp connections.

```python
    ip = "192.168.1.6"
    dashboardPort = 29999
    movePort = 30003
    feedPort = 30004
    print("正在建立连接...")
    dashboard = DobotApiDashboard(ip, dashboardPort)
    move = DobotApiMove(ip, movePort)
    feed = DobotApi(ip, feedPort)
    
```

Use the control port to issue control command information to enable and enable operations.


```python
     dashboard.EnableRobot()
     dashboard.DisableRobot()
```

Use the motion port to issue operating command information to control machine movement.

```python
    x=10
    y=10
    z=10
    r=10
    move.MovL(x,y,z,r)
    move.MovJ(x,y,z,r)
```

Get machine status via feedback port

```python
    data = bytes()
    while hasRead < 1440:
        temp = feed.socket_dobot.recv(1440 - hasRead)
        if len(temp) > 0:
            hasRead += len(temp)
            data += temp
    hasRead = 0
    feedInfo = np.frombuffer(data, dtype=MyType)
    if hex((feedInfo['test_value'][0])) == '0x123456789abcdef':
        print(feedInfo['EnableStatus'][0])   #输出机器使能状态
```
**Please see the code example PythonExample.py and Demo example for specific usage details**



# 6. Frequently Asked Questions

Problem 1: Tcp connection port 29999/30003 cannot be connected or cannot issue commands after connecting.

 Solution: If the controller version is below version 1.6.0.0, you can try to upgrade the controller to version 1.6.0.0 or above. If the machine is already version 1.6.0.0 or above, you can feedback the problem symptoms and operations to technical support



Question 2: During the Tcp connection process, the 29999 control port can send commands, but the 30003 motion port cannot send commands.

 Solution: The motion queue is blocked. Try to use the 29999 port to issue clearerror() and continue() instructions to reopen the queue.



Question 3: How to judge whether the machine movement command is in place

Solution: You can determine whether the machine motion command is in place by issuing sync commands.

​ It can be judged whether the target point is in place by comparing the Cartesian coordinate value of the target point with the actual Cartesian coordinate value of the machine.



# 7. Example

* Dobot-Demo implements TCP control of the machine and other interactions, conducts TCP connections to the control port, motion port, and feedback port respectively, issues instructions based on the machine motion instruction completion status, and handles machine abnormal status and other functions.

  

1. Main thread: Connect the machine control port, motion port, and feedback port respectively. Enable the machine, MovL movement instructions and other actions

![](/main.png)

2. Feedback status thread: real-time feedback of machine status information

![](/feed.png)

3. Machine motion thread: issues motion instructions to the machine

![](/move.png)

4. Exception handling thread: judge and handle the abnormal status of the machine

![](/excetion.png)

**The timing sequence of operation steps for Demo running is shown in the figure below:**

1. Obtain the Dobot TCP-IP-4Axis-Python-CMD secondary development API program from GitHub

   ```bash
   `git clone https://github.com/Dobot-Arm/TCP-IP-4Axis-Python.git
   ```

2. Connect to the machine through the LAN1 network port, and set the IP address of the local machine to the 192.168.1.X network segment

   Control Panel>>Network>>Internet>>Network Connections

   ![](/netConnect.png)

   

   Select the connected Ethernet >> Right-click >> Properties >> Internet Protocol Version (TCP/IPV4)

   Modify the ip address to 192.168.1.X network segment IP

   ![](/updateIP.png)

   

3. Connect to the host computer DobotStudio Pro, connect to the machine, and switch the machine mode to TCP/IP mode

   ![](/checkTcpMode.png)

   

4. To run the program, you need to detect and search the dynamic library, open the entire directory in VsCode/PyCharm, and run main.py directly.

   ![](/runpy.png)

   

  **common problem:**

​ **Question 1: ModuleNotFoundError: Nomode name 'numpy'**

Solution: The numpy environment is not installed, install numpy pip install numpy.

   

​ **Question 2: Cartesian coordinates corresponding to different models (MG400/M1pro) in the demo**

Solution: Confirm the Cartesian coordinates corresponding to the model and modify the Demo coordinate values.



**Please ensure that the machine is in a safe position before running the example to prevent unnecessary collisions with the machine**
