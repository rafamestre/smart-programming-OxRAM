#############################################################################################################################################
#  program modified from final_oxram_prog_v4.7.py
#	
#       14/04/2016      A.A     V1.0    Initial revision
#       18/04/2016      A.A     V1.1    Add dynamic trig parameters   
#       20/04/2016      A.A     V1.2    Add smart forming parameter    
#       21/04/2016      A.A     V1.3    Parameters switched from py file to testflow file
#
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
from madClassesAndFunctions_v3 import AddressingTrigger
from madClassesAndFunctions_v3 import SingleOperation
from madClassesAndFunctions_v3 import ReadOperation
from madClassesAndFunctions_v3 import Arduino
# IMPORT TEST PARAMETERS FILE
userFile = "endurance_testParams_v4_4"
import endurance_testParams_v4_4 as var

#With respect to v2, WLs are read first, before changing BL
##################################################
## FUNCTIONS DEFINITION
##################################################
# This function allows to repeat a sequence of test
def uncompress(test):
    testPlan=[]
    testPlan_str=[]
    counter=1
    test_temp=test.split(",")
    for j in range(len(test_temp)):        
        testPlan.append(var.dico[test_temp[j]])
        testPlan_str.append(test_temp[j])
    indice=len(test_temp)
    return testPlan,testPlan_str,indice

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

# This function analyze the test flow step by step
def parser(testPlan,testPlan_str,counter,counter_rst,counter_set,counter_forming,previous_state,dico_temp,log_dir):
    for k in range(len(testPlan_str)):
        if testPlan[k].name is "Reset":
            counter_rst=counter_rst+1
            dico_temp["Reset"]=counter_rst
            previous_state="Reset"                        
        elif testPlan[k].name is "Set":
            counter_set=counter_set+1
            dico_temp["Set"]=counter_set
            previous_state="Set"                        
        elif testPlan[k].name is "Forming":
            counter_forming=counter_forming+1
            dico_temp["Forming"]=counter_forming
            previous_state="Forming"                        
        elif testPlan[k].name is "Read":                        
            if previous_state=="":
                log_dir.append("Op" + str(counter) + "_Read" + previous_state)
            elif previous_state=="Read":
                log_dir.append("Op" + str(counter) + "_Read_" + previous_state)                
            else:     
                log_dir.append("Op" + str(counter) + "_Read_" + previous_state + "_" + str(dico_temp[previous_state]))
            previous_state="Read"
            counter=counter+1
    return counter,counter_rst,counter_set,counter_forming,previous_state,dico_temp,log_dir

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


