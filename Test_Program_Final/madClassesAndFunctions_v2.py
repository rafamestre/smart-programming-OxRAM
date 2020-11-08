# -*-coding:Latin-1 -*

import serial

##################################################
## CLASS DEFINITION
##################################################

class AddressingTrigger:
        def __init__(self, channel, duration, delay):
                # get class parameters
                self.channel = channel
                self.duration = duration
                self.delay = delay

class SingleOperation:
        def __init__(self, name, vTop, vBot, vGate, tTop, tBot, tGate):
                # get class parameters
                self.name = name
                self.vTop = vTop
                self.vBot = vBot
                self.vGate = vGate
                self.tTop = tTop
                self.tBot = tBot
                self.tGate = tGate

class ReadOperation:
        def __init__(self, name, iRange, vRange, vReadTop, vReadBot, vReadGate, duration):
                # settling time dictionary (as a function of current range), do not modify
                Setl_time = {'10mA':100e-9, '1mA':250e-9, '100uA':1e-6, '10uA':10e-6, '1uA':80e-6}
                # get class parameters
                self.name = name
                self.iRange = iRange
                self.vRange = vRange
                self.vReadTop = vReadTop
                self.vReadBot = vReadBot
                self.vReadGate = vReadGate
                self.duration = duration
                # define rise and fall times for read operation
                tRise = 1e-6
                tFall = 1e-6
                # calculate real pulse width (range-dependend current establishment + averaging)
                pulseWidth = self.duration + Setl_time.get(self.iRange)
                # generate V and time vectors, in PIV format
                self.vTop = [vReadTop,vReadTop,0]
                self.vBot = [vReadBot, vReadBot, 0]
                self.vGate = [vReadGate,vReadGate,0]
                self.tTop = [tRise, pulseWidth, tFall]
                self.tBot = [tRise, pulseWidth, tFall]
                self.tGate = [tRise, pulseWidth, tFall]
                # generate meas parameters for PIV meas function (meas start time, nb of meas points, sampling, averaging)
                self.measParams = [tRise + Setl_time.get(self.iRange), 1, self.duration, self.duration]
      
class Arduino:
        def _init_(self):
                self.adrsMode = ''
                self.adrsSingle = ''
                self.startAdrs = ''
                self.stopAdrs = ''
                self.stopAll = ''
        # load adresses in Arduino        
        def programAddressing(self, adrsMode, adrsSingle, startAdrs, stopAdrs, stopAll):
                # get addresses
                self.adrsMode = adrsMode
                self.adrsSingle = adrsSingle
                self.startAdrs = startAdrs
                self.stopAdrs = stopAdrs
                self.stopAll = stopAll
                # set Arduino status
                connected = False
                #open USB serial port
                try:
                        ser = serial.Serial("COM3", 9600)
                except:
                        try:
                                ser = serial.Serial("COM2", 9600)
                        except:
                                ser = serial.Serial("COM1", 9600)
                # loop until Arduino is connected (Arduino sends "1" when executing its setup() function)
                while not connected:
                        serin = ser.read()
                        connected = True
                # send address mode
                ser.write(self.adrsMode)
                # send addresses
                if self.adrsMode == 'A':
                        ser.write(self.adrsSingle)
                else:
                        ser.write(self.startAdrs + self.stopAdrs + self.stopAll)        
                #elif self.adrsMode == 'S':
                #        ser.write(self.startAdrs + self.stopAdrs + self.stopAll)
                # wait until Arduino is fully programmed (returns "0") 
                while ser.read() != '0':
                        ser.read()
                # close port
                ser.close()
        # function to be called when finishing single address characterization
        def stopSingleAddressing(self):
                connected = False
                ser = serial.Serial("COM3", 9600)
                while not connected:
                        serin = ser.read()
                        connected = True
                ser.write('R')
                ser.close()
