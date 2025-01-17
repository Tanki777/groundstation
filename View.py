import sys
import struct
from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTextBrowser, QLineEdit, QLabel, QCheckBox, QFrame, QSizePolicy, QPlainTextEdit)
import Model
import Controller

class TelecommandWindow(QWidget):
    #initialization. called when the object is created
    def __init__(self):
        super().__init__()

        self.title = "Telecommand"
        self.top = 100
        self.left = 100
        self.width = 300
        self.height = 250

        self.InitWindow()

    #initialize the telecommand window
    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #label
        self.sendTc_label = QLabel("Send Telecommand")
        self.sendTc_label.setFont(QtGui.QFont("Courier New", 20))

        #combobox to select a telecommand
        self.tc_comboBox = QComboBox()

        for tc in Model.dataModel.telecommands:
            self.tc_comboBox.addItem(tc)

        #container for telecommand label and combobox
        self.upperLeft_vbox = QVBoxLayout()
        self.upperLeft_vbox.addWidget(self.sendTc_label)
        self.upperLeft_vbox.addWidget(self.tc_comboBox)

        #label
        self.param_label = QLabel("Parameter")
        self.param_label.setFont(QtGui.QFont("Courier New", 20))

        #input field for the parameter value
        self.param_lineEdit = QLineEdit()

        #button for sending the telecommand
        self.sendTc_button = QPushButton()
        self.sendTc_button.clicked.connect(self.sendTelecommand)

        #container for parameter label, input field and send telecommand button
        self.upperRight_vbox = QVBoxLayout()
        self.upperRight_vbox.addWidget(self.param_label)
        self.upperRight_vbox.addWidget(self.param_lineEdit)
        self.upperRight_vbox.addWidget(self.sendTc_button)

        #container for upper left and upper right containers
        self.upperHalf_hbox = QHBoxLayout()
        self.upperHalf_hbox.addLayout(self.upperLeft_vbox)
        self.upperHalf_hbox.addLayout(self.upperRight_vbox)

        #label
        self.tcLog_label = QLabel("Telecommand Log")

        #telecommand log
        self.tcLog_textBrowser = QTextBrowser()

        #container for telecommand log label and text browser
        self.lowerLeft_vbox = QVBoxLayout()
        self.lowerLeft_vbox.addWidget(self.tcLog_label)
        self.lowerLeft_vbox.addWidget(self.tcLog_textBrowser)

        #label
        self.tcFeedbackLog_label = QLabel("Telecommand Feedback Log")


        #telecommand feedback log
        self.tcFeedbackLog_textBrowser = QTextBrowser()

        #container for telecommand feedback log label and text browser
        self.lowerRight_vbox = QVBoxLayout()
        self.lowerRight_vbox.addWidget(self.tcFeedbackLog_label)
        self.lowerRight_vbox.addWidget(self.tcFeedbackLog_textBrowser)

        #container for lower left and lower right containers
        self.lowerHalf_hbox = QHBoxLayout()
        self.lowerHalf_hbox.addLayout(self.lowerLeft_vbox)
        self.lowerHalf_hbox.addLayout(self.lowerRight_vbox)

        #main layout
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.upperHalf_hbox)
        self.layout.addLayout(self.lowerHalf_hbox)
        self.setLayout(self.layout)

        #send the telecommand
    def sendTelecommand(self):
        #TODO
        print("DEBUG: sent tc: {}\n".format(self.tc_comboBox.currentText()))

class TelemetryWindow(QWidget):
    #initialization. called when the object is created
    def __init__(self, title, onCloseCallback):
        super().__init__()
        self.title = title
        self.onCloseCallback = onCloseCallback
        self.top = 100
        self.left = 100
        self.width = 300
        self.height = 250

        self.InitWindow()

    def InitWindow(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)

        self.log_textfield = QPlainTextEdit()
        self.log_textfield.setReadOnly(True)
        self.log_textfield.setMaximumBlockCount(2000) #what is this for?
        
        layout = QVBoxLayout()
        layout.addWidget(self.log_textfield)

        self.setLayout(layout)

    def updateTelemetry(self, message):
        self.log_textfield.insertPlainText(message) #add message
        self.log_textfield.verticalScrollBar().setValue(self.log_textfield.verticalScrollBar().maximum()) #auto scroll
        self.log_textfield.update() #update
    
    def closeEvent(self, a0):
        self.onCloseCallback(self.title)
        return super().closeEvent(a0)
    
