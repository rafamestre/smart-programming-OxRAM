#############################################################################################################################################
#  program modified from final_RRAM_Prog_v3.1.py
#	
#  To clarify, and to prevent issues, program is now renamed final_oxram_prog_v3.1.py
#	14/03/2016	A.A     V3.2	Add the use of PIV to drive Vdd
#                       		Data are recorded with only 3 digits behind coma to reduce datalog size (convert function)
#                                       Before 1Mbit gave a 59Mb file, now it is 25Mb file
#	15/03/2016	A.A 	V3.3	Reading of a list of addresses to be tested (file address_list.txt) (Functions parser & address_list)
#					Hide of cascade prober
#	16/03/2016	A.A	V3.4	Add the possibility to repeat subsequences ie call to variables_testParams_v3
#	16/03/2016	A.A	V3.5    Correction of bitmapping
#       24/03/2016      R.M     V3.6    Main function defined. It is needed in order to be able to call the execution several
#                                       times from a different file as object.main()
#
#
#############################################################################################################################################

# -*-coding:Latin-1 -*

import B1530driver as B1530
import serial
import visa
import re
import os as os
import numpy as np
import scipy as scipy
import datetime as dt
import shutil
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cm
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_pdf import PdfPages
#from time import time
import time
import csv
import wx
import sys
import locale


from madClassesAndFunctions_v3 import AddressingTrigger
from madClassesAndFunctions_v3 import SingleOperation
from madClassesAndFunctions_v3 import ReadOperation
from madClassesAndFunctions_v3 import Arduino
from madClassesAndFunctions_v3 import SmartStrategy 


# important! change both 'userFile = XXX ' and 'import XXX as var' according to file name
userFile = "variables_testParams_v3"
import variables_testParams_v3 as var


#With respect to v2, WLs are read first, before changing BL
##################################################
## FUNCTIONS DEFINITION
##################################################

# This function allows to repeat a sequence of test
def testPlan_uncompress(testplan_compressed):
    testPlan=[]
    counter=1
    if isinstance(testplan_compressed,list) is True:
        if len(testplan_compressed) > 1:
            for i in range(0,len(testplan_compressed)):
                if isinstance(testplan_compressed[i], int) is True: 
                    counter=testplan_compressed[i] 
                else:    
                    if isinstance(testplan_compressed[i], list) is True: 
                        for j in range (0,counter):               
                            testPlan.extend(testplan_compressed[i])
                        counter=1    
                    else:
                        for j in range (0,counter):               
                            testPlan.extend([testplan_compressed[i]])
                        counter=1
        elif len(testplan_compressed) == 1:
            if isinstance(testplan_compressed[0],list) is True:
                testPlan.extend(testplan_compressed[0])
                if isinstance(testplan_compressed[0][0],list) is True:
                    raise NameError('Too many nested lists in testPlan')
            else:
                testPlan.extend(testplan_compressed)
    elif isinstance(testplan_compressed,list) is False:
        testPlan = [testplan_compressed]
                
    return testPlan

# This function is parsing the address list file to be tested in case "Single Address is selected"
def parser(line_to_parse):
    if re.match(r"(^[0-9]*[0-9]*)", line_to_parse) is not None:
        data=re.findall("([0-9]*),", line_to_parse)
        if len(data)==3:
            return data[0],data[1],data[2]
        else:
            return '','',''

# This function fills an array with the list of addresses to be tested in case "Single Address is selected", and provides the array size
# Tableau = array of selected addresses
# i= number of lines of the array
def address_list():
    fichier = open(var.addressList, "r")
    # We read the header of address list
    line=fichier.readline()
    i=0
    tableau=[[]]
    while line!="":
        #Here we are filling an array with the different addresses
        line=fichier.readline()
        data0,data1,data2=parser(line)
        if data0!='':
            if i==0:
                tableau= [[int(data0), int(data1),int(data2)]]
            else:    
                tableau.append([int(data0), int(data1),int(data2)])            
            i=i+1
    fichier.close()
    return tableau,i