############################################################################
# This function creates patterns used for smart forming       
# It creates patterns made of form_smart and rd100 objects      
############################################################################
def genPIV_smartforming(topCh, botCh, gateCh,trigParams,form_obj,flag):
        # clear all PIV patterns
        B1530.clear()
        operation=[]
        topPattern=['','']
        botPattern=['','']
        gatePattern=['','']
        # set operation modes (PG for gate in order to benefit from more aggressive timing capabilities (MRAM)
        B1530.setOperationMode(topCh, B1530._operationMode['fastiv'])
        B1530.setOperationMode(botCh, B1530._operationMode['fastiv'])
        B1530.setOperationMode(gateCh, B1530._operationMode['pg'])
        # measurement modes (V or I)
        B1530.setMeasureMode(topCh, B1530._measureMode['voltage'])
        B1530.setMeasureMode(botCh, B1530._measureMode['current'])
        B1530.setMeasureMode(gateCh, B1530._measureMode['voltage'])
        # measurement ranges
        B1530.setMeasureVoltageRange(topCh, B1530._measureVoltageRange[var.rd100.vRange])
        B1530.setMeasureCurrentRange(botCh, B1530._measureCurrentRange[var.rd100.iRange])
        B1530.setMeasureVoltageRange(gateCh, B1530._measureVoltageRange[var.rd100.vRange])
        # create trig pattern @V=0 to be added before Operation patterns (wait for addressing...)
        B1530.createPattern('trigPattern', 0.0)
        # update trig pattern according to addressing delay
        B1530.addVector('trigPattern', trigParams.delay, 0.0)
        # attach trigger event to the trigger pattern
        B1530.setTriggerOutMode(trigParams.channel, B1530._triggerOutMode['event'], B1530._triggerOutPolarity['positive'])
        B1530.setTriggerOutEvent('trigPattern', 'trigEvent', 0.0, trigParams.duration)        
        if flag==1:     # for read pristine
            operation=[var.rd100]
        elif flag==2:   # for read after forming
            operation=[form_obj,var.rd100]
        for lp in range(flag):
            # define PIV patterns names
            topPattern[lp] = 'topPat_'+ str(lp) + operation[lp].name
            botPattern[lp] = 'botPat_'+ str(lp) +operation[lp].name
            gatePattern[lp] = 'gatePat_'+ str(lp) + operation[lp].name
            # create PIV patterns
            B1530.createPattern(topPattern[lp], 0.0)
            B1530.createPattern(botPattern[lp], 0.0)
            B1530.createPattern(gatePattern[lp], 0.0)
            # update PIV patterns with V and t values
            B1530.addVectors(topPattern[lp], operation[lp].tTop, operation[lp].vTop, len(operation[lp].tTop))
            B1530.addVectors(botPattern[lp], operation[lp].tBot, operation[lp].vBot, len(operation[lp].tBot))
            B1530.addVectors(gatePattern[lp], operation[lp].tGate, operation[lp].vGate, len(operation[lp].tGate))
            # if read operation, define measurements to be performed
            if operation[lp].__class__ is ReadOperation:
                    # measure events for attached to each pattern
                    B1530.setMeasureEvent(topPattern[lp], "topMeas", operation[lp].measParams[0], operation[lp].measParams[1], operation[lp].measParams[2], operation[lp].measParams[3], B1530._measureEventData['averaged'])
                    B1530.setMeasureEvent(botPattern[lp], "botMeas", operation[lp].measParams[0], operation[lp].measParams[1], operation[lp].measParams[2], operation[lp].measParams[3], B1530._measureEventData['averaged'])
                    B1530.setMeasureEvent(gatePattern[lp], "gateMeas", operation[lp].measParams[0], operation[lp].measParams[1], operation[lp].measParams[2], operation[lp].measParams[3], B1530._measureEventData['averaged'])
            if lp==0:
                # finally, merge trig and operation patterns, in order to get final operation patterns with an addressing delay (timing of meas and trig events are automatically kept)
                B1530.createMergedPattern(topPattern[lp], 'trigPattern', topPattern[lp], B1530._axis['time'])
                B1530.createMergedPattern(botPattern[lp], 'trigPattern', botPattern[lp], B1530._axis['time'])
                B1530.createMergedPattern(gatePattern[lp], 'trigPattern', gatePattern[lp], B1530._axis['time'])
            # If we have a forming pattern, then we merge forming + read in one pattern
            if lp==1:
                B1530.createMergedPattern(topPattern[0], topPattern[0], topPattern[1], B1530._axis['time'])
                B1530.createMergedPattern(botPattern[0], botPattern[0], botPattern[1], B1530._axis['time'])
                B1530.createMergedPattern(gatePattern[0], gatePattern[0], gatePattern[1], B1530._axis['time'])
        # add final sequences to PIV channels, according to nbMeas
        B1530.addSequence(topCh, topPattern[0], 1)
        B1530.addSequence(botCh, botPattern[0], 1)
        B1530.addSequence(gateCh, gatePattern[0], 1)
        # connect B1530 channels
        B1530.connect(topCh)
        B1530.connect(botCh)
        B1530.connect(gateCh)

def genPIV(topCh, botCh, gateCh, operation,pattern_name,WL_refresh):
        # define PIV patterns names
        topPattern = 'topPat_'+ pattern_name
        botPattern = 'botPat_'+ pattern_name
        gatePattern = 'gatePat_'+ pattern_name       
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
        if WL_refresh=='on':
            # finally, merge trig and operation patterns, in order to get final operation patterns with an addressing delay (timing of meas and trig events are automatically kept)
            B1530.createMergedPattern(topPattern, 'trigPattern', topPattern, B1530._axis['time'])
            B1530.createMergedPattern(botPattern, 'trigPattern', botPattern, B1530._axis['time'])
            B1530.createMergedPattern(gatePattern, 'trigPattern', gatePattern, B1530._axis['time'])

def trigPIV(trigParams):
        # create trig pattern @V=0 to be added before Operation patterns (wait for addressing...)
        B1530.createPattern('trigPattern', 0.0)
        # update trig pattern according to addressing delay
        B1530.addVector('trigPattern', trigParams.delay, 0.0)
        # attach trigger event to the trigger pattern
        B1530.setTriggerOutMode(trigParams.channel, B1530._triggerOutMode['event'], B1530._triggerOutPolarity['positive'])
        B1530.setTriggerOutEvent('trigPattern', 'trigEvent', 0.0, trigParams.duration)

