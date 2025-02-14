import sys
import struct
import time
import os
from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTextBrowser, QLineEdit, QLabel
                             , QCheckBox, QFrame, QSizePolicy, QPlainTextEdit, QScrollArea, QGridLayout, QTextEdit)
import pyqtgraph as pg
import Model
import Controller
import Compass
import subprocess
import faulthandler
faulthandler.enable()

app_icon_path = os.path.abspath("assets/chart.png")
start_time = time.time()


def getColorByIndex(index):
    if index == 0: return "r" #red
    if index == 1: return "b" #blue
    if index == 2: return "g" #green?
    if index == 3: return "y" #yellow?

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
        self.tc_comboBox.setEditable(True)
        self.tc_comboBox.setInsertPolicy(self.tc_comboBox.InsertPolicy.NoInsert) #prevents adding new items
        self.tc_comboBox.completer().setCompletionMode(self.tc_comboBox.completer().CompletionMode.PopupCompletion) #shows suggestions

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
        self.mainWindow.controller.tmTCFB.connect(self.updateTelecommandFeedback) #connect to signal from controller

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

    def updateTelecommandFeedback(self, data):
        hour = time.localtime().tm_hour
        min = time.localtime().tm_min
        sec = time.localtime().tm_sec
        self.tcFeedbackLog_textBrowser.append("{}:{}:{} {}".format(hour, min, sec, data))

