## CTD Library
#  serves as a dictionary of commands and communications functions for the 
#  SBE 49 FastCAT CTD Sensor Model No. 49 350M using command descriptions from Manual version 19. 
#  Created by Jolie Elliott with support from Braidan Duffy
#  Started 2/11/2022

## Variable definitions
# from tkinter import N <-- why is that there

## STARTUP PROTOCOL???

import serial
CR = b'\r'



class SBE_49_CTD_Sensor(serial.Serial):
    #Constants
    YES                    = b'Y' + CR
    NO                     = b'N' + CR
    DS                     = "DS"
    BAUD_RATE_CMD          = "Baud="
    OUTPUT_FORMAT_CMD      = "OutputFormat="
    OUTPUT_RAW_FREQUENCIES = 0 # includes A/D counts and voltages in Hexadecimal
    OUTPUT_CONVERTED_DATA  = 1 # Hexidecimal form
    OUTPUT_RAW_DATA        = 2 # Decimal form
    OUTPUT_ROV             = 3 # converted data in decimal form
    OUTPUT_SAL_CMD         = "OutputSal="   # Output Salinity
    OUTPUT_SOUND_VELOCITY  = "OutputSV="
    SAMPLE_AVG             = "NAvg="
    CONDUCTIVITY_FREQUENCY = "MinCondFreq="
    TIME_TO_DELAY          = "PumpDelay="
    PROCESS_DATA           = "ProcessRealTime="
    TEMP_ADVANCE           = "TAdvance="
    ALPHA_COEFFICIENT      = "Alpha=x"
    TAU_COEFFICIENT        = "Tau=x"
    AUTO_SAMPLE            = "AutoRun=x"
    START_SAMPLE           = "Start"
    STOP_SAMPLE            = "Stop"
    PUMP_ON                = "PumpOn"
    Pump_OFF               = "PumpOff"
    TAKE_SAMPLE            = "TS"
    TEST_TEMP              = "TT"
    TEST_CONDUCTIVITY      = "TC"
    TEST_PRESSURE          = "TP"
    TEST_TEMP_RAW          = "TTR"
    TEST_CONDUCTIVITY_RAW  = "TCR"
    TEST_PRESSURE_RAW      = "TPR"

    # Flags


    def __init__(self,port,baudrate,timeout=1,*args,**kwargs):
        super().__init__(port=port, baudrate = baudrate, timeout = timeout, *args, **kwargs) # initializing for serial output
        self.reset_output_buffer() # Clear input/ooutput buffers on initialization

    ## ************************Utility Functions *****************************
    def write_Data(self, msg):
        self.write(msg)
        return self.read_Data()

    def read_Data(self):
        _gen_ack = b'S>'
        _read_buffer = self.read_until('\r')
        # print(_read_buffer) # Debug
        if _read_buffer == "?CMD".encode('utf-8'): # convert string to bytes
            return -1
        elif _read_buffer == _gen_ack:
            return 1
        else:
            return _read_buffer



    def parse_DS(self):
        """
        Display Operating Status + Setup
        Includes Serial number, Number of scans to average, Range,
        ADD MORE AS THIS IS CLEARER
        """
        pass
    # *******************Command Functions******************************
    def get_DS(self):
        return self.write_Data(self.DS.encode('utf-8') + CR)

    def set_baud(self, rate=9600):
        """
        Default 9600.
        
        Options include 1200, 2400, 4800, 9600, 19200, or 38400
        """
        # check if string, make int
        # check if in list/range, format
        # if n in range (): n = format(n, '01n').encode('utf-8')
        # return -1

        return self.write_data(self.BAUD_RATE_CMD.encode('utf-8') + rate + CR)

    def set_output_format(self, Output_Format):
        if Output_Format == self.OUTPUT_RAW_FREQUENCIES: 
            self.write_data(self.OUTPUT_FORMAT_CMD.encode('utf-8') + self.OUTPUT_RAW_FREQUENCIES + CR)
        elif Output_Format == self.OUTPUT_RAW_DATA:
            self.write_data(self.OUTPUT_FORMAT_CMD.encode('utf-8') + self.OUTPUT_RAW_DATA + CR)
        elif Output_Format == self.OUTPUT_CONVERTED_DATA: 
            self.write_data(self.OUTPUT_FORMAT_CMD.encode('utf-8') + self.OUTPUT_CONVERTED_DATA + CR)
        elif Output_Format == self.OUTPUT_ROV: 
            self.write_data(self.OUTPUT_FORMAT_CMD + self.OUTPUT_ROV)
        #UPDATE BAUD
        #CHECK ACKNOWLEDGED

    def set_output_salinity(self):
        self.write_data(self.OUTPUT_SAL_CMD.encode('utf-8') + self.YES + CR)

    # Calculated in (meters/second)
    def set_output_sound_velocity(self, BOOLEAN):
        if BOOLEAN == True:
            self.write_data(self.OUTPUT_SOUND_VELOCITY.encode('utf-8') + self.YES + CR)
        if BOOLEAN == False:
            self.write_data(self.OUTPUT_SOUND_VELOCITY.encode('utf-8') + self.NO + CR)

    def set_defaults(self):
        """
        OutputFormat          = 3
        outputSalinity        = Y
        Output Sound Velocity = Y
        N Avg                 = 1
        MinConductivityFreq   = 3000
        PumpDelay             = 30
        ProcessRealTime       = Y
        TAdvance              = 0.0625
        Alpha                 = 0.03
        Tau                   = 7.0
        AutoRun               = N
        """
        self.write_data("SetDefaults".encode('utf-8') + CR)


    def set__sample_avg(self, rate):
        """
        Range: 1-255 samples.
        Defines the number of values the CTD will average
        Outputs only the average.
        """
        if rate >= 1 and rate <= 255:
            return self.write_data(self.SAMPLE_AVG.encode('utf-8') + rate)
        else:
            return 1


    def set_min_conductivity(self, frequency):
        """
        Minimum conductivity frequency must be reached before pump turns on
        Ensures pump is in water before use
        Typical for salt water is 500 Hz; default is 3000 Hz
        """
        self.write_data(self.CONDUCTIVITY_FREQUENCY.encode('utf-8') + frequency)


    def pump_delay(self, time):
        """
        Delays pump after Conductivity Frequency threshold has been met
        """
        self.write_data(self.TIME_TO_DELAY + time)


    # post-processing data is not applicable to use in AUVs and ROVs
    # ROV records data on command
    # preventing post-calculations from being performed. 
    # For more information, google it. 
    def process_data(self, Bool):
        """
        When Yes: Corrects for alignment, filtering, and conductivity cell thermal mass 
        for data in real time. Cannot be used if output format is not 1 or 3.
        Note that post-processing data is not applicable for AUVs and ROVs.
        """
        if Bool == True:
            self.write_data(self.PROCESS_DATA + self.YES)
        else:
            self.write_data(self.PROCESS_DATA + self.NO)


    def temp_advance(self, Temp_Time):
        """
        Advances temperature,
        used to align temperature data with conductivity data
        Allows for accurate salinity readings
        Range 0 to 0.125 seconds
        Default = 0.0625
        Conditions: Process_Data=Y
        Ouptut_Format=1 or 3.
        """

        self.write_data(self.TEMP_ADVANCE + Temp_Time)


    def thermal_cell_alpha(self, Alpha):
        """
        Conductivity Cell Thermal Mass Alpha Correction
        corrects amplitude
        Range: 0.02 to 0.05
        Default: 0.03
        Conditions: ProcessRealTime=Y
        OutputFormat=1 or 3
        """
        self.write_data(self.ALPHA_COEFFICIENT + Alpha)

    def thermal_cell_tau(self, Tau):
        """
        Conductivity Cell Thermal Mass Tau Correction
        corrects time constant
        Range: 5.0 to 10.0
        Default: 7.0
        Conditions: ProcessRealTime=Y and OutputFormat=1 or 3
        """
        self.write_data(self.TAU_COEFFICIENT + Tau)

    def auto_sample(self, Bool):
        """
        Auto_Sqample = YES starts autonomous sampling automatically
        Must turn power off and on or call start_sample
        Default: auto_sample = NO
        Turn on Power
        Waits for command when power is ON
        """
        if Bool == True:
            self.write_data(self.AUTO_SAMPLE + self.YES)
        else:
            self.write_data(self.AUTO_SAMPLE + self.NO)

    def start_sample(self):
        self.write_data(self.START_SAMPLE)

    def stop_sample(self):
        """
        May need to send command multiple times for a response
        Backup is to remove power
        """
        self.write_data(self.STOP_SAMPLE)


    #**************************Polled Sampling Commands***********************

    def pump_on(self):
        """
        Must turn pump on before calling take_sample or testing pump
        """
        self.write_data(self.PUMP_ON)

    def pump_off(self):
        """Literally just turns the pump off. """
        self.write_data(self.Pump_OFF)

    def take_sample(self):
        """Takes 1 sample and transmits the data"""
        self.write_data(self.TAKE_SAMPLE)

    #************************ Testing Commands *******************************
    ## OUTPUTS???
    def test_temp(self):
        self.write_data(self.TEST_TEMP)

    def test_conductivity(self):
        self.write_data(self.TEST_CONDUCTIVITY)

    def test_pressure(self):
        self.write_data(self.TEST_PRESSURE)

    def test_temp_raw(self):
        self.write_data(self.TEST_TEMP_RAW)

    def test_conductivity_raw(self):
        self.write_data(self.TEST_CONDUCTIVITY_RAW)

    def test_pressure_raw(self):
        self.write_data(self.TEST_CONDUCTIVITY_RAW)