class MainWindow(QWidget):

    #initialization. called when the object is created
    def __init__(self):
        super().__init__()

        self.title = "Ground Station"
        self.top = 100
        self.left = 100
        self.width = 300
        self.height = 250

        self.cmd_window = TelecommandWindow()
        #self.tmAD_window = TelemetryWindow("Attitude Determination", self.onTelemetryWindowClosed)

        #stores widgets
        self.telemetryWindows = {}
        self.telemetryCheckBoxes = {}

        self.InitWindow()

    #initialize the entry window
    def InitWindow(self):
        #---TMTC section---
        #button which opens the telecommand window
        self.cmd_button = QPushButton("Telecommand\nSystem")
        self.cmd_button.setFont(QtGui.QFont("Courier New", 20))
        self.cmd_button.adjustSize()
        self.cmd_button.clicked.connect(self.openTelecommand)
        
        #layout of TMTC section
        self.vbox_TMTC = QVBoxLayout()
        self.vbox_TMTC.addWidget(self.cmd_button)

        for topic in Model.dataModel.telemetryWindows:
            checkBox = QCheckBox(topic)
            checkBox.setFont(QtGui.QFont("Courier New", 14))
            checkBox.toggled.connect(lambda checked, _topic = topic: self.toggleTelemetry(checked, _topic)) #connect toggle behavior
            self.telemetryCheckBoxes[topic] = checkBox #store widget into dictionary
            self.vbox_TMTC.addWidget(checkBox) #add widget to layout

        #---connection section---
        #label for connection status
        self.connection_label = QLabel("not connected")
        self.connection_label.setFont(QtGui.QFont("Courier New", 14))
        self.connection_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.connection_label.setStyleSheet("background-color: red")

        #button to connect to satellite
        connection_button = QPushButton("connect")
        connection_button.setFont(QtGui.QFont("Courier New", 20))
        connection_button.clicked.connect(self.onConnectionButtonClicked)

        #layout
        connection_vbox = QVBoxLayout()
        connection_vbox.addWidget(self.connection_label)
        connection_vbox.addWidget(connection_button)

        #---body container---
        self.hbox = QHBoxLayout()
        self.hbox.addLayout(self.vbox_TMTC, stretch=1)
        self.hbox.addLayout(connection_vbox, stretch=1)
        self.hbox.addStretch(1)

        #---parent level---
        #self.setWindowIcon(QtGui.QIcon("nasa.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #label which contains the mission name
        self.mission_label = QLabel(f"Mission Name:\nSolarFloat4Vision")
        self.mission_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.mission_label.setFont(QtGui.QFont("Courier New", 16))
        self.mission_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        #layout is a vbox
        frame1 = QFrame()
        frame1.setFrameShape(QFrame.Shape.HLine)
        #frame1.setFrameShadow(QFrame.Shadow.Sunken)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(frame1)
        self.vbox.addWidget(self.mission_label)
        frame2 = QFrame()
        frame2.setFrameShape(QFrame.Shape.HLine)
        #frame2.setFrameShadow(QFrame.Shadow.Sunken)
        self.vbox.addWidget(frame2)
        self.vbox.addLayout(self.hbox)
        self.vbox.addStretch(1)

        self.setLayout(self.vbox) #set total layout for the main window
        

    #open the telecommand window
    def openTelecommand(self):
        self.cmd_window.show()
        

    #opens/closes the telemetry window for the topic AttitudeDetermination
    def toggleTelemetry(self, checked, topic):
        if checked:
            if topic not in self.telemetryWindows:
                telemetryWindow = TelemetryWindow(topic, self.onTelemetryWindowClosed)
                self.telemetryWindows[topic] = telemetryWindow
            telemetryWindow.show()

        else:
            self.telemetryWindows[topic].close() #close the window            
            del self.telemetryWindows[topic] #remove from the dictionary



    def onTelemetryWindowClosed(self, topic):
        self.telemetryCheckBoxes[topic].setChecked(False)
        
    def onConnectionButtonClicked(self):
        try:
            Controller.controller.connectSatellite()
            self.connection_label.setText("connected")
            self.connection_label.setStyleSheet("background-color: green")

        except Exception as e:
            print(e)
        
