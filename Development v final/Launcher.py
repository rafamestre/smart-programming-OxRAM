import xlrd
import variables_testParams_v3 as var
import SmartProgrammingAnalyzer as analyzer
#from SmartProgrammingAnalyzer import launch
from madClassesAndFunctions_v3 import SmartStrategy 
import datetime as dt
import os
from shutil import copyfile
import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy import stats
import sys
import wx
import fnmatch
from AnalysisStatistics import plotter

def readTestFlow():

    global now
    now = dt.datetime.now()

    ##Open TestFlow
    global workbook
    workbook = xlrd.open_workbook('SmartProgrammingTestFlow.xls')

    #Extract the parameters of the default strategies
    default = workbook.sheet_by_name('DefaultStrategies')
    global dVs
    global dVr
    global dVg
    global dts
    global dtr
    global dtg
    dVs = default.col(1)
    dVr = default.col(2)
    dVg = default.col(3)
    dts = default.col(4)
    dtr = default.col(5)
    dtg = default.col(6)

    #Extract parameter sheet and put it inside of the python file of variables
    parameters = workbook.sheet_by_name('MainParameters')
    global testName
    global waferLot
    global waferNb
    global AD
    global Barrette
    global Size
    global readTypeStr
    global readType
    testName = parameters.cell(0,1).value
    waferLot = parameters.cell(1,1).value
    waferNb = parameters.cell(2,1).value
    AD = parameters.cell(3,1).value
    Barrette = parameters.cell(4,1).value
    Size = parameters.cell(5,1).value
    readTypeStr = parameters.cell(6,1).value
    readType = var.dico.get(readTypeStr)

    global Xdie
    global Ydie

    #If the function is called from the prober, flag is 1 and it will recieve an updated list of the dies probed
    if proberFlag == 1:
        Xdie = X_die
        Ydie = Y_die
        waferLot = waferLotProber
        waferNb = waferNumberProber
        Size = matrixSizeProber
        testName = Size+'bitTest'
    elif proberFlag == 0:
        Xdie = parameters.cell(7,1).value
        Ydie = parameters.cell(8,1).value

    #Extract the information of the test plan

    testflow = workbook.sheet_by_name('TestFlow')
    global tests
    global plans
    global repPlan
    global strategies
    global Vs
    global Vr
    global repSet
    global repReset
    global repForming
    global ts
    global tr
    global Vgs
    global Vgr
    global stepVs
    global stepVr
    global Ronthres
    global Roffthres
    global Rformthres
    global Vsmart
    global dies
    tests = testflow.col(0)
    plans = testflow.col(1)
    repPlan = testflow.col(2)
    strategies = testflow.col(3)
    Vs = testflow.col(4)
    Vr = testflow.col(5)
    repSet = testflow.col(6)
    repReset = testflow.col(7)
    repForming = testflow.col(8)
    ts = testflow.col(9)
    tr = testflow.col(10)
    Vgs = testflow.col(11)
    Vgr = testflow.col(12)
    stepVs = testflow.col(13)
    stepVr = testflow.col(14)
    Ronthres = testflow.col(15)
    Roffthres = testflow.col(16)
    Rformthres = testflow.col(17)
    Vsmart = testflow.col(18)
    dies = testflow.col(19)


def create_plan(plan,readType):
    dicPlans = ['set','reset','form','read']
    testPlan=[]
    counter=1
    plan_temp=plan.split(",")
    for j in range(len(plan_temp)):
        if not plan_temp[j] in dicPlans:
            raise NameError('Error 8: Wrong kind of plan (has to be "set", "reset", "form" or "read")')
        if plan_temp[j] == 'read':
            testPlan.append(readType)
        else:
            testPlan.append(var.dico.get(plan_temp[j]))
    index=len(plan_temp)
    return testPlan,index

