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
import madClassesAndFunctions_vtest
from matplotlib import cm
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import LogFormatterMathtext
import matplotlib.ticker as ticker


def readTestFlow(path,launchNb):

    launchStr = (3-len(str(launchNb)))*"0"+str(launchNb)
    f = open(path+'\\launch_'+launchStr+'.txt','r')

    global nowTime
    global matrixSize
    global die
    nowTime = f.readline().splitlines()[0]
    lot = f.readline().splitlines()[0]
    waferNb = f.readline().splitlines()[0]
    barrette = f.readline().splitlines()[0]
    matrixSize = f.readline().splitlines()[0]
    die = f.readline().splitlines()
    die = die[0].split('x')

    global testList
    testList = f.read().splitlines()
    workbookPath = path+'\\TestFlow_'+nowTime+'_die_'+str(die[0])+'-'+str(die[1])+'.xls'
    
    ##Open TestFlow
    workbook = xlrd.open_workbook(workbookPath)

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

def fmt(x, pos):
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

def generateBitmap(Rmeas, loc):
        R = [np.abs(float(Rmeas[i])) for i in range(0,len(Rmeas))]
        R2 = []
        if matrixSize =='1M':
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
                    cbar = plt.colorbar(orientation='vertical',format=ticker.FuncFormatter(fmt))  # colour bar
                pp.savefig()
            pp.close()
            plt.close()
        else:
            if matrixSize == '64K':
                stopWl = 256
                for i in range(int(len(R)/stopWl)):
                    R2.append(R[i*stopWl:(i*stopWl)+stopWl])
                fig,(ax) = plt.subplots()
                
                image = np.array(R2)
                plt.imshow(image, cmap=cm.jet, interpolation='nearest',aspect='auto', origin='lower')
                ## if log scale add: norm=matplotlib.colors.LogNorm(vmin=1e7, vmax=2e8))
                cbar = plt.colorbar(orientation='vertical',format=ticker.FuncFormatter(fmt))  # colour bar 
                #cbar.ax.tick_params(labelsize=8)                             # set the label size of the colour bar
                #plt.clim(4e7,2e8)                                            # set the limits of the colour bar
                plt.ylabel('Bitline', fontsize=10)
                plt.xlabel('Wordline', fontsize=10)
                plt.savefig(r'%s/Bitmap_expanded.pdf'%loc)                            #save bitmap.pdf
                plt.close()
                
                plt.imshow(image, cmap=cm.jet, interpolation='nearest',aspect='auto', origin='lower',norm=cm.colors.LogNorm())
                lvls = np.logspace(np.log10(min(R)),np.log10(max(R)),10)
                cbar = plt.colorbar(orientation='vertical',ticks=lvls,format=ticker.FuncFormatter(fmt)) 
                plt.ylabel('Bitline', fontsize=10)
                plt.xlabel('Wordline', fontsize=10)
                plt.savefig(r'%s/Bitmap_expanded_log.pdf'%loc)
                plt.close()
                stopWl = 16
                R2 = []
            else:
                stopWl = 16
                
            for i in range(int(len(R)/stopWl)):
                R2.append(R[i*stopWl:(i*stopWl)+stopWl])
            fig,(ax) = plt.subplots()           
            image = np.array(R2)
            plt.imshow(image, cmap=cm.jet, interpolation='nearest',aspect='auto', origin='lower')   ## if log scale add: norm=matplotlib.colors.LogNorm(vmin=1e7, vmax=2e8))
            cbar = plt.colorbar(orientation='vertical',format=ticker.FuncFormatter(fmt))  # colour bar 
            #cbar.ax.tick_params(labelsize=8)                             # set the label size of the colour bar
            #plt.clim(4e7,2e8)                                            # set the limits of the colour bar
            plt.ylabel('Bitline', fontsize=10)
            plt.xlabel('Wordline', fontsize=10)
            plt.savefig(r'%s/Bitmap.pdf'%loc)                            #save bitmap.pdf
            plt.close()
            
            lvls = np.logspace(np.log10(min(R)),np.log10(max(R)),10)
            plt.imshow(image, cmap=cm.jet, interpolation='nearest',aspect='auto', origin='lower',norm=cm.colors.LogNorm())
            cbar = plt.colorbar(orientation='vertical', ticks=lvls,format=ticker.FuncFormatter(fmt))
            plt.ylabel('Bitline', fontsize=10)
            plt.xlabel('Wordline', fontsize=10)
            plt.savefig(r'%s/Bitmap_log.pdf'%loc)
            plt.close()