def mergePIV(topCh, botCh, gateCh,testPlan_str,indice1,indice2,loop):
        if len(testPlan_str)==1:
            # define PIV patterns names
            topPattern = 'topPat_'+ testPlan_str[0]
            botPattern = 'botPat_'+ testPlan_str[0]
            gatePattern = 'gatePat_'+ testPlan_str[0]
        else:
            topPattern = 'topPat_'+ str(indice1) + "_" + str(indice2)
            botPattern = 'botPat_'+ str(indice1) + "_" + str(indice2)
            gatePattern = 'gatePat_'+ str(indice1) + "_" + str(indice2)        
        # add final sequences to PIV channels, according to nbMeas
        B1530.addSequence(topCh, topPattern,loop)
        B1530.addSequence(botCh, botPattern,loop)
        B1530.addSequence(gateCh, gatePattern,loop)      

def merge_base_PIV(testPlan,testPlan_str,indice,sequences):
        # define PIV patterns names
        topPattern = 'topPat_'+ str(indice) + "_" + str(sequences)
        botPattern = 'botPat_'+ str(indice) + "_" + str(sequences)
        gatePattern = 'gatePat_'+ str(indice) + "_" + str(sequences)
        if range(len(testPlan_str))!=1:
            for j in range(len(testPlan_str)):
                if j==1:
                    B1530.createMergedPattern(topPattern, ('topPat_' + testPlan_str[0]), ('topPat_' + testPlan_str[1]), B1530._axis['time'])
                    B1530.createMergedPattern(botPattern, ('botPat_' + testPlan_str[0]), ('botPat_' + testPlan_str[1]), B1530._axis['time'])
                    B1530.createMergedPattern(gatePattern, ('gatePat_' + testPlan_str[0]), ('gatePat_' + testPlan_str[1]), B1530._axis['time'])
                elif j>1:
                    B1530.createMergedPattern(topPattern, topPattern, ('topPat_' + testPlan_str[j]), B1530._axis['time'])
                    B1530.createMergedPattern(botPattern, botPattern, ('botPat_' + testPlan_str[j]), B1530._axis['time'])
                    B1530.createMergedPattern(gatePattern, gatePattern, ('gatePat_' + testPlan_str[j]), B1530._axis['time'])

def runPIV_SmartForming(ard,topCh, botCh, gateCh,testFolder,X_pos,Y_pos,SL,WL,BL,startAdrs,stopAdrs,stopAll,flag):
        # load Arduino parameters
        if flag==0:
            ard.programAddressing('Z',str(SL)+"/"+str(WL)+"/"+str(BL)+"/", startAdrs, stopAdrs, stopAll)
        # init B1530 outputs
        status = 0
        elapsT = 0
        totalT = 0
        error = 0
        B1530.execute()
        while(status!=10000):
            error,status,elapsT,totalT = B1530.getStatus()
        # Send reset command to Arduino
        error, timeTemp, vTop = B1530.getMeasureValues(var.chTop, 0, 1)
        error, timeTemp, iBot = B1530.getMeasureValues(var.chBot, 0, 1)
        error, timeTemp, vGate = B1530.getMeasureValues(var.chGate, 0, 1)
        R = -1*vTop[0]/iBot[0] # Rcell
        
        #Creation of log files
        if os.path.exists("%s\\X_%s_Y_%s_Smart_form.csv" % (testFolder,X_pos,Y_pos)) is not True:
            rslfile = open("%s\\X_%s_Y_%s_Smart_form.csv" % (testFolder,X_pos,Y_pos), "ab")
            rslfile.write("topVmeas," + convert(vTop[0],4) + ",gateVmeas," + convert(vGate[0],4)+ ",\n")
            rslfile.write("SL," + "WL," + "BL," + "Pristine,")
            for i in range(19):
                rslfile.write(str(1.4+i*0.2))
                rslfile.write(",")
        if flag==0:               
            rslfile = open("%s\\X_%s_Y_%s_Smart_form.csv" % (testFolder,X_pos,Y_pos), "ab")
            rslfile.write("\n" + str(SL) + "," + str(WL) + "," + str(BL) + ",")
            rslfile.write(str((-1*vTop[0]/iBot[0])) + ",")
            rslfile.close()
        elif flag==1:   
            rslfile = open("%s\\X_%s_Y_%s_Smart_form.csv" % (testFolder,X_pos,Y_pos), "ab")
            rslfile.write(str((-1*vTop[0]/iBot[0])) + ",")
            rslfile.close()
        return R
            
