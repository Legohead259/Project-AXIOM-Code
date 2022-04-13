## CTD Library
#  serves as a dictionary of commands and communications functions for the 
#  SBE 49 FastCAT CTD Sensor Model No. 49 350M 
#  using command descriptions from manual version 19. 
#  Created by Jolie Elliott with support from Braidan Duffy
#  Started 2/11/2022
#  Last Modified 4/12/2022

## Variable definitions
#  from tkinter import N <-- why is that there

## STARTUP PROTOCOL???

from pickle import TRUE
import serial
CR = b'\r' #Character Return



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
        baud_rates = [1200, 2400, 4800, 9600, 19200, 38400]

        if isinstance(rate, int) == False:
            rate = int(rate)

        if rate in baud_rates:
            return self.write_Data(self.BAUD_RATE_CMD.encode('utf-8') + rate + CR)
        else:
            return -1


    def set_output_format(self, Output_Format):
        """
        Default is Output_Format = OUTPUT_ROV = 3
        """
        if Output_Format == self.OUTPUT_RAW_FREQUENCIES: 
            self.write_Data(self.OUTPUT_FORMAT_CMD.encode('utf-8') + self.OUTPUT_RAW_FREQUENCIES + CR)
        elif Output_Format == self.OUTPUT_RAW_DATA:
            self.write_Data(self.OUTPUT_FORMAT_CMD.encode('utf-8') + self.OUTPUT_RAW_DATA + CR)
        elif Output_Format == self.OUTPUT_CONVERTED_DATA: 
            self.write_Data(self.OUTPUT_FORMAT_CMD.encode('utf-8') + self.OUTPUT_CONVERTED_DATA + CR)
        elif Output_Format == self.OUTPUT_ROV: 
            self.write_Data(self.OUTPUT_FORMAT_CMD + self.OUTPUT_ROV)
        #UPDATE BAUD
        #CHECK ACKNOWLEDGED

    def set_output_salinity(self, bool):
        """
        If Yes: Calculates and outputs salinity in psu. 
        Must have Output Format = OUTPUT_ROV
        If No: Does not calculate output salinity.
        """
        if bool == True:
            self.write_Data(self.OUTPUT_SAL_CMD.encode('utf-8') + self.YES + CR)
        elif bool == False:
            self.write_Data(self.OUTPUT_SAL_CMD.encode('utf-8') + self.YES + CR)
        else:
            return -1

    # Calculated in (meters/second)
    def set_output_sound_velocity(self, BOOLEAN):
        """
        If Yes: Calculates and outputs sound velocity in m/sec
        Output Format == OUTPUT_ROV == 3
        If No: Does not calculate nor output the sound velocity
        """
        if BOOLEAN == True:
            self.write_Data(self.OUTPUT_SOUND_VELOCITY.encode('utf-8') + self.YES + CR)
        if BOOLEAN == False:
            self.write_Data(self.OUTPUT_SOUND_VELOCITY.encode('utf-8') + self.NO + CR)

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
        self.write_Data("SetDefaults".encode('utf-8') + CR)


    def set_sample_avg(self, rate):
        """
        Range: 1-255 samples.
        Defines the number of values the CTD will average
        Outputs only the average.
        """
        if rate >= 1 and rate <= 255:
            return self.write_Data(self.SAMPLE_AVG.encode('utf-8') + rate + CR)
        else:
            return -1


    def set_min_conductivity(self, frequency):
        """
        Minimum conductivity frequency must be reached before pump turns on
        Ensures pump is in water before use
        Typical for salt water is 500 Hz
        Freshwater is 5Hz
        Default is 3000 Hz
        """
        self.write_Data(self.CONDUCTIVITY_FREQUENCY.encode('utf-8') + frequency + CR)


    def pump_delay(self, time):
        """
        Delays pump after Conductivity Frequency threshold has been met
        Used to allow tubing to fill with water
        Default 30 seconds
        Used when conductivity cell's frequency greater than min_conductivity
        """
        self.write_Data(self.TIME_TO_DELAY.encode('utf-8') + time + CR)


    # post-processing data is not applicable to use in AUVs and ROVs
    # ROV records data on command which 
    # prevents post-calculations from being performed. 
    # For more information, google it. 
    def process_data(self, Bool):
        """
        When Yes: Corrects for alignment, filtering, and conductivity cell thermal mass 
        for data in real time. 
        Cannot be used if output format is not 1 or 3.
        Note that post-processing data is not applicable for AUVs and ROVs.
        """
        if Bool == True:
            self.write_Data(self.PROCESS_DATA.encode('utf-8') + self.YES + CR)
        else:
            self.write_Data(self.PROCESS_DATA.encode('utf-8') + self.NO + CR)


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
        if Temp_Time >= 0 and Temp_Time <= 0.125:
            self.write_Data(self.TEMP_ADVANCE.encode('utf-8') + Temp_Time + CR)
        else: 
            return -1 


    def thermal_cell_alpha(self, Alpha):
        """
        Conductivity Cell Thermal Mass Alpha Correction
        corrects amplitude
        Range: 0.02 to 0.05
        Default: 0.03
        Conditions: ProcessRealTime=Y (default)
        OutputFormat=1 or 3
        """
        if Alpha >= 0.02 and Alpha <= 0.05:
            self.write_Data(self.ALPHA_COEFFICIENT.encode('utf-8') + Alpha + CR)
        else: 
            return -1

    def thermal_cell_tau(self, Tau):
        """
        Conductivity Cell Thermal Mass Tau Correction
        Corrects time constant
        Range: 5.0 to 10.0
        Default: 7.0
        Conditions: ProcessRealTime=Y (default) and OutputFormat=1 or 3
        """
        if Tau >= 5 and Tau <= 10:
            self.write_Data(self.TAU_COEFFICIENT.encode('utf-8') + Tau + CR)
        else:
            return -1

    def auto_sample(self, Bool):
        """
        Auto_Sample = YES starts autonomous sampling automatically
        Must turn power off and on or call start_sample
        Default: auto_sample = NO
        When Auto_sample is no, must turn on Power
        Waits for command when power is ON
        """
        if Bool == True:
            self.write_Data(self.AUTO_SAMPLE.encode('utf-8') + self.YES + CR)
        else:
            self.write_Data(self.AUTO_SAMPLE.encode('utf-8') + self.NO + CR)

    def start_sample(self):
        """
        begins autonomous sampling (when auto_sample = NO)
        May need to send if auto_sample = YES command was just sent 
        """
        self.write_Data(self.START_SAMPLE.encode('utf-8') + CR)


    def stop_sample(self):
        """
        must press enter key to get S> prompt before entering Stop
        May need to send command multiple times for a response
        Backup is to remove power
        """
        self.write_Data(self.STOP_SAMPLE.encode('utf-8') + CR)



    #**************************Polled Sampling Commands***********************

    def pump_on(self):
        """
        Must turn pump on before calling take_sample or testing pump
        """
        self.write_data(self.PUMP_ON.encode('utf-8') + CR)

    def pump_off(self):
        """
        Literally just turns the pump off. 
        """
        self.write_data(self.Pump_OFF.encode('utf-8') + CR)

    def take_sample(self):
        """
        Takes 1 sample and transmits the data
        """
        self.write_data(self.TAKE_SAMPLE.encode('utf-8') + CR)

    #************************ Testing Commands *******************************
    ## OUTPUTS???
    def test_temp(self):
        """
        Measure temperature and transmits 100 samples of converted data
        """
        self.write_data(self.TEST_TEMP.encode('utf-8') + CR)

    def test_conductivity(self):
        """
        Measures conductivity and transmits 100 samples of converted data
        """
        self.write_data(self.TEST_CONDUCTIVITY.encode('utf-8') + CR)

    def test_pressure(self):
        """
        Measures pressure transmits 100 samples of converted data
        """
        self.write_data(self.TEST_PRESSURE.encode('utf-8') + CR)

    def test_temp_raw(self):
        """
        Measures temperature, transmits 100 samples of raw data
        """
        self.write_data(self.TEST_TEMP_RAW.encode('utf-8') + CR)

    def test_conductivity_raw(self):
        """ 
        measures conductivity, transmits 100 samples of raw data
        """
        self.write_data(self.TEST_CONDUCTIVITY_RAW.encode('utf-8') + CR)

    def test_pressure_raw(self):
        """
        Measures pressure, transmits 100 samples of raw data
        """
        self.write_data(self.TEST_CONDUCTIVITY_RAW.encode('utf-8') + CR)
