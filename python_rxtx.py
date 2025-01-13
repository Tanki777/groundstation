#!/bin/python3

#address of bluetooth module 00:0E:EA:CF:7B:E7

import sys
import time
import struct

sys.path.insert(1,'rodos/support/support-programs/middleware-python')
import rodosmwinterface as rodos
rodos.printTopicInit(enable=True)

# Callback for AC TM
def topicHandlerAC_TM(data):
  try:
    unpacked = struct.unpack("d?QQdd", data)
    print("RODOS sends time: {} | tmprd: {} | ctrprd: {} | yr: {} | ydr: {}".format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5]))
  except Exception as e:
    print(e)
    print(data)
    print(len(data))

# Callback for AD TM
def topicHandlerAD_TM(data):
  try:
    unpacked = struct.unpack("d?Qdddd", data)
    #att = struct.unpack("dddd",unpacked[3])
    print("RODOS sends time: {} | tmprd: {} | attTime: {} | roll: {} | pitch: {} | yaw: {}".format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5], unpacked[6]))
  except Exception as e:
    print(e)
    print(data)
    print(len(data))

python2rodos = rodos.Topic(2000) #telecommand
rodos2python = rodos.Topic(3000) #telemetry
acTM = rodos.Topic(3001) #AC TM
adTM = rodos.Topic(3002) #AD TM

luart = rodos.LinkinterfaceUART(path="/dev/rfcomm0")
gwUart = rodos.Gateway(luart)
gwUart.run()

#rodos2python.addSubscriber(topicHandler)
acTM.addSubscriber(topicHandlerAC_TM)
adTM.addSubscriber(topicHandlerAD_TM)
gwUart.forwardTopic(python2rodos)

sensor_index = 0

timeSeconds = 0
tcSent = False

while True:
  # Dummy sensor data
  #sensor_index += 1
  #x = 3.1415
  #y = 2.7182
  #z = 12345

  # Pack sensor data to a struct that RODOS recognizes
  #sensor_struct = struct.pack("20sIddd", b"Magnetometer", sensor_index, x, y, z)
  #python2rodos.publish(sensor_struct)
  if timeSeconds >= 3 and tcSent == False:
    telecommand = struct.pack("HQHq",0x2001,0,1,0)
    python2rodos.publish(telecommand)
    tcSent = True

  timeSeconds = timeSeconds + 1
  time.sleep(1)