def runPIV(ard,topCh, botCh, gateCh,testFolder,test_list,X_pos,Y_pos,SL,WL,BL,startAdrs,stopAdrs,stopAll):
        # load Arduino parameters
        ard.programAddressing('Z',str(SL)+"/"+str(WL)+"/"+str(BL)+"/", startAdrs, stopAdrs, stopAll)
        
        # connect B1530 channels
        B1530.connect(topCh)
        B1530.connect(botCh)
        B1530.connect(gateCh)
        # init B1530 outputs
        status = 0
        elapsT = 0
        totalT = 0
        error = 0
        B1530.execute()
        while(status!=10000):
            error,status,elapsT,totalT = B1530.getStatus()
        # Send reset command to Arduino
        ard.stopSingleAddressing()       
        if len(test_list)!=0:
            error, timeTemp, vTopTemp = B1530.getMeasureValues(var.chTop, 0, len(test_list))
            error, timeTemp, iBotTemp = B1530.getMeasureValues(var.chBot, 0, len(test_list))
            error, timeTemp, vGateTemp = B1530.getMeasureValues(var.chGate, 0, len(test_list))
            #Creation of log files
            if os.path.exists("%s\\X_%s_Y_%s_Set.csv" % (testFolder,X_pos,Y_pos)) is not True:
                rslfile = open("%s\\X_%s_Y_%s_Set.csv" % (testFolder,X_pos,Y_pos), "ab")
                rslfile.write("topVmeas," + convert(vTopTemp[0],4) + ",gateVmeas," + convert(vGateTemp[0],4)+ ",\n")                
                rslfile.write("SL," + "WL," + "BL,")
                for lp in range(len(test_list)):
                    if len(test_list[lp].split("_"))==4 and test_list[lp].split("_")[2]=='Set':
                        rslfile.write(str(test_list[lp].split("_")[3]) + ",")
                rslfile.write("\n")    
                rslfile.close()
            if os.path.exists("%s\\X_%s_Y_%s_Reset.csv" % (testFolder,X_pos,Y_pos)) is not True:
                rslfile = open("%s\\X_%s_Y_%s_Reset.csv" % (testFolder,X_pos,Y_pos), "ab")
                rslfile.write("topVmeas," + convert(vTopTemp[0],4) + ",gateVmeas," + convert(vGateTemp[0],4)+ ",\n")                
                rslfile.write("SL," + "WL," + "BL,")
                for lp in range(len(test_list)):
                    if len(test_list[lp].split("_"))==4 and test_list[lp].split("_")[2]=='Reset':
                        rslfile.write(str(test_list[lp].split("_")[3]) + ",")
                rslfile.write("\n")        
                rslfile.close()            
            if os.path.exists("%s\\X_%s_Y_%s_Forming.csv" % (testFolder,X_pos,Y_pos)) is not True:
                rslfile = open("%s\\X_%s_Y_%s_Forming.csv" % (testFolder,X_pos,Y_pos), "ab")
                rslfile.write("topVmeas," + convert(vTopTemp[0],4) + ",gateVmeas," + convert(vGateTemp[0],4)+ ",\n")                
                rslfile.write("SL," + "WL," + "BL,")
                for lp in range(len(test_list)):
                    if len(test_list[lp].split("_"))==4 and test_list[lp].split("_")[2]=='Forming':
                        rslfile.write(str(test_list[lp].split("_")[3]) + ",")
                rslfile.write("\n")        
                rslfile.close() 
            if os.path.exists("%s\\X_%s_Y_%s_Full.csv" % (testFolder,X_pos,Y_pos)) is not True:
                rslfile = open("%s\\X_%s_Y_%s_Full.csv" % (testFolder,X_pos,Y_pos), "ab")
                rslfile.write("topVmeas," + convert(vTopTemp[0],4) + ",gateVmeas," + convert(vGateTemp[0],4)+ ",\n")                
                rslfile.write("SL," + "WL," + "BL,") 
                for lp in range(len(test_list)):
                    rslfile.write(str(test_list[lp]) + ",")
                rslfile.write("\n")        
                rslfile.close() 
            writeResultFile(testFolder,test_list,X_pos,Y_pos,vTopTemp,vGateTemp,iBotTemp,SL,BL,WL)