# This function reduces the number of digit of a float (used to reduce file size)
# data_int is the float to be converted ex: 0.156188484848e-6
# digit is the number of digit allowed, eg if digit=5 then data_out=0.15618e-6
def convert(data_int, digit):
    exposant=""
    data_int_char=str(data_int)
    data=re.findall("(.*\.[0-9]{%s})"%(digit), data_int_char)[0]  
# If the format of input integrates exponent    
    if re.match(r"(.*\.[0-9]*[eE]+[0-9]*)", data_int_char) is not None:
        exposant=re.findall("e.+", data_int_char)[0]
    data_out=data+exposant
    #data_out=float(data_out)
    return data_out

def loadPIV(topCh, botCh, gateCh, operation, measMatrixMode, nbMeas, trigParams):
        # clear all PIV patterns
        B1530.clear()
        # define PIV patterns names
        topPattern = 'topPat_'+ operation.name
        botPattern = 'botPat_'+ operation.name
        gatePattern = 'gatePat_'+ operation.name
        # create PIV patterns
        B1530.createPattern(topPattern, 0.0)
        B1530.createPattern(botPattern, 0.0)
        B1530.createPattern(gatePattern, 0.0)
        # update PIV patterns with V and t values
        B1530.addVectors(topPattern, operation.tTop, operation.vTop, len(operation.tTop))
        B1530.addVectors(botPattern, operation.tBot, operation.vBot, len(operation.tBot))
        B1530.addVectors(gatePattern, operation.tGate, operation.vGate, len(operation.tGate))
        # set operation modes (PG for gate in order to benefit from more aggressive timing capabilities (MRAM)
        B1530.setOperationMode(topCh, B1530._operationMode['fastiv'])
        B1530.setOperationMode(botCh, B1530._operationMode['fastiv'])
        B1530.setOperationMode(gateCh, B1530._operationMode['pg'])
        # if read operation, define measurements to be performed
        if operation.__class__ is ReadOperation:
                # measure events for attached to each pattern
                B1530.setMeasureEvent(topPattern, "topMeas", operation.measParams[0], operation.measParams[1], operation.measParams[2], operation.measParams[3], B1530._measureEventData['averaged'])
                B1530.setMeasureEvent(botPattern, "botMeas", operation.measParams[0], operation.measParams[1], operation.measParams[2], operation.measParams[3], B1530._measureEventData['averaged'])
                B1530.setMeasureEvent(gatePattern, "gateMeas", operation.measParams[0], operation.measParams[1], operation.measParams[2], operation.measParams[3], B1530._measureEventData['averaged'])
                # measurement modes (V or I)
                B1530.setMeasureMode(topCh, B1530._measureMode['voltage'])
                B1530.setMeasureMode(botCh, B1530._measureMode['current'])
                B1530.setMeasureMode(gateCh, B1530._measureMode['voltage'])
                # measurement ranges
                B1530.setMeasureVoltageRange(topCh, B1530._measureVoltageRange[operation.vRange])
                B1530.setMeasureCurrentRange(botCh, B1530._measureCurrentRange[operation.iRange])
                B1530.setMeasureVoltageRange(gateCh, B1530._measureVoltageRange[operation.vRange])
        # define trigger operation when scan mode ('S')
        if measMatrixMode == 'S' or measMatrixMode == 'L':
                # create trig pattern @V=0 to be added before Operation patterns (wait for addressing...)
                B1530.createPattern('trigPattern', 0.0)
                # update trig pattern according to addressing delay
                B1530.addVector('trigPattern', trigParams.delay, 0.0)
                # attach trigger event to the trigger pattern
                B1530.setTriggerOutMode(trigParams.channel, B1530._triggerOutMode['event'], B1530._triggerOutPolarity['positive'])
                B1530.setTriggerOutEvent('trigPattern', 'trigEvent', 0.0, trigParams.duration)
                # finally, merge trig and operation patterns, in order to get final operation patterns with an addressing delay (timing of meas and trig events are automatically kept)
                B1530.createMergedPattern(topPattern, 'trigPattern', topPattern, B1530._axis['time'])
                B1530.createMergedPattern(botPattern, 'trigPattern', botPattern, B1530._axis['time'])
                B1530.createMergedPattern(gatePattern, 'trigPattern', gatePattern, B1530._axis['time'])
        # add final sequences to PIV channels, according to nbMeas
        B1530.addSequence(topCh, topPattern, nbMeas)
        B1530.addSequence(botCh, botPattern, nbMeas)
        B1530.addSequence(gateCh, gatePattern, nbMeas)
        # connect B1530 channels
        B1530.connect(topCh)
        B1530.connect(botCh)
        B1530.connect(gateCh)

