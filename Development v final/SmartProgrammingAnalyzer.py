#import variables_testParams_v3 as var
import numpy as np
import math
import variables_testParams_v3 as var
import csv
import re
import final_oxram_prog_v3_6 as final
import datetime as dt
import os
import sys
import matplotlib.pyplot as plt
from shutil import copyfile
from madClassesAndFunctions_v3 import ReadOperation
from madClassesAndFunctions_v3 import SingleOperation
from madClassesAndFunctions_v3 import SmartStrategy 


def increase_voltage(plan,stepSet,stepReset,stepForm):

    ###It only increases components 0 and 1 because they are the rising and final voltages
    ###the third component is the falling, which will always be zero
    if plan.name == "Set":
        plan.vTop[0] += stepSet
        plan.vTop[1] += stepSet
        print('Increasing set voltage to '+ str(plan.vTop[0]))
    elif plan.name == "Reset":
        plan.vBot[0] += stepReset
        plan.vBot[1] += stepReset
        print'Increasing reset voltage to '+ str(plan.vBot[0])
    elif plan.name == "Forming":
        plan.vTop[0] += stepForm
        plan.vTop[1] += stepForm
        print('Increasing forming voltage to '+ str(plan.vTop[0]))
    

def restart_voltage(initVset, initVreset):   ###This function resets the initial set and reset voltage to its initial conditions in order to start a new section

    var.set1.vTop[0] = initVset
    var.set1.vTop[1] = initVset

    var.reset1.vBot[0] = initVreset
    var.reset1.vBot[1] = initVreset

    print('\n\nVoltage restarted to Vs = '+str(initVset)+' V and Vr = '+str(initVreset))

    
def setReset(plan):

    print(plan.name)
    ###If the test is a reset, do this programming algorithm
    ###But if it is a Set, just do the increase voltage
    if plan.name == "Reset":
        newPlan = [var.setSmart, var.reset1]
    elif plan.name == "Set":
        #increase_voltage(plan)
        newPlan = [var.resetSmart, var.set1]
    print(newPlan)
    return newPlan
        

    
##Writes the log file        
def writeLogInTest(logDirectory, originalPlan, firstTime, testNb, strategy, operation, repetition, notWorking, stepSet, stepReset, Ron, Roff,Rform):

    withForming = False
    initVset = var.set1.vTop[1]
    initVreset = var.reset1.vBot[1]
    smartSetV = var.setSmart.vTop[1]
    smartResetV = var.resetSmart.vBot[1]
    if firstTime:
        wr = open(logDirectory+'\\log.txt','w')
        wr.write('Test:\t'+str(testNb)+'\n')
        wr.write('Plan:\t ')
        for i in range(len(originalPlan)):
            wr.write(originalPlan[i].name+'\t')
            if originalPlan[i].name == 'Forming':
                withForming = True
        if withForming:
            wr.write('\nRform (Ohm)\t'+str(Rform)+'\n')
        else:
            wr.write('\nRon (Ohm)\t'+str(Ron)+'\tRoff (Ohm)\t'+str(Roff)+'\n')
        if strategy == '':
            wr.write('No strategy')
        else:
            wr.write('Strategy:\t'+strategy+'\n')
        if strategy == 'V':
            wr.write('Init Vset:\t'+str(initVset)+'\tInit Vreset:\t'+str(initVreset)+'\tStep Vset:\t'+str(stepSet)+'\tStep Vreset:\t'+str(stepReset)+'\n')
        elif strategy == 'SR':
            wr.write('Init Vset:\t'+str(initVset)+'\tInit Vreset:\t'+str(initVreset)+'\tSmart Vset:\t'+str(smartSetV)+'\tSmart Vreset:\t'+str(smartResetV)+'\n')
        elif strategy == 'TB':
            wr.write('Vset:\t'+str(initVset)+'\tVreset:\t'+str(initVreset)+'\n')
            wr.write('\n')
        wr.write('Operation\tRepetition\tBad cells\n')
    else:
        wr = open(logDirectory+'\\log.txt','a')

    wr.write(str(operation)+'\t'+str(repetition-1)+'\t'+str(notWorking)+'\n')
    wr.close()

