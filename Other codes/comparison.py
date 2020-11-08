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
import matplotlib.backends.backend_pdf



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
    workbookPath = path+'\\comparison.xls'
    
    ##Open TestFlow
    workbook = xlrd.open_workbook(workbookPath)

    #Extract the information of the test plan
    testflow = workbook.sheet_by_name('Feuil'+str(sheet))

        
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


    return tests, strategies, plan, die, Vs, stepVs, repSet, date, size, threshold




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

    return Rmeas




def plotter(path,sheet):
    
    f1 = plt.figure()
    f2 = plt.figure()

    dic = {'4k':4096,'64k':65536}

    Rforming = 100000


    [tests, strategies, plan, die, Vs, stepVs, repSet, date, size, threshold] = readTestFlow(path,sheet)
        
    count = 0
    print(tests)
    
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
                Rmeas = readR(mypath,operationFolder)

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
            print(testPlan)

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
                    
                if testPlan[0] == 'set':
                    colorForPlot = 'r'
                elif testPlan[0] == 'reset':
                    colorForPlot = 'b'
                
                filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'*__Read*') if os.path.isdir(mypath+f)]

                operationFolderAfter = filesAux[-1]
                operationFolderBefore = 'Op1__Read'

                print(operationFolderAfter)
                print(operationFolderBefore)

                RmeasBefore = readR(mypath,operationFolderBefore)
                RmeasAfter = readR(mypath,operationFolderAfter)

                mypath2 = mypath+'\\'+operationFolder+'\\x0_y0\\'
                
                RmeasFloatBefore = [np.abs(float(RmeasBefore[i])) for i in range(0,len(RmeasBefore))]
                RmeasFloatAfter = [np.abs(float(RmeasAfter[i])) for i in range(0,len(RmeasAfter))]

                RBefore = []
                RAfter = []

                for res in range(len(RmeasFloatBefore)):

                    if nonWorkingForming[res] == 0:

                        RBefore.append(RmeasFloatBefore[res])
                        RAfter.append(RmeasFloatAfter[res])

                print(len(RBefore))
                print(len(RAfter))
                (quantiles, values), (slope, intercept, r) = stats.probplot(RBefore, dist='norm')
                plt.plot(values, quantiles,colorForPlot+'-')
                (quantiles, values), (slope, intercept, r) = stats.probplot(RAfter, dist='norm')
                plt.plot(values, quantiles,colorForPlot+'-.')
                #plt.legend(loc='lower right')
                ticks_perc=[0.0001,0.001,0.01,0.1,1, 5, 10, 20, 50, 80, 90, 95, 99,99.9,99.99,99.999,99.9999]
                ticks_quan=[stats.norm.ppf(i/100.) for i in ticks_perc]
                plt.yticks(ticks_quan,ticks_perc)
                plt.grid(True)
                plt.axis([1e2, 1e7,-5,5])
                ax = plt.gca()
                ax.set_xscale('log')
                #plt.title('Forming voltage distribution')
                plt.xlabel('Resistance (Ohm)')
                plt.ylabel('Probability (%)')

                
                fig_title = 'improvement_'+strategies[test].value+'_'+testPlan[0]
                plt.savefig(r'%s/%s' % (path+'\\Mixed\\improvement\\',fig_title+'.pdf'))
                plt.clf()



if '__main__'==__name__:

    
    path = r'C:\\Users\\rm248200\\Documents\\Data\\D15S1058W23\\'
    path = r'C:\\Users\\Rafa\\Desktop\\Data\\D15S1058W23'
    sheet = 1

    plotter(path,sheet)








    
