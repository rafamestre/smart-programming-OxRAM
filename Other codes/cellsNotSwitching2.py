# -*- coding: cp1252 -*-
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

    print('here')
    workbookPath = path+'\\notSwitching.xls'
    
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
    compare = testflow.col(15)
    compare = compare[1].value


    return tests, strategies, plan, die, Vs, Vr, stepVs, stepVr, repSet, repReset, date, size, threshold,time, repPlan, compare




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
    
def plotter(path,sheet):


    sizeDic = {'4k':4096,'64k':65536,'1M':1048576}
    
    [tests, strategies, plan, die, Vs, Vr, stepVs, stepVr, repSet, repReset, date, size, threshold, time, repPlan, compare] = readTestFlow(path,sheet)
        
    count = 0

    colorList = ['b','r','g','c','m','y','k']
    
    for i in range(1,len(tests)):
        if isinstance(tests[i].value,float) is True:
            count += 1
        else:
            break
    nbTests = count

    dies = [0]*(nbTests)
    doTest = [0]*(nbTests)
    
    auxCount = 0

    for test in range(1,nbTests+1):

        dies[test-1] = die[test].value

        if plan[test].value == 'form':

            doTest[test-1] = 0

        else:

            doTest[test-1] = 1

    for test in range(1,nbTests+1):
        if strategies[1].value != strategies[test].value and not doTest[test-1]:
            raise NameError('Strategies should be the same')
    if compare == 'Th' or compare == 'th':
        compareList = [threshold[t].value for t in range(1,nbTests+1) if doTest[test-1]]
        compareList = list(set(compareList))
    elif compare == 't':
        compareList = [time[t].value for t in range(1,nbTests+1) if doTest[test-1]]
        compareList = list(set(compareList))
    elif compare == 'vs' or compare == 'Vs':
        testPlan = plan[nbTests].value.split(",")
        if strategies[nbTests].value == 'SR' and testPlan[0] == 'set':
            compareList = [Vr[t].value for t in range(1,nbTests+1) if doTest[test-1]]
        elif strategies[nbTests].value == 'SR' and testPlan[0] == 'reset':
            compareList = [Vs[t].value for t in range(1,nbTests+1) if doTest[test-1]]
        else:
            compareList = [Vr[t].value for t in range(1,nbTests+1) if doTest[test-1]]
        compareList = list(set(compareList))
    elif compare == 'vr' or compare == 'Vr':
        compareList = [Vr[t].value for t in range(1,nbTests+1) if doTest[test-1]]
        compareList = list(set(compareList))
    print(compareList)
    legendFlag = [0]*len(compareList)

    diffDies = list(set(dies))
        
    for d in range(len(diffDies)):

        dieTests = [i+1 for i, j in enumerate(dies) if dies[i] == diffDies[d]]
        
        formed = False
        
        for test in dieTests:
            
            theDate = getDay(date[test].value)
            testPlan = plan[test].value.split(",")
            
            if testPlan[0] == 'form':

                formed = True
                
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

                    repePlan = repPlan[test].value
                    flagSet = False
                    flagReset = False
                    
                    if testPlan[0] == 'set':
                        setFolder = 1
                        resetFolder = 0
                    elif testPlan[0] == 'reset':
                        setFolder = 0
                        resetFolder = 1

                    for planRep in range(1,2*(int(repePlan)+1)):
                    
                        filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'Op'+str(planRep)+'__Read*') if os.path.isdir(mypath+f)]

                        nbWorking = []
                        xAxis = []

                        for repe in range(len(filesAux)):

                            
                            operationFolder = filesAux[repe]
                            mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
                            if not os.path.exists(mypath2):
                                print('All repetitions achieved in one plan')
                                break
                            else:
                                Rmeas, SL, WL, BL = readR(mypath,operationFolder)
                            print(mypath2)

                            xAxis.append(repe)
                            RmeasLog = [np.log10(np.abs(float(Rmeas[i]))) for i in range(0,len(Rmeas))]
                            RmeasFloat = [np.abs(float(Rmeas[i])) for i in range(0,len(Rmeas))]
                            Working = [0]*int(len(RmeasFloat)/2)
                            nonWorkingFormingTB = [0]*int(len(RmeasFloat)/2)

                            for res in range(0,len(RmeasFloat),2):

                                if nonWorkingForming[res] == 1 or nonWorkingForming[res+1] == 1:
                                    nonWorkingFormingTB[int(res/2)] = 1

                                if planRep%2 == setFolder: 

                                    if RmeasFloat[res] - RmeasFloat[res+1] < 0 and nonWorkingFormingTB[int(res/2)] == 0:
                                        Working[int(res/2)] = 1
                                        
                                elif planRep%2 == resetFolder:
                                    if RmeasFloat[res] - RmeasFloat[res+1] > 0 and nonWorkingFormingTB[int(res/2)] == 0:
                                        Working[int(res/2)] = 1

                            print(nonWorkingForming.count(1))
                            print(nonWorkingFormingTB.count(1))
                            print(Working.count(1))
                            nbWorking.append(Working.count(1)/(int(len(RmeasFloat)/2)-nonWorkingFormingTB.count(1)))
                        

                        if compare == 't':
                            if planRep%2 == setFolder:
                                plotMark = '*-'
                                legendLabel = 'Set: '+str(time[test].value)+' micro s'
                                flagSet = True
                            elif planRep%2 == resetFolder:
                                plotMark = '.--'
                                legendLabel = 'Reset: '+str(time[test].value)+' micro s'
                                flagReset  = True
                            plotColor = colorList[compareList.index(time[test].value)]
                            plotTitle = 'Efficiency for different programming times (TB)'
                            if legendFlag[compareList.index(time[test].value)]==0 and (flagSet or flagReset):
                                plt.plot([],plotColor+plotMark,label=legendLabel)
                                if flagSet and flagReset:
                                    legendFlag[compareList.index(time[test].value)]=1
                        elif compare == 'th':
                            if planRep%2 == setFolder:
                                plotMark = '*-'
                                legendLabel = 'Set: '+str(threshold[test].value)+' Ohm'
                                flagSet = True
                            elif planRep%2 == resetFolder:
                                plotMark = '.--'
                                legendLabel = 'Reset: '+str(threshold[test].value)+' Ohm'
                                flagReset  = True
                            plotColor = colorList[compareList.index(threshold[test].value)]
                            plotTitle = 'Efficiency for different programming times (TB, Vs = '+str(Vs[test].value)+', Vr = '+str(Vr[test].value)+')'
                            if legendFlag[compareList.index(threshold[test].value)]==0 and (flagSet or flagReset):
                                plt.plot([],plotColor+plotMark,label=legendLabel)
                                if flagSet and flagReset:
                                    legendFlag[compareList.index(threshold[test].value)]=1
                        elif compare == 'vr':
                            if planRep%2 == setFolder:
                                plotMark = '*-'
                                legendLabel = 'Set: '+str(Vs[test].value)+' V'
                                flagSet = True
                            elif planRep%2 == resetFolder:
                                plotMark = '.--'
                                legendLabel = 'Reset: '+str(Vr[test].value)+' V'
                                flagReset  = True
                            plotColor = colorList[compareList.index(Vr[test].value)]
                            plotTitle = 'Efficiency for different Vreset (TB, t = '+str(time[test].value)+')'
                            if legendFlag[compareList.index(Vr[test].value)]==0 and (flagSet or flagReset):
                                plt.plot([],plotColor+plotMark,label=legendLabel)
                                if flagSet and flagReset:
                                    legendFlag[compareList.index(Vr[test].value)]=1                                    
                            
                        
                        plt.plot(xAxis,nbWorking,plotColor+plotMark,label='_nolegend_')
                        count += 1
                        plt.annotate(str(count),xy=(xAxis[0],nbWorking[0]),textcoords="offset points",xytext=(-40,-15))
                        plt.title(plotTitle)
                        plt.xlabel('Repetitions (TB)')
                        plt.ylabel('Percentage of switched cells (%)')
                        plt.grid(True)
                        plt.legend(loc='lower right')
                        plt.xlim([-0.5,repe+0.5])
                        plt.yscale('log')
                        print(nbWorking)

                        
                else:
                    print('and here')
                    filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'*Read_rep*') if os.path.isdir(mypath+f)]
                    if len(filesAux) == 0:
                        filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'*Read') if os.path.isdir(mypath+f)]
                    else:                        
                        opNb = [filesAux[t][2:3] for t in range(len(filesAux))]
                        opNb = [int(list(set(opNb))[t]) for t in range(len(set(opNb)))]
                        opNb = str(min(opNb))

                    nbWorking = []
                    xAxis = []
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
                        if not os.path.exists(mypath2):
                            print('All repetitions achieved in one plan')
                            break
                        else:
                            Rmeas, SL, WL, BL = readR(mypath,operationFolder)

                        if strategies[test].value == 'V' and testPlan[0]=='set':
                            xAxis.append(Vs[test].value+stepVs[test].value*repe)
                        elif strategies[test].value == 'V' and testPlan[0]=='reset':
                            xAxis.append(Vr[test].value+stepVr[test].value*repe)
                        elif strategies[test].value == 'SR':
                            xAxis.append(repe)
                            
                        RmeasLog = [np.log10(np.abs(float(Rmeas[i]))) for i in range(0,len(Rmeas))]
                        RmeasFloat = [np.abs(float(Rmeas[i])) for i in range(0,len(Rmeas))]
                        Working = [0]*len(RmeasFloat)

                        for res in range(len(RmeasFloat)):

                            if testPlan[0] == 'set':

                                if sheet == 43:
                                    threshold[test].value = 12
                                elif sheet == 444:
                                    threshold[test].value = 15
                                if RmeasFloat[res] < threshold[test].value*1e3 and nonWorkingForming[res] == 0:

                                    Working[res] = 1

                                    
                            elif testPlan[0] == 'reset':

                                if RmeasFloat[res] > threshold[test].value*1e3 and nonWorkingForming[res] == 0:
                                    
                                    Working[res] = 1


                        nbWorking.append(Working.count(1)/(len(RmeasFloat)-nonWorkingForming.count(1)))
                    if compare == 'Th' or compare == 'th':
                        plotColor = colorList[compareList.index(threshold[test].value)]
                        plotTitle = 'Efficiency for different thresholds (t = '+str(time[test].value)+')'
                        legendLabel = str(int(threshold[test].value))+' Ohm'
                        if legendFlag[compareList.index(threshold[test].value)]==0:
                            plt.plot([],plotColor,label=legendLabel)
                            legendFlag[compareList.index(threshold[test].value)]=1
                    elif compare == 't':
                        plotColor = colorList[compareList.index(time[test].value)]
                        plotTitle = 'Efficiency for different programming times (th = '+str(threshold[test].value)+')'
                        legendLabel = str(time[test].value)+' micro s'
                        if legendFlag[compareList.index(time[test].value)]==0:
                            print(legendLabel)
                            plt.plot([],plotColor,label=legendLabel)
                            legendFlag[compareList.index(time[test].value)]=1
                        if strategies[test].value == 'SR':
                            if testPlan[0] == 'set':
                                plotTitle +=  ' (th = '+str(threshold[test].value)+', Vsmart = '+str(Vr[test].value)+\
                                ' V, Vs = '+str(Vs[test].value)+' V)'
                            elif testPlan[0] == 'reset':
                                plotTitle +=  ' (th = '+str(threshold[test].value)+', Vsmart = '+str(Vs[test].value)+\
                                ' V, Vr = '+str(Vr[test].value)+' V)'                                                                                                                               
                    elif compare == 'vs' or compare == 'Vs':
                        plotTitle = 'Efficiency for different V (t = '+str(time[test].value)+', th = '+str(threshold[test].value)+')'
                        if testPlan[0] == 'reset':
                            plotColor = colorList[compareList.index(Vs[test].value)]
                            legendLabel = str(Vs[test].value)+' V'
                            if legendFlag[compareList.index(Vs[test].value)]==0:
                                plt.plot([],plotColor,label=legendLabel)
                                legendFlag[compareList.index(Vs[test].value)]=1
                        elif testPlan[0] == 'set':
                            plotColor = colorList[compareList.index(Vr[test].value)]
                            legendLabel = str(Vr[test].value)+' V'
                            if legendFlag[compareList.index(Vr[test].value)]==0:
                                plt.plot([],plotColor,label=legendLabel)
                                legendFlag[compareList.index(Vr[test].value)]=1
                    elif compare == 'vr' or compare == 'Vr':
                        plotTitle = 'Efficiency for different Vreset (t = '+str(time[test].value)+', th = '+str(threshold[test].value)+')'
                        plotColor = colorList[compareList.index(Vr[test].value)]
                        legendLabel = str(Vr[test].value)+' V'
                        if legendFlag[compareList.index(Vr[test].value)]==0:
                            plt.plot([],plotColor,label=legendLabel)
                            legendFlag[compareList.index(Vr[test].value)]=1
                            
                    if strategies[test].value == 'V':
                        if testPlan[0] == 'set':
                            xLabel = 'Set voltage (V)'
                        elif testPlan[0] == 'reset':
                            xLabel = 'Reset voltage (V)'
                    elif strategies[test].value == 'SR':
                        xLabel = 'Repetitions (SR)'
                    plt.plot(xAxis,nbWorking,plotColor+'.-',label='_nolegend_')
                    plt.title(plotTitle)
                    plt.xlabel(xLabel)
                    plt.ylabel('Percentage of switched cells (%)')
                    plt.grid(True)

                    plt.legend(loc='lower right')

    if sheet == 7:
        plt.xlim([0,5])

    fig_title = 'sheet'+str(sheet)
    plt.savefig(r'%s/%s' % (path+'\\Mixed\\NotSwitched\\',fig_title+'.pdf'))

    sheets = [40,31,39,41,20]

    if sheet in sheets:
        ax = plt.gca()
        ax.legend_.remove()
        #plt.yscale('log')
        
        if sheet == 41 or sheet == 20:
            plt.ylim([0.95,1])
            ax.set_yticks([0.95,0.96,0.97,0.98,0.99,0.999])
            ax.set_yticklabels(['0.95','0.96','0.97','0.98','0.99','0.999'])
        elif sheet == 39:
            plt.ylim([0.95,1])
            plt.xlim([1.4,2.5])
            ax.set_yticks([0.95,0.96,0.97,0.98,0.99,0.999])
            ax.set_yticklabels(['0.95','0.96','0.97','0.98','0.99','0.999'])
        else:
            plt.ylim([0.99,1.0001])
            ax.set_yticks([0.99,0.995,0.999,0.9999,1])
            ax.set_yticklabels(['0.99','0.995','0.999','0.9999','1'])
        
        

        
        
        fig_title = 'sheet'+str(sheet)+'_inset'
        plt.savefig(r'%s/%s' % (path+'\\Mixed\\NotSwitched\\',fig_title+'.pdf'))
    
    plt.close()
            




if '__main__'==__name__:

    stop = False

    path = r'C:\\Users\\rm248200\\Documents\\Data\\D15S1058W23'
    #path = r'E:\New data\D15S1058W23'

    stop = False
    while not stop:
        try:
            sheet = raw_input('Insert test sheet number:')
        except:
            sheet = input('Insert test sheet number:')

        try: 
            sheet = int(sheet)
            stop = True
        except:
            print('\nInsert a number please')

    plotter(path,sheet)









