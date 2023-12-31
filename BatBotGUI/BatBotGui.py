"""Author: Mason Lopez
    Date: November 13th
    About: This GUI controls the BatBot system, Tendons, GPS, and Sonar
    """
import typing
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLayout,
    QGroupBox,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QSlider,
    QSpinBox,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QAbstractItemView,
    QMenu,
    QTabBar,
    QTabWidget,
    QGridLayout,
    QLineEdit,
    QSpacerItem,
    QDoubleSpinBox,
    QSizePolicy,

)
from PyQt6.QtCore import Qt, QFile, QTextStream, QThread, pyqtSignal,QObject
import sys
import serial
import serial.tools.list_ports
import time
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from datetime import datetime 

# showing plots in qt from matlab
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


# logging stuff
import logging
logging.basicConfig(level=logging.DEBUG)


# frequency of dac and adc
DAC_ADC_FREQ = 1e6

class Widget(QWidget):
    """GUI for controlling Bat Bot"""
    
    # main vertical layout everything is added to
    mainVLay = QVBoxLayout()
    
    
    
    def __init__(self):
        """Adds all the widgets to GUI"""
        QWidget.__init__(self)
        self.setWindowTitle("Bat Bot 7 GUI")
        
        # add experiment box
        self.Add_Experiment_GB()

        # add sonar and GPS controller box
        self.Add_Echo_GB()

        # add pinnae controls layout
        self.Add_Pinnae_Control_GB()

        
        self.setLayout(self.mainVLay)
        