def doCummulative(Rmeas,plan,voltage,step,repetition,planNb,twoCells,mypath,strategy,testNb):

    RmeasLog = [np.log10(np.abs(float(Rmeas[i]))) for i in range(0,len(Rmeas))]
    RmeasFloat = [np.abs(float(Rmeas[i])) for i in range(0,len(Rmeas))]
    
    if repetition == -1:
        #Then the operation is a read
        plan = 'Read'
        title = 'for Read'
        titleFig = 'Op'+str(planNb)
    elif repetition == 0:
        title = 'for '+plan +' at V = '+str(voltage)+' V'
        titleFig = 'Op'+str(planNb)
    elif repetition > 0:
        if strategy == 'SR':
            actualVoltage = voltage
            title = 'for '+plan +' at V = '+str(voltage)+\
                    ' V rep. '+str(int(repetition))
            titleFig = 'Op'+str(planNb)+'_rep'+str(repetition)
        elif strategy == 'TB':
            actualVoltage = voltage
            title = 'for '+plan +' at V = '+str(voltage)+\
                    ' V rep. '+str(int(repetition))
            titleFig = 'Op'+str(planNb)+'_rep'+str(repetition)
        else:
            actualVoltage = voltage+repetition*step
            title = 'for '+plan +' at V = '+str(voltage)+\
                    ' V rep. '+str(int(repetition))+' ('+str(actualVoltage)+' V)'
            titleFig = 'Op'+str(planNb)+'_rep'+str(repetition)
            
            
    if plan == 'Set':
        colorForPlot = 'r.'
    elif plan == 'Reset':
        colorForPlot = 'b.'
    elif plan == 'Forming':
        colorForPlot = 'g.'
    elif plan == 'Read':
        colorForPlot = 'c.'
    if twoCells:

        evenCells = [i for i in range(0,len(RmeasFloat),2)]
        oddCells = [i for i in range(1,len(RmeasFloat),2)]
    
        diff = [RmeasFloat[evenCells[i]]-RmeasFloat[oddCells[i]] for i in range(0,int(len(RmeasFloat)/2))]



        values, base = np.histogram(diff, bins=100000)
        cumulative = np.cumsum(values)
        cumulative = 100*cumulative/(max(cumulative))
        plt.plot(base[:-1], cumulative, colorForPlot)
        plt.xscale('symlog')
        plt.grid(True)
        plt.axis([-1e7, 1e7,0,100])
        plt.title('Cumulative distribution (TB) '+title)
        plt.xlabel('Resistance [Ohm]')
        plt.ylabel('Cells not working')
        fig_title = 'cumulativeTB_'+titleFig+'.png'
        plt.savefig(r'%s/%s' % (mypath,fig_title))
        plt.clf()
        
        (quantiles, values), (slope, intercept, r) = stats.probplot(diff, dist='norm')
        plt.plot(values, quantiles,colorForPlot)
        ticks_perc=[0.0001,0.001,0.01,0.1,1, 5, 10, 20, 50, 80, 90, 95, 99,99.9,99.99,99.999,99.9999]
        ticks_quan=[stats.norm.ppf(i/100.) for i in ticks_perc]
        plt.yticks(ticks_quan,ticks_perc)
        plt.grid(True)
        plt.xscale('symlog')
        plt.axis([-1e7, 1e7,-5,5])
        plt.title('Normal probability plot (TB) '+title)
        plt.xlabel('Log of resistance [log(Ohm)]')
        plt.ylabel('Probability (%)')
        fig_title = 'normalPlotTB_'+titleFig+'.png'
        plt.savefig(r'%s/%s' % (mypath,fig_title))
        plt.close()

        if withForming == True and not repetition == -1 and not plan == 'Forming':
            title = title + ' (corrected)'
            titleFig = titleFig + '_corrected'
            correctedForming = []
            evenCellsAux = []
            oddCellsAux = []
            workingMeas = getWorkingCells(twoCells,plan,Rmeas,Ronthres[testNb].value*1e3,Roffthres[testNb].value*1e3,Rformthres[testNb].value*1e3)
            for i in range(0,len(RmeasFloat),2):
                if workingForming[i] == 1:
                    if workingForming[i+1] == 1:
                        evenCellsAux.append(i)
                        oddCellsAux.append(i+1)    
            diff = [RmeasFloat[evenCellsAux[i]]-RmeasFloat[oddCellsAux[i]] for i in range(0,int(len(oddCellsAux)/2))]
            
            values, base = np.histogram(diff, bins=100000)
            cumulative = np.cumsum(values)
            cumulative = 100*cumulative/(max(cumulative))
            plt.plot(base[:-1], cumulative, colorForPlot)
            plt.xscale('symlog')
            plt.grid(True)
            plt.axis([-1e7, 1e7,0,100])
            plt.title('Cumulative distribution (TB) '+title)
            plt.xlabel('Resistance [Ohm]')
            plt.ylabel('Cells not working')
            fig_title = 'cumulativeTB_'+titleFig+'.png'
            plt.savefig(r'%s/%s' % (mypath,fig_title))
            plt.clf()
            
            (quantiles, values), (slope, intercept, r) = stats.probplot(diff, dist='norm')
            plt.plot(values, quantiles,colorForPlot)
            ticks_perc=[0.0001,0.001,0.01,0.1,1, 5, 10, 20, 50, 80, 90, 95, 99,99.9,99.99,99.999,99.9999]
            ticks_quan=[stats.norm.ppf(i/100.) for i in ticks_perc]
            plt.yticks(ticks_quan,ticks_perc)
            plt.grid(True)
            plt.xscale('symlog')
            plt.axis([-1e7, 1e7,-5,5])
            plt.title('Normal probability plot (TB) '+title)
            plt.xlabel('Log of resistance [log(Ohm)]')
            plt.ylabel('Probability (%)')
            fig_title = 'normalPlotTB_'+titleFig+'.png'
            plt.savefig(r'%s/%s' % (mypath,fig_title))
            plt.close()

        

    else:




        values, base = np.histogram(RmeasFloat, bins=100000)
        cumulative = np.cumsum(values)
        cumulative = 100*cumulative/(max(cumulative))
        plt.plot(base[:-1], cumulative, colorForPlot)
        plt.xscale('log')
        plt.axis([np.power(10,2.5), 1e8,0,100])
        plt.title('Cumulative distribution '+title)
        plt.xlabel('Resistance [Ohm]')
        plt.ylabel('Cells not working')
        plt.grid(True)
        fig_title = 'cumulative_'+titleFig+'.png'
        plt.savefig(r'%s/%s' % (mypath,fig_title))
        plt.clf()
        
        (quantiles, values), (slope, intercept, r) = stats.probplot(RmeasLog, dist='norm')
        plt.plot(values, quantiles,colorForPlot)
        ticks_perc=[0.0001,0.001,0.01,0.1,1, 5, 10, 20, 50, 80, 90, 95, 99,99.9,99.99,99.999,99.9999]
        ticks_quan=[stats.norm.ppf(i/100.) for i in ticks_perc]
        plt.yticks(ticks_quan,ticks_perc)
        plt.grid(True)
        plt.axis([2.5, 8,-5,5])
        plt.title('Normal probability plot '+title)
        plt.xlabel('Log of resistance [log(Ohm)]')
        plt.ylabel('Probability (%)')
        fig_title = 'normalPlot_'+titleFig+'.png'
        plt.savefig(r'%s/%s' % (mypath,fig_title))

