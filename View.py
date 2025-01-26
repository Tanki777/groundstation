import sys
import struct
import time
from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTextBrowser, QLineEdit, QLabel
                             , QCheckBox, QFrame, QSizePolicy, QPlainTextEdit, QScrollArea)
import Model
import Controller
import Compass
import subprocess
import faulthandler
faulthandler.enable()

class TelecommandWindow(QWidget):
    #initialization. called when the object is created
    def __init__(self, _mainWindow):
        super().__init__()

        self.title = "Telecommand"
        self.top = 100
        self.left = 100
        self.width = 300
        self.height = 250
        self.mainWindow = _mainWindow

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
        #magically limits the max visible items to 10
        self.tc_comboBox.setStyleSheet("combobox-popup: 0;")

        for tc in self.mainWindow.dataModel.telecommands:
            self.tc_comboBox.addItem("{} | {}".format(tc.word, tc.description))

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
        self.sendTc_button = QPushButton("SEND")
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
        hour = time.localtime().tm_hour
        min = time.localtime().tm_min
        sec = time.localtime().tm_sec
        sentTC = self.mainWindow.dataModel.telecommands[self.tc_comboBox.currentIndex()] #gets the corresponding telecommand via index
        parameter = self.param_lineEdit.text()
        if parameter == "": parameter = "0"

        #add to telecommand log
        self.tcLog_textBrowser.append("{}:{}:{} | {} | {}".format(hour, min, sec, sentTC.word, parameter))
        
        #send telecommand to satellite
        telecommand = struct.pack("HQHd",sentTC.id,0,0,float(parameter))
        self.mainWindow.controller.telecommandTopic.publish(telecommand)

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
        #self.log_textfield.setMaximumBlockCount(2000) #what is this for?
        
        layout = QVBoxLayout()
        layout.addWidget(self.log_textfield)

        self.setLayout(layout)

    def updateTelemetry(self, message: str):
        self.log_textfield.appendPlainText(message) #add message
        #self.log_textfield.verticalScrollBar().setValue(self.log_textfield.verticalScrollBar().maximum()) #auto scroll
        #self.log_textfield.update() #update
    
    def closeEvent(self, a0):
        self.onCloseCallback(self.title)
        return super().closeEvent(a0)
    
