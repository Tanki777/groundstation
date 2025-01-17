import sys

sys.path.insert(1,'rodos/support/support-programs/middleware-python')
import rodosmwinterface as rodos
#rodos.printTopicInit(enable=True)

class Controller():
    def __init__(self):
        x = None #placeholder

    def connectSatellite(self):
        from View import TelemetryHandler #import locally and hope that it works

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

        acTopic.addSubscriber(TelemetryHandler.topicHandlerAC_TM)
        adTopic.addSubscriber(TelemetryHandler.topicHandlerAD_TM)
        imuTopic.addSubscriber(TelemetryHandler.topicHandlerIMU_TM)
        lsTopic.addSubscriber(TelemetryHandler.topicHandlerLS_TM)
        mtTopic.addSubscriber(TelemetryHandler.topicHandlerMT_TM)
        plTopic.addSubscriber(TelemetryHandler.topicHandlerPL_TM)
        pwTopic.addSubscriber(TelemetryHandler.topicHandlerPW_TM)
        rwTopic.addSubscriber(TelemetryHandler.topicHandlerRW_TM)
        gwUart.forwardTopic(telecommandTopic)

    

controller = Controller()