# function returning addresses list (when scan mode)
def adrsTable(scanMode,startBtl, startWl, startWlm, stopBtl, stopWl, stopWlm, stopWlall, stopBtlall):
        adrs = []
        strBtl = '{0:08b}'.format(startBtl)
        strWl = '{0:08b}'.format(startWl)
        strWlm = '{0:04b}'.format(startWlm)
        stpBtl = '{0:08b}'.format(stopBtl)
        stpWl = '{0:08b}'.format(stopWl)
        stpWlm = '{0:04b}'.format(stopWlm)
        firstAdrs = int(strWlm + strWl + strBtl, 2)
        secAdrs = int(stpWlm + stpWl + stpBtl, 2)
        noAdrs = secAdrs - firstAdrs + 1
                
        if scanMode == 'All':    
            for i in range(noAdrs):
                adrs1=[]
                adrs1.append(str(startWlm))
                adrs1.append(str(startWl))
                adrs1.append(str(startBtl))
                adrs.append(adrs1)
                startWl= startWl+1
                if (startWl == stopWlall+1) and (startBtl != stopBtlall):
                        startBtl += 1
                        startWl = 0
                elif startWl == stopWlall+1 and startBtl == stopBtlall and startWlm != stopWlm:
                        startWlm += 1
                        startWl = 0
                        startBtl = 0
        elif scanMode=="CKBD":
            #noAdrs=noAdrs/2
            for i in range(noAdrs):            
                adrs1=[]
                adrs1.append(str(startWlm))
                adrs1.append(str(startWl))
                adrs1.append(str(startBtl))
                adrs.append(adrs1)
                startWl= startWl+2
                if ((startWl == stopWlall+1) and (startBtl != stopBtlall) and (startBtl%2)==0):         
                    startBtl += 1
                    startWl = 1
                elif ((startWl == stopWlall+2) and (startBtl != stopBtlall) and (startBtl%2)!=0): 
                    startBtl += 1
                    startWl = 0
                elif ((startWl == stopWlall+2) and (startBtl == stopBtlall) and (startWlm != stopWlm)):
                    startWlm += 1
                    startWl = 0
                    startBtl = 0
        elif scanMode=="ICKBD":
            #noAdrs=noAdrs/2
            for i in range(noAdrs):            
                adrs1=[]
                if ((startWl == 0) and (startBtl == 0)):
                    startWl=1
                adrs1.append(str(startWlm))
                adrs1.append(str(startWl))
                adrs1.append(str(startBtl))
                adrs.append(adrs1)
                startWl= startWl+2
                if ((startWl == stopWlall+2) and (startBtl != stopBtlall) and (startBtl%2)==0): 
                    startBtl += 1
                    startWl = 0
                elif ((startWl == stopWlall+1) and (startBtl != stopBtlall) and (startBtl%2)!=0): 
                    startBtl += 1
                    startWl = 1
                elif ((startWl == stopWlall+2) and (startBtl == stopBtlall) and (startWlm != stopWlm)):
                    startWlm += 1
                    startWl = 0
                    startBtl = 0
        elif scanMode == "RS":
            #noAdrs=noAdrs/2
            for i in range(noAdrs):
                adrs1=[]
                adrs1.append(str(startWlm))
                adrs1.append(str(startWl))
                adrs1.append(str(startBtl))
                adrs.append(adrs1)
                startWl= startWl+2
                if (startWl == stopWlall+1) and (startBtl != stopBtlall):
                        startBtl += 1
                        startWl = 0
                elif startWl == stopWlall+1 and startBtl == stopBtlall and startWlm != stopWlm:
                        startWlm += 1
                        startWl = 0
                        startBtl = 0
        elif scanMode == "IRS":
            #noAdrs=noAdrs/2
            for i in range(noAdrs):
                adrs1=[]
                if ((startWl == 0) and (startBtl == 0)):
                    startWl=1
                adrs1.append(str(startWlm))
                adrs1.append(str(startWl))
                adrs1.append(str(startBtl))
                adrs.append(adrs1)
                startWl= startWl+2
                if (startWl == stopWlall+2) and (startBtl != stopBtlall):
                        startBtl += 1
                        startWl = 1
                elif startWl == stopWlall+2 and startBtl == stopBtlall and startWlm != stopWlm:
                        startWlm += 1
                        startWl = 1
                        startBtl = 0
        return adrs
    