# write read operation results
def writeResultFile(location,test_list,X_pos,Y_pos,V_top,V_gate,I_bottom,SL,BL,WL):
        rsl_Full = open("%s\\X_%s_Y_%s_Full.csv" % (location,X_pos,Y_pos), "ab")
        rsl_Reset = open("%s\\X_%s_Y_%s_Reset.csv" % (location,X_pos,Y_pos), "ab")
        rsl_Set = open("%s\\X_%s_Y_%s_Set.csv" % (location,X_pos,Y_pos), "ab")
        rsl_Forming = open("%s\\X_%s_Y_%s_Forming.csv" % (location,X_pos,Y_pos), "ab")
        rsl_Full.write(str(SL) + "," + str(WL) + "," + str(BL) + ",")            
        rsl_Reset.write(str(SL) + "," + str(WL) + "," + str(BL) + ",")
        rsl_Set.write(str(SL) + "," + str(WL) + "," + str(BL) + ",")
        rsl_Forming.write(str(SL) + "," + str(WL) + "," + str(BL) + ",")            
        for lp in range(len(test_list)):    
            rsl_Full.write(str((-1*V_top[lp]/I_bottom[lp])) + ",")
            if len(test_list[lp].split("_"))==4 and test_list[lp].split("_")[2]=='Reset':
                rsl_Reset.write(str((-1*V_top[lp]/I_bottom[lp])) + ",")
            elif len(test_list[lp].split("_"))==4 and test_list[lp].split("_")[2]=='Set':     
                rsl_Set.write(str((-1*V_top[lp]/I_bottom[lp])) + ",")    
            elif len(test_list[lp].split("_"))==4 and test_list[lp].split("_")[2]=='Forming':
                rsl_Forming.write(str((-1*V_top[lp]/I_bottom[lp])) + ",")
        rsl_Full.write("\n")
        rsl_Reset.write("\n")
        rsl_Set.write("\n")
        rsl_Forming.write("\n")
        rsl_Full.close()
        rsl_Reset.close()
        rsl_Set.close()
        rsl_Forming.close()
  
# function returning addresses list (when scan mode)
def adrsTable(startBtl, startWl, startWlm, stopBtl, stopWl, stopWlm):
        adrs = []
        for Wlm in range(startWlm,stopWlm+1):
            for BL in range(startBtl,stopBtl+1):
                for Wl in range(startWl,stopWl+1):    
                    adrs.append([Wlm,Wl,BL])
        return adrs
    
# function creating a new folder if not already existing, then Test_xxx subfolder which increment at each run                
def createFolder(waferLot,waferNo,Folder_creation_flag,testName,dutName):
        folders = []
        y = []
        now = dt.datetime.now()
        mypath = r'%s\%s\%s' % (var.resultsOutput,
                                waferLot + 'w' + waferNo,
                                now.strftime("%Y-%m-%d")+"__test="+testName+"__dut="+dutName)
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


def writeLogFile(X,Y,path,comments):
        if os.path.exists("%s\\%s_X_%s_Y_%s.txt" % (path,"datalog",str(X),str(Y))) is not True:
            flag=1
        rslfile = open("%s\\%s_X_%s_Y_%s.txt" % (path,"datalog",str(X),str(Y)), "ab")
        rslfile.write(comments)
        rslfile.close()

def parse_patterns():
    workbook = xlrd.open_workbook(var.testflow)
    worksheet = workbook.sheet_by_name('Testflow')
    lines_nb = worksheet.nrows-1
    tableau=[]    
    #Loop on the different sequences to test (lines of xls file)
    for i in range (lines_nb):  
        tableau=tableau+str(worksheet.cell(i+1,1).value).split(",")
        if worksheet.cell(i+1,2).value != '':
            tableau=tableau+str(worksheet.cell(i+1,2).value).split(",")
    tableau_final=list(set(tableau))
    return tableau_final       