##Writes the number of cells that didn't switch after smart forming with addresslist
def writeLogForming(logDirectory, addressNotWorking):

    wr = open(logDirectory+'\\nonSwitched.txt','w')
    wr.write('Cells not formed \n')
    wr.write('Wln,WL,BL,\n')
    for j in range(0,len(addressNotWorking)/3):
        wr.write(addressNotWorking[j*3]+','+addressNotWorking[j*3+1]+','+addressNotWorking[j*3+2]+','+'\n')
    wr.close()


def writeLog(now,string):

    mypath = r'%s\%s\%s' % (var.resultsOutput,
                                var.waferLot + 'w' + var.waferNo,
                                now.strftime("%Y-%m-%d")+"__test="+var.testName+"__dut="+var.dutName)
    if not os.path.exists(mypath):
        os.makedirs(mypath)

    nowTime = now.strftime("%H-%M-%S")
    wr = open(mypath+'\\log_'+nowTime+'.txt','a')
    if isinstance(string,list) is True:
        for i in range(len(string)):
            wr.write(string[i]+'\n')
    else:
        wr.write(string+'\n')
    wr.close()


def plotDistributions(data,logDirectory,operationFolder):

    plt.clf()
    floatdata = [np.log10(float(data[i])) for i in range(0,len(data))]
    bins = np.linspace(2.5,7,75)
    plt.hist(floatdata, bins)
    ##plt.show()
    plt.savefig(logDirectory+'\\distribution_'+operationFolder+'.png')
    print('   OK\n')

def getWorkingCells(twoCells,plan,Rmeas,Ron,Roff,Rform):

            

    if twoCells == True:
        working = np.zeros(len(Rmeas)/2)    
        if plan.name is "Set":
            for i in range(0,len(Rmeas),2):
                if np.abs(float(Rmeas[i])) - np.abs(float(Rmeas[i+1])) < 0:
                    working[i/2] = 1

        elif plan.name is "Reset":
            for i in range(0,len(Rmeas),2):
                if np.abs(float(Rmeas[i])) - np.abs(float(Rmeas[i+1])) > 0:
                    working[i/2] = 1
    elif twoCells == False:
        working = np.zeros(len(Rmeas))
        
        if plan.name is "Set":
            for i in range(0,len(Rmeas)):
                if np.abs(float(Rmeas[i])) < Ron:
                    working[i] = 1
        elif plan.name is "Reset":
            for i in range(0,len(Rmeas)):
                if np.abs(float(Rmeas[i])) > Roff:
                    working[i] = 1
        elif plan.name is "Forming":
            for i in range(0,len(Rmeas)):
                if np.abs(float(Rmeas[i])) < Rform:
                    working[i] = 1

    return working
             
