from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys
import serial.tools.list_ports
import serial
import threading

class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.setGeometry(0, 0, 750, 600)
        
        self.setWindowTitle("Tendon Controller GUI")

        # main window vertical layout
        self.mainVLayout = QVBoxLayout()
        
    
        # add serial layout
        self.add_serial_box()

        # add motor dial and LCD boxes
        self.add_motor_dial_box()
        
        # attach callback for changing dial
        self.attach_control_callbacks()
        
        # controlling motor sections
        self.add_controls_box()
        
        # serial message boxes
        # self.add_serial_message_box()
        
        # create thread for receiving serial
        # self.serialThread = threading.Thread(target=self.serial_recieve_thread,daemon=True)
        # self.serialThread = None
        
        # default disable controls 
        self.enable_controls(False)

        
        # set main layout
        self.setLayout(self.mainVLayout)



    def serial_recieve_thread(self):

        while self.serial_dev_connected:
            data = self.serial_dev.readline().decode()
            
            self.serialTextBox.append(data)
            self.serialTextBox.ensureCursorVisible()
            # self.serialTextBox.update()
        
        
            
    def add_serial_message_box(self):
        # serial message boxes
        serialMsgBox = QGroupBox("Serial Output")
        serialHLay = QHBoxLayout()
        self.serialTextBox = QTextEdit()
        self.serialTextBox.setReadOnly(True)
        self.serialTextBox.setMinimumHeight(325)
        
        
        serialHLay.addWidget(self.serialTextBox)
        serialMsgBox.setLayout(serialHLay)
        self.mainVLayout.addWidget(serialMsgBox)
        
        
        
        
        
    def add_controls_box(self):
        # controlling motor sections
        controlBox = QGroupBox("Controls")
        controlLay = QHBoxLayout()
        
        allMotorBox = QGroupBox("All Motors")
        allMotorVlay = QVBoxLayout()
        
        # create dial
        self.allMotorDial = QDial()
        self.allMotorDial.setRange(-360,360)
        # self.allMotorDial.setMinimumSize(100,100)
        # attach callback
        self.allMotorDial.valueChanged.connect(lambda: self.all_motor_dial_callback())
        allMotorVlay.addWidget(self.allMotorDial)
        
        # spinner
        self.allMotorSpinner = QSpinBox()
        self.allMotorSpinner.setSuffix(" deg")
        self.allMotorSpinner.setRange(-360,360)
        allMotorVlay.addWidget(self.allMotorSpinner)
        self.allMotorSpinner.valueChanged.connect(lambda: self.allMotorDial.setValue(self.allMotorSpinner.value()))
        
        # invert button
        self.allMotorInvertAngleButton = QPushButton("Invert")
        
        allMotorVlay.addWidget(self.allMotorInvertAngleButton)
        
        # add or override value
        self.allMotorOverrideAngleCheckbox = QCheckBox("Add to individual angles")
        self.allMotorOverrideAngleCheckbox.stateChanged.connect(lambda: self.add_to_individual_angle_checkbox())
        allMotorVlay.addWidget(self.allMotorOverrideAngleCheckbox)
        
        allMotorBox.setLayout(allMotorVlay)
        controlLay.addWidget(allMotorBox)
        
        # jogGrid = QGridLayout()
        # # start value
        # jogGrid.addWidget(QLabel("Start Angle"),0,0)
        # self.startBox = QDoubleSpinBox()
        # self.startBox.setSuffix(" deg")
        # self.startBox.setDecimals(1)
        # jogGrid.addWidget(self.startBox,0,1)
        
        # # end value
        # jogGrid.addWidget(QLabel("End Angle"),1,0)
        # self.endBox = QDoubleSpinBox()
        # self.endBox.setSuffix(" deg")
        # self.endBox.setDecimals(1)
        # jogGrid.addWidget(self.endBox,1,1)
        
        # # increment value
        # jogGrid.addWidget(QLabel("Increment"),0,3)
        # self.incrementBox = QDoubleSpinBox()
        # self.incrementBox.setSuffix(" deg")
        # self.incrementBox.setDecimals(1)
        # jogGrid.addWidget(self.incrementBox,0,4)
        
        # # time between job value
        # jogGrid.addWidget(QLabel("Time Between"),1,3)
        # self.timeBox = QSpinBox()
        # self.timeBox.setSuffix(" sec")
        # jogGrid.addWidget(self.timeBox,1,4)
        
        # # start run button
        # self.startJogButton = QPushButton("Start")

        # jogGrid.addWidget(self.startJogButton,0,2)
        
        # # formatting to make it look pretty
        # jogGrid.setColumnStretch(1,1)
        # jogGrid.setColumnStretch(2,1)
        # jogGrid.setColumnStretch(4,1)
        
        # jogBox = QGroupBox("Jog Settings")
        # jogBox.setLayout(jogGrid)
        # controlLay.addWidget(jogBox)
        
        
        # serial stuff
        # serialMsgBox = QGroupBox("Serial Output")
        # serialHLay = QHBoxLayout()
        # self.serialTextBox = QTextEdit()
        # self.serialTextBox.setReadOnly(True)
        # self.serialTextBox.setMinimumHeight(325)
        # self.serialTextBox.setMinimumWidth(100)
        
        
        # serialHLay.addWidget(self.serialTextBox)
        # serialMsgBox.setLayout(serialHLay)
        # controlLay.addWidget(serialMsgBox)

        # add angle run through box
        angleInsrBox = QGroupBox("Instructions")
        angleLay = QHBoxLayout()
        self.anglesText = QTableWidget(12,6)
        angleLay.addWidget(self.anglesText)
        
        
        vLay = QVBoxLayout()
        self.startButton = QPushButton("Start")
        self.startButton.pressed.connect(self.start_instructions_callback)
        vLay.addWidget(self.startButton)
        
        self.addRow = QPushButton("Add")
        vLay.addWidget(self.addRow)

        self.deleteRow = QPushButton("Delete")
        vLay.addWidget(self.deleteRow)
                
        self.timeDelaySpinner = QDoubleSpinBox()
        self.timeDelaySpinner.setSuffix(" s")
        
        vLay.addWidget(self.timeDelaySpinner)
        angleLay.addLayout(vLay)
        
        angleInsrBox.setLayout(angleLay)
        
        controlLay.addWidget(angleInsrBox)        
        

        controlBox.setLayout(controlLay)
        
        self.mainVLayout.addWidget(controlBox)


    def start_instructions_callback(self):
        ...

    def add_serial_box(self):
        # horizontal layout for port combo box and button
        serialLayout = QHBoxLayout()
        
        # layout for serial label and combo box
        self.searchPorts = QPushButton("Search")
        self.searchPorts.setFixedWidth(65)
        self.searchPorts.pressed.connect(self.find_serial_ports)
        serialLayout.addWidget(self.searchPorts)
    

        # create combobox
        self.portComboBox = QComboBox()
        serialLayout.addWidget(self.portComboBox)
    

        # create connect button
        self.connectButton = QPushButton("Connect")
        self.connectButton.setMaximumWidth(90)
        self.connectButton.pressed.connect(self.connect_serial_device)
        
        # vars for keeping serial device
        self.serial_dev = None
        self.serial_dev_connected = False
        
        

        serialLayout.addWidget(self.connectButton)
        
        
        
        serialBox = QGroupBox("Serial")
        serialBox.setLayout(serialLayout)
        serialBox.setMaximumHeight(90)
        
        
        self.mainVLayout.addWidget(serialBox)
    
    
    
    def add_motor_dial_box(self):
        # dials
        self.motorDials = [QDial(), QDial(), QDial(), QDial(), QDial(), QDial()]
        
        
        # spinner boxes
        self.motorSpinners = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
        ]
        
        self.motorSlider = [
            QSlider(Qt.Orientation.Horizontal),
            QSlider(Qt.Orientation.Horizontal),
            QSlider(Qt.Orientation.Horizontal),
            QSlider(Qt.Orientation.Horizontal),
            QSlider(Qt.Orientation.Horizontal),
            QSlider(Qt.Orientation.Horizontal)

        ]
        
        self.copyAngleValues = [0,0,0,0,0,0]
        
        # invert angle buttons
        self.invertAngleButton = [
            QPushButton("Invert"),
            QPushButton("Invert"),
            QPushButton("Invert"),
            QPushButton("Invert"),
            QPushButton("Invert"),
            QPushButton("Invert"),
        ]

        # for dial and lcd segment
        middleLayout = QHBoxLayout()

        # stacking dial and segment layout
        motorVertLayouts = [
            QVBoxLayout(),
            QVBoxLayout(),
            QVBoxLayout(),
            QVBoxLayout(),
            QVBoxLayout(),
            QVBoxLayout(),
        ]
        
        # making boxes for dial and segment layout
        motorBoxes = [
            QGroupBox(),
            QGroupBox(),
            QGroupBox(),
            QGroupBox(),
            QGroupBox(),
            QGroupBox(),
        ]
        
        self.minMotorSpinner = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox()
        ]
        
        self.maxMotorSpinner = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox()
        ]
        
        self.goMinButton = [
            QPushButton("Min"),
            QPushButton("Min"),
            QPushButton("Min"),
            QPushButton("Min"),
            QPushButton("Min"),
            QPushButton("Min")
        ]
        
        self.goMaxButton = [
            QPushButton("Max"),
            QPushButton("Max"),
            QPushButton("Max"),
            QPushButton("Max"),
            QPushButton("Max"),
            QPushButton("Max")
        ]

        middleHBox = QGroupBox()

        # add dials and its segment to vertical
        for i in range(0, 6):
            # make notches visible and not visible
            # self.motorDials[i].setNotchesVisible(True)
            # self.motorDials[i].setMinimumSize(100,100)
    
            min = -180
            max = 180
            # config spinners
            self.motorSpinners[i].setSuffix(" deg")
            self.motorSpinners[i].setRange(min,max)
            self.motorSpinners[i].setSingleStep(2)
            
            self.motorSlider[i].setRange(min,max)
            # self.mot
            # set ranges of dials
            self.motorDials[i].setRange(min, max)

            # make width
            motorBoxes[i].setTitle("Motor: " + str(i))
    
            # motorVertLayouts[i].addWidget(self.motorDials[i])
            motorVertLayouts[i].addWidget(self.motorSlider[i])
            motorVertLayouts[i].addWidget(self.motorSpinners[i])
            motorVertLayouts[i].addWidget(self.invertAngleButton[i])
            
            hLay = QHBoxLayout()
            hLay.addWidget(self.minMotorSpinner[i])
            hLay.addWidget(self.maxMotorSpinner[i])
            self.minMotorSpinner[i].setRange(min,max)
            self.maxMotorSpinner[i].setRange(min,max)
            
            motorVertLayouts[i].addLayout(hLay)
            
            bLay = QHBoxLayout()
            bLay.addWidget(self.goMinButton[i])
            bLay.addWidget(self.goMaxButton[i])
            motorVertLayouts[i].addLayout(bLay)
            
            
            motorBoxes[i].setLayout(motorVertLayouts[i])
            
            
            
    

        # add vertical to middle layout
        for i in range(0, 6):
            middleLayout.addWidget(motorBoxes[i])
            
        # add middle boxes to larger motor box
        middleHBox.setLayout(middleLayout)
        
        # add motor box
        self.mainVLayout.addWidget(middleHBox)
 
 
 
    def add_to_individual_angle_checkbox(self):
        if self.allMotorOverrideAngleCheckbox.isChecked():
            for i in range(0,6):
                self.allMotorDial.setValue(0)
                self.copyAngleValues[i] = self.motorDials[i].value()
        else:
            for i in range(0,6):
                self.motorDials[i].setValue(self.copyAngleValues[i])
                
                
                
    def spinner_value_changed(self,index):
        """ when spinner value changes"""   
        self.motorDials[index].setValue(self.motorSpinners[index].value())
        
        
        
    def all_motor_spinner_changed(self):
        self.allMotorDial.setValue(self.allMotorSpinner.value())    
    
    
    
    def all_motor_dial_callback(self):
        """controls the all motor dial"""
        newVAl = self.allMotorDial.value()
        self.allMotorSpinner.setValue(newVAl)
        
        if self.allMotorOverrideAngleCheckbox.isChecked():
            for i in range(0,6):
                self.motorDials[i].setValue(self.copyAngleValues[i] + newVAl)
        else:
            dataStr = b"all " + str(newVAl).encode() + b" \r"
        
            if self.serial_dev is not None and self.serial_dev.is_open:
                self.serial_dev.write(dataStr)
        
        
        
    def dial_value_changed(self, i):
        """ " updates the angles in the spinner and writes to serial dev"""

        newVal = self.motorDials[i].value()
        self.motorSpinners[i].setValue(newVal)

        if not self.allMotorOverrideAngleCheckbox.isChecked():
            self.copyAngleValues[i] = newVal
        
        dataStr = self.get_serial_write_string()
        
        # make sure port is open
        if self.serial_dev is not None and self.serial_dev.is_open:
            self.serial_dev.write(dataStr)


    def get_serial_write_string(self):
        dataStr = (
            str(self.motorDials[0].value()).encode()
            + b" "
            + str(self.motorDials[1].value()).encode()
            + b" "
            + str(self.motorDials[2].value()).encode()
            + b" "
            + str(self.motorDials[3].value()).encode()
            + b" "
            + str(self.motorDials[4].value()).encode()
            + b" "
            + str(self.motorDials[5].value()).encode()
            + b" \r"
        )
        return dataStr


    def attach_control_callbacks(self):
        """Attaches callback when dial is turned"""
        self.motorDials[0].valueChanged.connect(lambda: self.dial_value_changed(0))
        self.motorDials[1].valueChanged.connect(lambda: self.dial_value_changed(1))
        self.motorDials[2].valueChanged.connect(lambda: self.dial_value_changed(2))
        self.motorDials[3].valueChanged.connect(lambda: self.dial_value_changed(3))
        self.motorDials[4].valueChanged.connect(lambda: self.dial_value_changed(4))
        self.motorDials[5].valueChanged.connect(lambda: self.dial_value_changed(5))
        
        self.motorSpinners[0].valueChanged.connect(lambda: self.spinner_value_changed(0))
        self.motorSpinners[1].valueChanged.connect(lambda: self.spinner_value_changed(1))
        self.motorSpinners[2].valueChanged.connect(lambda: self.spinner_value_changed(2))
        self.motorSpinners[3].valueChanged.connect(lambda: self.spinner_value_changed(3))
        self.motorSpinners[4].valueChanged.connect(lambda: self.spinner_value_changed(4))
        self.motorSpinners[5].valueChanged.connect(lambda: self.spinner_value_changed(5))
        
        self.invertAngleButton[0].pressed.connect(lambda: self.motorSpinners[0].setValue(-1*self.motorSpinners[0].value()))
        self.invertAngleButton[1].pressed.connect(lambda: self.motorSpinners[1].setValue(-1*self.motorSpinners[1].value()))
        self.invertAngleButton[2].pressed.connect(lambda: self.motorSpinners[2].setValue(-1*self.motorSpinners[2].value()))
        self.invertAngleButton[3].pressed.connect(lambda: self.motorSpinners[3].setValue(-1*self.motorSpinners[3].value()))
        self.invertAngleButton[4].pressed.connect(lambda: self.motorSpinners[4].setValue(-1*self.motorSpinners[4].value()))
        self.invertAngleButton[5].pressed.connect(lambda: self.motorSpinners[5].setValue(-1*self.motorSpinners[5].value()))
        
        self.goMinButton[0].pressed.connect(lambda: self.motorSpinners[0].setValue(self.minMotorSpinner[0].value()))
        self.goMinButton[1].pressed.connect(lambda: self.motorSpinners[1].setValue(self.minMotorSpinner[1].value()))
        self.goMinButton[2].pressed.connect(lambda: self.motorSpinners[2].setValue(self.minMotorSpinner[2].value()))
        self.goMinButton[3].pressed.connect(lambda: self.motorSpinners[3].setValue(self.minMotorSpinner[3].value()))
        self.goMinButton[4].pressed.connect(lambda: self.motorSpinners[4].setValue(self.minMotorSpinner[4].value()))
        self.goMinButton[5].pressed.connect(lambda: self.motorSpinners[5].setValue(self.minMotorSpinner[5].value()))
        
        self.goMaxButton[0].pressed.connect(lambda: self.motorSpinners[0].setValue(self.maxMotorSpinner[0].value()))
        self.goMaxButton[1].pressed.connect(lambda: self.motorSpinners[1].setValue(self.maxMotorSpinner[1].value()))
        self.goMaxButton[2].pressed.connect(lambda: self.motorSpinners[2].setValue(self.maxMotorSpinner[2].value()))
        self.goMaxButton[3].pressed.connect(lambda: self.motorSpinners[3].setValue(self.maxMotorSpinner[3].value()))
        self.goMaxButton[4].pressed.connect(lambda: self.motorSpinners[4].setValue(self.maxMotorSpinner[4].value()))
        self.goMaxButton[5].pressed.connect(lambda: self.motorSpinners[5].setValue(self.maxMotorSpinner[5].value()))
        
        self.motorSlider[0].valueChanged.connect(lambda: self.motorDials[0].setValue(self.motorSlider[0].value()))
        self.motorSlider[1].valueChanged.connect(lambda: self.motorDials[1].setValue(self.motorSlider[1].value()))
        self.motorSlider[2].valueChanged.connect(lambda: self.motorDials[2].setValue(self.motorSlider[2].value()))
        self.motorSlider[3].valueChanged.connect(lambda: self.motorDials[3].setValue(self.motorSlider[3].value()))
        self.motorSlider[4].valueChanged.connect(lambda: self.motorDials[4].setValue(self.motorSlider[4].value()))
        self.motorSlider[5].valueChanged.connect(lambda: self.motorDials[5].setValue(self.motorSlider[5].value()))
        
        
    def find_serial_ports(self):
        """finds serial ports and puts them into combo box"""

        print("finding ports")
        ports = [port.device for port in serial.tools.list_ports.comports()]
        
        self.portComboBox.clear()
        for port in ports:
            self.portComboBox.addItem(port)
            
            
            
    def enable_controls(self,state):
        """Turns on or off all control items depending on serial connection state"""
        
        # individual dials
        for dial in self.motorDials:
            dial.setEnabled(state)
            dial.setValue(0)
        
        # reset spinner
        for spinner in self.motorSpinners:
            spinner.setEnabled(state)
            spinner.setValue(0)
            
        # buttons
        for button in self.invertAngleButton:
            button.setEnabled(state)
        
        # all motor dial
        self.allMotorDial.setEnabled(state)
        self.allMotorDial.setValue(0)
        
        # all motor spinner
        self.allMotorSpinner.setEnabled(state)
        self.allMotorSpinner.setValue(0)
        
        # all motor invert angle button
        self.allMotorInvertAngleButton.setEnabled(state)
        
        # override angle checkbox
        self.allMotorOverrideAngleCheckbox.setEnabled(state)
        
        # # jog start button
        # self.startJogButton.setEnabled(state)
        
        

    def connect_serial_device(self):
        """connects serial device"""
        
        if not self.serial_dev_connected:
            try:
                self.serial_dev = serial.Serial(self.portComboBox.currentText(), 9600)
                self.serial_dev_connected = True
                self.connectButton.setText("Disconnect")

                # enable dials
                self.enable_controls(True)
                
                # start serial thread
                # self.serialThread.start()
                    
                print("Success connecting serial")
                
            except:
                print("Failed connecting serial")
                self.connectButton.setText("Connect")
                
                self.serial_dev_connected = False
                self.enable_controls(False)
        else:
            # reset bool and close port 
            self.serial_dev_connected = False
            if self.serial_dev is not None:
                self.serial_dev.close()
                
            # disable dials and reset values
            self.enable_controls(False)
            
            # if self.serialThread.is_alive():
            #     self.serialThread.join()
                
            # change title of button
            self.connectButton.setText("Connect")
            
            print("Closing serial device")
    
    
    
    def closeEvent(self,event):
        if self.serial_dev is not None:
            self.serial_dev.close()
            
        # if self.serialThread.is_alive():
        #     self.serialThread.join()
        print("called closed")
        event.accept()


if __name__ == "__main__":
    app = QApplication([])

    widget = Widget()
    widget.show()

    sys.exit(app.exec_())