class TelemetryWindow(QWidget):
    #initialization. called when the object is created
    def __init__(self, _mainWindow):
        super().__init__()
        self.mainWindow = _mainWindow
        #self.title = title
        #self.onCloseCallback = onCloseCallback
        #self.top = 0
        #self.left = 0
        #self.width = 1000
        #self.height = 80

        self.InitWindow()

    def InitWindow(self):
        #self.setGeometry(self.left, self.top, self.width, self.height)
        #self.resize(1000, 80)

        #stores widgets
        self.telemetryWidgets = {}
        self.telemetryCheckBoxes = {}
        self.tm_frames = {}
        self.graphWidgets = {}
        self.graph_frames = {}

        #stores signals
        self.telemetrySignals = {}
        self.telemetrySignals["Attitude Control"] = self.mainWindow.controller.tmAC
        self.telemetrySignals["Attitude Determination"] = self.mainWindow.controller.tmAD
        self.telemetrySignals["IMU"] = self.mainWindow.controller.tmIMU
        self.telemetrySignals["Light Sensor"] = self.mainWindow.controller.tmLS
        self.telemetrySignals["Magnetic Torquer"] = self.mainWindow.controller.tmMT
        self.telemetrySignals["Payload"] = self.mainWindow.controller.tmPL
        self.telemetrySignals["Power"] = self.mainWindow.controller.tmPW
        self.telemetrySignals["Reaction Wheel"] = self.mainWindow.controller.tmRW
        self.telemetrySignals["Error Messages"] = self.mainWindow.controller.tmERR
        #self.telemetrySignals["Debug"] = self.mainWindow.controller.tmDebug

        self.plotSignals = {}
        self.plotSignals["Attitude Control"] = self.mainWindow.controller.plotAC
        self.plotSignals["Attitude Determination"] = self.mainWindow.controller.plotAD
        self.plotSignals["IMU"] = self.mainWindow.controller.plotIMU
        self.plotSignals["Light Sensor"] = self.mainWindow.controller.plotLS
        self.plotSignals["Magnetic Torquer"] = self.mainWindow.controller.plotMT
        self.plotSignals["Payload"] = self.mainWindow.controller.plotPL
        self.plotSignals["Power"] = self.mainWindow.controller.plotPW
        self.plotSignals["Reaction Wheel"] = self.mainWindow.controller.plotRW
        self.plotSignals["Error Messages"] = self.mainWindow.controller.plotPW

        self.setWindowTitle("Telemetry")
        self.setGeometry(0,0,1500,900)

        #selection section
        self.selection_hbox1 = QHBoxLayout()
        self.selection_hbox2 = QHBoxLayout()

        i = 0
        for tm in self.mainWindow.dataModel.telemetry:
            checkBox = QCheckBox(tm.topic)
            checkBox.setFont(QtGui.QFont("Courier New", 11))
            checkBox.toggled.connect(lambda checked, _tm = tm: self.toggleTelemetry(checked, _tm)) #connect toggle behavior
            self.telemetryCheckBoxes[tm.topic] = checkBox #store widget into dictionary

            if i < 5:
                self.selection_hbox1.addWidget(checkBox) #add widget to layout
            else:
                self.selection_hbox2.addWidget(checkBox) #add widget to layout
            

            i = i + 1

        #parent layout
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.selection_hbox1)
        self.vbox.addLayout(self.selection_hbox2)
        frame1 = QFrame()
        frame1.setFrameShape(QFrame.Shape.HLine)
        #frame1.setFrameShadow(QFrame.Shadow.Sunken)

        #scroll area for telemetry
        self.tm_scrollarea = QScrollArea()
        self.tm_scrollarea.setWidgetResizable(True)
        self.tm_scroll_vbox = QVBoxLayout()
        
        self.tm_container = QWidget()
        self.tm_container.setLayout(self.tm_scroll_vbox)

        self.tm_scrollarea.setWidget(self.tm_container)

        #scroll area for graphs
        self.graph_scrollarea = QScrollArea()
        self.graph_scrollarea.setWidgetResizable(True)
        self.graph_scroll_vbox = QVBoxLayout()

        self.graph_container = QWidget()
        self.graph_container.setLayout(self.graph_scroll_vbox)

        self.graph_scrollarea.setWidget(self.graph_container)

        self.scrollWrapper_hbox = QHBoxLayout()
        self.scrollWrapper_hbox.addWidget(self.tm_scrollarea,3)
        self.scrollWrapper_hbox.addWidget(self.graph_scrollarea,2)

        self.vbox.addWidget(frame1)
        self.vbox.addLayout(self.scrollWrapper_hbox)
        #self.vbox.addStretch(1)

        #self.log_textfield = QPlainTextEdit()
        #self.log_textfield.setReadOnly(True)
        #self.log_textfield.setMaximumBlockCount(2000) #what is this for?
        
        #layout = QVBoxLayout()
        #layout.addWidget(self.log_textfield)

        self.setLayout(self.vbox)

    #opens/closes the telemetry window for the topic AttitudeDetermination
    def toggleTelemetry(self, checked, tm):
        if checked:
            #---telemetry widget---#
            tm_widget = TelemetryWidget(self.mainWindow.dataModel, tm)
            self.telemetrySignals[tm.topic].connect(tm_widget.updateTelemetry)
            self.telemetryWidgets[tm.topic] = tm_widget

            frame1 = QFrame()
            frame1.setFrameShape(QFrame.Shape.HLine)
            #frame1.setFrameShadow(QFrame.Shadow.Sunken)
            self.tm_frames[tm.topic] = frame1

            #---graph widget---#
            graph_widget = GraphWidget(self.mainWindow.dataModel,tm.topic)
            self.graphWidgets[tm.topic] = graph_widget
            #connect signal from controller
            self.plotSignals[tm.topic].connect(graph_widget.updateData)
            tm_widget.graph_button.clicked.connect(graph_widget.onGraphClicked)

            
                
            self.tm_scroll_vbox.addWidget(tm_widget)
            self.tm_scroll_vbox.addWidget(frame1)

            self.graph_scroll_vbox.addWidget(graph_widget)
            #self.graph_scroll_vbox.addWidget(frame2)

            
        else:
            self.tm_scroll_vbox.removeWidget(self.telemetryWidgets[tm.topic])
            self.tm_scroll_vbox.removeWidget(self.tm_frames[tm.topic])  
            del self.telemetryWidgets[tm.topic] #remove from the dictionary
            del self.tm_frames[tm.topic]

            self.graph_scroll_vbox.removeWidget(self.graphWidgets[tm.topic])
            self.graph_scroll_vbox.removeWidget(self.graph_frames[tm.topic])
            del self.graphWidgets[tm.topic]
            del self.graph_frames[tm.topic]
            #self.telemetryCheckBoxes[topic].setChecked(False)


    
