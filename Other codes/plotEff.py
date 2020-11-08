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

def all():

    path = 'C:\\Users\\rm248200\\Documents\\Data\\D15S1058W23\\Mixed\\efficiencies\\'

    colors = {'SR':'b','V':'r','TB':'g'}
    markers = {'4k':'o','64k':'s','1M':'D'}

    for op in ['set','reset']:

        for mat in ['4k','64k','1M']:

            for strategy in ['SR','V','TB']:
                
                fileName = mat+'_'+strategy+'_'+op+'.txt'

##                if mat == '64k' and strategy == 'TB' and op == 'reset':
##                    break

                if os.path.isfile(path+fileName):

                    
                    
                    txt = open(path+fileName)

                    g=[]

                    for line in txt:
                        g.append(line)

                    allData = []

                    for i in range(1,len(g)):
                        allData.append(g[i].split('\t'))

                    dataX = [float(allData[k][0]) for k in range(len(allData))]
                    dataY = [float(allData[k][1]) for k in range(len(allData))]
                    total = [float(allData[k][2]) for k in range(len(allData))]
                    V1 = [float(allData[k][3]) for k in range(len(allData))]
                    V2 = [float(allData[k][4]) for k in range(len(allData))]
                    repe = [float(allData[k][5]) for k in range(len(allData))]
                    time = [float(allData[k][9]) for k in range(len(allData))]

                    effx = [dataX[k]/total[k] for k in range(len(dataX))]
                    effy = [dataY[k]/total[k] for k in range(len(dataY))]

                    eliminate = []
                    for k in range(len(dataX)):
                        if strategy == 'TB' and ((V1[k] < 1.5 and time[k]<0.3) or V2[k] < 1):
                            eliminate.append(k)
                        elif strategy == 'V' and repe[k] <5:
                            eliminate.append(k)
##                        if strategy == 'TB' and (effx[k] < 0.4 or effx[k]>effy[k]):
##                            plt.annotate(
##                                str(str(int(V1[k])))+', '+str(int(V2[k]))+', '+str(time[k]),
##                                size = 8,
##                                xy = (effx[k],effy[k]), xytext = (-20, 20),
##                                textcoords = 'offset points', ha = 'right', va = 'bottom',
##                                arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
                    if len(eliminate) > 0:
                        effxaux = [v for i, v in enumerate(effx) if i not in eliminate]
                        effyaux = [v for i, v in enumerate(effy) if i not in eliminate]
                        effx = effxaux
                        effy = effyaux

                    f = plt.figure(1)
                    plt.plot(effx,effy,colors.get(strategy)+markers.get('4k'),label=strategy)

##                    f2 = plt.figure(2)
##                    relative = [dataY[i]/dataX[i] for i in range(len(dataX))]
##                    plt.plot(dataX,relative,colors.get(strategy)+markers.get(mat),label=strategy+' '+mat)

                    print(min(dataX))
                    txt.close()

        f = plt.figure(1)
        plt.title('Strategy comparison for '+op)
        plt.xlabel('Initial efficiency')
        plt.ylabel('Percentage of switched cells (%)')
        plt.grid()
        plt.legend(loc='lower right')
        plt.plot([0,1],[0,1],'r-.',label='_nolegend_')
        axes = plt.gca()
        axes.set_xlim([0,1])
        axes.set_ylim([0,1])
        fig_title = op+'_comp'
        plt.savefig(path+fig_title+'.png')
        #plt.savefig(path+fig_title+'.pdf')

        
        axes.set_ylim([0.97,1])
        axes.set_xlim([0.75,1])
        plt.legend(loc='lower left')
        fig_title = op+'_comp_zoom'
        plt.savefig(path+fig_title+'.png')

        axes.set_ylim([0.98,1])
        axes.set_xlim([0.98,1])
        plt.legend(loc='lower left')
        fig_title = op+'_comp_zoom2'
        plt.savefig(path+fig_title+'.png')
        
        plt.close()

        f = plt.figure(2)
        plt.title('Strategy comparison for '+op)
        plt.xlabel('Initial efficiency')
        plt.ylabel('Relative efficiency')
        #plt.yscale('log')
        plt.grid()
        plt.legend(loc='upper right')
        fig_title = op+'_relative'
        #plt.savefig(path+fig_title+'.png')
        plt.close()