##        plt.plot(quantiles * slope + intercept, quantiles, 'r')
##        fig_title = 'normalPlot_'+titleFig+'_line.png'
##        plt.savefig(r'%s/%s' % (mypath,fig_title))
        plt.close()

        if withForming == True and not repetition == -1 and not plan == 'Forming':
            title = title + ' (corrected)'
            titleFig = titleFig + '_corrected'
            correctedWorking = []
            correctedWorkingLog = []
            workingMeas = getWorkingCells(twoCells,plan,Rmeas,Ronthres[testNb].value*1e3,Roffthres[testNb].value*1e3,Rformthres[testNb].value*1e3)
            for i in range(len(RmeasFloat)):
                if workingForming[i] == 1:
                    correctedWorking.append(RmeasFloat[i])
                    correctedWorkingLog.append(RmeasLog[i])
            RmeasFloat = correctedWorking
            RmeasLog = correctedWorkingLog

            values, base = np.histogram(RmeasFloat, bins=100000)
            cumulative = np.cumsum(values)
            cumulative = 100*cumulative/(max(cumulative))
            plt.plot(base[:-1], cumulative, colorForPlot)
            plt.xscale('log')
            plt.axis([np.power(10,2.5), 1e8,0,100])
            plt.title('Cumulative distribution '+title)
            plt.xlabel('Resistance [Ohm]')
            plt.ylabel('Cells not working')
            plt.grid(True)
            fig_title = 'cumulative_'+titleFig+'.png'
            plt.savefig(r'%s/%s' % (mypath,fig_title))
            plt.clf()
            
            (quantiles, values), (slope, intercept, r) = stats.probplot(RmeasLog, dist='norm')
            plt.plot(values, quantiles,colorForPlot)
            ticks_perc=[0.0001,0.001,0.01,0.1,1, 5, 10, 20, 50, 80, 90, 95, 99,99.9,99.99,99.999,99.9999]
            ticks_quan=[stats.norm.ppf(i/100.) for i in ticks_perc]
            plt.yticks(ticks_quan,ticks_perc)
            plt.grid(True)
            plt.axis([2.5, 8,-5,5])
            plt.title('Normal probability plot '+title)
            plt.xlabel('Log of resistance [log(Ohm)]')
            plt.ylabel('Probability (%)')
            fig_title = 'normalPlot_'+titleFig+'.png'
            plt.savefig(r'%s/%s' % (mypath,fig_title))