class TelemetryWidget(QWidget):
    def __init__(self, _dataModel, _tm):
        super().__init__()
        self.dataModel = _dataModel
        self.telemetry = _tm
        self.initWidget()

    def initWidget(self):
        #topic display
        topic_label = QLabel(self.telemetry.topic)

        #telemetry log
        self.log_textfield = QPlainTextEdit()
        self.log_textfield.setReadOnly(True)
        self.log_textfield.setMaximumBlockCount(2000) #what is this for?

        #telemetry label for siplaying names of variables
        values_label = QLabel(self.telemetry.format)

        #vertical layout
        vbox = QVBoxLayout()
        vbox.addWidget(topic_label)
        vbox.addWidget(self.log_textfield)
        vbox.addWidget(values_label)

        #button for graph
        self.graph_button = QPushButton()
        self.graph_button.setFixedSize(40,40)
        self.graph_button.setIcon(QtGui.QIcon("assets/chart.png"))
        self.graph_button.setIconSize(QtCore.QSize(30,30))

        self.nobutton = QPushButton()
        self.nobutton.setStyleSheet("""
            QPushButton {
                border-image: url(assets/chart.png);
                border-radius: 15px; /* Rounded corners */
                background-color: #0078D7; /* Light blue background */
                color: black; /* Text color */
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border: 2px solid #005a9e; /* Border color */
            }
            QPushButton:hover {
                background-color: #005a9e; /* Darker blue on hover */
            }
            QPushButton:pressed {
                background-color: #003f7f; /* Even darker on press */
            }
        """)
        
        
        
        #TODO: add behavior

        

        #parent layout
        layout = QHBoxLayout()
        layout.addLayout(vbox,5)
        layout.addWidget(self.graph_button,1)
        self.setLayout(layout)

    def updateTelemetry(self, message: str):
        self.log_textfield.appendPlainText(message) #add message
        #self.log_textfield.verticalScrollBar().setValue(self.log_textfield.verticalScrollBar().maximum()) #auto scroll
        #self.log_textfield.update() #update

class NoScrollZoomPlotWidget(pg.PlotWidget):
        def __init__(self):
            super().__init__()

        def wheelEvent(self, event):
            self.parentWidget().wheelEvent(event)

