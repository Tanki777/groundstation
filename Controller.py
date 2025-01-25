import sys
import struct

sys.path.insert(1,'rodos/support/support-programs/middleware-python')
import rodosmwinterface as rodos
from PyQt6.QtCore import QThread, pyqtSignal
#rodos.printTopicInit(enable=True)

class Controller(QThread):

    tmAC = pyqtSignal(str)
    tmAD = pyqtSignal(str)
    tmHeading = pyqtSignal(float)
    tmIMU = pyqtSignal(str)
    tmLS = pyqtSignal(str)
    tmMT = pyqtSignal(str)
    tmPL = pyqtSignal(str)
    tmPW = pyqtSignal(str)
    tmRW = pyqtSignal(str)

    

    #handler for AttitudeControl
    def topicHandlerAC_TM(self, data):
        try:
            #print("DEBUG: trying to handle AC_TM\n")
            unpacked = struct.unpack("d?QQdd", data)
            message = "time: {} | tmprd: {} | ctrprd: {} | yr: {} | ydr: {}\n".format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5])
            self.tmAC.emit(message)

        except Exception as e:
            #print("DEBUG: error!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for AttitudeDetermination
    def topicHandlerAD_TM(self, data):
        try:
            #print("DEBUG: trying to handle AC_TM\n")
            unpacked = struct.unpack("d?Qdddd", data)
            message = "time: {} | tmprd: {} | attTime: {} | roll: {} | pitch: {} | yaw: {}\n".format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5], unpacked[6])
            self.tmAD.emit(message)  
            self.tmHeading.emit(unpacked[6])

        except Exception as e:
            #print("DebuG: error!\n")
            print(e)
            print(data)
            print(len(data)) 

    #handler for IMU
    def topicHandlerIMU_TM(self, data):
        try:
            unpacked = struct.unpack("d?QQddddddddddd", data)
            message = ("TIM={} | TMPRD={} | SNSPRD={} | SNSTIM={} | AX={} | AY={} | AZ={} | GX={} | GY={} | GZ={} | MX={} | MY={} | MZ={} | TEMP={} "
                           .format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5], unpacked[6], unpacked[7], unpacked[8], unpacked[9]
                                   , unpacked[10], unpacked[11], unpacked[12], unpacked[13], unpacked[14]))
            self.tmIMU.emit(message)

        except Exception as e:
            #print("DEBUG: error!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for LightSensor
    def topicHandlerLS_TM(self, data):
        try:
            unpacked = struct.unpack("d?QQd", data) #TODO: adjust, waiting for stm code
            message = ("TIM={} | TMPRD={} | SNSPRD={} | SNSTIM={}"
                           .format(unpacked[0], unpacked[2], unpacked[3], unpacked[4])) #TODO: adjust, waiting for stm code
            self.tmLS.emit(message)

        except Exception as e:
            print("DEBUG: error!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for MagneticTorquer
    def topicHandlerMT_TM(self, data):
        try:
            unpacked = struct.unpack("d?Qd", data)
            message = ("TIM={} | TMPRD={} | IREF={}"
                           .format(unpacked[0], unpacked[2], unpacked[3]))
            self.tmMT.emit(message)
            
        except Exception as e:
            print("DEBUG: error!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for Payload
    def topicHandlerPL_TM(self, data):
        try:
            unpacked = struct.unpack("d?Q", data) #TODO: adjust, waiting for stm code
            message = ("TIM={} | TMPRD={}"
                           .format(unpacked[0], unpacked[2])) #TODO: adjust, waiting for stm code
            self.tmPL.emit(message)
            
        except Exception as e:
            print("DEBUG: error!\n")
            print(e)
            print(data)
            print(len(data))

    #handler for Power
    def topicHandlerPW_TM(self, data):
        try:
            unpacked = struct.unpack("d?QQdddddddd", data)
            message = ("TIM={} | TMPRD={} | SNSPRD={} | SNSTIM={} | BATV={} | BATI={} | BATPCT={} | SPLV={} | SPLI={} | SPRV={} | SPRI={}"
                           .format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5], unpacked[6], unpacked[7]
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
            unpacked = struct.unpack("d?QQddd", data)
            message = ("TIM={} | TMPRD={} | SNSPRD={} | SNSTIM={} | SPD={} | SPDREF={}"
                           .format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5], unpacked[6]))
            self.tmRW.emit(message)
            
        except Exception as e:
            print("DEBUG: unpacking error RW!\n")
            print(e)
            print(data)
            print(len(data))

    def run(self):
        #telecommand topics
        telecommandTopic = rodos.Topic(2000) #telecommand

        #telemetry topics
        acTopic = rodos.Topic(3001) #AttitudeControl
        adTopic = rodos.Topic(3002) #AttitudeDetermination
        imuTopic = rodos.Topic(3003) #IMU
        lsTopic = rodos.Topic(3004) #LightSensor
        mtTopic = rodos.Topic(3005) #MagneticTorquer
        plTopic = rodos.Topic(3006) #PayLoad
        pwTopic = rodos.Topic(3007) #Power
        rwTopic = rodos.Topic(3008) #ReactionWheel
        #thTopic = rodos.Topic(3009) #Thermal ditched

        luart = rodos.LinkinterfaceUART(path="/dev/rfcomm0")
        gwUart = rodos.Gateway(luart)
        gwUart.run()

        acTopic.addSubscriber(self.topicHandlerAC_TM)
        adTopic.addSubscriber(self.topicHandlerAD_TM)
        imuTopic.addSubscriber(self.topicHandlerIMU_TM)
        lsTopic.addSubscriber(self.topicHandlerLS_TM)
        mtTopic.addSubscriber(self.topicHandlerMT_TM)
        plTopic.addSubscriber(self.topicHandlerPL_TM)
        pwTopic.addSubscriber(self.topicHandlerPW_TM)
        rwTopic.addSubscriber(self.topicHandlerRW_TM)
        gwUart.forwardTopic(telecommandTopic)
        print("DEBUG: connected!\n")



  