# function creating a new folder if not already existing, then Test_xxx subfolder which increment at each run                
def createFolder(now=None):
        folders = []
        y = []
        if now is None:
            now = dt.datetime.now()
        mypath = r'%s\%s\%s' % (var.resultsOutput,
                                var.waferLot + 'w' + var.waferNo,
                                now.strftime("%Y-%m-%d")+"__test="+var.testName+"__dut="+var.dutName)
        if not os.path.exists(mypath):
                os.makedirs(mypath)
        folders = [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]
        if not folders:
                testname = "Test_000"
        else:
                for i in range(len(folders)):
                        y.sort(y.append(int(folders[i][-3:])))   #return a list of the last 3 digits in folders as integers
                for i in range(len(y)):
                        if i != y[i]:
                                x = i
                        else:
                                x = y[len(y)-1]+1
                testname = 'Test_%s' % ((3 - len(str(x)))*"0" + str(x))
        resultsLoc = r'%s\%s' % (mypath, testname)
        if not os.path.exists(resultsLoc):
                os.makedirs(resultsLoc)
        return resultsLoc

def createFolder_SmartProgramming(now=None):   ##########!!!!!!!!!!!!!!!!!!!!!!!!!!!
        folders = []
        y = []
        if now is None:
            now = dt.datetime.now()
        mypath = r'%s\%s\%s' % (var.resultsOutput,
                                var.waferLot + 'w' + var.waferNo,
                                now.strftime("%Y-%m-%d")+"__test="+var.testName+"__dut="+var.dutName)
        if not os.path.exists(mypath):
                os.makedirs(mypath)
        folders = [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]
        if not folders:
                testname = "Test_000"
        else:
                for i in range(len(folders)):
                        y.sort(y.append(int(folders[i][-3:])))   #return a list of the last 3 digits in folders as integers
                testname = 'Test_%s' % ((3 - len(str(y[-1])))*"0" + str(y[-1]))
        resultsLoc = r'%s\%s' % (mypath, testname)
        return resultsLoc    

# function creating die folder depending on die coordinates
def dieFolder(loc, die, x=0, y=0):
        """ function to create a folder depending on die no and location : dieNo_xNo_yNo"""
        rsl_loc = loc +'\\'+'x'+str(x)+'_'+'y'+str(y)
        if os.path.exists(rsl_loc) is not True:
            os.makedirs(rsl_loc)
        return rsl_loc