#----------------------------------------------------------------------
    def Add_Experiment_GB(self):
        """Adds layout for where to save data for this experient"""
        self.experiment_settings_GB = QGroupBox("Experiment")
        # -------------------------------------------------------------------
        # directory groupbox
        directory_grid = QGridLayout()        
        directory_GB = QGroupBox("Directory Settings")

        # where to save directory
        self.directory_TE = QLineEdit("/home/batbot/experiments/")
        self.directory_TE.setObjectName("directory_TE")
        directory_grid.addWidget(QLabel("Directory:"),0,0)
        directory_grid.addWidget(self.directory_TE,0,1)

        # name of experiment
        curExperiment = self.get_current_experiment_time()
        # set the window title the name of experiment
        self.setWindowTitle("BatBot 7 GUI:\t\t\t\t" + curExperiment)
        
        # set the name
        self.experiment_folder_name_TE = QLineEdit(curExperiment)
        self.experiment_folder_name_TE.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.experiment_folder_name_TE.customContextMenuRequested.connect(self.experiment_folder_name_TE_contextMenu)
        
        directory_grid.addWidget(QLabel("Experiment Folder:"),1,0)
        directory_grid.addWidget(self.experiment_folder_name_TE,1,1)
        directory_GB.setLayout(directory_grid)
        
        # -------------------------------------------------------------------
        # settings for chirps
        chirp_GB = QGroupBox("Chirp && Listen Settings")
        chirp_grid = QGridLayout()
        # start freq
        self.chirp_start_freq_SB = QSpinBox()
        self.chirp_start_freq_SB.setSuffix(" kHz")
        self.chirp_start_freq_SB.setValue(50)
        self.chirp_start_freq_SB.setRange(0,300)
        self.chirp_start_freq_SB.valueChanged.connect(self.chirp_settings_changed_callback)
        chirp_grid.addWidget(QLabel("Start:"),0,0)
        chirp_grid.addWidget(self.chirp_start_freq_SB,0,1)

        # end freq
        self.chirp_stop_freq_SB = QSpinBox()
        self.chirp_stop_freq_SB.setSuffix(" kHz")
        self.chirp_stop_freq_SB.setRange(0,300)
        self.chirp_stop_freq_SB.setValue(150)
        self.chirp_stop_freq_SB.valueChanged.connect(self.chirp_settings_changed_callback)
        chirp_grid.addWidget(QLabel("Stop:"),1,0)
        chirp_grid.addWidget(self.chirp_stop_freq_SB,1,1)

        # length of chirp
        self.chirp_duration_SB = QSpinBox()
        self.chirp_duration_SB.setValue(1)
        self.chirp_duration_SB.setSuffix(" mS")
        self.chirp_duration_SB.valueChanged.connect(self.chirp_settings_changed_callback)
        chirp_grid.addWidget(QLabel("Duration:"),0,2)
        chirp_grid.addWidget(self.chirp_duration_SB,0,3)
        
        # type of chirp
        self.chirp_type_CB = QComboBox()
        self.chirp_type_CB.addItem('linear')
        self.chirp_type_CB.addItem('quadratic')
        self.chirp_type_CB.addItem('logarithmic')
        self.chirp_type_CB.addItem('hyperbolic')
        self.chirp_type_CB.currentTextChanged.connect(self.chirp_settings_changed_callback)
        chirp_grid.addWidget(QLabel("Type:"),1,2)
        chirp_grid.addWidget(self.chirp_type_CB,1,3)
        
        buffer_col_len = 90
        # length of chirp buffer
        self.chirp_buffer_length_SB = QLineEdit()
        self.chirp_buffer_length_SB.setReadOnly(True)
        self.chirp_buffer_length_SB.setMaximumWidth(buffer_col_len)
        chirp_grid.addWidget(QLabel("Chirp:"),0,4)
        chirp_grid.addWidget(self.chirp_buffer_length_SB,0,5)
        
        # lengthf of listen buffers
        self.listen_buffer_length_SB = QLineEdit()
        self.listen_buffer_length_SB.setReadOnly(True)
        self.listen_buffer_length_SB.setMaximumWidth(buffer_col_len)
        chirp_grid.addWidget(QLabel("Listen:"),1,4)
        chirp_grid.addWidget(self.listen_buffer_length_SB,1,5)
        
        # preview chirp
        self.preview_chirp_PB = QPushButton("Preview")
        self.preview_chirp_PB.clicked.connect(self.preview_chirp_PB_Clicked)
        chirp_grid.addWidget(self.preview_chirp_PB,0,6)
        
        # upload to board
        self.upload_chirp_PB = QPushButton("Upload")
        self.upload_chirp_PB.clicked.connect(self.upload_chirp_PB_Clicked)
        chirp_grid.addWidget(self.upload_chirp_PB,1,6)
        
        chirp_GB.setLayout(chirp_grid)
        
        
        
        # -------------------------------------------------------------------
        # put together two groupboxes
        hLay = QHBoxLayout()
        hLay.addWidget(directory_GB)
        hLay.addWidget(chirp_GB)
        
        self.chirp_settings_changed_callback()
        
        self.experiment_settings_GB.setLayout(hLay)
        self.mainVLay.addWidget(self.experiment_settings_GB)
        

    def get_current_experiment_time(self):
        """Get the current time string that can be used as a file name or folder name"""
        return datetime.now().strftime("experiment_%m-%d-%Y_%H-%M-%S%p")
    
    def experiment_folder_name_TE_contextMenu(self,position):
        """Custom context menu for experiment folder name"""
        context_menu = QMenu()
        
        set_current_time = context_menu.addAction("Set Current Time")
        copy_name = context_menu.addAction("Copy")
        paste_name = context_menu.addAction("Paste")
        # action = context_menu.exec(self.experiment_folder_name_TE.viewport().mapToGlobal(position))
        action = context_menu.exec(self.experiment_folder_name_TE.mapToGlobal(position))
        
        if action == set_current_time:
            self.experiment_folder_name_TE.setText(self.get_current_experiment_time())
            
    
    # callback
    def preview_chirp_PB_Clicked(self):
        """_summary_
        """
        logging.debug("preview_chirp_PB_Clicked")
        

        plt.close('Chirp Preview')
        plt.figure("Chirp Preview")
        
        duration = self.chirp_duration_SB.value() * 1e-3
        start = self.chirp_start_freq_SB.value() * 1e3
        stop = self.chirp_stop_freq_SB.value() * 1e3
        method = self.chirp_type_CB.currentText()
        sample_rate = 1e6  # Define your desired sample rate (1 MHz in this case)
        t = np.arange(0, duration, 1 / sample_rate)

        y_chirp = signal.chirp(t, f0=start, f1=stop, t1=t[-1], method=method)

        # Plotting the spectrogram
        plt.specgram(y_chirp, Fs=sample_rate)
        plt.xlabel('Time (s)')
        plt.ylabel('Frequency (Hz)')
        plt.title('Spectrogram of Chirp Signal')
        plt.colorbar(label='Intensity')
        plt.show()


    def upload_chirp_PB_Clicked(self):
        """ when clicked"""
        logging.debug("upload_chirp_PB_Clicked")
        print(plt.get_figlabels())
        
    def chirp_settings_changed_callback(self):
        open_figures = plt.get_figlabels()
        
        duration = self.chirp_duration_SB.value()
        
        # display chirp buffer length
        chirp_len = duration*1e-3*1e6
        self.chirp_buffer_length_SB.setText(f"{chirp_len:.0f}")
        
        # display listen buffer length
        listen_buffer_len = np.floor((80000 - chirp_len)/2)
        listen_buffer_time = listen_buffer_len*1e-3
        self.listen_buffer_length_SB.setText(f"{listen_buffer_len:.0f} {listen_buffer_time:.1f} mS")
        
        
        if 'Chirp Preview' in open_figures:
            self.preview_chirp_PB_Clicked()
        
        