class TelemetryHandler():
    def __init__(self):
        self.mainWindow = window

    #handler for AttitudeControl
    def topicHandlerAC_TM(self, data):
        topic = "Attitude Control"
        try:
            unpacked = struct.unpack("d?QQdd", data)
            if topic in self.mainWindow.telemetryWindows:
                message = "time: {} | tmprd: {} | ctrprd: {} | yr: {} | ydr: {}".format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5])
                self.mainWindow.telemetryWindows[topic].updateTelemetry(message)
            
        except Exception as e:
            print(e)
            print(data)
            print(len(data))

    #handler for AttitudeDetermination
    def topicHandlerAD_TM(self, data):
        topic = "Attitude Determination"
        try:
            unpacked = struct.unpack("d?Qdddd", data)
            if topic in self.mainWindow.telemetryWindows:
                message = "time: {} | tmprd: {} | attTime: {} | roll: {} | pitch: {} | yaw: {}".format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5], unpacked[6])
                self.mainWindow.telemetryWindows[topic].updateTelemetry(message)

        except Exception as e:
            print(e)
            print(data)
            print(len(data)) 

    #handler for IMU
    def topicHandlerIMU_TM(self, data):
        topic = "IMU"
        try:
            unpacked = struct.unpack("d?QQddddddddddd", data)
            if topic in self.mainWindow.telemetryWindows:
                message = ("TIM={} | TMPRD={} | SNSPRD={} | SNSTIM={} | AX={} | AY={} | AZ={} | GX={} | GY={} | GZ={} | MX={} | MY={} | MZ={} | TEMP={} "
                           .format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5], unpacked[6], unpacked[7], unpacked[8], unpacked[9]
                                   , unpacked[10], unpacked[11], unpacked[12], unpacked[13], unpacked[14]))
                self.mainWindow.telemetryWindows[topic].updateTelemetry(message)
            
        except Exception as e:
            print(e)
            print(data)
            print(len(data))

    #handler for LightSensor
    def topicHandlerLS_TM(self, data):
        topic = "Light Sensor"
        try:
            unpacked = struct.unpack("d?QQd", data) #TODO: adjust, waiting for stm code
            if topic in self.mainWindow.telemetryWindows:
                message = ("TIM={} | TMPRD={} | SNSPRD={} | SNSTIM={}"
                           .format(unpacked[0], unpacked[2], unpacked[3], unpacked[4])) #TODO: adjust, waiting for stm code
                self.mainWindow.telemetryWindows[topic].updateTelemetry(message)
            
        except Exception as e:
            print(e)
            print(data)
            print(len(data))

    #handler for MagneticTorquer
    def topicHandlerMT_TM(self, data):
        topic = "Magnetic Torquer"
        try:
            unpacked = struct.unpack("d?Qd", data)
            if topic in self.mainWindow.telemetryWindows:
                message = ("TIM={} | TMPRD={} | IREF={}"
                           .format(unpacked[0], unpacked[2], unpacked[3]))
                self.mainWindow.telemetryWindows[topic].updateTelemetry(message)
            
        except Exception as e:
            print(e)
            print(data)
            print(len(data))

    #handler for Payload
    def topicHandlerPL_TM(self, data):
        topic = "Payload"
        try:
            unpacked = struct.unpack("d?Q", data) #TODO: adjust, waiting for stm code
            if topic in self.mainWindow.telemetryWindows:
                message = ("TIM={} | TMPRD={}"
                           .format(unpacked[0], unpacked[2])) #TODO: adjust, waiting for stm code
                self.mainWindow.telemetryWindows[topic].updateTelemetry(message)
            
        except Exception as e:
            print(e)
            print(data)
            print(len(data))

    #handler for Power
    def topicHandlerPW_TM(self, data):
        topic = "Power"
        try:
            unpacked = struct.unpack("d?QQdddddddd", data)
            if topic in self.mainWindow.telemetryWindows:
                message = ("TIM={} | TMPRD={} | SNSPRD={} | SNSTIM={} | BATV={} | BATI={} | BATPCT={} | SPLV={} | SPLI={} | SPRV={} | SPRI={}"
                           .format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5]))
                self.mainWindow.telemetryWindows[topic].updateTelemetry(message)
            
        except Exception as e:
            print(e)
            print(data)
            print(len(data))

    #handler for ReactionWheel
    def topicHandlerRW_TM(self, data):
        topic = "Reaction Wheel"
        try:
            unpacked = struct.unpack("d?QQddf", data)
            if topic in self.mainWindow.telemetryWindows:
                message = ("TIM={} | TMPRD={} | SNSPRD={} | SNSTIM={} | SPD={} | SPDREF={}"
                           .format(unpacked[0], unpacked[2], unpacked[3], unpacked[4], unpacked[5]))
                self.mainWindow.telemetryWindows[topic].updateTelemetry(message)
            
        except Exception as e:
            print(e)
            print(data)
            print(len(data))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QtGui.QFont("Courier New"))
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