##            plt.plot(quantiles * slope + intercept, quantiles, 'r')
##            fig_title = 'normalPlot_'+titleFig+'_line.png'
##            plt.savefig(r'%s/%s' % (mypath,fig_title))
            plt.close()


def plotHistograms(Rmeas,mypath,operationFolder,repetition,planNb,voltage,step,plan,strategy):

    if repetition == -1:
        #Then the operation is a read
        plan = 'Read'
        title = 'for Read'
    elif repetition == 0:
        title = 'for '+plan +' at V = '+str(voltage)+' V'
    elif repetition > 0:
        if strategy == 'SR':
            actualVoltage = voltage
            title = 'for '+plan +' at V = '+str(voltage)+\
                    ' V rep. '+str(int(repetition))
        elif strategy == 'TB':
            actualVoltage = voltage
            title = 'for '+plan +' at V = '+str(voltage)+\
                    ' V rep. '+str(int(repetition))+' (TB)'
        else:
            actualVoltage = voltage+repetition*step
            title = 'for '+plan +' at V = '+str(voltage)+\
                    ' V rep. '+str(int(repetition))+' ('+str(actualVoltage)+' V)'
            

    plt.clf()
    RmeasLog = [np.log10(np.abs((float(Rmeas[i])))) for i in range(0,len(Rmeas))]

    bins = np.linspace(2.5,8,600)
    plt.hist(RmeasLog, bins)
    plt.xlim(2.5,8)
    plt.yscale('log',nonposy='clip')
    plt.title('Histogram '+title)
    plt.xlabel('Log of resistance [log(Ohm)]')
    plt.ylabel('Number of cells')
    fig_title = 'histogram_'+operationFolder+'.png'
    plt.savefig(r'%s/%s' % (mypath,fig_title))
    plt.close()

        