# write read operation results
########!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def writeResultFile(location, test, adrsList, topV, botI, gateV, seqCounts):
        if os.path.exists("%s\\%s.csv" % (location,"results")) is not True:
            flag=1
        else:
            flag=0
        rslfile = open("%s\\%s.csv" % (location,"results"), "ab")
        if flag==1:
            rslfile.write("adrs mode:" + "," + var.adrsMode + "," + "\n")
        if var.adrsMode == 'S':
                rslfile.write("first adrs:,{0},final adrs:,{1},no adrs:,{2}, \n".format('/'.join(adrsList[0]),'/'.join(adrsList[len(adrsList)-1]),str(len(adrsList))))
        if var.adrsMode=='S':
                rslfile.write("topVmeas," + convert(topV[0],4) + ",gateVmeas," + convert(gateV[0],4)+ ",\n")                
                rslfile.write("\n" + "Address,,," +"Results," + "\n" )                
                rslfile.write("SL," + "WL," + "BL," + "Rmeas," + "\n")
                for index in range(seqCounts):
                        rslfile.write(str(adrsList[index][0]) + "," + str(adrsList[index][1]) + ","
                                                        + str(adrsList[index][2]) + "," + str((-1*topV[index]/botI[index]))
                                                        + "," + "\n")																											
        if var.adrsMode=="A":
                if flag==1:
                    rslfile.write("topVmeas," + convert(topV[0],4) + ",gateVmeas," + convert(gateV[0],4)+ ",\n")
                    rslfile.write("\n" + "Address,,," +"Results," + "\n\n" )  
                    rslfile.write("SL," + "WL," + "BL," + "Rmeas," + "\n")
                for index in range(seqCounts):
                        rslfile.write(str(adrsList[0][0]) + "," + str(adrsList[0][1]) + ","
                                                + str(adrsList[0][2]) + "," +str((-1*topV[index]/botI[index])) + "," + "\n")						
        if var.adrsMode == 'L':
                if flag==1:
                    rslfile.write("topVmeas," + convert(topV[0],4) + ",gateVmeas," + convert(gateV[0],4)+ ",\n")
                    rslfile.write("\n" + "Address,,," +"Results," + "\n\n" )  
                    rslfile.write("SL," + "WL," + "BL," + "Rmeas," + "\n")
                for index in range(seqCounts):
                        rslfile.write(str(adrsList[index][0]) + "," + str(adrsList[index][1]) + ","
                                                        + str(adrsList[index][2]) + "," + str((-1*topV[index]/botI[index]))
                                                        + "," + "\n")
        rslfile.close()