class GraphWidget(QWidget):
    def __init__(self, _dataModel, _topic):
        super().__init__()
        self.dataModel = _dataModel
        self.topic = _topic
        self.initWidget()

    def initWidget(self):
        #parent layout
        self.vbox = QVBoxLayout()

        frame2 = QFrame()
        frame2.setFrameShape(QFrame.Shape.HLine)
        #self.graph_frames[tm.topic] = frame2

        topic_label = QLabel(self.topic)
        self.vbox.addWidget(frame2)
        self.vbox.addWidget(topic_label)

        self.figureCount = 0
        self.dataCount = []
        self.plotDataItems = []

        #dictionary to store figures by title
        figure = {}

        self.x_data_inner = list(range(-100,0))
        self.x_data_outer = []
        self.y_data_inner = [0] * 100
        self.y_data_outer = []

        for plot in self.dataModel.plots:

            #only plot the corresponding topic
            if plot.topic is self.topic:

                #if the figure for a topic was not created yet, create one
                if plot.title not in figure:
                    plot_widget = NoScrollZoomPlotWidget()
                    plot_item = plot_widget.plotItem
                    plot_widget.setFixedHeight(150)

                    self.x_data_outer.append(self.x_data_inner.copy())
                    self.y_data_outer.append(self.y_data_inner.copy())
                    
                    plot_item.addLegend(offset=(1,1))
                    plot_data_item = plot_item.plot(self.x_data_inner, self.y_data_inner, pen=getColorByIndex(0),name=plot.legend)
                    plot_item.setTitle(plot.title)
                    #plot_item.setLabel("bottom","time [s]")
                    plot_item.setLabel("left",plot.y_label)
                    
                    #plot_widget.addItem(plot_item)

                    self.plotDataItems.append(plot_data_item)

                    #add figure to dictionary
                    figure[plot.title] = plot_item

                    #add plot widget to the layout
                    self.vbox.addWidget(plot_widget)

                    self.figureCount = self.figureCount + 1
                    self.dataCount.append(1)

                #if the figure for a topic is already created, add the plot to the existing figure
                else:
                    plot_data_item = figure[plot.title].plot(self.x_data_inner, self.y_data_inner, pen=getColorByIndex(self.dataCount[self.figureCount-1]),name=plot.legend)
                    self.dataCount[self.figureCount - 1] = self.dataCount[self.figureCount - 1] + 1
                    self.plotDataItems.append(plot_data_item)

                    self.x_data_outer.append(self.x_data_inner.copy())
                    self.y_data_outer.append(self.y_data_inner.copy())

        self.setLayout(self.vbox)

        self.hide()

    def onGraphClicked(self):
        if(self.isHidden()):
            self.show()

        else:
            self.hide()

    def updateData(self, data):
        dataIndex = 0
        
        for i in range(self.vbox.count() - 1):
            #print("DEBUG: i {}".format(i))
            item = self.vbox.itemAt(i + 1)
            widget = item.widget()

            for k in range(self.dataCount[i]):
                #print("DEBUG: k {}".format(k))
                self.x_data_outer[dataIndex].pop(0)
                self.x_data_outer[dataIndex].append(time.time() - start_time)

                self.y_data_outer[dataIndex].pop(0)
                #self.y_data.pop(0) #removes oldest value
                #print("DEBUG: dataindex {}".format(dataIndex))
                self.y_data_outer[dataIndex].append(data[dataIndex])
                #self.y_data.append(data[dataIndex])
                #print("DEBUG: yaw {}".format(data[4]))
                self.plotDataItems[dataIndex].setData(self.x_data_outer[dataIndex], self.y_data_outer[dataIndex])
                dataIndex = dataIndex + 1
                    


        
    
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

        #self.setGeometry(self.left, self.top, self.width, self.height)

        self.cmd_window = TelecommandWindow(self)
        self.tm_window = TelemetryWindow(self)
        #self.tmAD_window = TelemetryWindow("Attitude Determination", self.onTelemetryWindowClosed)

        self.connected = False
        self.setWindowIcon(QtGui.QIcon(app_icon_path))

        self.InitWindow()


    #initialize the entry window
    def InitWindow(self):
        #---TMTC section---
        #button which opens the telecommand window
        self.cmd_button = QPushButton("Telecommand\nSystem")
        self.cmd_button.setFont(QtGui.QFont("Courier New", 20))
        #self.cmd_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.cmd_button.clicked.connect(self.openTelecommand)

        #button which opens the telemetry window
        self.tm_button = QPushButton("Telemetry")
        self.tm_button.setFont(QtGui.QFont("Courier New", 20))
        self.tm_button.clicked.connect(self.openTelemetry)
        
        #layout of TMTC section
        self.vbox_TMTC = QVBoxLayout()
        self.vbox_TMTC.addWidget(self.cmd_button)
        self.vbox_TMTC.addWidget(self.tm_button)
       

        #---connection section---
        #label for connection status
        self.connection_label = QLabel("not connected")
        self.connection_label.setFont(QtGui.QFont("Courier New", 14))
        
        #self.connection_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        #self.connection_label.setStyleSheet("background-color: red")
        self.connection_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

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
        #self.vbox.addWidget(self.imageScrollArea)
        #self.vbox.addStretch(1)

        self.setLayout(self.vbox) #set total layout for the main window

        #test
        #img1 = QtGui.QImage("testImage10")
        #self.addImage(img1)
        #img2 = QtGui.QImage("testImage12")
        #self.addImage(img2)
        #img3 = QtGui.QImage("testImage13")
        #self.addImage(img3)
        #img4 = QtGui.QImage("testImage15")
        #self.addImage(img4)
        #img5 = QtGui.QImage("testImage19")
        #self.addImage(img5)
        

    #open the telecommand window
    def openTelecommand(self):
        self.cmd_window.show()

    #open the telemetry window
    def openTelemetry(self):
        self.tm_window.show()
        
    def onConnectionButtonClicked(self):
        try:    
            if not self.connected:
                self.controller.start()
                self.connection_label.setText("connected")
                #self.connection_label.setStyleSheet("background-color: green")
                self.connected = True
            
            else:
                self.controller.reconnectStm()

        except Exception as e:
            print(e)
    
    def addImage(self, qimage):
        #print("addImage...\n")
        #convert QImage to QPixmap
        pixmap = QtGui.QPixmap.fromImage(qimage)
        #print("pixmap...\n")

        #create image label
        imageLabel = QLabel()
        imageLabel.setPixmap(pixmap)
        imageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        imageLabel.setScaledContents(True) #scale to fit within label dimensions
        imageLabel.setFixedSize(600, 400)
        
        #create image description
        descrLabel = QLabel("Object {}".format(self.imageHbox.count() + 1))
        descrLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        #create vbox for image and description
        vbox = QVBoxLayout()
        vbox.addWidget(descrLabel)
        vbox.addWidget(imageLabel)

        #add image label to container
        #self.imageHbox.addWidget(imageLabel)
        self.imageHbox.addLayout(vbox)
        #print("image added...\n")
        
        

if __name__ == '__main__':

    
    app = QApplication(sys.argv)
    app.setFont(QtGui.QFont("Courier New"))
    app.setWindowIcon(QtGui.QIcon(app_icon_path))

    window = MainWindow()
    #window.setWindowIcon(QtGui.QIcon(app_icon_path))

    #telemetryHandler = TelemetryHandler(window)
    print(app_icon_path)
    window.show()
    
    sys.exit(app.exec())