def getWorkingCells(twoCells,plan,Rmeas,Ron,Roff,Rform):
    ##1 means working
    if twoCells == True:
        working = [0]*int(len(Rmeas)/2)    
        if plan == "Set":
            for i in range(0,len(Rmeas),2):
                if np.abs(float(Rmeas[i])) - np.abs(float(Rmeas[i+1])) < 0:
                    working[int(i/2)] = 1

        elif plan == "Reset":
            for i in range(0,len(Rmeas),2):
                if np.abs(float(Rmeas[i])) - np.abs(float(Rmeas[i+1])) > 0:
                    working[int(i/2)] = 1
    elif twoCells == False:
        working = [0]*int(len(Rmeas))
        if plan == "Set":
            for i in range(0,len(Rmeas)):
                if np.abs(float(Rmeas[i])) < Ron:
                    working[i] = 1
        elif plan == "Reset":
            for i in range(0,len(Rmeas)):
                if np.abs(float(Rmeas[i])) > Roff:
                    working[i] = 1
        elif plan == "Forming":
            for i in range(0,len(Rmeas)):
                if np.abs(float(Rmeas[i])) < Rform:
                    working[i] = 1

    return working


            
def plotRepetitions(minIndex,repNb,notWorkingVector,plan,voltage,step,planNb,threshold,mypath,strategy,notWorking):


        if strategy == 'V':
            labelx = 'Repetition voltage (V)'
            labels = [str(voltage+step*i) for i in range(minIndex,repNb+1)]
            theTitle = 'Cells not working for '+plan +' at V = '+\
                    str(voltage)+' and R = '+str(threshold)
        elif strategy == 'TB':
            labelx = 'Repetitions'
            labels = [str(i) for i in range(minIndex,repNb+1)]
            theTitle = 'Cells not working for '+plan +' at V = '+str(voltage)
        else:
            labelx = 'Repetitions'
            labels = [str(i) for i in range(minIndex,repNb+1)]
            theTitle = 'Cells not working for '+plan +' at V = '+\
                    str(voltage)+' and R = '+str(threshold)
        if minIndex == -1:
            labels[0] = 'Read'
            actualRep = len(notWorkingVector)-2
        else:
            actualRep = len(notWorkingVector)-1
    
        plt.plot(range(minIndex,actualRep+1),notWorkingVector,'ro-')
        plt.axis([minIndex-1,actualRep+2,0,max(notWorkingVector)+20])
        plt.grid(True)
        plt.title(theTitle)
        plt.xlabel(labelx)
        plt.xticks(range(minIndex,actualRep+1), labels)
        plt.ylabel('Cells not working')
        plt.ylim(0,max(notWorkingVector)*1.1)
        plt.xticks(range(minIndex,actualRep+1), labels)
        fig_title = 'notWorking_Op'+str(planNb)+'.png'
        if withForming and not plan == 'Forming':
            plt.plot(range(minIndex,actualRep+1),notWorking,'go')                         
        
        plt.savefig(r'%s/%s' % (mypath,fig_title))

        plt.ylim(1,max(notWorkingVector)*1.1)
        plt.yscale('log')
        ax = plt.gca()
        #ax.autoscale()
        fig_title = 'notWorking_plan'+str(planNb)+'_log.png'
        plt.savefig(r'%s/%s' % (mypath,fig_title))
        plt.close()



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

    for res in range(len(Rmeas)):
        if np.float(Rmeas[res]) < 0:
            Rmeas[res] = 1e9
        elif np.float(Rmeas[res]) < 0:
            Rmeas[res] = np.float(Rmeas[res])

    print(mypath2)
    return Rmeas






    