def checkErrors():

    #It checks if the following parameters make sense in each test
    #It doesn't modify the value of any of them, only raises errors
    #e.g. if the plan is 'set', Vs,Vgs,ts cannot be empty or wrong
    global plans
    global repPlan
    global strategies
    global Vs
    global Vr
    global ts
    global tr
    global Vgs
    global Vgr
    global Ronthres
    global Roffthres
    global Rformthres
    global Vsmart
    global dies

    global tests
    global readType
    
    dicStrategies = ['V','SR','TB']

    #Things that are not allowed:
    #1) Having a read in the test plan, unless it's right at the beginning
    #2) Having more than one forming
    #3) Having a forming together with other operations
    #4) Empty Rthreshold for an operation to be made
    #5) Invalid strategy
    #6) Empty voltage for a given operation
    #7) Empty time for a given operation
    #8) Wrong kind of plan

    count = 0
    for i in range(1,len(tests)):
        print(i)
        if isinstance(tests[i].value,float) == True:
            count += 1
        else:
            break
    nbTests = count

    errors = []
    
    for i in range(1,nbTests+1):
        
        firstRead = False
        withForming = False
        testPlan,index = create_plan(plans[i].value,readType)
        for j in range(index):
            if testPlan[0].name == 'Read':
                firstRead = True
##            elif not testPlan[0].name is 'Read' and strategies[i].value not in dicStrategies:
##                raise NameError('Error 5: invalid strategy name')
            
            if j == 0:
                if testPlan[j].name == 'Forming':
                    withForming = True
                    if index > 1 and not testPlan[1].name == 'Read':
                        
                        errors.append('Error 3: forming needs to be alone (or with read first) in a test plan')
                    if strategies[i].value == 'SR' or strategies[i].value == 'TB':
                        errors.append('Error 5: forming only goes with strategy V')    
            if j == 1:
                if testPlan[j].name == 'Read':
                    errors.append('Error 1: read can only appear at the beginning of the test plan (all operations include a read)')
                if testPlan[j].name == 'Forming':
                    withForming = True
                    if index > 2:
                        errors.append('Error 3: forming needs to be alone (or with read first) in a test plan')
                    if strategies[i].value == 'SR' or strategies[i].value == 'TB':
                        errors.append('Error 5: forming only goes with strategy V')
                    if firstRead is False:
                        errors.append('Error 3: forming needs to be alone (or with read first) in a test plan')
            if j > 1:
                if testPlan[j].name == 'Forming':
                    errors.append('Error 2: forming can only be at the beginning of the tests plan')
                if testPlan[j].name == 'Read':
                    errors.append('Error 1: read is only allowed in the first operation (all operations include a read)')
##                if strategies[j].value not in dicStrategies:
##                    raise NameError('Error 5: invalid strategy name')
                
            if testPlan[j].name == 'Set':
                if isinstance(Vs[i].value,basestring) is True:
                    errors.append('Error 6: invalid Vs voltage for '+testPlan[j].name)
                if isinstance(ts[i].value,basestring) is True:
                    errors.append('Error 7: invalid time for '+testPlan[j].name)
                if isinstance(Vgs[i].value,basestring) is True:
                    errors.append('Error 6: invalid Vgs voltage for '+testPlan[j].name)
            elif testPlan[j].name == 'Reset':
                if isinstance(Vr[i].value,basestring) is True:
                    errors.append('Error 6: invalid Vs voltage for '+testPlan[j].name)
                if isinstance(tr[i].value,basestring) is True:
                    errors.append('Error 7: invalid time for '+testPlan[j].name)
                if isinstance(Vgr[i].value,basestring) is True:
                    errors.append('Error 6: invalid Vgr voltage for '+testPlan[j].name)
                if strategies[i].value == 'SR':
                    if isinstance(Vsmart[i].value,basestring) is True:
                        errors.append('Error 6: invalid Vsmart voltage for '+testPlan[j].name)
            elif testPlan[j].name == 'Forming':
                if isinstance(Vs[i].value,basestring) is True:
                    errors.append('Error 6: invalid Vs voltage for '+testPlan[j].name)
                if isinstance(ts[i].value,basestring) is True:
                    errors.append('Error 7: invalid time for '+testPlan[j].name)
                if isinstance(Vgs[i].value,basestring) is True:
                    errors.append('Error 6: invalid Vgs voltage for '+testPlan[j].name)                
            if not testPlan[j].name == 'Read':
                threshold = [0,0,0]
                threshold[0] = Ronthres[i].value
                threshold[1] = Roffthres[i].value
                threshold[2] = Rformthres[i].value
                for m in range(0,3):
                    try:
                        float(threshold[m])
                    except ValueError:
                        errors.append('Error 4: threshold needs to be a number')
                    if float(threshold[m]) == 0:
                        errors.append('Error 4: treshold cannot be 0')
            elif testPlan[j].name == 'Read':
                if isinstance(repPlan[i].value,basestring) is False:
                    if repPlan[i].value > 0 and index > 1:
                        errors.append('Error 1: read at the beginning is not compatible with repetition of the test plan')
    if len(errors) == 0:
        writeLog(now,'Everything OK\n')
    elif len(errors) == 1:
        writeLog(now,errors)
        writeLog(now,'\n\n    EXECUTION ABORTED')
        raise NameError(errors)
    elif len(errors) > 1:
        writeLog(now,errors)
        writeLog(now,'\n\n    EXECUTION ABORTED')
        raise NameError('There were several errors (check log file)')
                
    
