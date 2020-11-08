from __future__ import division
import xlrd
import datetime as dt
import os
from shutil import copyfile
import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy import stats
import sys
import fnmatch
from matplotlib import cm
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import LogFormatterMathtext
import matplotlib.ticker as ticker
from itertools import compress



def getDay(date):

    date = date.split(';')
    day = date[0]
    month = date[1]
    year = date[2]

    theDate = day+'-'+month+'-'+year

    return theDate

def getDie(die):

    die = die.split(';')
    die1 = die[0]
    die2 = die[1]

    return die1,die2


def readTestFlow(path,sheet):

    print('Read')
    workbookPath = path+'\\efficiencies.xls'
    
    ##Open TestFlow
    workbook = xlrd.open_workbook(workbookPath)

    #Extract the information of the test plan
    sheetName = 'Feuil'+str(sheet)
    testflow = workbook.sheet_by_name(sheetName)
    global compare
        
    tests = testflow.col(0)
    strategies = testflow.col(1)
    plan = testflow.col(2)
    die = testflow.col(3)
    Vs = testflow.col(4)
    Vr = testflow.col(5)
    stepVs = testflow.col(6)
    stepVr = testflow.col(7)
    repSet = testflow.col(8)
    repReset = testflow.col(9)
    date = testflow.col(10)
    time = testflow.col(11)
    size = testflow.col(12)
    threshold = testflow.col(13)
    repPlan = testflow.col(14)
    opNb = testflow.col(15)


    return tests, strategies, plan, die, Vs, Vr, stepVs, stepVr, repSet, repReset, date, size, threshold,time, repPlan, opNb




def readR(mypath,operationFolder):


    ###Initialization
    headerNb = 6
    results=[]
    header=[]
    SL=[]
    WL=[]
    BL=[]
    Rmeas=[]
    addressNotWorking=[]

    mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'

    if os.path.isdir(mypath2) == False:
        mypath2 = mypath+'\\'+operationFolder+'\\'
    
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

    return Rmeas, SL, WL, BL
    