# NOTE: THE BITMAP IS NOW CREATED IN THE STATISTICAL ANALYSIS MODULE
def generateBitmap(R, loc):
        app= wx.App(False)
        app.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        R2 = []
        if var.mtxSize=='1M':
            fig, (ax) = plt.subplots()        	
            pp = PdfPages(r'%s/Bitmap.pdf'%loc)
            plt.ylabel('Bitline', fontsize=10)
            plt.xlabel('Wordline', fontsize=10)        
            for i in range(0,16):
                R2 = []
                for j in range(0,256):     
                    R2.append(R[(i*256+j)*256:((i*256+j)*256)+256])
                image = np.array(R2)
                plt.title('Sector%s'%i)
                plt.imshow(image, cmap=cm.jet, interpolation='nearest',aspect='auto', origin='lower')   ## if log scale add: norm=matplotlib.colors.LogNorm(vmin=1e7, vmax=2e8))
                if i==0:
                    cbar = plt.colorbar(orientation='vertical', format='%.1e')  # colour bar
                pp.savefig()
            pp.close()            
        else:
            if var.mtxSize=='64K':
                stopWl = 256
                for i in range(len(R)/stopWl):
                    R2.append(R[i*stopWl:(i*stopWl)+stopWl])
                print(locale.getdefaultlocale())
                fig,(ax) = plt.subplots()        	
                image = np.array(R2)
                plt.imshow(image, cmap=cm.jet, interpolation='nearest',aspect='auto', origin='lower')   ## if log scale add: norm=matplotlib.colors.LogNorm(vmin=1e7, vmax=2e8))
                cbar = plt.colorbar(orientation='vertical', format='%.1e')  # colour bar 
                #cbar.ax.tick_params(labelsize=8)                             # set the label size of the colour bar
                #plt.clim(4e7,2e8)                                            # set the limits of the colour bar
                plt.ylabel('Bitline', fontsize=10)
                plt.xlabel('Wordline', fontsize=10)
                plt.savefig(r'%s/Bitmap_expanded.pdf'%loc)                            #save bitmap.pdf
                plt.clf()
                stopWl = 16
                R2 = []
            else:
                stopWl = 16
                
            for i in range(len(R)/stopWl):
                R2.append(R[i*stopWl:(i*stopWl)+stopWl])
            fig,(ax) = plt.subplots()        	
            image = np.array(R2)
            plt.imshow(image, cmap=cm.jet, interpolation='nearest',aspect='auto', origin='lower')   ## if log scale add: norm=matplotlib.colors.LogNorm(vmin=1e7, vmax=2e8))
            cbar = plt.colorbar(orientation='vertical', format='%.1e')  # colour bar 
            #cbar.ax.tick_params(labelsize=8)                             # set the label size of the colour bar
            #plt.clim(4e7,2e8)                                            # set the limits of the colour bar
            plt.ylabel('Bitline', fontsize=10)
            plt.xlabel('Wordline', fontsize=10)
            plt.savefig(r'%s/Bitmap.pdf'%loc)                            #save bitmap.pdf
            plt.clf()

# read address list in *.csv file and generate 1/ Arduino-compatible data to feed in and 2/ address list for retrieving PIV data (in 'L' mode)
def parseSingleAddressList(fileName):
        strTable = ['']*300
        pivInputMatrix = []
        nbLines = 0
        firstRow = True
        with open(fileName) as inputFile:
                for row in csv.reader(inputFile, delimiter=','):
                    if not firstRow:
                        strTable[np.divide(nbLines, 5)] += '%s/%s/%s/' % (str(row[0]), str(row[1]), str(row[2]))
                        temp=[]
                        temp.append(str(row[0]))
                        temp.append(str(row[1]))
                        temp.append(str(row[2]))
                        pivInputMatrix.append(temp)
                        nbLines +=1
                        # stop parsing if number of cells > Arduino Flash size
                        if nbLines == 1500:
                                break
                    firstRow = False
        finalTable=[]
        for x in strTable:
                if x != '':
                        finalTable.append(x)
        return finalTable, pivInputMatrix

##################################################
## IMPORT TEST PARAMETERS FILE
##################################################

#This method will be called externally if the module is being imported, by doing *.main(), or if the file is run (through the __main__ method)

