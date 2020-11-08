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
    workbookPath = path+'\\bitmaps.xls'
    
    ##Open TestFlow
    workbook = xlrd.open_workbook(workbookPath)

    #Extract the information of the test plan
    sheetName = 'Feuil'+str(sheet)
    testflow = workbook.sheet_by_name(sheetName)
    global compare

    print(sheetName)
        
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
    order = testflow.col(15)
    previous = testflow.col(16)


    return tests, strategies, plan, die, Vs, Vr, stepVs, stepVr, repSet, repReset, date, size, threshold,time, repPlan, order, previous



def fmt(x, pos):
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)

def generateBitmap(Rmeas, loc, op):
        R = [np.abs(float(Rmeas[i])) for i in range(0,len(Rmeas))]
        R2 = []
        Raux = []
        
        if op == 'TB':
            stopWl = 8
            for i in range(int(len(R)/2)):
                if R[2*i] - R[2*i+1] > 0:
                    Raux.append(1)
                else:
                    Raux.append(0)
            for i in range(int(len(Raux)/stopWl)):
                R2.append(Raux[i*stopWl:(i*stopWl)+stopWl]+[100,100,100,100,100,100,100,100])
            fig,(ax) = plt.subplots()
            image = np.array(R2)
            cmap = plt.get_cmap('rainbow')

            cmap.set_bad('black')
            image = np.ma.masked_equal(image, 0)
            cmap.set_under('green')
            cmap.set_over('white')
            plt.imshow(image, cmap=cmap, interpolation='nearest',aspect='auto', origin='lower', vmin=2, vmax = 10)
            plt.ylabel('Bitline', fontsize=10)
            plt.xlabel('Wordline', fontsize=10)
            plt.title(str(Raux.count(1)) +' switched cells')
            fig_title = 'Bitmap_'+op+'.pdf'
            plt.savefig(r'%s/%s' %(loc,fig_title))
            plt.close()
            stopWl = 16
            R2 = []
        else:
            stopWl = 16
            for i in range(int(len(R))):
                if op == 'set':
                    if R[i] < 10000:
                        Raux.append(1)
                    else:
                        Raux.append(0)
                elif op == 'reset':
                    if R[i] > 30000:
                        Raux.append(1)
                    else:
                        Raux.append(0)
                        
            for i in range(int(len(Raux)/stopWl)):
                R2.append(Raux[i*stopWl:(i*stopWl)+stopWl])
            fig,(ax) = plt.subplots()           
            image = np.array(R2)
            cmap = plt.get_cmap('rainbow')
            cmap.set_bad('black')
            image = np.ma.masked_equal(image, 0)
            cmap.set_under('green')

            plt.imshow(image, cmap=cmap, interpolation='nearest',aspect='auto', origin='lower', vmin=2, vmax = 10)
            plt.title(str(Raux.count(1)) +' switched cells')
            plt.ylabel('Bitline', fontsize=10)
            plt.xlabel('Wordline', fontsize=10)
            fig_title = 'Bitmap_'+op+'.pdf'
            plt.savefig(r'%s/%s' %(loc,fig_title))
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



def bitmaps(path):


    
    [tests, strategies, plan, die, Vs, Vr, stepVs, stepVr, repSet, repReset, date, size, threshold, time, repPlan,order,previous] = readTestFlow(path,2)

    count = 0
    for i in range(1,len(tests)):
        if isinstance(tests[i].value,float) is True:
            count += 1
        else:
            break
    nbTests = count
    
    for test in range(1,nbTests+1):

        if strategies[test].value == 'TB':

            theDate = getDay(date[test].value)
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

            operationFolder = 'Op1__Read'

            
            Rmeas = readR(mypath,operationFolder)
            mypath2 = path+'\\Mixed\\bitmaps'
            generateBitmap(Rmeas,mypath2,'TB')

        
        elif strategies[test].value == 'c':

            testPlan = plan[test].value.split(",")
            theDate = getDay(date[test].value)
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

            operationFolder = 'Op1__Read'
            
            Rmeas = readR(mypath,operationFolder)
            mypath2 = path+'\\Mixed\\bitmaps'
            generateBitmap(Rmeas,mypath2,testPlan[0])

            operationFolder = 'Op2__Read'
            
            Rmeas = readR(mypath,operationFolder)
            mypath2 = path+'\\Mixed\\bitmaps'
            generateBitmap(Rmeas,mypath2,testPlan[1])

            








if '__main__'==__name__:


    path = r'C:\\Users\\rm248200\\Documents\\Data\\D15S1058W23'

    bitmaps(path)