#----------------------------------------------------------------------
    def Add_Pinnae_Control_GB(self):
        """Adds the controls box layout"""
        # self.pinnaeControlBox = QGroupBox("Pinnae Control")
        # controlsHLay = QHBoxLayout()
        
        # # create tabs for each ear mode
        # self.singleEarTab = QWidget()
        # self.dualEarTab = QWidget()
        
        # # create tabs 
        # self.tabs = QTabWidget()
        # self.tabs.addTab(self.singleEarTab,"Single")
        # self.tabs.addTab(self.dualEarTab,"Dual")
        
        # # init left controls
        # self.init_leftControls()
        # # init right controls
        # self.init_rightControls()
        
        # # init box for both ears
        # self.init_bothControls()

        # # init sonar controls
        
        # # init the tabs
        # self.init_singleEarTab()
        # self.init_dualEarTab()
        
        
        # controlsHLay.addWidget(self.tabs)
        # self.pinnaeControlBox.setLayout(controlsHLay)
        # self.mainVLay.addWidget(self.pinnaeControlBox)

        self.pinnae_controls_GB = QGroupBox("Controls")
        
        control_h_lay = QHBoxLayout()
        
        motor_GB = [
            QGroupBox("Motor 1"),
            QGroupBox("Motor 2"),
            QGroupBox("Motor 3"),
            QGroupBox("Motor 4"),
            QGroupBox("Motor 5"),
            QGroupBox("Motor 6")
        ]

        self.motor_max_PB = [
            QPushButton("Max"),
            QPushButton("Max"),
            QPushButton("Max"),
            QPushButton("Max"),
            QPushButton("Max"),
            QPushButton("Max"),
        ]
        
        self.motor_min_PB = [
            QPushButton("Min"),
            QPushButton("Min"),
            QPushButton("Min"),
            QPushButton("Min"),
            QPushButton("Min"),
            QPushButton("Min"),
        ]

        self.motor_max_limit_SB = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox()
        ]

        self.motor_min_limit_SB = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox()
        ]

        self.motor_value_SB = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox()
        ]
        
        self.motor_value_SLIDER = [
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
        ]
        
        self.motor_set_zero_PB = [
            QPushButton("Set Zero"),
            QPushButton("Set Zero"),
            QPushButton("Set Zero"),
            QPushButton("Set Zero"),
            QPushButton("Set Zero"),
            QPushButton("Set Zero")
        ]
        
        number_motors = 6
        max_value = 10000
        
        for index in range(number_motors):
            vertical_layout = QVBoxLayout()
            
            temp_CB = QGroupBox("Control")
            
            # 4 row by 2 columns
            grid_lay = QGridLayout()
            
            # add max button
            grid_lay.addWidget(self.motor_max_PB[index],0,0)
            
            # add max spinbox
            self.motor_max_limit_SB[index].setRange(-max_value,max_value)
            self.motor_max_limit_SB[index].setValue(180)
            grid_lay.addWidget(self.motor_max_limit_SB[index],0,1)
            
            # add value spinbox
            self.motor_value_SB[index].setRange(-max_value,max_value)
            grid_lay.addWidget(self.motor_value_SB[index],1,0)
            
            # add value slider
            self.motor_value_SLIDER[index].setMinimumHeight(100)
            self.motor_value_SLIDER[index].setRange(-max_value,max_value)
            self.motor_value_SLIDER[index].setValue(0)
            grid_lay.addWidget(self.motor_value_SLIDER[index],1,1)
            
            # add min button
            grid_lay.addWidget(self.motor_min_PB[index],2,0)
            
            # add min spinbox
            self.motor_min_limit_SB[index].setRange(-max_value,max_value)
            grid_lay.addWidget(self.motor_min_limit_SB[index],2,1)
            
            ## add the layout
            vertical_layout.addLayout(grid_lay)
            
            # add set zero
            vertical_layout.addWidget(self.motor_set_zero_PB[index])
        
            motor_GB[index].setMaximumWidth(160)
            
            motor_GB[index].setLayout(vertical_layout)
            control_h_lay.addWidget(motor_GB[index])
        
        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(control_h_lay)
        
        hLay = QHBoxLayout()
        # add the instruction table
        self.instruction_TABLE = QTableWidget(1,number_motors)
        # vertical_layout.addWidget(self.instruction_TABLE)
        hLay.addWidget(self.instruction_TABLE)
        
        
        # create layout for buttons side of table
        table_side_v_lay = QVBoxLayout()
        
        # settings for making ears realistic
        self.realistic_ears_CB = QCheckBox("Realistic Ears")
        self.realistic_ears_CB.setToolTip("Each ear will be out of phase if checked like a real bat")
        table_side_v_lay.addWidget(self.realistic_ears_CB)
        
        # create 
        table_side_grid = QGridLayout()
        self.start_stop_instruction_PB = QPushButton("Start")
        table_side_grid.addWidget(self.start_stop_instruction_PB,0,0)
        self.intstruction_speed_SB = QSpinBox()
        self.intstruction_speed_SB.setSuffix(" Hz")
        table_side_grid.addWidget(self.intstruction_speed_SB,0,1)
        
        
        table_side_v_lay.addLayout(table_side_grid)

        hLay.addLayout(table_side_v_lay)        
        vertical_layout.addLayout(hLay)
        
        self.pinnae_controls_GB.setLayout(vertical_layout)
        self.mainVLay.addWidget(self.pinnae_controls_GB)
        
    def init_leftControls(self):
        """Creates box of left controls"""
        self.leftControlBox = QGroupBox("Left Pinnae")

        minAngleSBHlay = QHBoxLayout()
        self.leftMinAngleSB = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
        ]
        maxAngleSBHlay = QHBoxLayout()
        self.leftMaxAngleSB = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
        ]
        
        angleSliderBHlay = QHBoxLayout()
        self.leftAngleSlider = [
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
        ]
        
        for SB in self.leftMinAngleSB:
            SB.setRange(-1000,1000)
            SB.setFixedWidth(48)
            SB.setValue(-180)
            minAngleSBHlay.addWidget(SB)

        for SB in self.leftMaxAngleSB:
            SB.setFixedWidth(48)
            SB.setRange(-1000,1000)
            SB.setValue(180)
            maxAngleSBHlay.addWidget(SB)
            
        for slider in self.leftAngleSlider:
            angleSliderBHlay.addWidget(slider)
            
        vLay = QVBoxLayout()
        vLay.addLayout(minAngleSBHlay)
        vLay.addLayout(angleSliderBHlay)
        vLay.addLayout(maxAngleSBHlay)
        
        self.leftControlBox.setLayout(vLay)

    def init_rightControls(self):
        """Creates box of left controls"""
        self.rightControlBox = QGroupBox("Right Pinnae")

        minAngleSBHlay = QHBoxLayout()
        self.rightMinAngleSB = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
        ]
        maxAngleSBHlay = QHBoxLayout()
        self.rightMaxAngleSB = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
        ]

        angleSBHlay = QHBoxLayout()
        self.rightAngleSB = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
        ]
        
        angleSliderBHlay = QHBoxLayout()
        self.rightAngleSlider = [
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
        ]
        
        for SB in self.rightMinAngleSB:
            SB.setRange(-10000,10000)
            SB.setFixedWidth(48)
            SB.setValue(-180)
            minAngleSBHlay.addWidget(SB)

        for SB in self.rightMaxAngleSB:
            SB.setFixedWidth(48)
            SB.setRange(-10000,10000)
            SB.setValue(180)
            maxAngleSBHlay.addWidget(SB)

        for SB in self.rightAngleSB:
            SB.setFixedWidth(48)
            SB.setRange(-10000,10000)
            SB.setValue(180)
            angleSBHlay.addWidget(SB)
            
        for slider in self.rightAngleSlider:
            angleSliderBHlay.addWidget(slider)
            
        vLay = QVBoxLayout()
        vLay.addLayout(minAngleSBHlay)
        vLay.addLayout(angleSliderBHlay)
        vLay.addLayout(maxAngleSBHlay)

        
        self.rightControlBox.setLayout(vLay)
   
    def init_bothControls(self):
        """Creates box of left controls"""
        self.bothControlBox = QGroupBox("Both")
        self.bothControlBox.setFixedHeight(230)

        minAngleSBHlay = QHBoxLayout()
        self.bothMinAngleSB = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
        ]
        maxAngleSBHlay = QHBoxLayout()
        self.bothMaxAngleSB = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
        ]
        
        self.bothAngleSB = [
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
            QSpinBox(),
        ]
        
        angleSliderBHlay = QHBoxLayout()
        self.bothAngleSlider = [
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
            QSlider(Qt.Orientation.Vertical),
        ]
        
        for SB in self.bothMinAngleSB:
            SB.setRange(-1000,1000)
            SB.setFixedWidth(48)
            SB.setValue(-180)
            minAngleSBHlay.addWidget(SB)

        for SB in self.bothMaxAngleSB:
            SB.setFixedWidth(48)
            SB.setRange(-1000,1000)
            SB.setValue(180)
            maxAngleSBHlay.addWidget(SB)
            
        for slider in self.bothAngleSlider:
            angleSliderBHlay.addWidget(slider)
            
        vLay = QVBoxLayout()
        vLay.addLayout(minAngleSBHlay)
        vLay.addLayout(angleSliderBHlay)
        vLay.addLayout(maxAngleSBHlay)

        
        self.bothControlBox.setLayout(vLay)
        # gridLay  = [
        #     QGridLayout(),
        #     QGridLayout(),
        #     QGridLayout(),
        #     QGridLayout(),
        #     QGridLayout(),
        #     QGridLayout(),
        # ]

        # hLay = QHBoxLayout()

        # for i, lay in enumerate(gridLay):
        #     lay.addWidget(self.bothMinAngleSB[i],0,0)
        #     lay.addWidget(self.bothMaxAngleSB[i],0,1)
        #     lay.addWidget(self.bothAngleSlider[i],1,0,1,2)
        #     hLay.addLayout(lay)
        
        # self.bothControlBox.setLayout(hLay)
        
    def init_singleEarTab(self):
        """inits the single ear tab"""
        vLay = QVBoxLayout()
        vLay.addWidget(self.bothControlBox)

        
        tableHLay = QHBoxLayout()
        tableBox = QGroupBox("Instructions")
        self.singleEarInstructionTable = QTableWidget()
        self.init_singleEarInstructionTable()

        tableHLay.addWidget(self.singleEarInstructionTable)

        buttonsVLay = QVBoxLayout()
        # start button
        self.singleEarStartPB = QPushButton("Start")
        buttonsVLay.addWidget(self.singleEarStartPB)

        # hz options
        self.singleEarHzSB = QSpinBox()
        self.singleEarHzSB.setRange(0,400)
        self.singleEarHzSB.setValue(1)
        self.singleEarHzSB.setSuffix('Hz')
        buttonsVLay.addWidget(self.singleEarHzSB)

        # read from file
        self.singleEarReadFilePB = QPushButton("Read File")
        buttonsVLay.addWidget(self.singleEarReadFilePB)


        tableHLay.addLayout(buttonsVLay)
        tableBox.setLayout(tableHLay)

        vLay.addWidget(tableBox)


        self.singleEarTab.setLayout(vLay)
    
    def init_singleEarInstructionTable(self):
        self.singleEarInstructionTable.setRowCount(1)
        self.singleEarInstructionTable.setColumnCount(6)

        # preload with zeros and set width
        widthValue = 80
        for i in range(6):
            intNum = QTableWidgetItem()
            intNum.setData(0,0)
            self.singleEarInstructionTable.setItem(0,i,intNum)
            self.singleEarInstructionTable.setColumnWidth(i,widthValue)
        self.singleEarInstructionTable.setFixedWidth(widthValue*6+20)

    def init_dualEarTab(self):
        """inits the dual ear tab"""
        vLay = QVBoxLayout()
        hLay = QHBoxLayout()
        hLay.addWidget(self.leftControlBox)
        hLay.addWidget(self.rightControlBox)
        # add left and right control box
        vLay.addLayout(hLay)

        tableHLay = QHBoxLayout()
        tableBox = QGroupBox("Instructions")
        self.dualEarInstructionTable = QTableWidget()
        self.init_dualEarInstructionTable()

        tableHLay.addWidget(self.dualEarInstructionTable)

        buttonsVLay = QVBoxLayout()
        # start button
        self.dualEarStartPB = QPushButton("Start")
        buttonsVLay.addWidget(self.dualEarStartPB)

        # hz options
        self.dualEarHzSB = QSpinBox()
        self.dualEarHzSB.setRange(0,400)
        self.dualEarHzSB.setValue(1)
        self.dualEarHzSB.setSuffix('Hz')
        buttonsVLay.addWidget(self.dualEarHzSB)

        # read from file
        self.dualEarReadFilePB = QPushButton("Read File")
        buttonsVLay.addWidget(self.dualEarReadFilePB)


        tableHLay.addLayout(buttonsVLay)
        tableBox.setLayout(tableHLay)

        vLay.addWidget(tableBox)



        self.dualEarTab.setLayout(vLay)

    def init_dualEarInstructionTable(self):
        self.dualEarInstructionTable.setRowCount(1)
        self.dualEarInstructionTable.setColumnCount(12)

        # preload with zeros and set width
        widthValue = 50
        for i in range(12):
            intNum = QTableWidgetItem()
            intNum.setData(0,0)
            self.dualEarInstructionTable.setItem(0,i,intNum)
            self.dualEarInstructionTable.setColumnWidth(i,widthValue)

        self.dualEarInstructionTable.setFixedWidth(widthValue*12+20)
        self.dualEarInstructionTable.setHorizontalHeaderLabels(["L1", "L2","L3","L4","L5","L6","R1","R2","R3","R4","R5","R6",])
        
        