def some():

    
    path = 'C:\\Users\\rm248200\\Documents\\Data\\D15S1058W23\\Mixed\\efficiencies\\'

    colors = {'SR':'b','V':'r','TB':'g'}
    markers = {'4k':'o','64k':'s','1M':'D'}

    figTh = []
    figVinit = []
    figVfin = []

    thres = []
    Vinit = []
    Vfin = []


    for op in ['set','reset']:

        figTh = []
        figVinit = []
        figVfin = []
        figVsmart = []

        thres = []
        Vinit = []
        Vfin = []
        Vsmart = []


        for mat in ['4k','64k','1M']:

            for strategy in ['SR','V','TB']:
                
                fileName = mat+'_'+strategy+'_'+op+'.txt'

                if os.path.isfile(path+fileName):
                    
                    txt = open(path+fileName)

                    g=[]

                    for line in txt:
                        g.append(line)

                    allData = []

                    for i in range(1,len(g)):
                        allData.append(g[i].split('\t'))

                    dataX = [float(allData[k][0]) for k in range(len(allData))]
                    dataY = [float(allData[k][1]) for k in range(len(allData))]
                    total = [float(allData[k][2]) for k in range(len(allData))]

                    effx = [dataX[k]/total[k] for k in range(len(dataX))]
                    effy = [dataY[k]/total[k] for k in range(len(dataY))]

                    thresholds = [float(allData[k][8]) for k in range(len(allData))]
                    Vinits = [float(allData[k][3]) for k in range(len(allData))]
                    Vfins = [float(allData[k][4]) for k in range(len(allData))]

                    for point in range(0,len(g)-1):

                        if not thresholds[point] in thres:

                            thres.append(thresholds[point])
                            figTh.append(len(figTh))
                            
                            f = plt.figure(figTh[-1])
                            plt.plot(effx[point],effy[point],colors.get(strategy)+markers.get(mat))

                        elif thresholds[point] in thres:

                            f = plt.figure(figTh[thres.index(thresholds[point])])
                            plt.plot(effx[point],effy[point],colors.get(strategy)+markers.get(mat))

                        if not Vinits[point] in Vinit:

                            Vinit.append(Vinits[point])
                            figVinit.append(len(figVinit))

                            f = plt.figure(100+figVinit[-1])
                            plt.plot(effx[point],effy[point],colors.get(strategy)+markers.get(mat))

                        elif Vinits[point] in Vinit:

                            f = plt.figure(100+figVinit[Vinit.index(Vinits[point])])
                            plt.plot(effx[point],effy[point],colors.get(strategy)+markers.get(mat))

                        if strategy == 'V' or strategy == 'TB':
                            if not Vfins[point] in Vfin:

                                Vfin.append(Vfins[point])
                                figVfin.append(len(figVfin))

                                f = plt.figure(10000+figVfin[-1])
                                plt.plot(effx[point],effy[point],colors.get(strategy)+markers.get(mat))

                            elif Vfins[point] in Vfin:

                                f = plt.figure(10000+figVfin[Vfin.index(Vfins[point])])
                                plt.plot(effx[point],effy[point],colors.get(strategy)+markers.get(mat))
                        elif strategy == 'SR':
                            if not Vfins[point] in Vsmart:

                                Vsmart.append(Vfins[point])
                                figVsmart.append(len(figVsmart))

                                f = plt.figure(20000+figVsmart[-1])
                                plt.plot(effx[point],effy[point],colors.get(strategy)+markers.get(mat))

                            elif Vfins[point] in Vsmart:

                                f = plt.figure(20000+figVsmart[Vsmart.index(Vfins[point])])
                                plt.plot(effx[point],effy[point],colors.get(strategy)+markers.get(mat))


                    txt.close()

        print(figTh)
        print(figVinit)
        print(figVfin)
        for i in ['threshold','Vinit','Vfin','Vsmart']:

            if i == 'threshold':
                for j in range(len(thres)):
                    
                    f = plt.figure(figTh[thres.index(thres[j])])
                    for mat in ['4k','64k','1M']:
                        for strategy in ['SR','V','TB']:
                            plt.plot([],[],colors.get(strategy)+markers.get(mat),label=strategy+' '+mat)
                    plt.title('Strategy comparison for '+op+' and R threshold = '+str(int(thres[j])))
                    plt.xlabel('Initial efficiency')
                    plt.ylabel('Percentage of switched cells (%)')
                    plt.grid()
                    plt.legend(loc='lower right')
                    plt.plot([0,1.05],[0,1.05],'r-.',label='_nolegend_')
                    axes = plt.gca()
                    axes.set_xlim([0,1.05])
                    axes.set_ylim([0,1.05])
                    fig_title = op+'_thres_'+str(int(thres[j]))
                    plt.savefig(path+fig_title+'.png')
                    plt.close()

            if i == 'Vinit':
                for j in range(len(Vinit)):
                    
                    f = plt.figure(100+figVinit[Vinit.index(Vinit[j])])
                    for mat in ['4k','64k','1M']:
                        for strategy in ['SR','V','TB']:
                            plt.plot([],[],colors.get(strategy)+markers.get(mat),label=strategy+' '+mat)
                    strategy
                    plt.title('Strategy comparison for '+op+' and initial V = '+('%.1f' % Vinit[j])+' V')
                    plt.xlabel('Initial efficiency')
                    plt.ylabel('Percentage of switched cells (%)')
                    plt.grid()
                    plt.legend(loc='lower right')
                    plt.plot([0,1.05],[0,1.05],'r-.',label='_nolegend_')
                    axes = plt.gca()
                    axes.set_xlim([0,1.05])
                    axes.set_ylim([0,1.05])
                    fig_title = op+'_Vinit_'+('%.1f' % Vinit[j])
                    plt.savefig(path+fig_title+'.png')
                    plt.close()

            if i == 'Vfin':
                for j in range(len(Vfin)):
                    
                    f = plt.figure(10000+figVfin[Vfin.index(Vfin[j])])
                    for mat in ['4k','64k','1M']:
                        for strategy in ['V']:
                            plt.plot([],[],colors.get(strategy)+markers.get(mat),label=strategy+' '+mat)
                    plt.title('Strategy comparison for '+op+' and final V = '+('%.1f' % Vfin[j])+' V')
                    plt.xlabel('Initial efficiency')
                    plt.ylabel('Percentage of switched cells (%)')
                    plt.grid()
                    plt.legend(loc='lower right')
                    plt.plot([0,1.05],[0,1.05],'r-.',label='_nolegend_')
                    axes = plt.gca()
                    axes.set_xlim([0,1.05])
                    axes.set_ylim([0,1.05])
                    fig_title = op+'_Vfin_'+('%.1f' % Vfin[j])
                    plt.savefig(path+fig_title+'.png')
                    plt.close()

            if i == 'Vsmart':
                for j in range(len(Vsmart)):
                    
                    f = plt.figure(20000+figVsmart[Vsmart.index(Vsmart[j])])
                    for mat in ['4k','64k','1M']:
                        for strategy in ['SR']:
                            plt.plot([],[],colors.get(strategy)+markers.get(mat),label=strategy+' '+mat)
                    plt.title('Strategy comparison for '+op+' (SR) and smart V = '+('%.1f' % Vsmart[j])+' V')
                    plt.xlabel('Initial efficiency')
                    plt.ylabel('Percentage of switched cells (%)')
                    plt.grid()
                    plt.legend(loc='lower right')
                    plt.plot([0,1.05],[0,1.05],'r-.',label='_nolegend_')
                    axes = plt.gca()
                    axes.set_xlim([0,1.05])
                    axes.set_ylim([0,1.05])
                    fig_title = op+'_Vsmart_'+('%.1f' % Vfin[j])
                    plt.savefig(path+fig_title+'.png')
                    plt.close()