def fillTestFlow(name,testNb):

    #After checking if there is an important error with check_errors, this function checks
    #if the parameters that are not vital make sense.
    #If they don't make sense, they're value is set to the default
    #It checks the following
    global repPlan
    global strategies
    global Vs
    global Vr
    global repSet
    global repReset
    global repForming
    global ts
    global tr
    global Vgs
    global Vgr
    global stepVs
    global stepVr
    global Ronthres
    global Roffthres
    global Rformthres
    global Vsmart

    #For the strategies, it uses the following default values
    global dVs
    global dVr
    global dVg
    global dts
    global dtr
    global dtg

    #The warning is also global
    global warning

    dicAux = {'Set': 1,'Reset': 2, 'Forming':3}
    dicStrategies = ['V','SR','TB']
    
    warning = []

    #If one of the next parameters is not defined with a number, it will be set to 0

    if isinstance(repSet[testNb].value,basestring) is True:
        repSet[testNb].value = 0.0
        warning.append('    RepSet was a string, value set to 0')
    if isinstance(repReset[testNb].value,basestring) is True:
        repReset[testNb].value = 0.0
        warning.append('    RepReset was a string, value set to 0')
    if isinstance(repForming[testNb].value,basestring) is True:
        repForming[testNb].value = 0.0
        warning.append('    RepForming was a string, value set to 0')
    if isinstance(stepVs[testNb].value,basestring) is True:
        stepVs[testNb].value = 0.0
        warning.append('    StepVs was a string, value set to 0')
    if isinstance(stepVr[testNb].value,basestring) is True:
        stepVr[testNb].value = 0.0
        warning.append('    StepVr was a string, value set to 0')
    if isinstance(repPlan[testNb].value,basestring) is True:
        warning.append('    RepPlan was a string, value set to 0')
        repPlan[testNb].value = 0.0

    if not strategies[testNb].value in dicStrategies:
        warning.append('    Strategy was unknown, value set to X (will simply repeat)')
        strategies[testNb].value = 'X'

    #If one of these important parameters is not defined with a number, it will be set to the default value
    #Note: they were already checked with checkErrros(), therefore only the non-critical ones will be set to default

    if isinstance(Vs[testNb].value,basestring) is True:
        Vs[testNb].value = dVs[dicAux.get('Set')].value
        warning.append('    Vs was a string, value set to default: '+str(dVs[dicAux.get('Set')].value)+' V')
    if isinstance(Vr[testNb].value,basestring) is True:
        Vr[testNb].value = dVr[dicAux.get('Reset')].value
        warning.append('    Vr was a string, value set to default: '+str(dVr[dicAux.get('Reset')].value)+' V')
    if isinstance(Vgs[testNb].value,basestring) is True:
        warning.append('    Vgs was a string, value set to default (check in parameter file)')
        if name == 'Set':
            Vgs[testNb].value = dVg[dicAux.get('Set')].value
        elif name == 'Forming':
            Vgs[testNb].value = dVg[dicAux.get('Forming')].value
    if isinstance(Vgr[testNb].value,basestring) is True:
        Vgr[testNb].value = dVg[dicAux.get('Reset')].value
        warning.append('    Vgr was a string, value set to default: '+str(dVg[dicAux.get('Reset')].value)+' V')
    if isinstance(ts[testNb].value,basestring) is True:
        if name == 'Set':
            ts[testNb].value = dts[dicAux.get('Set')].value
        elif name == 'Forming':
            ts[testNb].value = dts[dicAux.get('Forming')].value
        warning.append('    ts was a string, value set to default: (check in parameter file)')
    if isinstance(tr[testNb].value,basestring) is True:
        tr[testNb].value = dtr[dicAux.get('Reset')].value
        warning.append('    tr was a string, value set to default: '+str(dtr[dicAux.get('Reset')].value)+' micro s')
    if isinstance(Vsmart[testNb].value,basestring) is True:
        Vsmart[testNb].value = dVs[dicAux.get('Set')].value
        warning.append('    Vsmart was a string, value set to default: '+str(dVs[dicAux.get('Set')].value)+' V')

    #Finally, fill in the threshold resistances (already checked in error function)

    if name == 'Set':
        var.Ron = Ronthres[testNb].value*1e3
    elif name == 'Reset':
        var.Roff = Roffthres[testNb].value*1e3
    elif name == 'Forming':
        var.Rform = Rformthres[testNb].value*1e3