def runTestPlan(testPlan,smartStrategy,readType,initVset,initVreset,now):
    
    ###I CHECK HOW MANY TESTS WERE DONE
    nbTests = len(testPlan)
    originalPlan = testPlan

    firstTime = True
    isFirstRead = False
    readRep = False
    
    for test in range(0,nbTests):

        writeLog(now,'Operation '+str(test+1)+': '+originalPlan[test].name)
        
        if smartStrategy[test] == '': ##Because when the first plan is a read, the smart strategy is empty
            if nbTests > 1:
                if not smartStrategy[1] == '':
                    if smartStrategy[1].strategy == 'TB':
                        twoCells = True
                    else:
                        twoCells = False
                else:
                    readRep = True
                    twoCells = False
        else:
            if smartStrategy[test].strategy == 'TB':
                twoCells = True
            else:
                twoCells = False

        #Assigns parameters depending on the kind of operation
        if originalPlan[test].name is "Set":
            stepSet = smartStrategy[test].step
            stepReset = None
            stepForm = None
            maxSet = smartStrategy[test].maxRep
            maxReset = None
            maxForm = None
            Ron = smartStrategy[test].threshold
            Roff = var.Roff
            Rform = var.Rform
            strategy = smartStrategy[test].strategy
            readOperation = smartStrategy[test].read
        elif originalPlan[test].name is "Reset":
            stepSet = None
            stepReset = smartStrategy[test].step
            stepForm = None
            maxSet = None
            maxReset = smartStrategy[test].maxRep
            maxForm = None
            Ron = var.Ron
            Roff = smartStrategy[test].threshold
            Rform = var.Rform
            strategy = smartStrategy[test].strategy
            readOperation = smartStrategy[test].read
        elif originalPlan[test].name is "Forming":
            stepSet = None
            stepReset = None
            stepForm = smartStrategy[test].step
            maxSet = None
            maxReset = None
            maxForm = smartStrategy[test].maxRep
            Ron = var.Ron
            Roff = var.Roff
            Rform = smartStrategy[test].threshold
            strategy = smartStrategy[test].strategy
            readOperation = smartStrategy[test].read
        elif originalPlan[test].__class__ is ReadOperation:
            isFirstRead = True


        ###Initially I send the test together with a read operation
        if isFirstRead is False:
            testPlan = [originalPlan[test],readOperation]
            var.testPlan = testPlan
        elif isFirstRead is True:
            var.testPlan = [readType]
        print(isFirstRead)
        print(readRep)

        #Voltage is restarted to the original value in each test
        restart_voltage(initVset,initVreset) 

        #final.main arguments:
        #1) smart == 'n' tells that is not a smart strategy, for example the first operation. It will create a new test folder
        #if smart == 'y' will take the last folder instead of creating a new one
        #2) operationNb: is the number of the operation within the test plan. Repetitions of smart strategy are considered the same operation
        #3) repetition: indicates the repetition of the strategy. Helps reading properly the folders
        #4) now: it is necessary to drag it across the whole program so that it doesn't get confused when the experiment is run through
        #several days and the date changes

        if isFirstRead is False:
            if twoCells == False:
                var.adrsMode = 'S'
                if originalPlan[test].name == 'Set' or originalPlan[test].name == 'Forming':
                    auxV = originalPlan[test].vTop[1]
                    auxt = originalPlan[test].tTop[1]
                    writeLog(now,['    '+originalPlan[test].name+' at Vs = '+str(auxV)+' V and ts = '+str(auxt)+' micro s','    Read'])
                elif originalPlan[test].name == 'Reset':
                    auxV = originalPlan[test].vBot[1]
                    auxt = originalPlan[test].tBot[1]
                    writeLog(now,['    '+originalPlan[test].name+' at Vr = '+str(auxV)+' V and tr = '+str(auxt)+' micro s','    Read'])
                if test == 0:
                    final.main('n',test+1,0,now)
                elif test > 0:
                    ###By doing this, it will create the folder for the test only the firs time
                    final.main('y',test+1,0,now)
            elif twoCells == True:
                if originalPlan[test].name is "Set":
                    writeLog(now,'    Set half at Vs = '+str(var.set1.vTop[1])+' V and ts = '+str(var.set1.tTop[1])+' micro s')
                    var.testPlan = [var.set1]
                    var.scanMode = 'RS'
                    if test == 0:
                        final.main('n',test+1,0,now)
                    else:
                        final.main('y',test+1,0,now)
                    var.scanMode = 'IRS'
                    writeLog(now,'    Reset half at Vr = '+str(var.reset1.vBot[1])+' V and tr = '+str(var.reset1.tBot[1])+' micro s')
                    var.testPlan = [var.reset1] 
                    final.main('y',test+1,0,now)
                elif originalPlan[test].name is "Reset":
                    writeLog(now,'    Reset half at Vr = '+str(var.reset1.vBot[1])+' V and tr = '+str(var.reset1.tBot[1])+' micro s')
                    var.testPlan = [var.reset1]
                    var.scanMode = 'RS'
                    if test == 0:
                        final.main('n',test+1,0,now)
                    else:
                        final.main('y',test+1,0,now)
                    var.scanMode = 'IRS'
                    writeLog(now,'    Set half at Vs = '+str(var.set1.vTop[1])+' V and ts = '+str(var.set1.tTop[1])+' micro s')
                    var.testPlan = [var.set1]
                    final.main('y',test+1,0,now)
                else:
                    raise NameError('Unexpected operation in TB strategy')
                var.scanMode = 'All'
                var.adrsMode = 'S'
                writeLog(now,'    Read')
                var.testPlan = [readOperation]
                final.main('y',test+1,0,now)
        
        ###Necessary initialization: do not touch
        times = 1
        stop = False

        if isFirstRead is True: #In the first read, I don't do the smart programming stuff
            stop = True #Don't do the while loop below
            isFirstRead = False
            writeLog(now,'    Read')
            final.main('n',test+1,0,now)
            if readRep is True:
                for i in range(1,nbTests):
                    writeLog(now,'    Read')
                    final.main('y',i+1,0,now)

        if readRep is True:
            break
                
            ##Add a function that checks if the cell is pristine
        
        ###I repeat the execution of the test plan until:
        ###1) it reaches the maximum number of times allowed, or
        ###2) all the cells are switched
        while stop is False:

            #now = dt.datetime.now() #now is given as an input
            mypath = r'%s\%s\%s' % (var.resultsOutput,
                                            var.waferLot + 'w' + var.waferNo,
                                            now.strftime("%Y-%m-%d")+"__test="+var.testName+"__dut="
                                            +var.dutName)
            folders = [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]

            y=[]
            for i in range(len(folders)):
                y.append(int(folders[i][-3:]))
                y.sort()
                
            ###I ONLY NEED THE LAST TEST DONE
            lastTest = y[-1]
            testname = 'Test_%s' % ((3 - len(str(lastTest)))*"0" + str(lastTest))
            mypath+='\\'+testname
            folders = [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]

            ###Initialization
            results=[]
            header=[]
            SL=[]
            WL=[]
            BL=[]
            Rmeas=[]
            addressNotWorking=[]
            ###NOT VALID FOR SEVERAL READS IN THE SAME TEST PLAN
            ###NEED TO ADD LATER (COUNT NUMBER OF READ FOLDERS TO INITIALIZE ARRAYS)

            ###I read the results of the test plan
            ###By the way is defined, the current test will always be a read
            if times == 1:
                operationFolder = 'Op'+str(test+1)+'__Read'
            else:
                operationFolder = 'Op'+str(test+1)+'__Read_rep'+str(times-1)
            print(var.adrsMode)
            headerNb = 6
            
            mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
            with open(mypath2+'results.csv','rt') as f:
                reader = csv.reader(f)
                j = 0
                for row in reader:
                    if j<headerNb:
                        header.append(row)
                    else:
                        SL.append(row[0])
                        WL.append(row[1])
                        BL.append(row[2])
                        Rmeas.append(row[3])
                    j+=1
            
            ###The operation before the reading is supposed to be the target state
            ###It will check if it's working depending if it's Set or Reset
            working = getWorkingCells(twoCells,originalPlan[test],Rmeas,Ron,Roff,Rform)
            print(len(working))

            ###Makes the distributions
            #print('Creating histograms...  ')
            #plotDistributions(Rmeas,mypath,operationFolder)

            ###Rewrites the address list with the number of cells that were not working
            if twoCells == True:
                for i in range(0,len(working)):
                    if working[i] == 0:
                        addressNotWorking.append(SL[i*2])
                        addressNotWorking.append(WL[i*2])
                        addressNotWorking.append(BL[i*2])
                notWorking = int(len(addressNotWorking)/3)
            elif twoCells == False:
                for i in range(0,len(working)):
                    if working[i] == 0:
                        addressNotWorking.append(SL[i])
                        addressNotWorking.append(WL[i])
                        addressNotWorking.append(BL[i])
                notWorking = int(len(addressNotWorking)/3)
                    
            ###It checkes if it's necessary to stop
            if len(addressNotWorking) == 0:
                stop = True
                print('All cells were switched!')
                writeLog(now,'    All cells were switched!')
            elif originalPlan[test].name is "Set":
                if times == maxSet:
                    stop = True
                    print('The maximum number of repetitions of Set has been achieved')
                    writeLog(now,'    The maximum number of repetitions of Set has been achieved')
            elif originalPlan[test].name is "Reset":
                if times == maxReset:
                    stop = True
                    print('The maximum number of repetitions of Reset has been achieved')
                    writeLog(now,'    The maximum number of repetitions of Reset has been achieved')
            elif originalPlan[test].name is "Forming":
                if times == maxForm:
                    stop = True
                    print('The maximum number of repetitions of Forming has been achieved')
                    writeLog(now,'    The maximum number of repetitions of Forming has been achieved')

            writeLog(now,'        '+str(notWorking)+' cells were not switched')
            print(str(notWorking)+' cells were not switched \n')
            print("      Updating log file...  ")
            ###It creates the log file
            if firstTime:
                writeLogInTest(mypath, originalPlan, firstTime, lastTest, strategy, test+1, times, notWorking, stepSet, stepReset, Ron, Roff, Rform)
                firstTime = False
            elif not firstTime:
                writeLogInTest(mypath, originalPlan, firstTime, lastTest, strategy, test+1, times, notWorking, stepSet, stepReset, Ron, Roff, Rform)
            if originalPlan[test].name is "Forming":
                if times == maxForm:
                    writeLogForming(mypath, addressNotWorking)
                elif times < maxForm and stop == True:
                    writeLogForming(mypath, addressNotWorking)
            print("OK\n")

            if stop == False:
                
                ###CHOOSE SMART PROGRAMMING STRATEGY AND START THE EXECUTION
                testPlan = originalPlan[test]
                if strategy == 'V':
                    increase_voltage(originalPlan[test],stepSet,stepReset,stepForm)
                elif strategy == 'SR':
                    if originalPlan[test].name == "Forming":
                        raise NameError('Forming is not compatible with SR strategy')
                    if originalPlan[test].name == "Reset":
                        testPlan = setReset(originalPlan[test])
                        writeLog(now,'    Set back at Vs = '+str(testPlan[0].vTop[1])+' V and ts = '+str(testPlan[0].tTop[1])+' micro s')
                    elif originalPlan[test].name == "Set":
                        testPlan = setReset(originalPlan[test])
                        writeLog(now,'    Reset back at Vr = '+str(testPlan[0].vBot[1])+' V and tr = '+str(testPlan[0].tBot[1])+' micro s')
                for i in range(int(math.ceil((len(addressNotWorking)/3.0)/274))):
                    print('Starting execution number '+str(times)+ ' with improved conditions. Part '+ str(i+1))
                    print (' ('+str(int(math.ceil((len(addressNotWorking)/3.0)/274)))+' parts) \n')
                    if not os.path.exists(mypath+'\\addressList\\'):
                        os.makedirs(mypath+'\\addressList\\')
                    if twoCells == True:
                        if i == int(math.ceil((len(addressNotWorking)/3.0)/274))-1:
                            print('done here')
                            if originalPlan[test].name == "Set":
                                var.testPlan = [var.set1]
                                updateAddressList_twoCells('even',addressNotWorking[i*274*3:])
                            elif originalPlan[test].name == "Reset":
                                var.testPlan = [var.reset1]
                                updateAddressList_twoCells('even',addressNotWorking[i*274*3:])
                        else:
                            print('done there')
                            if originalPlan[test].name == "Set":
                                var.testPlan = [var.set1]
                                updateAddressList_twoCells('even',addressNotWorking[i*274*3:(i+1)*274*3])
                            elif originalPlan[test].name == "Reset":
                                var.testPlan = [var.reset1]
                                updateAddressList_twoCells('even',addressNotWorking[i*274*3:(i+1)*274*3])
                   
                        copyfile('address_list.txt',mypath+'\\addressList\\address_list_op_'+str(test+1)+'_rep'+str(times)+'_part'+str(i+1)+'_even.txt')

                        var.adrsMode = 'L'
                        final.main('y',test+1,times,now)

                        if i == int(math.ceil((len(addressNotWorking)/3.0)/274))-1:
                            if originalPlan[test].name == "Set":
                                var.testPlan = [var.reset1]
                                updateAddressList_twoCells('odd',addressNotWorking[i*274*3:])
                            elif originalPlan[test].name == "Reset":
                                var.testPlan = [var.set1]
                                updateAddressList_twoCells('odd',addressNotWorking[i*274*3:])
                        else:
                            if originalPlan[test].name == "Set":
                                var.testPlan = [var.reset1]
                                updateAddressList_twoCells('odd',addressNotWorking[i*274*3:(i+1)*274*3])
                            elif originalPlan[test].name == "Reset":
                                var.testPlan = [var.set1]
                                updateAddressList_twoCells('odd',addressNotWorking[i*274*3:(i+1)*274*3])

                        copyfile('address_list.txt',mypath+'\\addressList\\address_list_op_'+str(test+1)+'_rep'+str(times)+'_part'+str(i+1)+'_odd.txt')

                        var.adrsMode = 'L'
                        final.main('y',test+1,times,now)
                        
                    elif twoCells == False:
                        
                        updateAddressList_oneCell(addressNotWorking,i)
                        copyfile('address_list.txt',mypath+'\\addressList\\address_list_op_'+str(test+1)+'_rep'+str(times)+'_part'+str(i+1)+'.txt')

                        var.testPlan = testPlan
                        var.adrsMode = 'L'
                        final.main('y',test+1,times,now)

                if twoCells == False:
                    if originalPlan[test].name == 'Set' or originalPlan[test].name == 'Forming':
                        writeLog(now,'    '+originalPlan[test].name+' at Vs = '+str(originalPlan[test].vTop[1])+\
                                 ' V and ts = '+str(originalPlan[test].tTop[1])+' micro s (rep. '+str(times)+')')
                    elif originalPlan[test].name == 'Reset':
                        writeLog(now,'    '+originalPlan[test].name+' at Vr = '+str(originalPlan[test].vBot[1])+\
                                 ' V and tr = '+str(originalPlan[test].tBot[1])+' micro s (rep. '+str(times)+')')
                elif twoCells == True:
                    if originalPlan[test].name == "Set":
                        writeLog(now,'    '+originalPlan[test].name+' half at Vs = '+str(var.set1.vTop[1])+\
                                 ' V and ts = '+str(var.set1.tTop[1])+' micro s (rep. '+str(times)+')')
                        writeLog(now,'    Reset half at Vr = '+str(var.reset1.vBot[1])+\
                                 ' V and tr = '+str(var.reset1.tBot[1])+' micro s (rep. '+str(times)+')')
                    elif originalPlan[test].name == 'Reset':
                        writeLog(now,'    '+originalPlan[test].name+' half at Vr = '+str(var.reset1.vBot[1])+\
                                 ' V and tr = '+str(var.reset1.tBot[1])+' micro s (rep. '+str(times)+')')
                        writeLog(now,'    Set half at Vs = '+str(var.set1.vTop[1])+\
                                 ' V and ts = '+str(var.set1.tTop[1])+' micro s (rep. '+str(times)+')')
                        
                writeLog(now,'        Addresses sent '+str(int(math.ceil((len(addressNotWorking)/3.0)/274)))+' times')
                ###Now only read the whole matrix in S mode
                var.adrsMode = 'S'
                var.testPlan = [readOperation]
                writeLog(now,'    Read')
                print('Starting repetition number '+ str(times)+ ' with improved conditions. Last part (read)\n')
                final.main('y',test+1,times,now)
                                    
            times += 1

            #Here if stop is not True it will do again the loop until stop is finally set to False
            #After this it will continue to the next
                  