def test_die(wafer_lot,wafer_number,X_die,Y_die,cut_size,flag):
    # Reading of testflow parameters
    workbook = xlrd.open_workbook(var.testflow)
    worksheet = workbook.sheet_by_name('Parameters')
    mtxSize=str(worksheet.cell(6,2).value)
    Vddvalue=worksheet.cell(7,2).value    
    startBL = int(worksheet.cell(15,2).value)
    startWL = int(worksheet.cell(16,2).value)
    startSL = int(worksheet.cell(17,2).value)
    stopBL = int(worksheet.cell(19,2).value)
    stopWL = int(worksheet.cell(20,2).value)
    stopSL = int(worksheet.cell(21,2).value)   
    SmartForm = str(worksheet.cell(10,2).value)
    WL_refresh = str(worksheet.cell(9,2).value)
    AdrsMode=str(worksheet.cell(12,2).value)
    scanMode=str(worksheet.cell(13,2).value)

    testName= str(worksheet.cell(1,2).value)
    waferLot = str(worksheet.cell(2,2).value)       
    waferNo= str(int(worksheet.cell(3,2).value))    
    dutName= str(worksheet.cell(4,2).value)    

    #If test_die is called from prober test program, we must have flag=1
    if flag==1:
        Lot_pos=wafer_lot
        Wafer_pos=wafer_number
        X_pos=X_die
        Y_pos=Y_die
        Folder_creation_flag="A"
        mtxSize=cut_size
    else:
        Lot_pos=waferLot
        Wafer_pos=waferNo
        X_pos=var.X_pos
        Y_pos=var.Y_pos
        Folder_creation_flag=""
    # MANAGE ADDRESSING...
    mtxDic = {'256': 0, '4K':1, '64K':2, '1M':3}     
    nbWL = [0, 15, 255, 255]
    nbSL = [0, 0, 0, 15]
    nbBL = [255, 255, 255, 255]
    # retrieve addresses depending on scan mode
    if scanMode == 'All':
        startBL = 0
        startWL = 0
        startSL = 0
        stopBL = nbBL[mtxDic.get(mtxSize)]
        stopWL = nbWL[mtxDic.get(mtxSize)]
        stopSL = nbSL[mtxDic.get(mtxSize)]
    # set first, last, and max addresses (will be used only if scan mode is set)
    startAdrs = str(startSL)+'/'+str(startWL)+'/'+str(startBL)+'/'
    stopAdrs = str(stopSL)+'/'+str(stopWL)+'/'+str(stopBL)+'/'
    stopAll = str(nbWL[mtxDic.get(mtxSize)])+'/'+str(nbBL[mtxDic.get(mtxSize)])+'/'
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
    print "Vdd connected at",Vddvalue,"V"
    B1530.setOperationMode(var.chVdd, B1530._operationMode['dc'])
    B1530.connect(var.chVdd)
    B1530.dcforceVoltage(var.chVdd, Vddvalue)
    # Wait 20ms
    time.sleep(0.02)
    ########################################################
    # Datalog directory creation 
    ########################################################
    testFolder = createFolder(Lot_pos,Wafer_pos,Folder_creation_flag,testName,dutName)
    # copy of the test flow in the test folder
    shutil.copy(userFile+".py", testFolder)
    shutil.copy(var.testflow, testFolder)  
    testPlan=[]         #object list
    testPlan_str=[]     #object name list (str)
    counter=0           #iterations after a specific number of operations
    counter_rst=0       #number of rst since beginning of the flow
    counter_set=0       #number of set since beginning of the flow
    counter_forming=0   #number of forming since beginning of the flow
    test_list=[]        #list of all the tests to be run
    log_dir=[]          #list of the directories where data will be stored
    interval_flag=0
    interval_list=[]
    dico_temp={}
    form_smart = SingleOperation("Forming", # operation name
                       [4.0,4.0,0.],        # top pulse bias
                       [0.0,0.0,0.],        # bottom pulse bias
                       [2,2,0.0],           # gate pulse bias
                       [1e-7,1e-5,1e-7],    # top pulse timing 1e-5
                       [1e-7,1e-5,1e-7],    # bottom pulse timing 1e-5
                       [1e-7,1e-5,1e-7])    # gate pulse timing 1e-5
    
    #####################################################################################################################
    # Function reading the testflow and giving back a unique list of tests to be launched (to construct B1500 patterns)
    #####################################################################################################################
    pattern_list=parse_patterns() 
    ########################################################
    # generation of the different PIV unique base patterns
    ########################################################
    # clear all PIV patterns
    B1530.clear()

    # Dynamic delay before measurement
    if int(nbSL[mtxDic.get(mtxSize)])==0:    
        delay=0.5e-6*int(nbWL[mtxDic.get(mtxSize)])+12e-6
    else:
        delay=0.5e-6*int(nbWL[mtxDic.get(mtxSize)])*int(nbSL[mtxDic.get(mtxSize)])+12e-6

    trig = AddressingTrigger(var.chTrig, 2e-6, delay)   # trigger configuration

    ###########################################
    # Loop on the different sequences to test
    ###########################################
    workbook = xlrd.open_workbook(var.testflow)
    worksheet = workbook.sheet_by_name('Testflow')
    
    lines_nb = worksheet.nrows-1  
    #array_single_adress contains a list a addresses to be tested in A mode
    #single_address_number contains the number of addresses to be testes
    array_single_address=[]
    array_single_address,single_address_number_temp=address_list(workbook)
    #We calculate the addresses list and number of measurements to perform depending of AdrsMode field
    singleAdrs=0
    adrsList=[]
    seqCounts=0
    if AdrsMode == 'A':
        single_address_number=single_address_number_temp
    elif AdrsMode == 'S':
        single_address_number=1
        adrsList = adrsTable(startBL, startWL, startSL, stopBL, stopWL, stopSL)
        seqCounts = len(adrsList)

    ###################################################################################################################
    # We check if Smart formating is requested in the test flow
    ###################################################################################################################
    if SmartForm=='on':
        print "Start of Smartforming"        
        if AdrsMode == 'A':
            for lp in range(len(array_single_address)):
                print "Forming SL = ",
                print array_single_address[lp][0],
                print "WL =",
                print array_single_address[lp][1],
                print "BL =",
                print array_single_address[lp][2]
                # R pristine
                genPIV_smartforming(var.chTop,var.chBot,var.chGate,trig,form_smart,1) 
                R = runPIV_SmartForming(ard,var.chTop,var.chBot,var.chGate,testFolder,X_pos,Y_pos,array_single_address[lp][0],array_single_address[lp][1],array_single_address[lp][2],startAdrs,stopAdrs,stopAll,0)             
                #Smartforming
                for i in range(14):
                    # BL varies from 1.4V to 4V
                    form_smart.vTop=[1.4+0.2*i,1.4+0.2*i,0]
                    genPIV_smartforming(var.chTop,var.chBot,var.chGate,trig,form_smart,2)
                    R = runPIV_SmartForming(ard,var.chTop,var.chBot,var.chGate,testFolder,X_pos,Y_pos,array_single_address[lp][0],array_single_address[lp][1],array_single_address[lp][2],startAdrs,stopAdrs,stopAll,1)             
                    # if R formed is less than 50kOhms
                    if R < 50000:
                        break
        elif AdrsMode == 'S':
            for lp in range(len(adrsList)):
                print "Forming SL = ",
                print adrsList[lp][0],
                print "WL =",
                print adrsList[lp][1],           
                print "BL =",
                print adrsList[lp][2]                
                genPIV_smartforming(var.chTop,var.chBot,var.chGate,trig,form_smart,1)
                R = runPIV_SmartForming(ard,var.chTop,var.chBot,var.chGate,testFolder,X_pos,Y_pos,adrsList[lp][0],adrsList[lp][1],adrsList[lp][2],startAdrs,stopAdrs,stopAll,0) 
                #Smartforming
                for i in range(19): 
                    # BL varies from 1.4V to 4V
                    form_smart.vTop=[1.4+0.2*i,1.4+0.2*i,0]
                    genPIV_smartforming(var.chTop,var.chBot,var.chGate,trig,form_smart,2)
                    R = runPIV_SmartForming(ard,var.chTop,var.chBot,var.chGate,testFolder,X_pos,Y_pos,adrsList[lp][0],adrsList[lp][1],adrsList[lp][2],startAdrs,stopAdrs,stopAll,1) 
                    # if R formed is less than 50kOhms
                    if R < 50000:
                        break
        print "End of SmartForming"

    # clear all PIV patterns
    B1530.clear()

    # Creation of trigger parameter patterns
    trigPIV(trig)

    # Creation of all the basic patterns
    for i in range (len(pattern_list)):
        genPIV(var.chTop,var.chBot,var.chGate,var.dico[pattern_list[i]],pattern_list[i],WL_refresh)

    if WL_refresh=='off':
        # We add a trig signal before all the patterns for WL refresh (if we select 1 WL refresh before each cell)        
        B1530.addSequence(var.chTop, 'trigPattern',1)
        B1530.addSequence(var.chBot, 'trigPattern',1)
        B1530.addSequence(var.chGate, 'trigPattern',1)    

    #Loop on the different sequences to test (lines of xls file)
    for sequences in range (lines_nb):
        ######################################################################
        # We uncompress the test plan
        ######################################################################
        testPlan,testPlan_str,indice=uncompress(str(worksheet.cell(sequences+1,1).value))
        ######################################################################
        # Creation of patterns made with merge of "Sequence" & "Option read"
        ######################################################################
        merge_base_PIV(testPlan,testPlan_str,1,sequences)
        # We check if sequence has to be added at regular interval
        if (str(worksheet.cell(sequences+1,2).value)!='' and str(worksheet.cell(sequences+1,3).value)!='' and str(worksheet.cell(sequences+1,4).value)!=''):
            interval_list=interval_list_creation(int(worksheet.cell(sequences+1,0).value),int(worksheet.cell(sequences+1,3).value),str(worksheet.cell(sequences+1,4).value))                   
            #We uniquify the list "interval_list"
            interval_list=sorted(list(set(interval_list)))
            testPlan_option_read,testPlan_option_read_str,indice_option_read=uncompress(str(worksheet.cell(sequences+1,2).value))
            merge_base_PIV(testPlan_option_read,testPlan_option_read_str,2,sequences)
            interval_flag=1
        else:
            interval_list=[]
            interval_flag=0
        # We loop on the number of executions (Loop field)
        loop=worksheet.cell(sequences+1,0).value
        # Case we have no subsequence
        if interval_flag==0:
            mergePIV(var.chTop,var.chBot,var.chGate,testPlan_str,1,sequences,loop)                    
        # Case we have a subsequence
        elif interval_flag==1:
            count_temp=0
            for lp in range(len(interval_list)):
                mergePIV(var.chTop,var.chBot,var.chGate,testPlan_str,1,sequences,interval_list[lp]-count_temp)
                mergePIV(var.chTop,var.chBot,var.chGate,testPlan_option_read_str,2,sequences,1)
                count_temp=interval_list[lp]
        previous_state=""            #indicates the previous performed test
        if interval_flag==1:         # We have a subsequence 
            count_temp=0
            for lp in range(len(interval_list)):
                #Main sequence 
                for j in range(interval_list[lp]-count_temp):
                    counter,counter_rst,counter_set,counter_forming,previous_state,dico_temp,log_dir=parser(testPlan,testPlan_str,counter,counter_rst,counter_set,counter_forming,previous_state,dico_temp,log_dir)
                    count_temp=interval_list[lp]
                counter,counter_rst,counter_set,counter_forming,previous_state,dico_temp,log_dir=parser(testPlan_option_read,testPlan_option_read_str,counter,counter_rst,counter_set,counter_forming,previous_state,dico_temp,log_dir)                    
        elif interval_flag==0:         # We have no subsequence 
            for j in range(int(worksheet.cell(sequences+1,0).value)):
                counter,counter_rst,counter_set,counter_forming,previous_state,dico_temp,log_dir=parser(testPlan,testPlan_str,counter,counter_rst,counter_set,counter_forming,previous_state,dico_temp,log_dir)                       
        testPlan=[]

    ##########################################################
    # Execution of the PIV commands for all the lines of testflow
    # To loop on addesses to be tested
    ##########################################################
    if AdrsMode == 'A':
        for lp in range(len(array_single_address)):
            print "Testing SL = ",
            print array_single_address[lp][0],
            print "WL =",
            print array_single_address[lp][1],
            print "BL =",
            print array_single_address[lp][2]
            runPIV(ard,var.chTop,var.chBot,var.chGate,testFolder,log_dir,X_pos,Y_pos,array_single_address[lp][0],array_single_address[lp][1],array_single_address[lp][2],startAdrs,stopAdrs,stopAll)
    elif AdrsMode == 'S':
        for lp in range(len(adrsList)):
            print "Testing SL = ",
            print adrsList[lp][0],
            print "WL =",
            print adrsList[lp][1],           
            print "BL =",
            print adrsList[lp][2]
            runPIV(ard,var.chTop,var.chBot,var.chGate,testFolder,log_dir,X_pos,Y_pos,adrsList[lp][0],adrsList[lp][1],adrsList[lp][2],startAdrs,stopAdrs,stopAll)

    print "End Cycling"
    # wait 20ms
    time.sleep(0.02)
    # terminate B1530 session

    B1530.disconnect(var.chVdd)
    B1530.closeSession()

#main program in stand alone
if '__main__'==__name__:
    test_die('wafer_lot','wafer_number','X_die','Y_die','cut_size',0)



        





