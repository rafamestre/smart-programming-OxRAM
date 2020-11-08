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
#       18/03/2016      A.A     V4.0    Testflow written in excel file to have a better test flexibility
#                                       Add of a datalog in the root
#                                       Only Read directories are written
#       21/03/2016      A.A     V4.1    Add of log readpoints + directories are renamed during loops
#       22/03/2016      A.A     V4.2    Management of patterns (ckbd, Ickbd)
#       23/03/2016      A.A     V4.3    Management of CKB/ICKBD patterns in datalog 
#       24/03/2016      A.A     V4.4    Add of optional arguments for prober to parameter the chip position
#       29/03/2016      A.A     V4.5    Debug of 64kbits bitmap
#############################################################################################################################################

# -*-coding:Latin-1 -*

import B1530driver as B1530
import serial
import visa
import math
import re
import os as os
import numpy as np
import scipy as scipy
import datetime as dt
import shutil
import matplotlib.pyplot as plt
import matplotlib as mpl
import time
import xlrd
import xlwt
import sys

from matplotlib import cm
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_pdf import PdfPages
from madClassesAndFunctions_v2 import AddressingTrigger
from madClassesAndFunctions_v2 import SingleOperation
from madClassesAndFunctions_v2 import ReadOperation
from madClassesAndFunctions_v2 import Arduino