def writeLog(now,string):

    mypath = r'%s\%s\%s' % (var.resultsOutput,
                                var.waferLot + 'w' + var.waferNo,
                                now.strftime("%Y-%m-%d")+"__test="+var.testName+"__dut="+var.dutName)
    if not os.path.exists(mypath):
        os.makedirs(mypath)

    nowTime = now.strftime("%H-%M-%S")
    if os.path.isfile(mypath+'\\log_'+nowTime+'.txt') is False:
        wr = open(mypath+'\\log_'+nowTime+'.txt','w')
        wr.write('Log file for test flow on ' + now.strftime("%Y-%m-%d") +' at ' + now.strftime("%H:%M:%S") + '\n\n')
        wr.close()
        
    wr = open(mypath+'\\log_'+nowTime+'.txt','a')
    if isinstance(string,list) is True:
        for i in range(len(string)):
            wr.write(string[i]+'\n')
    else:
        wr.write(string+'\n')
    wr.close()

def writeWarnings(currentTest):


    mypath = r'%s\%s\%s' % (var.resultsOutput,
                            var.waferLot + 'w' + var.waferNo,
                            now.strftime("%Y-%m-%d")+"__test="+var.testName+"__dut="+var.dutName)

    nowTime = now.strftime("%H-%M-%S")    

    if os.path.isfile(mypath+'\\warnings_'+nowTime+'.txt') is False:
        wr = open(mypath+'\\warnings_'+nowTime+'.txt','w')
    else:
        wr = open(mypath+'\\warnings_'+nowTime+'.txt','a')
        
    wr.write(currentTest+'\n')
    if len(warning) == 0:
        wr.write('No warnings\n\n')
    else:
        for i in range(len(warning)):
            wr.write(warning[i]+'\n')
    wr.write('\n')
    wr.close()

def writeLaunch(nbTests):

    folders = []
    y = []
    newY = []
    global launchNb
    newFolders = ''
    mypath = r'%s\%s\%s' % (var.resultsOutput,
                            var.waferLot + 'w' + var.waferNo,
                            now.strftime("%Y-%m-%d")+"__test="+var.testName+"__dut="+var.dutName)
    if not os.path.exists(mypath):
            os.makedirs(mypath)
    files = [f for f in fnmatch.filter(os.listdir(mypath),'launch*')]
    if len(files) == 0:
        filename = "launch_001.txt"
        launchNb = 1
    else:
        for i in range(len(files)):
            y.sort(y.append(int(files[i][-7:-4])))   #return a list of the last 3 digits in folders as integers
        filename = ('launch_%s%s' % ((3 - len(str(y[-1]+1)))*"0" + str(y[-1]+1),'.txt'))
        launchNb = y[-1]+1

    folders = [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]
    y=[]
    global testList
    testList = []
    if len(folders) == 0:
        testList = []
        y.append(-1)
    else:
        for i in range(len(folders)):
            y.sort(y.append(int(folders[i][-3:])))   #return a list of the last 3 digits in folders as integers
    for i in range(len(testsToDo)):
        newY.append(y[-1]+1+i)
    for i in range(len(newY)):
        testList.append(('Test_%s' % ((3 - len(str(newY[i])))*"0" + str(newY[i]))))
    for i in range(len(testList)):
        newFolders += testList[i]
        if not i == len(testList)-1:
            newFolders += ', '

            
    nowTime = now.strftime("%H-%M-%S")
    
    wr = open(mypath+'\\'+filename,'w')

    nowTime = now.strftime("%H-%M-%S")
    
    writeLog(now,['Test folders: ','    '+newFolders])
    
    wr.write(nowTime+'\n')
    wr.write(waferLot+'\n')
    wr.write(str(int(waferNb))+'\n')
    wr.write(AD+'_'+Barrette+'\n')
    wr.write(Size+'\n')
    wr.write(str(int(Xdie))+'x'+str(int(Ydie))+'\n')
    for i in range(len(testList)):
        wr.write(testList[i]+'\t'+str(tests[testsToDo[i]].value)+'\n')
    wr.close()
    
    

