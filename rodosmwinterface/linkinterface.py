# rodos-middleware: This file is a part of the Master Thesis of Sebastian Kind 2023


from .networkmessage import *


#needed for LinkinterfaceUART and LinkinterfaceBluetooth
class LinkinterfaceI():
    def __init__(self):
        self.BIGENDIAN_P = True
        pass

    def sendNetworkMessage(self, msg: NetworkMessage):
        pass

    def getNetworkMessage(self):
        pass