def main():
    #With respect to v2, WLs are read first, before changing BL
    ##################################################
    ## FUNCTIONS DEFINITION
    ##################################################
    # This function allows to repeat a sequence of test
    def uncompress(test):
        testPlan=[]
        counter=1
        test_temp=test.split(",")
        for j in range(len(test_temp)):        
            testPlan.append(var.dico[test_temp[j]])
        indice=len(test_temp)
        return testPlan,indice

    # This function creates a list of position were to "option read patterns" inside a loop
    def interval_list_creation(rpt_loop,interval,interval_type):
        inter_list_out=[]
        if interval<2:
            print "!!!!Error Interval must be >1!!!!"
        if interval_type=="LIN":
            for j in range(1,interval+1):
                if int(j*rpt_loop/interval)!=0:    
                    inter_list_out.append(int(j*rpt_loop/interval))
        elif interval_type=="LOG":
            for j in range(1,int(math.log10(rpt_loop))+2):
                for i in range(1,interval+1):
                    if j!=(int(math.log10(rpt_loop))+1) and int(i*math.pow(10,j)/interval)!=0:
                        inter_list_out.append(int(i*math.pow(10,j)/interval))
                    if j==(int(math.log10(rpt_loop))+1) and int(i*math.pow(10,j)/interval)!=0:
                            inter_list_out.append(int(i*rpt_loop/interval))
        else:
            print "!!!! Error !!!!"
            print "!!!! Bad syntax !!!!"
            print "!!!! only LIN or LOG are accepted !!!!"
        return inter_list_out

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
    def address_list(xls_file_to_read):
        worksheet = xls_file_to_read.sheet_by_name('Address_list')
        lines_nb = worksheet.nrows-1    
        tableau=[[]]
        
        #Loop on the different sequences to test (lines of xls file)
        for i in range (lines_nb):
            if i==0:
                tableau= [[int(worksheet.cell(i+1,0).value), int(worksheet.cell(i+1,1).value),int(worksheet.cell(i+1,2).value)]]
            else:    
                tableau.append([int(worksheet.cell(i+1,0).value), int(worksheet.cell(i+1,1).value),int(worksheet.cell(i+1,2).value)])            
        return tableau,lines_nb

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
            if measMatrixMode == 'S':
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
            return adrs

    # function creating a new folder if not already existing, then Test_xxx subfolder which increment at each run                
    def createFolder(waferLot,waferNo,Folder_creation_flag):
            folders = []
            y = []
            now = dt.datetime.now()
            mypath = r'%s\%s\%s' % (var.resultsOutput,
                                    waferLot + 'w' + waferNo,
                                    now.strftime("%Y-%m-%d")+"__test="+var.testName+"__dut="+var.dutName)
            if not os.path.exists(mypath):
                    os.makedirs(mypath)
            folders = [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]
            if Folder_creation_flag=="A":
                    testname= "Test_auto"
            elif not folders:
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

    # function creating die folder depending on die coordinates
    def dieFolder(loc, die, X, Y):
            """ function to create a folder depending on die no and location : dieNo_xNo_yNo"""
            rsl_loc = loc +'\\'+'x'+str(X)+'_'+'y'+str(Y)
            if os.path.exists(rsl_loc) is not True:
                os.makedirs(rsl_loc)
            return rsl_loc

    # write read operation results
    def writeResultFile(Address_mode,location, test, adrsList, topV, botI, gateV,seqCounts):
            if os.path.exists("%s\\%s.csv" % (location,"results")) is not True:
                flag=1
            else:
                flag=0
            rslfile = open("%s\\%s.csv" % (location,"results"), "ab")
            if flag==1:
                rslfile.write("adrs mode:" + "," + Address_mode + "," + "\n")
            if Address_mode == 'S':
                    rslfile.write("first adrs:,{0},final adrs:,{1},no adrs:,{2}, \n".format('/'.join(adrsList[0]),'/'.join(adrsList[len(adrsList)-1]),str(len(adrsList))))
            if Address_mode=='S':
                    rslfile.write("topVmeas," + convert(topV[0],4) + ",gateVmeas," + convert(gateV[0],4)+ ",\n")                
                    rslfile.write("\n" + "Address,,," +"Results," + "\n" )                
                    rslfile.write("SL," + "WL," + "BL," + "Rmeas," + "\n")
                    for index in range(seqCounts):
                            rslfile.write(str(adrsList[index][0]) + "," + str(adrsList[index][1]) + ","
                                                            + str(adrsList[index][2]) + "," + str((-1*topV[index]/botI[index]))
                                                            + "," + "\n")																											
            if Address_mode=="A":
                    if flag==1:
                        rslfile.write("topVmeas," + convert(topV[0],4) + ",gateVmeas," + convert(gateV[0],4)+ ",\n")                
                        rslfile.write("SL," + "WL," + "BL," + "Rmeas," + "\n")                    
                    for index in range(seqCounts):
                            rslfile.write(str(adrsList[0][0]) + "," + str(adrsList[0][1]) + ","
                                                    + str(adrsList[0][2]) + "," +str((-1*topV[index]/botI[index])) + "," + "\n")						
            rslfile.close()

    def writeLogFile(X,Y,path,comments):
            if os.path.exists("%s\\%s_X_%s_Y_%s.txt" % (path,"datalog",str(X),str(Y))) is not True:
                flag=1
            rslfile = open("%s\\%s_X_%s_Y_%s.txt" % (path,"datalog",str(X),str(Y)), "ab")
            rslfile.write(comments)
            rslfile.close()

    # create bitmap file
    def generateBitmap(R, loc):
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
            elif var.mtxSize=='64K':
                for i in range(len(R)/256):
                    R2.append(R[i*256:(i*256)+256])
                fig,(ax) = plt.subplots()        	
                image = np.array(R2)
                plt.imshow(image, cmap=cm.jet, interpolation='nearest',aspect='auto', origin='lower')   ## if log scale add: norm=matplotlib.colors.LogNorm(vmin=1e7, vmax=2e8))
                cbar = plt.colorbar(orientation='vertical', format='%.1e')  # colour bar 
                #cbar.ax.tick_params(labelsize=8)                             # set the label size of the colour bar
                #plt.clim(4e7,2e8)                                            # set the limits of the colour bar
                plt.ylabel('Bitline', fontsize=10)
                plt.xlabel('Wordline', fontsize=10)
                plt.savefig(r'%s/Bitmap.pdf'%loc)                            #save bitmap.pdf 	
            else:
                for i in range(0,len(R)/16):
                    R2.append(R[i*16:(i*16)+16])
                fig,(ax) = plt.subplots()        	
                image = np.array(R2)
                plt.imshow(image, cmap=cm.jet, interpolation='nearest',aspect='auto', origin='lower')   ## if log scale add: norm=matplotlib.colors.LogNorm(vmin=1e7, vmax=2e8))
                cbar = plt.colorbar(orientation='vertical', format='%.1e')  # colour bar 
                #cbar.ax.tick_params(labelsize=8)                             # set the label size of the colour bar
                #plt.clim(4e7,2e8)                                            # set the limits of the colour bar
                plt.ylabel('Bitline', fontsize=10)
                plt.xlabel('Wordline', fontsize=10)
                plt.savefig(r'%s/Bitmap.pdf'%loc)                            #save bitmap.pdf 	


    def run(AdrsMode,scanMode,count,singleAdrs,single_address_number,adrsList,seqCounts,testPlan,array_single_address,flag_loop,Test_number,loop_number,X,Y):    
        #Loop on the list of tests
        for j in range(len(testPlan)):
            # If single address is not selected, then we loop only one time
            for i in range(0,single_address_number):
                # We select the different addresses in case single address mode is chosen
                if AdrsMode == 'A':
                    # set single address (will be used only if single mode is set)
                    singleAdrs = str(array_single_address[i][0])+'/'+str(array_single_address[i][1])+'/'+str(array_single_address[i][2])+'/'
                    adrsList = [[str(array_single_address[i][0]),str(array_single_address[i][1]),str(array_single_address[i][2])]]
                    seqCounts = 1
                else:
                    print "Measuring die "+str(i+1)+" (x="+str(X)+"/y="+str(Y)+")"
                    # loop over the number of tests per matrix           
                print "   Running following test: "+testPlan[j].name
                if AdrsMode == 'A':
                    print "Wln/WL/BL = " + str(array_single_address[i][0]) + "/" + str(array_single_address[i][1]) + "/" + str(array_single_address[i][2]) 
                # load Arduino parameters
                #ard.programAddressing(AdrsMode, singleAdrs, startAdrs, stopAdrs, stopAll)
                if scanMode in var.patterns:               
                    ard.programAddressing(str(var.dico_patterns[scanMode]), singleAdrs, startAdrs, stopAdrs, stopAll)
                else:
                    ard.programAddressing(str(var.dico_patterns[AdrsMode]), singleAdrs, startAdrs, stopAdrs, stopAll)
                # load B1530 patterns and parameters
        ################## LOAD PIV #####################################
                loadPIV(var.chTop, var.chBot, var.chGate, testPlan[j], AdrsMode, seqCounts, var.trig)
                # init B1530 outputs
                status = 0
                elapsT = 0
                totalT = 0
                error = 0
                # launch program and wait (either one matrix characterization or repeated meas. on a single cell)
                B1530.execute()
                while(status!=10000):
                    error,status,elapsT,totalT = B1530.getStatus()
                # if single address mode, send reset command to Arduino
                if AdrsMode == 'A':
                    ard.stopSingleAddressing()
                # create operation folder in Test_xxx
                # Drectory is created only for Read operation
                if testPlan[j].__class__ is ReadOperation:
                    if flag_loop==1:
                        operationFolder = r'%s\%s' % (testFolder, "Op"+str(count+j+1)+"_"+testPlan[j].name+"_Test"+str(Test_number)+"_Loop"+str(loop_number))
                        if not os.path.exists(operationFolder):
                            os.makedirs(operationFolder)
                    else:                  
                        operationFolder = r'%s\%s' % (testFolder, "Op"+str(count+j+1)+"_"+testPlan[j].name)
                        if not os.path.exists(operationFolder):
                            os.makedirs(operationFolder)
                # copy parameters files only for the first operation            
                if (count+j+1)==1:
                    shutil.copy(userFile+".py", testFolder)
                    shutil.copy("testflow.xls", testFolder)
                #Write datalog
                if AdrsMode == 'A':
                    writeLogFile(X,Y,testFolder,str("Op"+str(count+j+1)+"_"+testPlan[j].name + "  Wln/WL/BL ="  + str(array_single_address[i][0]) + "/" + str(array_single_address[i][1]) + "/" + str(array_single_address[i][2]) + "\n"))  
                else:
                    writeLogFile(X,Y,testFolder,str("Op"+str(count+j+1)+"_"+testPlan[j].name +"\n"))                                       
                # if read operation, retrieve data and store in file
                if testPlan[j].__class__ is ReadOperation:
                    # create die subfolder 
                    dieFolderLoc = dieFolder(operationFolder,i+1, X, Y)
                    # save results
                    error, timeTemp, vTopTemp = B1530.getMeasureValues(var.chTop, 0, seqCounts)
                    error, timeTemp, iBotTemp = B1530.getMeasureValues(var.chBot, 0, seqCounts)
                    error, timeTemp, vGateTemp = B1530.getMeasureValues(var.chGate, 0, seqCounts)
                    # calculate resistance
                    resistance = np.absolute(np.divide(vTopTemp, iBotTemp))
                    averageR = np.average(resistance)
                    stdDevR = np.std(resistance)
                    print "      R average = "+str(averageR)+"  //  R standard deviation = "+str(stdDevR)
                    # write results in file
                    print "      Save data to file...  ",
                    writeResultFile(AdrsMode,dieFolderLoc, var.testName, adrsList, vTopTemp, iBotTemp, vGateTemp,seqCounts)
                    print "OK"
                    if AdrsMode == 'S' and scanMode=="All":
                        # create bitmap
                        print "   Save bitmap...  ",
                        generateBitmap(resistance, dieFolderLoc)
                        print "OK"
        
    ##################################################
    ## IMPORT TEST PARAMETERS FILE
    ##################################################

    # important! change both 'userFile = XXX ' and 'import XXX as var' according to file name
    userFile = "variables_testParams_v4_0"
    import variables_testParams_v4_0 as var

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


    ##################################################
    # Die position management in case of arguments usage
    ##################################################
    if len(sys.argv)==5:
        Lot_pos=str(sys.argv[0])
        Wafer_pos=str(sys.argv[1])
        X_pos=str(sys.argv[2])
        Y_pos=str(sys.argv[3])
        Folder_creation_flag=str(sys.argv[4])
    else:
        Lot_pos=var.waferLot
        Wafer_pos=var.waferNo
        X_pos=var.X_pos
        Y_pos=var.Y_pos
        Folder_creation_flag=""

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
    testFolder = createFolder(Lot_pos,Wafer_pos,Folder_creation_flag)

    testPlan=[]
    counter=0
    interval_flag=0
    interval_list=[]
    #Loop on the different sequences to test
    workbook = xlrd.open_workbook('testflow.xls')
    worksheet = workbook.sheet_by_name('Testflow')
    lines_nb = worksheet.nrows-1

    #array_single_adress contains a list a addresses to be tested in A mode
    #single_address_number contains the number of addresses to be testes
    array_single_address=[]
    array_single_address,single_address_number_temp=address_list(workbook)

    #Loop on the different sequences to test (lines of xls file)
    for sequences in range (lines_nb):
        #We calculate the addresses list and number of measurements to perform depending of AdrsMode field
        singleAdrs=0
        adrsList=[]
        seqCounts=0
        AdrsMode=str(worksheet.cell(sequences+1,1).value)
        scanMode=str(worksheet.cell(sequences+1,2).value)
        if AdrsMode == 'A':
            single_address_number=single_address_number_temp
        elif AdrsMode == 'S':
            single_address_number=1
            adrsList = adrsTable(scanMode,startBL, startWL, startSL, stopBL, stopWL, stopSL, nbWL[mtxDic.get(var.mtxSize)], nbBL[mtxDic.get(var.mtxSize)])
            if scanMode in var.patterns:
                #In case selected pattern is CKBD/ICKBD/RS/IRS/CS/ICS
                seqCounts = int(len(adrsList)/2)
            else:    
                seqCounts = len(adrsList)
        #We uncompress the test plan
        testPlan,indice=uncompress(str(worksheet.cell(sequences+1,3).value))
        # We check if sequence has to be added at regular interval
        if (str(worksheet.cell(sequences+1,4).value)!='' and str(worksheet.cell(sequences+1,5).value)!='' and str(worksheet.cell(sequences+1,6).value)!=''):
            interval_list=interval_list_creation(int(worksheet.cell(sequences+1,0).value),int(worksheet.cell(sequences+1,5).value),str(worksheet.cell(sequences+1,6).value))                   
            #We uniquify the list "interval_list"
            interval_list=list(set(interval_list))
            interval_flag=1
        else:
            interval_list=[]
            interval_flag=0
        #We loop on the number of executions (Loop field)
        loop=worksheet.cell(sequences+1,0).value
        for lp in range(int(loop)):
            #Launch of "option read" (cf field in xls file)
            if interval_flag==1:
                if lp in interval_list:
                    #We read the subsequence to be applied at the right interval
                    testPlan_option_read,indice_option_read=uncompress(str(worksheet.cell(sequences+1,4).value))
                    run(AdrsMode,scanMode,counter,singleAdrs,single_address_number,adrsList,seqCounts,testPlan_option_read,array_single_address,1,lines_nb,lp,X_pos,Y_pos)
                    counter=counter+indice_option_read
                    run(AdrsMode,scanMode,counter,singleAdrs,single_address_number,adrsList,seqCounts,testPlan,array_single_address,0,0,0,X_pos,Y_pos)
                    counter=counter+indice
                else:
                    run(AdrsMode,scanMode,counter,singleAdrs,single_address_number,adrsList,seqCounts,testPlan,array_single_address,0,0,0,X_pos,Y_pos)
                    counter=counter+indice
            else:
                run(AdrsMode,scanMode,counter,singleAdrs,single_address_number,adrsList,seqCounts,testPlan,array_single_address,0,0,0,X_pos,Y_pos)
                counter=counter+indice
        if interval_flag==1:
            run(AdrsMode,scanMode,counter,singleAdrs,single_address_number,adrsList,seqCounts,testPlan_option_read,array_single_address,1,lines_nb,int(loop),X_pos,Y_pos)
            counter=counter+indice_option_read
        testPlan=[]
    # wait 20ms
    time.sleep(0.02)
    # terminate B1530 session
    B1530.disconnect(var.chVdd)
    B1530.closeSession()


main()