def test_die(wafer_lot,wafer_number,X_die_prober,Y_die_prober,cut_size,flag):

    app= wx.App(False)
    app.locale = wx.Locale(wx.LANGUAGE_DEFAULT)

    global proberFlag
    global waferLotProber
    global waferNumberProber
    global matrixSizeProber
    waferLotProber = wafer_lot
    waferNumberProber = wafer_number
    matrixSizeProber = cut_size
    proberFlag = flag
    global X_die
    X_die = X_die_prober
    global Y_die
    Y_die = Y_die_prober
    
    readTestFlow()
        
    var.testName = testName
    var.waferLot = waferLot
    var.waferNo = str(int(waferNb))
    var.dutName = AD+'_'+Barrette
    var.mtxSize = Size
    print('\n\n'+Size+'  matrix')

    writeLog(now,['Wafer lot: '+waferLot,'Wafer Nb: '+str(int(waferNb)),\
                  'DUT: '+var.dutName,'Matrix size: '+Size,'Die: '+str(int(Xdie))+'-'+str(int(Ydie))+'\n'])
    writeLog(now,'Checking errors...')
    
    checkErrors()


    
    count = 0
    for i in range(1,len(tests)):
        if isinstance(tests[i].value,float) is True:
            count += 1
        else:
            break
    nbTests = count
    
    global testsToDo
    testsToDo = []
    for test in range(1,nbTests+1):
        dieNb = str(dies[test].value).split(';')
        if len(dieNb) == 1:
            testsToDo.append(test)
        elif len(dieNb) == 2:
            if dieNb[0] == str(Xdie) and dieNb[1] == str(Ydie):
                testsToDo.append(test)

    #writeDieFile(nbTests)
    writeLaunch(nbTests)
    
    testDic = {'Set':var.set1,'Reset':var.reset1,'Forming':var.form1}

    #Execution of all the test plans
    

    for test in range(1,nbTests+1):

        if test in testsToDo:
            writeLog(now,'\nEXECUTION OF TEST PLAN ' + str(int(tests[test].value))+'\n')
            testPlan,index = create_plan(plans[test].value,readType)
            var.testPlan = testPlan
            smart = []
            writeLog(now,'Obtaining parameters...')
            
            for opName in ['Set','Reset','Forming']:
                
                fillTestFlow(opName,test)
                if opName == 'Set':
                    if len(warning)>0:
                        writeLog(now,'There were some warnings: ')
                        writeLog(now,warning) #Warning written only the first time
                        writeWarnings(testList[testsToDo.index(test)])
                    else:
                        writeLog(now,'    No warnings')
                        writeWarnings(testList[testsToDo.index(test)])
                    var.set1.vTop = [Vs[test].value,Vs[test].value,0]
                    var.set1.vGate = [Vgs[test].value,Vgs[test].value,0]
                    var.set1.tTop[1] = ts[test].value*1e-6
                    var.set1.tBot[1] = ts[test].value*1e-6
                    var.set1.tGate[1] = ts[test].value*1e-6
                    if strategies[test].value == 'SR':
                        var.resetSmart.vTop = var.reset1.vTop
                        var.resetSmart.vGate = var.reset1.vGate
                        var.resetSmart.vBot = [Vsmart[test].value,Vsmart[test].value,0]
                        var.resetSmart.tBot = var.reset1.tBot
                        var.resetSmart.tGate = var.reset1.tGate
                        var.resetSmart.tTop = var.reset1.tTop
                elif opName == 'Forming':
                    var.form1.vTop = [Vs[test].value,Vs[test].value,0]
                    var.form1.vGate = [Vgs[test].value,Vgs[test].value,0]
                    var.form1.tTop[1] = ts[test].value*1e-6
                    var.form1.tBot[1] = ts[test].value*1e-6
                    var.form1.tGate[1] = ts[test].value*1e-6
                elif opName == 'Reset':
                    var.reset1.vBot = [Vr[test].value,Vr[test].value,0]
                    var.reset1.vGate = [Vgr[test].value,Vgr[test].value,0]
                    var.reset1.tTop[1] = tr[test].value*1e-6
                    var.reset1.tBot[1] = tr[test].value*1e-6
                    var.reset1.tGate[1] = tr[test].value*1e-6
                    if strategies[test].value == 'SR':
                        var.setSmart.vTop = [Vsmart[test].value,Vsmart[test].value,0]
                        var.setSmart.vGate = var.set1.vGate
                        var.setSmart.vBot = var.set1.vBot
                        var.setSmart.tBot = var.set1.tBot
                        var.setSmart.tGate = var.set1.tGate
                        var.setSmart.tTop = var.set1.tTop

            
            
            if repPlan[test].value > 0:
                writeLog(now,['\nCreating smart programs...','Test plan '+\
                              str(int(tests[test].value))+' consists of ('+str(int(repPlan[test].value))+' times):'])
            else:
                writeLog(now,['\nCreating smart programs...','Test plan '+\
                              str(int(tests[test].value))+' consists of:'])

            for j in range(0,index):
                if j == 0 and testPlan[j].name == 'Read':
                    writeLog(now,'    '+readTypeStr)
                    smart.append('')
                if testPlan[j].name == 'Set':
                    writeLog(now,'    '+testPlan[j].name+' with strategy '+strategies[test].value+' ('+\
                             str(int(repSet[test].value))+' rep)')
                    smart.append(SmartStrategy(strategies[test].value,testPlan[j],
                                             stepVs[test].value,int(repSet[test].value)+1,Ronthres[test].value*1e3,readType))
                elif testPlan[j].name == 'Reset':
                    writeLog(now,'    '+testPlan[j].name+' with strategy '+strategies[test].value+' ('+\
                             str(int(repReset[test].value))+' rep)')
                    smart.append(SmartStrategy(strategies[test].value,testPlan[j],
                                             stepVr[test].value,int(repReset[test].value)+1,Roffthres[test].value*1e3,readType))
                elif testPlan[j].name == 'Forming':
                    writeLog(now,'    '+testPlan[j].name+' with strategy '+strategies[test].value+' ('+\
                             str(int(repForming[test].value))+' rep)')
                    smart.append(SmartStrategy(strategies[test].value,testPlan[j],
                                             stepVs[test].value,int(repForming[test].value)+1,Rformthres[test].value*1e3,readType))

            writeLog(now,['\nThreshold resistances are:','    Ron:\t'+str(Ronthres[test].value*1e3)+' Ohm',\
                          '    Roff:\t'+str(Roffthres[test].value*1e3)+' Ohm','    Rform:\t'+str(Rformthres[test].value*1e3)+' Ohm'])

            if repPlan[test].value > 0:
                writeLog(now,'\nStarting execution of test plan '+\
                         str(int(tests[test].value))+':\n')
                testPlan = var.testPlan*(int(repPlan[test].value)+1)
                smart = smart*(int(repPlan[test].value)+1)
            else:
                writeLog(now,'\nStarting '+str(int(repPlan[test].value))+' executions of test plan '+\
                         str(int(tests[test].value))+':\n')
            ##sys.exit()
            analyzer.launch(testPlan,smart,readType,now)
            writeLog(now,'')


    writeLog(now,'\nCopying test flow...')
    mypath = r'%s\%s\%s' % (var.resultsOutput,
                                var.waferLot + 'w' + var.waferNo,
                                now.strftime("%Y-%m-%d")+"__test="+var.testName+"__dut="+var.dutName)
    nowTime = now.strftime("%H-%M-%S")
    copyfile('SmartProgrammingTestFlow.xls',mypath+'/TestFlow'+\
             '_'+nowTime+'_die_'+str(int(Xdie))+'-'+str(int(Ydie))+'.xls')
    writeLog(now,'\nPROGRAM FINISHED CORRECTLY')


##        
##    writeLog(now,'\nEXECUTING STATISTIC ANALYSIS\n')
##
##    print('Starting statistical analysis\n')
##
##    try:
##        print(launchNb)
##        plotter(mypath,launchNb)
##    except:
##        plt.close('all')
##        print('There was an error during the statistical analysis')
##        writeLog(now,'There was an error during the statistical analysis')
##
##    writeLog(now,'\nSTATISTICS FINISHED\n\n\n\n')

if '__main__'==__name__:
    
    test_die(wafer_lot='',wafer_number='',X_die_prober='',Y_die_prober='',cut_size='',flag=0)