def some2():


    path = 'C:\\Users\\rm248200\\Documents\\Data\\D15S1058W23\\Mixed\\efficiencies\\'

    colors = {'SR':'b','V':'r','TB':'g','set':'r','reset':'b'}
    markers = {'4k':'o','64k':'s','1M':'D'}

    strPlot = 'TB'
    thresPlot = 40000
    ViniPlot = 2
    VfinPlot = 2



    
    for op in ['set','reset']:
        
        fig_title = ['']*1000
        x = [[]for j in range(10)]
        y = [[]for j in range(10)]
        lab = [[]for j in range(10)]
        texts = [[]for j in range(10)]

        for mat in ['4k','64k','1M']:

            for strategy in ['SR','V','TB']:
                
                fileName = mat+'_'+strategy+'_'+op+'.txt'

                if os.path.isfile(path+fileName):
                    
                    txt = open(path+fileName)

                    g=[]

                    for line in txt:
                        g.append(line)

                    allData = []

                    for i in range(1,len(g)):
                        allData.append(g[i].split('\t'))

                    dataX = [float(allData[k][0]) for k in range(len(allData))]
                    dataY = [float(allData[k][1]) for k in range(len(allData))]
                    total = [float(allData[k][2]) for k in range(len(allData))]

                    effx = [dataX[k]/total[k] for k in range(len(dataX))]
                    effy = [dataY[k]/total[k] for k in range(len(dataY))]

                    thresholds = [float(allData[k][8]) for k in range(len(allData))]
                    Vinits = [float(allData[k][3]) for k in range(len(allData))]
                    Vfins = [float(allData[k][4]) for k in range(len(allData))]
                    times = [float(allData[k][9]) for k in range(len(allData))]
                    opNb = [float(allData[k][10]) for k in range(len(allData))]

                    for k in range(len(effx)):
                        if strategy == 'TB' and Vinits[k] == 2.2 and Vfins[k]==2.5:

                            if (op == 'set' and times[k] == 0.5) or op == 'reset':
                                f = plt.figure(0)
                                plt.plot(effx[k],effy[k],colors.get(op)+markers.get(mat))
                                plt.title('TB '+op+' for Vs = 2.2 and Vr = 2.5 (opNb, time)')
                                fig_title[0] = 'TB_Vs_2.2_Vr_2.5_'+op
                                plt.annotate(
                                        str(int(opNb[k]))+', '+str(times[k]),
                                        size = 8,
                                        xy = (effx[k],effy[k]), xytext = (-20, 20),
                                        textcoords = 'offset points', ha = 'right', va = 'bottom',
                                        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
                                if op == 'set':
                                    plt.xlim([0.997,1])
                            
                            

                        if strategy == 'TB' and Vinits[k] == 2 and Vfins[k]==2.5 and mat!='4k':


                            f = plt.figure(1)
                            plt.plot(effx[k],effy[k],colors.get(op)+markers.get(mat))
                            plt.title('TB '+op+' for Vs = 2 and Vr = 2.5 (opNb, time)')
                            fig_title[1] = 'TB_Vs_2_Vr_2.5_'+op
                            ax = plt.gca()
                            an = ax.annotate(
                                    str(int(opNb[k]))+', '+str(times[k]),
                                    size = 8,
                                    xy = (effx[k],effy[k]), xytext = (-20, 20),
                                    textcoords = 'offset points', ha = 'right', va = 'bottom',
                                    arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

                        if strategy == 'TB' and Vinits[k] == 2 and times[k]==1:

                            f = plt.figure(2)
                            plt.plot(effx[k],effy[k],colors.get(op)+markers.get(mat))
                            plt.title('TB '+op+' for Vs = 2 and t = 1 (opNb, time)')
                            fig_title[2] = 'TB_Vs_2_t_1_'+op
                            plt.annotate(
                                    str(int(opNb[k]))+', '+str(Vfins[k]),
                                    size = 8,
                                    xy = (effx[k],effy[k]), xytext = (-20, 20),
                                    textcoords = 'offset points', ha = 'right', va = 'bottom',
                                    arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))


                        if strategy == 'SR' and Vinits[k]==1.5:


                            f = plt.figure(3)
                            plt.plot(effx[k],effy[k],colors.get(op)+markers.get(mat))
                            plt.title('SR '+op+' for Vs = 1.5 (Vsmart, time)')
                            fig_title[3] = 'SR_Vs_1.5_'+op
                            plt.annotate(
                                    str(Vfins[k])+', '+str(times[k])+', '+str(opNb[k]),
                                    size = 8,
                                    xy = (effx[k],effy[k]), xytext = (-20, 20),
                                    textcoords = 'offset points', ha = 'right', va = 'bottom',
                                    arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
                        if strategy == 'SR' and times[k] == 1:

                            f = plt.figure(4)
                            plt.plot(effx[k],effy[k],colors.get(op)+markers.get(mat))
                            plt.title('SR '+op+' for Vs = 1 and t = 1 (Vsmart)')
                            fig_title[4] = 'SR_t_1_'+op
                            plt.annotate(
                                    str(Vfins[k])+', '+str(Vfins[k])+', '+str(opNb[k]),
                                    size = 8,
                                    xy = (effx[k],effy[k]), xytext = (-20, 20),
                                    textcoords = 'offset points', ha = 'right', va = 'bottom',
                                    arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

                        if strategy == 'V' and Vinits[k] == 2 and op == 'set':

                            f = plt.figure(5)
                            plt.plot(effx[k],effy[k],colors.get(op)+markers.get(mat))
                            plt.title('V '+op+' for Vs = 2(ratio, time)')
                            fig_title[5] = 'V_Vs_2_'+op
                            plt.annotate(
                                    str(Vfins[k]/Vinits[k])+', '+str(times[k]),
                                    size = 8,
                                    xy = (effx[k],effy[k]), xytext = (-20, 20),
                                    textcoords = 'offset points', ha = 'right', va = 'bottom',
                                    arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
                        if strategy == 'V' and Vinits[k] == 2.5 and op == 'set':

                            f = plt.figure(6)
                            plt.plot(effx[k],effy[k],colors.get(op)+markers.get(mat))
                            plt.title('V '+op+' for Vs = 2.5(ratio, time)')
                            fig_title[6] = 'V_Vs_2.5_'+op
                            plt.annotate(
                                    str(Vfins[k]/Vinits[k])+', '+str(times[k]),
                                    size = 8,
                                    xy = (effx[k],effy[k]), xytext = (-20, 20),
                                    textcoords = 'offset points', ha = 'right', va = 'bottom',
                                    arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

                        if strategy == 'V' and Vinits[k] == 1 and op == 'set':
                            f = plt.figure(7)
                            plt.plot(effx[k],effy[k],colors.get(op)+markers.get(mat))
                            plt.title('V '+op+' for Vs = 1(ratio, time)')
                            fig_title[7] = 'V_Vs_1_'+op
                            plt.annotate(
                                    str(Vfins[k]/Vinits[k])+', '+str(times[k]),
                                    size = 8,
                                    xy = (effx[k],effy[k]), xytext = (-20, 20),
                                    textcoords = 'offset points', ha = 'right', va = 'bottom',
                                    arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

                        



        for k in range(0,8):
            plt.figure(k)
            #adjust_text(texts[k],x[k],y[k], arrowprops=dict(arrowstyle="-", color='r', lw=0.5), expand_points=(1.2, 1.4))
            
            plt.savefig(path+fig_title[k]+'.png')

            if k == 0:
                plt.savefig(path+fig_title[k]+'.pdf')
                
            plt.close()


if '__main__'==__name__:

    all()





















