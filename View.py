from PyQt6 import QtGui, QtCore
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QTextBrowser, QLineEdit, QLabel, QRadioButton)
import Model
import sys

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

        #show telecommand window
        self.show()


    #send the telecommand
    def sendTelecommand(self):
        #TODO
        print("DEBUG: sent tc: {}\n".format(self.tc_comboBox.currentText()))

class MainWindow(QWidget):

    #initialization. called when the object is created
    def __init__(self):
        super().__init__()

        self.title = "Ground Station"
        self.top = 100
        self.left = 100
        self.width = 300
        self.height = 250

        self.InitWindow()

        self.cmd_window = None
        self.tmAD_window = None

        #states of telemtry windows
        self.tmAD_opened = False

    #initialize the entry window
    def InitWindow(self):
        #self.setWindowIcon(QtGui.QIcon("nasa.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #label which contains the mission name
        self.mission_label = QLabel(f"Mission Name:\nSolarFloat4Vision")
        self.mission_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.mission_label.setFont(QtGui.QFont("Courier New", 16))

        #button which opens the telecommand window
        self.cmd_button = QPushButton("Telecommand\nSystem")
        self.cmd_button.setFont(QtGui.QFont("Courier New", 20))
        self.cmd_button.clicked.connect(self.openTelecommand)

        #radio button which opens/closes the telemetry window for topic AttitudeDetermination
        self.tmAD_radio = QRadioButton("Attitude Determination")
        self.tmAD_radio.setFont(QtGui.QFont("Courier New", 14))
        self.tmAD_radio.clicked.connect(self.toggleTmAD)

        #layout of the entry window
        vbox = QVBoxLayout()
        vbox.addWidget(self.mission_label)
        vbox.addWidget(self.cmd_button)
        vbox.addWidget(self.tmAD_radio)
        self.setLayout(vbox)

        self.showMaximized()

    #open the telecommand window
    def openTelecommand(self):
        self.cmd_window = TelecommandWindow()
        self.cmd_window.show()

    #opens/closes the telemetry window for the topic AttitudeDetermination
    def toggleTmAD(self):
        if self.tmAD_opened:
            self.tmAD_window.close()
            self.tmAD_opened = false
        else:
            self.tmAD_window.show()
            self.tmAD_opened = true


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QtGui.QFont("Courier New"))
    window = MainWindow()
    sys.exit(app.exec())
