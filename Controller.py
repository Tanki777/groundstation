import sys
import struct
import socket
import io
import time
import math
import Model
from PIL import Image
import numpy as np
import cv2

sys.path.insert(1,'rodos/support/support-programs/middleware-python')
import rodosmwinterface as rodos
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
#rodos.printTopicInit(enable=True)

class Controller(QThread):

    def __init__(self):
        super().__init__()

        self.dataModel = Model.DataModel()

    tmAC = pyqtSignal(str)
    tmAD = pyqtSignal(str)
    tmHeading = pyqtSignal(float)
    tmIMU = pyqtSignal(str)
    tmLS = pyqtSignal(str)
    tmMT = pyqtSignal(str)
    tmPL = pyqtSignal(str)
    tmPW = pyqtSignal(str)
    tmRW = pyqtSignal(str)
    tmERR = pyqtSignal(str)
    tmTCFB = pyqtSignal(str)

    plotAC = pyqtSignal(Model.PlotDataAC)
    plotAD = pyqtSignal(Model.PlotDataAD)
    plotIMU = pyqtSignal(Model.PlotDataIMU)
    plotLS = pyqtSignal(Model.PlotDataLS)
    plotMT = pyqtSignal(Model.PlotDataMT)
    plotPL = pyqtSignal(Model.PlotDataPL)
    plotPW = pyqtSignal(Model.PlotDataPW)
    plotRW = pyqtSignal(Model.PlotDataRW)

    #tmDebug = pyqtSignal(str)

    payloadData = pyqtSignal(QImage)

    def getHour(self, time):
        hour = int(time / 60.0 / 60.0)
        return hour
    
    def getMin(self, time):
        hour = int(time / 60.0 / 60.0)
        min = int((time / 60.0 / 60.0 - hour) * 60)
        return min

    def getSec(self, time):
        hour = int(time / 60.0 / 60.0)
        min = int((time / 60.0 / 60.0 - hour) * 60)
        sec = int((((time / 60.0 / 60.0 - hour) * 60) - min) * 60)
        return sec

    #handler for AttitudeControl
    def topicHandlerAC_TM(self, data):
        try:
            #print("DEBUG: trying to handle AC_TM\n")
            #TIME TMPRD CTRPRD YAWREF YAWDOTREF YAWCURR YAWDOTCURR POS_CTRL_OUT POS_CTRL_P POS_CTRL_I POS_CTRL_D SPD_CTRL_OUT SPD_CTRL_P SPD_CTRL_I SPD_CTRL_D
            unpacked = struct.unpack("d?QQdddddddddddd", data)
            message = "{}:{}:{} | {} | {} | {:.3f} | {:.3f} | {:.1f} | {:.1f} | {:.1f} | {:.1f}".format(self.getHour(unpacked[0]), self.getMin(unpacked[0]), self.getSec(unpacked[0]), unpacked[2], unpacked[3], unpacked[4], unpacked[5], unpacked[12], unpacked[13], unpacked[14], unpacked[15])
            self.tmAC.emit(message)

            #target yaw, filtered yaw, target speed, filtered speed, POS_CTRL_OUT POS_CTRL_P POS_CTRL_I POS_CTRL_D SPD_CTRL_OUT SPD_CTRL_P SPD_CTRL_I SPD_CTRL_D
            plotData = Model.PlotDataAC(unpacked[4], unpacked[6] * 180 / math.pi, unpacked[5], unpacked[7] * 180 / math.pi, unpacked[8], unpacked[9], unpacked[10], unpacked[11], unpacked[12], unpacked[13], unpacked[14], unpacked[15])
            self.plotAC.emit(plotData)

        except Exception as e:
            print("DEBUG: unpacking error AC!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for AttitudeDetermination
    def topicHandlerAD_TM(self, data):
        try:
            #print("DEBUG: trying to handle AC_TM\n")
            #TIME | TMPRD | ROLL | PITCH | YAW | ROLLRAW | PITCHRAW | YAWRAW | YAWSPEED | YAWSPEEDRAW
            unpacked = struct.unpack("d?Qddddddddd", data)
            message = "{}:{}:{} | {} | {:.3f} | {:.3f} | {:.3f}".format(self.getHour(unpacked[0]), self.getMin(unpacked[0]), self.getSec(unpacked[0]), unpacked[2], unpacked[4] / math.pi * 180, unpacked[5] / math.pi * 180, unpacked[6] / math.pi * 180)
            self.tmAD.emit(message)  
            self.tmHeading.emit(unpacked[6] / math.pi * 180.0)

            #raw roll, filtered roll, raw pitch, filtered pitch, raw yaw, filtered yaw, raw yaw speed, filtered yaw speed
            plotData = Model.PlotDataAD(unpacked[7] / math.pi * 180, unpacked[4] / math.pi * 180, unpacked[8] / math.pi * 180, unpacked[5] / math.pi * 180, unpacked[9] / math.pi * 180, unpacked[6] / math.pi * 180, unpacked[11] / math.pi * 180, unpacked[10] / math.pi * 180)
            self.plotAD.emit(plotData)

        except Exception as e:
            print("DebuG: unpacking error AD!\n")
            print(e)
            print(data)
            print(len(data)) 

    #handler for IMU
    def topicHandlerIMU_TM(self, data):
        try:
            #TIME | TMPRD | SNSPRD | AX | AY | AZ | GX | GY | GZ | MX | MY | MZ
            unpacked = struct.unpack("d?QQddddddddddd", data)
            message = ("{}:{}:{} | {} | {} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f}"
                           .format(self.getHour(unpacked[0]), self.getMin(unpacked[0]), self.getSec(unpacked[0]), unpacked[2], unpacked[3], unpacked[4],unpacked[5], unpacked[6], unpacked[7], unpacked[8], unpacked[9]
                                   , unpacked[10], unpacked[11], unpacked[12], unpacked[13]))
            self.tmIMU.emit(message)

            #ax, ay, az, gx, gy, gz, mx, my, mz
            plotData = Model.PlotDataIMU(unpacked[5],unpacked[6],unpacked[7],unpacked[8] * 180 / math.pi ,unpacked[9] * 180 / math.pi ,unpacked[10] * 180 / math.pi ,unpacked[11],unpacked[12],unpacked[13],)
            self.plotIMU.emit(plotData)

        except Exception as e:
            print("DEBUG: unpacking error IMU!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for LightSensor
    def topicHandlerLS_TM(self, data):
        try:
            #TIME TMPRD SNSPRD LUX
            unpacked = struct.unpack("d?QQdd", data) #TODO: adjust, waiting for stm code
            message = ("{}:{}:{} | {} | {} | {:.3f}"
                           .format(self.getHour(unpacked[0]), self.getMin(unpacked[0]), self.getSec(unpacked[0]), unpacked[2], unpacked[3], unpacked[5]))
            self.tmLS.emit(message)

            #LUX
            plotData = Model.PlotDataLS(unpacked[5])
            #self.plotLS.emit(plotData)

        except Exception as e:
            print("DEBUG: unpacking error LS!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for MagneticTorquer
    def topicHandlerMT_TM(self, data):
        try:
            #TIME TMPRD IREF TRQNR PWM
            unpacked = struct.unpack("d?Qddddd", data)
            message = ("{}:{}:{} | {} | {:.3f} | {:.1f} | {:.1f} | {:.3f} | {:.3f} |"
                       .format(self.getHour(unpacked[0]), self.getMin(unpacked[0]), self.getSec(unpacked[0]), unpacked[2], unpacked[3], unpacked[4], unpacked[5], unpacked[6], unpacked[7]))
            self.tmMT.emit(message)

            #TRQNR PWM
            plotData = Model.PlotDataMT(0,0)
            if unpacked[4] == 1: #torquer 1
                plotData.pwm_torquer1 = unpacked[5]
                plotData.pwm_torquer2 = 0

            elif unpacked[4] == 2: #torquer 2
                plotData.pwm_torquer1 = 0
                plotData.pwm_torquer2 = unpacked[5]

            elif unpacked[4] == 121: #both torquers, quadrant 1
                plotData.pwm_torquer1 = 1000
                plotData.pwm_torquer2 = 1000

            elif unpacked[4] == 122: #both torquers, quadrant 2
                plotData.pwm_torquer1 = 1000
                plotData.pwm_torquer2 = -1000

            elif unpacked[4] == 123: #both torquers, quadrant 3
                plotData.pwm_torquer1 = -1000
                plotData.pwm_torquer2 = -1000

            elif unpacked[4] == 124: #both torquers, quadrant 4
                plotData.pwm_torquer1 = -1000
                plotData.pwm_torquer2 = 1000
                

            self.plotMT.emit(plotData)
            
        except Exception as e:
            print("DEBUG: unpacking error MT!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for Payload
    def topicHandlerPL_TM(self, data):
        try:
            #TIME TMPRD
            unpacked = struct.unpack("d?Q", data) #TODO: adjust, waiting for stm code
            message = ("{}:{}:{} | {}"
                           .format(self.getHour(unpacked[0]), self.getMin(unpacked[0]), self.getSec(unpacked[0]), unpacked[2])) #TODO: adjust, waiting for stm code
            self.tmPL.emit(message)
            
        except Exception as e:
            print("DEBUG: unpacking error PL!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for Power
    def topicHandlerPW_TM(self, data):
        try:
            #TIME TMPRD SNSPRD BATV BATI BATPCT SPLV SPLI SPRV SPRI
            unpacked = struct.unpack("d?QQdddddddd", data)
            message = ("{}:{}:{} | {} | {} | {:.1f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f} | {:.3f}"
                           .format(self.getHour(unpacked[0]), self.getMin(unpacked[0]), self.getSec(unpacked[0]), unpacked[2], unpacked[3], unpacked[5], unpacked[6], unpacked[7]
                                   ,unpacked[8], unpacked[9], unpacked[10], unpacked[11]))
            self.tmPW.emit(message)
            
        except Exception as e:
            print("DEBUG: unpacking error PW!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for ReactionWheel
    def topicHandlerRW_TM(self, data):
        try:
            #TIME TMPRD SNSPRD SPD SPDREF
            unpacked = struct.unpack("d?QQddddddd", data)
            message = ("{}:{}:{} | {} | {} | {:.3f} | {:.3f}"
                           .format(self.getHour(unpacked[0]), self.getMin(unpacked[0]), self.getSec(unpacked[0]), unpacked[2], unpacked[3], unpacked[5], unpacked[6]))
            self.tmRW.emit(message)

            #SPDREF, SPD, SPD_CTRL_OUT, SPD_CTRL_P, SPD_CTRL_I, SPD_CTRL_D
            plotData = Model.PlotDataRW(unpacked[6],unpacked[5],unpacked[7],unpacked[8],unpacked[9],unpacked[10])
            self.plotRW.emit(plotData)
            
        except Exception as e:
            print("DEBUG: unpacking error RW!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for ErrorMessage
    def topicHandlerERR_TM(self, data):
        try:
            unpacked = struct.unpack("d32s256s", data)
            message = ("{}:{}:{} | ORIGIN={} | MSG={}"
                           .format(self.getHour(unpacked[0]), self.getMin(unpacked[0]), self.getSec(unpacked[0]), unpacked[1].decode("utf-8").rstrip("\x00"), unpacked[2].decode("utf-8").rstrip("\x00")))
            self.tmERR.emit(message)
            
        except Exception as e:
            print("DEBUG: unpacking error ERR!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for Telecommand Feedback
    def topicHandlerTC_FB(self, data):
        print("bub\n")
        try:
            unpacked = struct.unpack("HQHd", data)
            cmdWordStr = ""

            #command word from hex to string
            for tc in self.dataModel.telecommands:
                if tc.id == unpacked[0]:
                    cmdWordStr = tc.word

            message = ("| {} | {}"
                           .format(cmdWordStr, unpacked[3]))
            self.tmTCFB.emit(message)
            
        except Exception as e:
            print("DEBUG: unpacking error TC_FB!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for Debug
    #def topicHandlerDebug(self, data):
    #    try:
    #        unpacked = struct.unpack("dddddd", data)
    #        message = ("{}:{}:{} | VT={:.2f} | w_measured={:.3f} | err={:.3f} | err_i={:.3f} | err_d={:.3f}"
    #                       .format(self.getHour(unpacked[0]), self.getMin(unpacked[0]), self.getSec(unpacked[0]), unpacked[1],unpacked[2],unpacked[3],unpacked[4],unpacked[5],))
    #        self.tmDebug.emit(message)
    #        
    #    except Exception as e:
    #        print("DEBUG: unpacking error ERR!\n")
    #        print(e)
    #        print(data)
    #        print(len(data))

    
    def connectStm(self):
        #telecommand topics
        self.telecommandTopic = rodos.Topic(2000) #telecommand

        #telemetry topics
        self.acTopic = rodos.Topic(3001) #AttitudeControl
        self.adTopic = rodos.Topic(3002) #AttitudeDetermination
        self.imuTopic = rodos.Topic(3003) #IMU
        self.lsTopic = rodos.Topic(3004) #LightSensor
        self.mtTopic = rodos.Topic(3005) #MagneticTorquer
        self.plTopic = rodos.Topic(3006) #PayLoad
        self.pwTopic = rodos.Topic(3007) #Power
        self.rwTopic = rodos.Topic(3008) #ReactionWheel
        self.errTopic = rodos.Topic(4000) #ErrorMessage
        self.tcFbTopic = rodos.Topic(3200) #Telecommand Feedback

        #self.debugTopic = rodos.Topic(8000)
        #thTopic = rodos.Topic(3009) #Thermal ditched

        #bluetooth connection to stm board
        self.luart = rodos.LinkinterfaceUART(path="/dev/rfcomm0")
        self.gwUart = rodos.Gateway(self.luart)
        self.gwUart.run()

        self.acTopic.addSubscriber(self.topicHandlerAC_TM)
        self.adTopic.addSubscriber(self.topicHandlerAD_TM)
        self.imuTopic.addSubscriber(self.topicHandlerIMU_TM)
        self.lsTopic.addSubscriber(self.topicHandlerLS_TM)
        self.mtTopic.addSubscriber(self.topicHandlerMT_TM)
        self.plTopic.addSubscriber(self.topicHandlerPL_TM)
        self.pwTopic.addSubscriber(self.topicHandlerPW_TM)
        self.rwTopic.addSubscriber(self.topicHandlerRW_TM)
        self.errTopic.addSubscriber(self.topicHandlerERR_TM)
        self.tcFbTopic.addSubscriber(self.topicHandlerTC_FB)

        #self.debugTopic.addSubscriber(self.topicHandlerDebug)
        self.gwUart.forwardTopic(self.telecommandTopic)
        print("DEBUG: connected!\n")

    def reconnectStm(self):
        print("DEBUG: reconnect\n")
        del self.luart
        del self.gwUart
        del self.telecommandTopic

        self.telecommandTopic = rodos.Topic(2000)
        #bluetooth connection to stm board
        self.luart = rodos.LinkinterfaceUART(path="/dev/rfcomm0")
        self.gwUart = rodos.Gateway(self.luart)
        self.gwUart.run()
        self.gwUart.forwardTopic(self.telecommandTopic)

    def connectPi(self):
        host = "0.0.0.0" #TODO: adjust
        port = 5005 #TODO: adjust
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.bind((host, port))
            #server_socket.listen(1)
            print(f"Listening for connections on {host}:{port}...")

            #client_socket, addr = server_socket.accept()
            print(f"Connection established with {host}")

            i = 0

            while self.running:
                i = i + 1
                try:
                    # Receive the image size (4 bytes)
                    #size_data = client_socket.recv(4)
                    #if not size_data:
                    #    break

                    # Convert size_data to integer
                    #img_size = struct.unpack('<L', size_data)[0]

                    # Receive the image data
                    #img_data = b''
                    img_data, _ = client_socket.recvfrom(65535)
                    frame = np.frombuffer(img_data, dtype=np.uint8)
                    cvimg = cv2.imdecode(frame, cv2.IMREAD_COLOR_RGB)
                    height, width, channels = cvimg.shape

                    if channels == 3:
                        self.qimage = QImage(cvimg.data, width, height, width*channels, QImage.Format.Format_RGB888)

                    else:
                        print("img error\n")

                    #while len(img_data) < img_size:
                    #    packet = client_socket.recv(img_size - len(img_data))
                    #    if not packet:
                    #        break
                    #    img_data += packet

                    # Convert the image data to QImage
                    print("converting...\n")
                    #image = Image.open(io.BytesIO(img_data))
                    print("image...\n")
                    #qimage = QImage(image.tobytes(), image.width, image.height, QImage.Format.Format_RGB888)
                    print("QImage...\n")
                    self.payloadData.emit(self.qimage)

                    #qimage.save("testImage{}".format(i),"JPEG")

                except Exception as e:
                    print(f"Error: {e}")
                    break
                #print("idle")
                #time.sleep(1)

            #client_socket.close()

    def stopPi(self):
        self.running = False
        #self.quit()
        #self.wait()
        

    def run(self):
        #connect to stm board
        self.connectStm()
        
        #wifi connection to raspberry
        self.running = True
        self.connectPi()


  