class MainWindow(QWidget):

    #initialization. called when the object is created
    def __init__(self):
        super().__init__()

        self.controller = Controller.Controller()
        #self.controller.start() #is this needed???
        self.dataModel = Model.DataModel()

        self.title = "Ground Station"
        self.top = 100
        self.left = 100
        self.width = 300
        self.height = 250

        self.cmd_window = TelecommandWindow(self)
        #self.tmAD_window = TelemetryWindow("Attitude Determination", self.onTelemetryWindowClosed)

        #stores widgets
        self.telemetryWindows = {}
        self.telemetryCheckBoxes = {}

        #stores signals
        self.telemetrySignals = {}
        self.telemetrySignals["Attitude Control"] = self.controller.tmAC
        self.telemetrySignals["Attitude Determination"] = self.controller.tmAD
        self.telemetrySignals["IMU"] = self.controller.tmIMU
        self.telemetrySignals["Light Sensor"] = self.controller.tmLS
        self.telemetrySignals["Magnetic Torquer"] = self.controller.tmMT
        self.telemetrySignals["Payload"] = self.controller.tmPL
        self.telemetrySignals["Power"] = self.controller.tmPW
        self.telemetrySignals["Reaction Wheel"] = self.controller.tmRW

        self.InitWindow()

    #initialize the entry window
    def InitWindow(self):
        #---TMTC section---
        #button which opens the telecommand window
        self.cmd_button = QPushButton("Telecommand\nSystem")
        self.cmd_button.setFont(QtGui.QFont("Courier New", 20))
        #self.cmd_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.cmd_button.clicked.connect(self.openTelecommand)
        
        #layout of TMTC section
        self.vbox_TMTC = QVBoxLayout()
        self.vbox_TMTC.addWidget(self.cmd_button)

        for topic in self.dataModel.telemetryWindows:
            checkBox = QCheckBox(topic)
            checkBox.setFont(QtGui.QFont("Courier New", 14))
            checkBox.toggled.connect(lambda checked, _topic = topic: self.toggleTelemetry(checked, _topic)) #connect toggle behavior
            self.telemetryCheckBoxes[topic] = checkBox #store widget into dictionary
            self.vbox_TMTC.addWidget(checkBox) #add widget to layout

        #---connection section---
        #label for connection status
        self.connection_label = QLabel("not connected")
        self.connection_label.setFont(QtGui.QFont("Courier New", 14))
        #self.connection_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.connection_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.connection_label.setStyleSheet("background-color: red")

        #button to connect to satellite
        connection_button = QPushButton("connect")
        connection_button.setFont(QtGui.QFont("Courier New", 20))
        #connection_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        connection_button.clicked.connect(self.onConnectionButtonClicked)

        #layout
        connection_vbox = QVBoxLayout()
        connection_vbox.addWidget(self.connection_label)
        connection_vbox.addWidget(connection_button)

        #---live orientation section---
        #compass widget
        self.compass = Compass.CompassWidget()
        self.controller.tmHeading.connect(self.compass.set_heading)

        #layout
        compass_vbox = QVBoxLayout()
        compass_vbox.addWidget(self.compass)

        #---body container---
        self.hbox = QHBoxLayout()
        self.hbox.addLayout(self.vbox_TMTC, stretch=1)
        self.hbox.addLayout(connection_vbox, stretch=1)
        self.hbox.addLayout(compass_vbox, stretch=1)

        #---parent level---
        #self.setWindowIcon(QtGui.QIcon("nasa.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #label which contains the mission name
        self.mission_label = QLabel(f"Mission Name:\nSolarFloat4Vision")
        self.mission_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.mission_label.setFont(QtGui.QFont("Courier New", 16))
        self.mission_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        #image section
        #scroll area
        self.imageScrollArea = QScrollArea()
        self.imageScrollArea.setWidgetResizable(True)

        #container for images
        self.imageContainer = QWidget()
        self.imageHbox = QHBoxLayout()
        self.imageContainer.setLayout(self.imageHbox)

        #add container to scroll area
        self.imageScrollArea.setWidget(self.imageContainer)

        #connect controller signal to handler
        self.controller.payloadData.connect(self.addImage)

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
        self.vbox.addWidget(self.imageScrollArea)
        #self.vbox.addStretch(1)

        self.setLayout(self.vbox) #set total layout for the main window
        

    #open the telecommand window
    def openTelecommand(self):
        self.cmd_window.show()
        

    #opens/closes the telemetry window for the topic AttitudeDetermination
    def toggleTelemetry(self, checked, topic):
        if checked:
            if topic not in self.telemetryWindows:
                telemetryWindow = TelemetryWindow(topic, self.onTelemetryWindowClosed)
                self.telemetrySignals[topic].connect(telemetryWindow.updateTelemetry)
                self.telemetryWindows[topic] = telemetryWindow
            telemetryWindow.show()

        else:
            self.telemetryWindows[topic].close() #close the window            
            del self.telemetryWindows[topic] #remove from the dictionary



    def onTelemetryWindowClosed(self, topic):
        self.telemetryCheckBoxes[topic].setChecked(False)
        
    def onConnectionButtonClicked(self):
        try:
            self.controller.run()
            self.connection_label.setText("connected")
            self.connection_label.setStyleSheet("background-color: green")

        except Exception as e:
            print(e)

    def addImage(self, qimage):
        #convert QImage to QPixmap
        pixmap = QtGui.QPixmap.fromImage(qimage)

        #create image label
        imageLabel = QLabel()
        imageLabel.setPixmap(pixmap)
        #imageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        imageLabel.setScaledContents(True) #scale to fit within label dimensions
        imageLabel.setFixedSize(600, 400)
        
        #add image label to container
        self.imageHbox.addWidget(imageLabel)
        
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QtGui.QFont("Courier New"))

    window = MainWindow()

    #telemetryHandler = TelemetryHandler(window)
    
    window.showMaximized()
    
    sys.exit(app.exec())



