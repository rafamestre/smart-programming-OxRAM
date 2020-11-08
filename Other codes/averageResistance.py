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
from adjustText import adjust_text



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
    workbookPath = path+'\\average.xls'
    
    ##Open TestFlow
    workbook = xlrd.open_workbook(workbookPath)

    #Extract the information of the test plan
    sheetName = 'Feuil'+str(sheet)
    testflow = workbook.sheet_by_name(sheetName)
        
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
    operation = testflow.col(15)



    return tests, strategies, plan, die, Vs, Vr, stepVs, stepVr, repSet, repReset, date, size, threshold,time, repPlan, operation




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



def main():

    path = r'C:\\Users\\rm248200\\Documents\\Data\\D15S1058W23\\'
    fileName = 'average.xls'
    sheet = 1
        
    [tests, strategies, plan, die, Vs, Vr, stepVs, stepVr, repSet, repReset, date, size, threshold, time, repPlan, operation] = readTestFlow(path,sheet)
        
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

    Ron = 10000
    Roff = 40000

    
    for test in range(1,nbTests+1):

        dies[test-1] = die[test].value

        if plan[test].value == 'form':

            doTest[test-1] = 0

        else:

            doTest[test-1] = 1

    
    diffDies = list(set(dies))

    print(diffDies)

    
    for d in range(len(diffDies)):

        dieTests = [i+1 for i, j in enumerate(dies) if dies[i] == diffDies[d]]
        
        formed = False

        print(diffDies)
        
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

            print(tests[test].value)
            print(diffDies[d])

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

                filesAux = [f for f in fnmatch.filter(os.listdir(mypath),'*Read') if os.path.isdir(mypath+f)]

                if testPlan[0] == 'set':

                    setFiles = [i for i in range(1,int(repPlan[test].value*2)+1) if i%2 == 1]
                    resetFiles = [i for i in range(1,int(repPlan[test].value*2)+1) if i%2 == 0]
                    operationSet = [operation[test].value + i - 1 for i in range(1,int(repPlan[test].value*2)+1) if i%2 == 1]
                    operationReset = [operation[test].value + i - 1 for i in range(1,int(repPlan[test].value*2)+1) if i%2 == 0]

                else:

                    resetFiles = [i for i in range(1,int(repPlan[test].value*2)+1) if i%2 == 1]
                    setFiles = [i for i in range(1,int(repPlan[test].value*2)+1) if i%2 == 0]
                    operationSet = [operation[test].value + i - 1 for i in range(1,int(repPlan[test].value*2)+1) if i%2 == 0]
                    operationReset = [operation[test].value + i - 1 for i in range(1,int(repPlan[test].value*2)+1) if i%2 == 1]

                
                nbWorkingSet = []
                nbWorkingReset = []
                nbWorkingSet2 = []
                nbWorkingReset2 = []


                for k in range(len(setFiles)):

                    operationFolderSet = 'Op'+str(setFiles[k])+'__Read'
                    operationFolderReset = 'Op'+str(resetFiles[k])+'__Read'
                    
                    mypath2Set = mypath+'\\'+operationFolderSet+'\\x0_y0\\'
                    RmeasSet = readR(mypath,operationFolderSet)

                    mypath2Reset = mypath+'\\'+operationFolderReset+'\\x0_y0\\'
                    RmeasReset = readR(mypath,operationFolderReset)

                    RmeasFloatSet = [np.abs(float(RmeasSet[i])) for i in range(0,len(RmeasSet))]
                    RmeasFloatReset = [np.abs(float(RmeasReset[i])) for i in range(0,len(RmeasReset))]

                    workingSet = [0]*len(RmeasFloatSet)
                    workingReset = [0]*len(RmeasFloatReset)

                    workingSet2 = [0]*int(len(RmeasFloatSet)/2)
                    workingReset2 = [0]*int(len(RmeasFloatReset)/2)
                    workingForming2 = []
                    

                    for res in range(0,len(RmeasFloatSet),2):


                        if RmeasFloatSet[res] < Ron and nonWorkingForming[res] == 0:

                            workingSet[res] = 1

                        if RmeasFloatSet[res+1] < Ron and nonWorkingForming[res+1] == 0:

                            workingSet[res+1] = 1

                        if RmeasFloatReset[res] > Roff and nonWorkingForming[res] == 0:

                            workingReset[res] = 1

                        if RmeasFloatReset[res+1] > Roff and nonWorkingForming[res+1] == 0:

                            workingReset[res+1] = 1

                        if nonWorkingForming[res] == 0 and nonWorkingForming[res+1] == 0:
        
                            if stats.gmean([RmeasFloatSet[res],RmeasFloatSet[res+1]]) < Ron:

                                workingSet2[int(res/2)] = 1

                            if stats.gmean([RmeasFloatReset[res],RmeasFloatReset[res+1]]) > Roff:

                                workingReset2[int(res/2)] = 1
                        else:
                            workingForming2.append(1)


                    nbWorkingSet.append(workingSet.count(1)/(len(RmeasFloatSet)-nonWorkingForming.count(1)))
                    nbWorkingReset.append(workingReset.count(1)/(len(RmeasFloatSet)-nonWorkingForming.count(1)))
                    nbWorkingSet2.append(workingSet2.count(1)/(int(len(RmeasFloatSet)/2)-workingForming2.count(1)))
                    nbWorkingReset2.append(workingReset2.count(1)/(int(len(RmeasFloatReset)/2)-workingForming2.count(1)))

                    plt.plot(nbWorkingSet[k],nbWorkingSet2[k],'rs')
                    plt.plot(nbWorkingReset[k],nbWorkingReset2[k],'bs')

                    plt.annotate(
                        str(operationSet[k]),
                        size = 8,
                        xy = (nbWorkingSet[k],nbWorkingSet2[k]), xytext = (20, -20),
                        textcoords = 'offset points', ha = 'right', va = 'bottom',
                        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
                    plt.annotate(
                        str(operationReset[k]),
                        size = 8,
                        xy = (nbWorkingReset[k],nbWorkingReset2[k]), xytext = (20, -20),
                        textcoords = 'offset points', ha = 'right', va = 'bottom',
                        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
                
                plt.title('Vs = '+str(Vs[test].value)+ ' V, Vr = '+str(Vr[test].value)+' V, t = '+str(time[test].value)+' micro s')
                plt.xlabel('Initial efficiency')
                plt.ylabel('Percentage of switched cells (%)')
                plt.grid(True)
                plt.plot([0,1],[0,1],'r-.',label='_nolegend_')
                minValue = min([nbWorkingSet,nbWorkingReset,nbWorkingSet2,nbWorkingReset2])
                print(minValue)
                minValue = min(minValue)
                print(minValue)
                axes = plt.gca()
                
                axes.set_xlim([minValue-0.05,1])
                axes.set_ylim([minValue-0.05,1])
                fig_title = 'die_'+str(die1)+'-'+str(die2)+'_test'+str(int(tests[test].value))
                plt.savefig(r'%s/%s' % (path+'\\Mixed\\average\\',fig_title+'.png'))
    
                plt.close()





if '__main__'==__name__:

    main()


    
    