def updateAddressList_oneCell(addresses,i):

    wr = open('address_list.txt','w')
    wr.write('Format must be like Wln,WL,BL,\n')
    for j in range(i*274,(i+1)*274):
        if j == len(addresses)/3:
            break
        wr.write(addresses[j*3]+','+addresses[j*3+1]+','+addresses[j*3+2]+','+'\n')
        
    wr.close()



def updateAddressList_twoCells(parity,addresses):

    wr = open('address_list.txt','w')
    wr.write('Format must be like Wln,WL,BL,\n')
    if parity == 'even':
        for j in range(0,len(addresses)/3):
            wr.write(addresses[j*3]+','+addresses[j*3+1]+','+addresses[j*3+2]+','+'\n')
    elif parity == 'odd':
        for j in range(0,len(addresses)/3):
            wr.write(addresses[j*3]+','+str(int(addresses[j*3+1])+1)+','+addresses[j*3+2]+','+'\n')                        
    wr.close()
    print(j)


def launch(testPlan,smartStrategy,readType,now):

##    if smartStrategy[0] == '': ##Because when the first test is a read, the smart strategy is empty
##        aux = 1
##    elif len(smartStrategy) > 1:
##        aux = 0
        
    #strategy = smartStrategy[aux].strategy #The strategy is the same for each group of operations (or test nb)
    #op = smartStrategy[aux].operation
    initVset = var.set1.vTop[1]
    initVreset = var.reset1.vBot[1]

    var.addressList = os.getcwd()+'\\address_list.txt'



    runTestPlan(testPlan,smartStrategy,readType,initVset,initVreset,now)





                                     