def writeFiles(path,matSize):

    if matSize == '4k':
        sheet = 2
    elif matSize == '64k':
        sheet = 1
    elif matSize == '1M':
        sheet = 3

    #sheet = 4

    sizeDic = {'4k':4096,'64k':65536,'1M':1048576}
    
    [tests, strategies, plan, die, Vs, Vr, stepVs, stepVr, repSet, repReset, date, size, threshold, time, repPlan,opNb] = readTestFlow(path,sheet)
        
    count = 0

    Ron = 10*1e3
    Roff = 40*1e3    

    colorList = ['b','r','g','c','m','y','k']
    
    for i in range(1,len(tests)):
        if isinstance(tests[i].value,float) is True:
            count += 1
        else:
            break
    nbTests = count

    dies = []
    for test in range(1,nbTests+1):
        dies.append(die[test].value)

    doTest = [0]*(nbTests)

    diffDies = list(set(dies))
    
    for d in range(len(diffDies)):

        dieTests = [i+1 for i, j in enumerate(dies) if dies[i] == diffDies[d]]
        
        formed = False

        print(dieTests)
        print(diffDies[d])
        
        for test in dieTests:
            
            theDate = getDay(date[test].value)
            testPlan = plan[test].value.split(",")
            
            if testPlan[0] == 'form':

                formed = True
                print('Forming die '+diffDies[d])


                mypath = r'%s' % (path+'\\'+size[test].value+'bit\\'+theDate+'\\')
                dirFiles = os.listdir(mypath)
                filesAux = [fnmatch.fnmatchcase(dirFiles[f],'Test_*') for f in range(len(dirFiles))]
                files = [t for t,k in zip(dirFiles,filesAux) if k]
                filename = []
                y=[]
                
                if len(files) == 0:
                    raise NameError('No files in directory')
                else:
                    for i in range(len(files)):
                        y.append(int(files[i][-3:]))   #return a list of the last 3 digits in folders as integers
                    y.sort()
                    
                index = [t for t,x in enumerate(y) if x == tests[test].value]
                theFile = files[index[0]]

                mypath = mypath + theFile + '\\'

                filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'*Read*') if os.path.isdir(mypath+f)]

                opNb = [filesAux[t][2:3] for t in range(len(filesAux))]
                opNb = [int(list(set(opNb))[t]) for t in range(len(set(opNb)))]
                opNb = str(max(opNb))

                filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'Op'+opNb+'__Read_Rep*') if os.path.isdir(mypath+f)]

                if len(filesAux) == 0:
                    operationFolder = 'Op'+opNb + '__Read'
                else:
                    repNb = len(filesAux)
                    operationFolder = 'Op'+opNb + '__Read_Rep'+str(repNb)
                
                mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
                Rmeas, SL, WL, BL = readR(mypath,operationFolder)

                RmeasLog = [np.log10(np.abs(float(Rmeas[i]))) for i in range(0,len(Rmeas))]
                RmeasFloat = [np.abs(float(Rmeas[i])) for i in range(0,len(Rmeas))]
                nonWorkingForming = [0]*len(RmeasFloat)

                for res in range(len(RmeasFloat)):

                    if RmeasFloat[res] > threshold[test].value*1e3:

                        nonWorkingForming[res] = 1

        if not formed:
            print(formed)
            nonWorkingForming = [0]*sizeDic.get(size[dieTests[0]].value)

        ###I read the forming, now I check the efficiency

        for test in dieTests:

            testPlan = plan[test].value.split(",")

            if not testPlan[0] == 'form':

                theDate = getDay(date[test].value)
                [die1,die2] = getDie(die[test].value)
            
                mypath = r'%s' % (path+'\\'+size[test].value+'bit\\'+theDate+'\\')
                dirFiles = os.listdir(mypath)
                filesAux = [fnmatch.fnmatchcase(dirFiles[f],'Test_*') for f in range(len(dirFiles))]
                files = [t for t,k in zip(dirFiles,filesAux) if k]
                filename = []
                y=[]
                
                if len(files) == 0:
                    raise NameError('No files in directory')
                else:
                    for i in range(len(files)):
                        y.append(int(files[i][-3:]))   #return a list of the last 3 digits in folders as integers
                    y.sort()
                    
                index = [t for t,x in enumerate(y) if x == tests[test].value]
                theFile = files[index[0]]

                mypath = mypath + theFile + '\\'


                if strategies[test].value == 'TB':

                    if size[test].value == '64k' or size[test].value == '1M':

                        print(size[test].value+' TB die '+diffDies[d])

                        repePlan = repPlan[test].value
                        flagSet = False
                        flagReset = False
                        
                        if testPlan[0] == 'set':
                            setFolder = 1
                            resetFolder = 0
                        elif testPlan[0] == 'reset':
                            setFolder = 0
                            resetFolder = 1


                        for planRep in range(1,2*(int(repePlan)+1)+1):
                        
                            filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'Op'+str(planRep)+'__Read*') if os.path.isdir(mypath+f)]

                            effAfter = []
                            effBefore = []
                            workingCellsAfter = []
                            workingCellsBefore = []

                            repetitions = len(filesAux)

                            for repe in range(repetitions):

                                operationFolder = filesAux[repe]
                                mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
                                Rmeas, SL, WL, BL = readR(mypath,operationFolder)
                                print(mypath2)

                                RmeasLog = [np.log10(np.abs(float(Rmeas[i]))) for i in range(0,len(Rmeas))]
                                RmeasFloat = [np.abs(float(Rmeas[i])) for i in range(0,len(Rmeas))]
                                Working = [0]*int(len(RmeasFloat)/2)
                                nonWorkingFormingTB = [0]*int(len(RmeasFloat)/2)
                                workingBefore = []
        
                                for res in range(0,len(RmeasFloat),2):

                                    if nonWorkingForming[res] == 1 or nonWorkingForming[res+1] == 1:
                                        nonWorkingFormingTB[int(res/2)] = 1

                                    if planRep%2 == setFolder: 

                                        if RmeasFloat[res] - RmeasFloat[res+1] < 0 and nonWorkingFormingTB[int(res/2)] == 0:
                                            Working[int(res/2)] = 1
                                        if RmeasFloat[res] < Ron and nonWorkingFormingTB[int(res/2)] == 0:
                                            workingBefore.append(1)
                                            
                                    elif planRep%2 == resetFolder:
                                        if RmeasFloat[res] - RmeasFloat[res+1] > 0 and nonWorkingFormingTB[int(res/2)] == 0:
                                            Working[int(res/2)] = 1
                                        if RmeasFloat[res] > Roff and nonWorkingFormingTB[int(res/2)] == 0:
                                            workingBefore.append(1)
                                        

                                effAfter.append(Working.count(1)/(int(len(RmeasFloat)/2)-nonWorkingFormingTB.count(1)))
                                workingCellsAfter.append(Working.count(1))
                                if repe == 0:
                                    effBefore = workingBefore.count(1)/(int(len(RmeasFloat)/2)-nonWorkingFormingTB.count(1))
                                    workingCellsBefore = workingBefore.count(1)
                                
                            totalCells = int(len(RmeasFloat)/2-nonWorkingFormingTB.count(1))                     
                                
                            if planRep%2 == setFolder:
                                fileName = size[test].value+'_'+'TB_set'
                                thres = Ron
                            else:
                                fileName = size[test].value+'_'+'TB_reset'
                                thres = Roff

                            print(fileName)
                            print(planRep)
                                
                            if os.path.isfile(path+'\\Mixed\\efficiencies\\'+fileName+'.txt') is False:
                                wr = open(path+'\\Mixed\\efficiencies\\'+fileName+'.txt','w')
                                wr.write('before\tafter\ttotal\tV1\tV2\trep\tdate\ttest\tth\tt\n')
                                wr.write(str(workingCellsBefore)+'\t'+str(workingCellsAfter[-1])+'\t'+str(totalCells)+'\t'+str(Vs[test].value)+'\t'+str(Vr[test].value)+\
                                         '\t'+str(repetitions-1)+'\t'+theDate+'\t'+str(int(tests[test].value))+\
                                         '\t'+str(int(thres))+'\t'+str(time[test].value)+'\n')
                                wr.close()
                            else:
                                wr = open(path+'\\Mixed\\efficiencies\\'+fileName+'.txt','a')
                                wr.write(str(workingCellsBefore)+'\t'+str(workingCellsAfter[-1])+'\t'+str(totalCells)+'\t'+str(Vs[test].value)+'\t'+str(Vr[test].value)+\
                                         '\t'+str(repetitions-1)+'\t'+theDate+'\t'+str(int(tests[test].value))+\
                                         '\t'+str(int(thres))+'\t'+str(time[test].value)+'\n')
                                wr.close()
                                
                    elif size[test].value == '4k':

                        print(size[test].value+' TB die '+diffDies[d])

                        filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'*Read_rep*') if os.path.isdir(mypath+f)]
                        opNb = [filesAux[t][2:3] for t in range(len(filesAux))]
                        opNb = [int(list(set(opNb))[t]) for t in range(len(set(opNb)))]
                        opNb = str(min(opNb))

                        effAfter = []
                        effBefore = []
                        workingCellsAfter = []
                        workingCellsBefore = []

                        repetitions = len(filesAux)+1

                        for repe in range(repetitions):

                            if repe == 0:
                                operationFolder = 'Op'+opNb + '__Read'
                            else:
                                operationFolder = 'Op'+opNb + '__Read_rep'+str(repe)

                            mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
                            Rmeas, SL, WL, BL = readR(mypath,operationFolder)
                            print(mypath2)
                            
                            RmeasLog = [np.log10(np.abs(float(Rmeas[i]))) for i in range(0,len(Rmeas))]
                            RmeasFloat = [np.abs(float(Rmeas[i])) for i in range(0,len(Rmeas))]
                            Working = [0]*int(len(RmeasFloat)/2)
                            nonWorkingFormingTB = [0]*int(len(RmeasFloat)/2)
                            workingBefore = []
    
                            for res in range(0,len(RmeasFloat),2):

                                if nonWorkingForming[res] == 1 or nonWorkingForming[res+1] == 1:
                                    nonWorkingFormingTB[int(res/2)] = 1

                                if testPlan[0]=='set':

                                    if RmeasFloat[res] - RmeasFloat[res+1] < 0 and nonWorkingFormingTB[int(res/2)] == 0:
                                        Working[int(res/2)] = 1
                                    if RmeasFloat[res] < Ron and nonWorkingFormingTB[int(res/2)] == 0:
                                        workingBefore.append(1)
                                        
                                elif testPlan[0]=='reset':

                                    if RmeasFloat[res] - RmeasFloat[res+1] > 0 and nonWorkingFormingTB[int(res/2)] == 0:
                                        Working[int(res/2)] = 1
                                    if RmeasFloat[res] > Roff and nonWorkingFormingTB[int(res/2)] == 0:
                                        workingBefore.append(1)

                            effAfter.append(Working.count(1)/(int(len(RmeasFloat)/2)-nonWorkingFormingTB.count(1)))
                            workingCellsAfter.append(Working.count(1))
                            if repe == 0:
                                effBefore = workingBefore.count(1)/(int(len(RmeasFloat)/2)-nonWorkingFormingTB.count(1))
                                workingCellsBefore = workingBefore.count(1)
                                
                        totalCells = int(len(RmeasFloat)/2-nonWorkingFormingTB.count(1))
                        
                        if testPlan[0]=='set':
                            fileName = size[test].value+'_'+'TB_set'
                            thres = Ron
                        else:
                            fileName = size[test].value+'_'+'TB_reset'
                            thres = Roff

                        
                        if os.path.isfile(path+'\\Mixed\\efficiencies\\'+fileName+'.txt') is False:
                            wr = open(path+'\\Mixed\\efficiencies\\'+fileName+'.txt','w')
                            wr.write('Before \tAfter\tTotal\tV set\tV reset\tRepetitions\tDate\tTest number\tThreshold\tTime\n')
                            wr.write(str(workingCellsBefore)+'\t'+str(workingCellsAfter[-1])+'\t'+str(totalCells)+'\t'+str(Vs[test].value)+'\t'+\
                                     str(Vr[test].value)+'\t'+str(repetitions-1)+'\t'+theDate+'\t'+str(int(tests[test].value))+\
                                     '\t'+str(int(thres))+'\t'+str(time[test].value)+'\n')
                            wr.close()
                        else:
                            wr = open(path+'\\Mixed\\efficiencies\\'+fileName+'.txt','a')
                            wr.write(str(workingCellsBefore)+'\t'+str(workingCellsAfter[-1])+'\t'+str(totalCells)+'\t'+str(Vs[test].value)+'\t'+\
                                     str(Vr[test].value)+'\t'+str(repetitions-1)+'\t'+theDate+'\t'+str(int(tests[test].value))+\
                                     '\t'+str(int(thres))+'\t'+str(time[test].value)+'\n')
                            wr.close()
                    
                else:

                    if strategies[test].value == 'V' and size[test].value == '64k' and len(testPlan) > 1:

                        print(size[test].value+' V (set,reset) die '+diffDies[d])

                        repePlan = repPlan[test].value
                        flagSet = False
                        flagReset = False
                        
                        if testPlan[0] == 'set':
                            setFolder = 1
                            resetFolder = 0
                        elif testPlan[0] == 'reset':
                            setFolder = 0
                            resetFolder = 1

                        rAux = threshold[test].value.split(';')
                        RonAux = float(rAux[0])*1e3
                        RoffAux = float(rAux[1])*1e3
                        
                        for planRep in range(1,2*(int(repePlan)+1)+1):
                        
                            filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'Op'+str(planRep)+'__Read*') if os.path.isdir(mypath+f)]

                            effAfterSet = []
                            effBeforeSet = []
                            effAfterReset = []
                            effBeforeReset = []
                            workingCellsAfterSet = []
                            workingCellsBeforeSet = []
                            workingCellsAfterReset = []
                            workingCellsBeforeReset = []

                            repetitions = len(filesAux)

                            for repe in range(repetitions):

                                operationFolder = filesAux[repe]
                                mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
                                Rmeas, SL, WL, BL = readR(mypath,operationFolder)
                                print(mypath2)

                                RmeasLog = [np.log10(np.abs(float(Rmeas[i]))) for i in range(0,len(Rmeas))]
                                RmeasFloat = [np.abs(float(Rmeas[i])) for i in range(0,len(Rmeas))]
                                WorkingSet = [0]*int(len(RmeasFloat))
                                WorkingReset = [0]*int(len(RmeasFloat))
                                workingBeforeSet = []
                                workingBeforeReset = []
        
                                for res in range(0,len(RmeasFloat)):

                                    if planRep%2 == setFolder: 

                                        if RmeasFloat[res] < RonAux and nonWorkingForming[res] == 0:
                                            WorkingSet[res] = 1
                                        if RmeasFloat[res] < RonAux and nonWorkingForming[res] == 0:
                                            workingBeforeSet.append(1)
                                            
                                    elif planRep%2 == resetFolder: 

                                        if RmeasFloat[res] > RoffAux and nonWorkingForming[res] == 0:
                                            WorkingReset[res] = 1
                                        if RmeasFloat[res] > RoffAux and nonWorkingForming[res] == 0:
                                            workingBeforeReset.append(1)

                                effAfterSet.append(WorkingSet.count(1)/(len(RmeasFloat)-nonWorkingForming.count(1)))
                                effAfterReset.append(WorkingReset.count(1)/(len(RmeasFloat)-nonWorkingForming.count(1)))
                                workingCellsAfterSet.append(WorkingSet.count(1))
                                workingCellsAfterReset.append(WorkingReset.count(1))
                                if repe == 0:
                                    effBeforeSet = effAfterSet[0]
                                    effBeforeReset = effAfterReset[0]
                                    workingCellsBeforeSet = WorkingSet.count(1)
                                    workingCellsBeforeReset = WorkingReset.count(1)
                                    
                            totalCells = int(len(RmeasFloat-nonWorkingForming.count(1)))

                            if planRep%2 == setFolder:
                                fileName = size[test].value+'_'+strategies[test].value+'_set'
                                Vinit = Vs[test].value
                                Vfin = Vs[test].value+stepVs[test].value*(repetitions-1)
                                effBefore = effBeforeSet
                                effAfter = effAfterSet
                                workingCellsAfter = workingCellsAfterSet
                                workingCellsBefore = workingCellsBeforeSet
                                thres = RonAux
                            elif planRep%2 == resetFolder:
                                fileName = size[test].value+'_'+strategies[test].value+'_reset'
                                Vinit = Vr[test].value
                                Vfin = Vr[test].value+stepVr[test].value*(repetitions-1)
                                effBefore = effBeforeReset
                                effAfter = effAfterReset
                                workingCellsAfter = workingCellsAfterReset
                                workingCellsBefore = workingCellsBeforeReset
                                thres = RoffAux
                                
                            if os.path.isfile(path+'\\Mixed\\efficiencies\\'+fileName+'.txt') is False:
                                wr = open(path+'\\Mixed\\efficiencies\\'+fileName+'.txt','w')
                                wr.write('Before \tAfter\tTotal\tV initial\tV final\tRepetitions\tDate\tTest number\tThreshold\tTime\n')
                                wr.write(str(workingCellsBefore)+'\t'+str(workingCellsAfter[-1])+'\t'+str(totalCells)+'\t'+str(Vinit)+'\t'+\
                                         str(Vfin)+'\t'+str(repetitions-1)+'\t'+theDate+'\t'+str(int(tests[test].value))+\
                                         '\t'+str(int(thres))+'\t'+str(time[test].value)+'\n')
                                wr.close()
                            else:    
                                wr = open(path+'\\Mixed\\efficiencies\\'+fileName+'.txt','a')
                                wr.write(str(workingCellsBefore)+'\t'+str(workingCellsAfter[-1])+'\t'+str(totalCells)+'\t'+str(Vinit)+'\t'+\
                                         str(Vfin)+'\t'+str(repetitions-1)+'\t'+theDate+'\t'+str(int(tests[test].value))+\
                                         '\t'+str(int(thres))+'\t'+str(time[test].value)+'\n')
                                wr.close()

                    else:

                        print(size[test].value+' '+strategies[test].value+' die '+diffDies[d])
                        
                        print('and here')
                        filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'*Read_rep*') if os.path.isdir(mypath+f)]
                        opNb = [filesAux[t][2:3] for t in range(len(filesAux))]
                        opNb = [int(list(set(opNb))[t]) for t in range(len(set(opNb)))]
                        opNb = str(min(opNb))
                        
                        if testPlan[0] == 'set':
                            repetitions = repSet[test].value
                        elif testPlan[0] == 'reset':
                            repetitions = repReset[test].value

                        for repe in range(0,int(repetitions)+1):

                            if repe == 0:
                                operationFolder = 'Op'+opNb + '__Read'
                            else:
                                operationFolder = 'Op'+opNb + '__Read_rep'+str(repe)

                            mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
                            Rmeas, SL, WL, BL = readR(mypath,operationFolder)

                            RmeasLog = [np.log10(np.abs(float(Rmeas[i]))) for i in range(0,len(Rmeas))]
                            RmeasFloat = [np.abs(float(Rmeas[i])) for i in range(0,len(Rmeas))]
                            Working = [0]*len(RmeasFloat)
                            effAfter = []
                            workingBefore = []
                            workingCellsAfter = []
                            

                            for res in range(len(RmeasFloat)):

                                if testPlan[0] == 'set':

                                    if RmeasFloat[res] < threshold[test].value*1e3 and nonWorkingForming[res] == 0:
                                        Working[res] = 1
                                    if RmeasFloat[res] < threshold[test].value*1e3 and nonWorkingForming[res] == 0:
                                        workingBefore.append(1)

                                        
                                elif testPlan[0] == 'reset':

                                    if RmeasFloat[res] > threshold[test].value*1e3 and nonWorkingForming[res] == 0:
                                        Working[res] = 1
                                    if RmeasFloat[res] > threshold[test].value*1e3 and nonWorkingForming[res] == 0:
                                        workingBefore.append(1)


                            effAfter.append(Working.count(1)/(len(RmeasFloat)-nonWorkingForming.count(1)))
                            workingCellsAfter.append(Working.count(1))
                            if repe == 0:
                                effBefore = effAfter[0]
                                workingCellsBefore = Working.count(1)

                        totalCells = int(len(RmeasFloat)-nonWorkingForming.count(1))
                        
                        if strategies[test].value == 'V':
                            
                            if testPlan[0] == 'set':
                                Vinit = Vs[test].value
                                Vfin = Vs[test].value + repetitions*stepVs[test].value
                                thres = threshold[test].value*1e3
                            elif testPlan[0] == 'reset':
                                Vinit = Vr[test].value
                                Vfin = Vr[test].value + repetitions*stepVr[test].value
                                thres = threshold[test].value*1e3
                                
                            fileName = size[test].value+'_'+strategies[test].value+'_'+testPlan[0]
                            if os.path.isfile(path+'\\Mixed\\efficiencies\\'+fileName+'.txt') is False:
                                wr = open(path+'\\Mixed\\efficiencies\\'+fileName+'.txt','w')
                                wr.write('Before \tAfter\tTotal\tV initial\tV final\tRepetitions\tDate\tTest number\tThreshold\tTime\n')
                                wr.write(str(workingCellsBefore)+'\t'+str(workingCellsAfter[-1])+'\t'+str(totalCells)+'\t'+str(Vinit)+'\t'+\
                                         str(Vfin)+'\t'+str(repetitions)+'\t'+theDate+'\t'+str(int(tests[test].value))+\
                                         '\t'+str(int(thres))+'\t'+str(time[test].value)+'\n')
                                wr.close()
                            else:    
                                wr = open(path+'\\Mixed\\efficiencies\\'+fileName+'.txt','a')
                                wr.write(str(workingCellsBefore)+'\t'+str(workingCellsAfter[-1])+'\t'+str(totalCells)+'\t'+str(Vinit)+'\t'+\
                                         str(Vfin)+'\t'+str(repetitions)+'\t'+theDate+'\t'+str(int(tests[test].value))+\
                                         '\t'+str(int(thres))+'\t'+str(time[test].value)+'\n')
                                wr.close()
                        elif strategies[test].value == 'SR':

                            if testPlan[0] == 'set':
                                Vinit = Vs[test].value
                                Vsmart = Vr[test].value
                                thres = threshold[test].value*1e3
                            elif testPlan[0] == 'reset':
                                Vinit = Vr[test].value
                                Vsmart = Vs[test].value
                                thres = threshold[test].value*1e3
                            
                            fileName = size[test].value+'_'+strategies[test].value+'_'+testPlan[0]
                            if os.path.isfile(path+'\\Mixed\\efficiencies\\'+fileName+'.txt') is False:
                                wr = open(path+'\\Mixed\\efficiencies\\'+fileName+'.txt','w')
                                wr.write('Before \tAfter\tTotal\tV initial\tV smart\tRepetitions\tDate\tTest number\tThreshold\tTime\n')
                                wr.write(str(workingCellsBefore)+'\t'+str(workingCellsAfter[-1])+'\t'+str(totalCells)+'\t'+str(Vinit)+'\t'+\
                                         str(Vsmart)+'\t'+str(repetitions)+'\t'+theDate+'\t'+str(int(tests[test].value))+\
                                         '\t'+str(int(thres))+'\t'+str(time[test].value)+'\n')
                                wr.close()
                            else:
                                    
                                wr = open(path+'\\Mixed\\efficiencies\\'+fileName+'.txt','a')
                                wr.write(str(workingCellsBefore)+'\t'+str(workingCellsAfter[-1])+'\t'+str(totalCells)+'\t'+str(Vinit)+'\t'+\
                                         str(Vsmart)+'\t'+str(repetitions)+'\t'+theDate+'\t'+str(int(tests[test].value))\
                                         +'\t'+str(int(thres))+'\t'+str(time[test].value)+'\n')
                                wr.close()






if '__main__'==__name__:

    stop = False

    path = r'C:\\Users\\rm248200\\Documents\\Data\\D15S1058W23'
    path = r'E:\New data\D15S1058W23'
    stop = False
    while not stop:
        try:
            matSize = raw_input('Insert matrix size ("4", "64" or "1"):\n')
        except:
            matSize = input('Insert matrix size ("4", "64" or "1"):\n')

        if matSize == '4' or matSize == '64' or matSize == '1':
            stop = True
        else:
            print('\nInsert a valid size\n')

    if matSize == '4':
        matSize = '4k'
    elif matSize == '64':
        matSize = '64k'
    elif matSize == '1':
        matSize = '1M'
    
    writeFiles(path,matSize)
























