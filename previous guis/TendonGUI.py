from PyQt5.QtWidgets import *



def window():
    app = QApplication([])
    window = QWidget()
    window.setGeometry(900,100,1000,300)
    window.setWindowTitle("Tendon Controller GUI")
    
    # main layout
    vLayout = QVBoxLayout()
    
    # serial layout
    serialLayout = QHBoxLayout()
    
    # port select box and its label
    portLabel = QLabel("Port")
    portDropDown = QComboBox()
    serialLayout.addWidget(portLabel)
    serialLayout.addWidget(portDropDown)
    # connect button
    serialConnectButton = QPushButton("Connect")
    serialLayout.addWidget(serialConnectButton)

    
    # dials and segments
    motorAngleDials = [QDial(),QDial(),QDial(),QDial(),QDial(),QDial()]
    motorAngleSegment = [QLCDNumber(3),QLCDNumber(3),QLCDNumber(3),QLCDNumber(3),QLCDNumber(3),QLCDNumber(3)]
    
    # dial layouts
    dialsLayout = QHBoxLayout()
    for i in motorAngleDials:
        i.setNotchesVisible(True)
        i.setValue(0)
        i.setRange(-360,360)
        i.setNotchTarget(5)
        i.valueChanged()
        dialsLayout.addWidget(i)
    
    
    # lcd segments
    segmentLayout = QHBoxLayout()
    for i in motorAngleSegment:
        segmentLayout.addWidget(i)
    
    vLayout.addLayout(serialLayout)
    vLayout.addLayout(dialsLayout)
    vLayout.addLayout(segmentLayout)
    
    window.setLayout(vLayout)
    window.show()
    app.exec_()
    
    
    
    
window()