#----------------------------------------------------------------------
    def init_echoControl_box(self):
        """Adds the sonar box layout"""
        self.sonarControlBox = QGroupBox("Echos")
        self.sonarControlBox.setMinimumHeight(300)
        vLay = QVBoxLayout()

        gridLay = QGridLayout()
        # # show directory pulling from
        # self.echoPlotDirectoryCB = QComboBox()
        # self.echoPlotDirectoryCB.addItem(self.directory_TE.text() +self.experiment_folder_name_TE.text()+"/gpsdata")
        # self.echoPlotDirectoryCB.setEditable(True)
        # self.echoPlotDirectoryCB.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred)
        # gridLay.addWidget(QLabel("Plot Data:"),0,0)
        # gridLay.addWidget(self.echoPlotDirectoryCB,0,1)
        
        # # show plots found
        # self.plotsFoundLE = QLineEdit("0")
        # self.plotsFoundLE.setReadOnly(True)

        # gridLay.addWidget(QLabel("Plots found:"),0,2)
        # gridLay.addWidget(self.plotsFoundLE,0,3)
    
        vLay.addLayout(gridLay)


        # left pinnae spectogram
        hLay = QHBoxLayout()
        self.leftPinnaeSpec = MplCanvas(self,width=5,height=4,dpi=100)
        self.leftPinnaeSpec.axes.set_title("Left Pinnae")
        
        Time_difference = 0.0001
        Time_Array = np.linspace(0, 5, math.ceil(5 / Time_difference))
        Data = 20*(np.sin(3 * np.pi * Time_Array))
        self.leftPinnaeSpec.axes.specgram(Data,Fs=6,cmap="rainbow")
        hLay.addWidget(self.leftPinnaeSpec)


        # middle section---------------------------------
        hLay2 = QHBoxLayout()

        # plot check button
        self.plotSpecCB = QCheckBox("Plot")
        # hLay.addWidget(self.plotSpecCB)
        hLay2.addWidget(self.plotSpecCB)

        # refreshrate for plots
        self.refreshRateSpecPlotsSB = QDoubleSpinBox()
        self.refreshRateSpecPlotsSB.setSuffix(" Sec")
        self.refreshRateSpecPlotsSB.setRange(0.1,100)
        self.refreshRateSpecPlotsSB.setValue(1)
        self.refreshRateSpecPlotsSB.setDecimals(1)
 
        # hLay.addWidget(QLabel("Plot Every:"))
        # hLay.addWidget(self.refreshRateSpecPlotsSB)
        hLay2.addWidget(QLabel("Plot Every:"))
        hLay2.addWidget(self.refreshRateSpecPlotsSB)

        vLay.addLayout(hLay2)

        # ---------------------------------------------
        # right pinnae spectogram
        self.rightPinnaeSpec = MplCanvas(self,width=5,height=4,dpi=100)
        self.rightPinnaeSpec.axes.set_title("Right Pinnae")
        Time_difference = 0.0001
        Time_Array = np.linspace(0, 5, math.ceil(5 / Time_difference))
        Data = 20*(np.sin(3 * np.pi * Time_Array))
        self.rightPinnaeSpec.axes.specgram(Data,Fs=6,cmap="rainbow")
        hLay.addWidget(self.rightPinnaeSpec)

        vLay.addLayout(hLay)
        self.sonarControlBox.setLayout(vLay)

    def init_GPS_box(self):
        """Inits the gps box"""
        self.gpsBox = QGroupBox("GPS")
        hLay = QHBoxLayout()
        gridLay = QGridLayout()

        # fakemap = QTextEdit("this is a map")
        fakemap = MplCanvas(self,width=5,height=4,dpi=100)
        Time_difference = 0.0001
        Time_Array = np.linspace(0, 5, math.ceil(5 / Time_difference))
        Data = 20*(np.sin(3 * np.pi * Time_Array))
        fakemap.axes.specgram(Data,Fs=6,cmap="rainbow")

        
        gridLay.addWidget(fakemap,0,0)

        # name to save file
        self.gpsFileNameTE = QLineEdit("gpsDataSave.txt")
        gridLay.addWidget(QLabel("File Name:"),0,1)
        gridLay.addWidget(self.gpsFileNameTE,0,2)
        
        self.gpsBox.setLayout(gridLay)
 

    def Add_Echo_GB(self):
        """adds sonar and gps box"""
        self.init_echoControl_box()

        self.sonarAndGPSLay = QHBoxLayout()
        self.sonarAndGPSLay.addWidget(self.sonarControlBox)
        # self.sonarAndGPSLay.addWidget(self.gpsBox)

        self.mainVLay.addLayout(self.sonarAndGPSLay)
        
    def closeEvent(self,event):
        plt.close('all')
        event.accept()
        
if __name__ == "__main__":
    app = QApplication([])
    widget = Widget()
    widget.show()
    sys.exit(app.exec())