def plotter(path,launchNb):

    dic = {'set': 'Set','reset': 'Reset', 'form':'Forming', 'read':'Read'}

    global withForming
    global workingForming

    readTestFlow(path,launchNb)
    print(launchNb)
    
    print(matrixSize)

    count = 0
    for i in range(1,len(tests)):
        if isinstance(tests[i].value,float) is True:
            count += 1
        else:
            break
    nbTests = count
    withForming = False
    #range(1,nbTests+1)
    currentTest = 0
    
    for test in range(1,nbTests+1):
        print(repPlan[test])

        currentDie = dies[test].value
        currentDie = currentDie.split(';')

        print('Launch die: '+die[0]+'x'+die[1])
        print('Current die: '+str(currentDie))
        
        if (die[0] == currentDie[0] and die[1] == currentDie[1]) or (len(currentDie)<2):
            print('good')

            currentTest += 1

            testPlan = plans[test].value.split(",")
            index = len(testPlan)
            for i in range(index):
                testPlan[i] = dic.get(testPlan[i])
            
            if repPlan[test].value > 0:
                testPlan = testPlan*(int(repPlan[test].value)+1)
                index = index*(int(repPlan[test].value)+1)

            mypath = r'%s\%s\%s' % (path,'\\',testList[currentTest-1])
            print('\n\n'+testList[currentTest-1])
                    
            if strategies[test].value == 'TB':
                twoCells = True
            else:
                twoCells = False

            if testPlan[0] == 'Read' and index == 1:
                doNothing = True
                operationFolder = 'Op1__Read'
                Rmeas = readR(mypath,operationFolder)
                mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
                if os.path.isdir(mypath2) == False:
                    mypath2 = mypath+'\\'+operationFolder+'\\'
                    
                print('Generating bitmap for '+testPlan[0])
                generateBitmap(Rmeas,mypath2)
                print('Plotting cumulative distributions for '+testPlan[0])
                plotHistograms(Rmeas,mypath,operationFolder,-1,0,0,0,'','')
                print('Plotting histograms for '+testPlan[0])
                doCummulative(Rmeas,testPlan[0],0,0,-1,'Read',twoCells,mypath,strategies[test].value,test)
                
            else:
                doNothing = False

            
            for i in range(index):
                if testPlan[i] == 'Forming':
                    withForming = True

            if not doNothing:

                folders = [f for f in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, f))]

                if testPlan[0] == 'Read':
                    minIndex = -1 #minIndex -1 means that the first test is a read, not an actual operation
                    startPlan = 1
                else:
                    minIndex = 0
                    startPlan = 0

                for planNb in range(startPlan,index):

                    if planNb > 1:
                        minIndex = 0 #The read can only be at the beginning, so after plan 1 minIndex is always 0

                    if testPlan[planNb]== 'Set':
                        repNb = int(repSet[test].value)
                        threshold = Ronthres[test].value*1e3
                        voltage = Vs[test].value
                        step = stepVs[test].value
                    elif testPlan[planNb] == 'Reset':
                        repNb = int(repReset[test].value)
                        threshold = Roffthres[test].value*1e3
                        voltage = Vr[test].value
                        step = stepVr[test].value
                    elif testPlan[planNb] == 'Forming':
                        repNb = int(repForming[test].value)
                        threshold = Rformthres[test].value*1e3
                        voltage = Vs[test].value
                        step = stepVs[test].value
                        withForming = True
                    

                    notWorkingVector = [0]*int(len((range(minIndex,repNb+1))))
                    notWorking = [0]*int(len((range(minIndex,repNb+1))))
                    count = 0
                    
                    for k in range(minIndex,repNb+1):

                        if k == -1: ##If it's -1, it means that the first operation was a read
                            operation = planNb
                            operationFolder = 'Op'+str(operation)+'__Read'
                        elif k == 0:
                            operation = planNb + 1
                            operationFolder = 'Op'+str(operation)+'__Read'
                        elif k > 0:
                            operation = planNb + 1
                            operationFolder = 'Op'+str(operation)+'__Read_rep'+str(k)

                        if os.path.isdir(mypath+'\\'+operationFolder) is False:
                            notWorkingVector[count] = 0
                            notWorkingForming = 0
                            break
                            #If all the cells were switched, the number of folders will not be the same as the
                            #theoretical number of repetitions. This break avoids problems

                        mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
                        if os.path.isdir(mypath2) == False:
                            mypath2 = mypath+'\\'+operationFolder+'\\'
                        Rmeas = readR(mypath,operationFolder)
                                
                        working = getWorkingCells(twoCells,testPlan[planNb],Rmeas,\
                                                    Ronthres[test].value*1e3,Roffthres[test].value*1e3,Rformthres[test].value*1e3)
                        
                        notWorkingVector[count] = working.count(0)
                        cc=0
                        ccc=0
                        cc2=0
                        ccc2=0


                        if withForming == True and not k == -1 and not testPlan[planNb] == 'Forming':
                            notWorking[count] = 0

                            if twoCells:
                                for i in range(0,len(workingForming),2):

                                    if workingForming[i] == 1 and workingForming[i+1] == 1:
                                        cc2+=1
                                        if working[int(i/2)] == 0:
                                            ccc2+=1
                                            notWorking[count]+=1
                                       

                            else:
                                for i in range(0,len(workingForming)):
                                    if workingForming[i] == 1 and working[i] == 0:
                                        notWorking[count] += 1
                        elif withForming == True and k == -1 and not testPlan[planNb] == 'Forming':
                            notWorking[count] = 0
                                 
                        
                        count+=1
    ##                    
    ##                    print('Plotting cumulative distributions for '+testPlan[planNb]+' ('+strategies[test].value+\
    ##                            ') rep. '+str(k))
    ##                    doCummulative(Rmeas,testPlan[planNb],voltage,step,k,operation,twoCells,mypath,strategies[test].value,test)
    ##                    
    ##                    print('Plotting histograms for '+testPlan[planNb]+' ('+strategies[test].value+\
    ##                            ') rep. '+str(k))
    ##                    #plotHistograms(Rmeas,mypath,operationFolder,k,operation,voltage,step,testPlan[planNb],strategies[test].value)
    ##
    ##                    print('Generating bitmap for '+testPlan[planNb]+' ('+strategies[test].value+\
    ##                            ') rep. '+str(k))
    ##                    #generateBitmap(Rmeas,mypath2)

                        print('Plotting cumulative distributions for '+testPlan[planNb]+' ('+strategies[test].value+\
                              ') rep. '+str(k))
                        try:
                            doCummulative(Rmeas,testPlan[planNb],voltage,step,k,operation,twoCells,mypath,strategies[test].value,test)
                        except:
                            plt.close('all')
                            print('There was an error in the Cumulative plot')
                        
                        print('Plotting histograms for '+testPlan[planNb]+' ('+strategies[test].value+\
                              ') rep. '+str(k))
                        try:
                            plotHistograms(Rmeas,mypath,operationFolder,k,operation,voltage,step,testPlan[planNb],strategies[test].value)
                        except:
                            plt.close('all')
                            print('There was an error in the histogram')

                        print('Generating bitmap for '+testPlan[planNb]+' ('+strategies[test].value+\
                              ') rep. '+str(k))
                        try:
                            generateBitmap(Rmeas,mypath2)
                        except:
                            plt.close('all')
                            print('There was an error in the Bitmap')

                    if testPlan[planNb] == 'Forming':
                        workingForming = working

                    if not repNb == 0: #If repNb is 0 it doesn't make sense to do the repetition plots
                        print('Plotting repetitions for '+testPlan[planNb]+' ('+strategies[test].value+')')

                        try:
                            plotRepetitions(minIndex,repNb,notWorkingVector,testPlan[planNb],voltage,\
                                        step,operation,threshold,mypath,strategies[test].value,notWorking)
                        except:
                            plt.close("all")
                            print('There was an error in the repetitions plot')

    plt.close('all')
    
if '__main__'==__name__:

    path = r'C:\Users\rm248200\Documents\Data\D15S1058W23\64kbit\20-05-2016'
    launchNb = 1
    stop = False

    while not stop:
        try:
            path = raw_input('Please enter the directory where the test files are: ')
        except:
            path = input('Please enter the directory where the test files are: ')

        if os.path.isdir(path) is False:
            print('\nThe directory does not exist.')
        else:
            stop = True

    stop = False
    
    while not stop:
        try:
            launchNb = raw_input('Please enter the launch number: ')
        except:
            launchNb = input('Please enter the launch number: ')

        
        try:
            assert int(launchNb)
            launchStr = (3-len(str(launchNb)))*"0"+str(launchNb)
            if os.path.isfile(path+'\\launch_'+launchStr+'.txt'):
                stop = True
            else:
                print('\nThe launch number does not exist')
        except ValueError:
            print('\nThe number is not valid')

    for launchNb in range(1,33):
        plotter(path,launchNb)