def main(smart = 'n', operationNb = None, repetition = None, now = None):

    ##################################################
    ## MANAGE ADDRESSING...
    ##################################################

    # dictionaries to assign index to each matrix size + max BL/WL/SL
    mtxDic = {'256': 0, '4K':1, '64K':2, '1M':3}     
    nbWL = [0, 15, 255, 255]
    nbSL = [0, 0, 0, 15]
    nbBL = [255, 255, 255, 255]

    # retrieve addresses depending on scan mode
    ##if var.scanMode == 'All':
    ##        startBL = 0
    ##        startWL = 0
    ##        startSL = 0
    ##        stopBL = nbBL[mtxDic.get(var.mtxSize)]
    ##        stopWL = nbWL[mtxDic.get(var.mtxSize)]
    ##        stopSL = nbSL[mtxDic.get(var.mtxSize)]
    ##elif var.scanMode == 'Range':
    ##        startBL = var.startBL
    ##        startWL = var.startWL
    ##        startSL = var.startSL
    ##        stopBL = var.stopBL
    ##        stopWL = var.stopWL
    ##        stopSL = var.stopSL
    ##We consider only All mode
    startBL = 0
    startWL = 0
    startSL = 0
    stopBL = nbBL[mtxDic.get(var.mtxSize)]
    stopWL = nbWL[mtxDic.get(var.mtxSize)]
    stopSL = nbSL[mtxDic.get(var.mtxSize)]

    # set first, last, and max addresses (will be used only if scan mode is set)
    startAdrs = str(startSL)+'/'+str(startWL)+'/'+str(startBL)+'/'
    stopAdrs = str(stopSL)+'/'+str(stopWL)+'/'+str(stopBL)+'/'
    stopAll = str(nbWL[mtxDic.get(var.mtxSize)])+'/'+str(nbBL[mtxDic.get(var.mtxSize)])+'/'

    # calculate addresses list and number of measurements to perform
    singleAdrs=0
    single_address_number=1
    if var.adrsMode == 'A':
        array_single_address,single_address_number=address_list()
        ardStrTable = []
    elif var.adrsMode == 'S':
        adrsList = adrsTable(var.scanMode,startBL, startWL, startSL, stopBL, stopWL, stopSL, nbWL[mtxDic.get(var.mtxSize)], nbBL[mtxDic.get(var.mtxSize)])
        ardStrTable = []
        if var.scanMode in var.patterns:
            #In case selected pattern is CKBD/ICKBD
            seqCounts = int(len(adrsList)/2)
        else:    
            seqCounts = len(adrsList)
    elif var.adrsMode == 'L':
        ardStrTable, adrsList = parseSingleAddressList(var.addressList)
        seqCounts = len(adrsList)

    ##################################################
    ## MAIN CODE
    ##################################################
    
    # create Arduino object
    print "Connecting Arduino...  ",
    ard = Arduino()
    print "OK"
    nbDice = 1

    # open B1530 session
    print "Opening and initializing B1530...  ",
    B1530.openSession(var.B1530_GPIB)
    B1530.initialize()
    print "OK"

    # Set Vdd
    print "Vdd connected at",var.Vddvalue,"V"
    B1530.setOperationMode(var.chVdd, B1530._operationMode['dc'])
    B1530.connect(var.chVdd)
    B1530.dcforceVoltage(var.chVdd, var.Vddvalue)
    # Wait 20ms
    time.sleep(0.02)

    # create test folder
    #####!!!!!!!!!!!!!!!!!!!!!!!!!
    if smart == 'Y' or smart == 'y':
        testFolder = createFolder_SmartProgramming(now)  ###It just keeps the last folder created to write the results
    else:
        testFolder = createFolder(now)
        
    #Die position
    pos = ['0','0']

    # We uncompress the test plan
    testPlan=testPlan_uncompress(var.testPlan)

    

    # If single address is not selected, then we loop only one time
    for i in range(0,single_address_number):
        # We select the different addresses in case single address mode is chosen
        if var.adrsMode == 'A':
            # set single address (will be used only if single mode is set)
            singleAdrs = str(array_single_address[i][0])+'/'+str(array_single_address[i][1])+'/'+str(array_single_address[i][2])+'/'
            adrsList = [[str(array_single_address[i][0]),str(array_single_address[i][1]),str(array_single_address[i][2])]]
            seqCounts = 1
        else:
            print "Measuring die "+str(i+1)+" (x="+str(pos[0])+"/y="+str(pos[1])+")"
            # loop over the number of tests per matrix
        for j in range(len(testPlan)):
            print "   Running following test: "+testPlan[j].name
            if var.adrsMode == 'A':
                print "Wln/WL/BL = " + str(array_single_address[i][0]) + "/" + str(array_single_address[i][1]) + "/" + str(array_single_address[i][2]) 
            # load Arduino parameters
            print "      Load Arduino program...  ",
            if var.scanMode in var.patterns:
                print var.dico_patterns[var.scanMode]
                ard.programAddressing(str(var.dico_patterns[var.scanMode]), singleAdrs, ardStrTable, startAdrs, stopAdrs, stopAll)
            else:
                ard.programAddressing(str(var.dico_patterns[var.adrsMode]), singleAdrs, ardStrTable, startAdrs, stopAdrs, stopAll)            
            # load B1530 patterns and parameters
            print "OK\n"
            print('      '+str(seqCounts)+' addresses')
            print "      Configuring B1530...  ",
    ################## LOAD PIV #####################################
            loadPIV(var.chTop, var.chBot, var.chGate, testPlan[j], var.adrsMode, seqCounts, var.trig)
            print "OK"
            # init B1530 outputs
            status = 0
            elapsT = 0
            totalT = 0
            error = 0
            # launch program and wait (either one matrix characterization or repeated meas. on a single cell)
            print "      Running test...  ",
            B1530.execute()
            while(status!=10000):
                error,status,elapsT,totalT = B1530.getStatus()
            print "OK"
            # if single address mode, send reset command to Arduino
            if var.adrsMode == 'A':
                ard.stopSingleAddressing()
            # create operation folder in Test_xxx
            #####!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            if testPlan[j].__class__ is ReadOperation:
                print "      Create operation folder...  ",
                if smart == 'n' or smart == 'N':
                    operationFolder = r'%s\%s' % (testFolder, "Op"+str(operationNb)+"__Read")
                    if not os.path.exists(operationFolder):
                        os.makedirs(operationFolder)
                    print "OK"
    ##                print "      Create parameter file...  ",
    ##                shutil.copy(userFile+".py", operationFolder)
    ##                print "OK"
                elif smart == "y" or smart == 'Y':
                    if repetition == 0:   ###If it's the first time (repetition 0) do not add the "rep"
                        operationFolder = r'%s\%s' % (testFolder, "Op"+str(operationNb)+"__Read") 
                    else:
                        operationFolder = r'%s\%s' % (testFolder, "Op"+str(operationNb)+"__Read_rep"+str(repetition))
                    if not os.path.exists(operationFolder):
                        os.makedirs(operationFolder)
                    print "OK"
    ##                if operationNb < 1:
    ##                    print "      Create parameter file...  ",
    ##                    shutil.copy(userFile+".py", operationFolder)
    ##                    print "OK"
            ######!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # if read operation, retrieve data and store in file
                # create die subfolder 
                print "      Create die folder...  ",
                dieFolderLoc = dieFolder(operationFolder, die=i+1, x=pos[0], y=pos[1])
                print "OK"
                # save results
                print "      Retrieve B1530 data (number of data = "+str(seqCounts)+")...  ",
                error, timeTemp, vTopTemp = B1530.getMeasureValues(var.chTop, 0, seqCounts)
                error, timeTemp, iBotTemp = B1530.getMeasureValues(var.chBot, 0, seqCounts)
                error, timeTemp, vGateTemp = B1530.getMeasureValues(var.chGate, 0, seqCounts)
                print "OK"
                # calculate resistance
                resistance = np.absolute(np.divide(vTopTemp, iBotTemp))
                averageR = np.average(resistance)
                stdDevR = np.std(resistance)
                print "      R average = "+str(averageR)+"  //  R standard deviation = "+str(stdDevR)
                # write results in file
                print "      Save data to file...  ",
                writeResultFile(dieFolderLoc, var.testName, adrsList, vTopTemp, iBotTemp, vGateTemp, seqCounts)
                print "OK"
                print('      '+str(len(resistance))+' values')

    # wait 20ms
    time.sleep(0.02)
    # terminate B1530 session
    B1530.disconnect(var.chVdd)
    B1530.closeSession()


            
#If the file is open directly, it will call the main method and start directly
if __name__=='__main__':
    
    main()





