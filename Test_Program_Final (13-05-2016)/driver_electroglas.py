
import visa
import time 
import os
import linecache
from final_oxram_prog_v4_8 import test_die

def manual_load():
    ################ Ouvrir liste des dies #############################################
    dies = open('DUT.txt', 'r')
    #compter le nombre de lignes
    linecount = len(open('DUT.txt', 'rU').readlines())
    ########################### Ouverture de connection avec le prober ################### 
    rm=visa.ResourceManager()
    electroglas=rm.open_resource("GPIB::2")
    ################################### Effacement du buffer #############################
    #electroglas.clear()
    #################### Profile wafer (mesure de l'epaisseur du wafer) ##################
    
    while electroglas.query("?C")[0:1]!=u'C':
        electroglas.query("?C")
    electroglas.query("?C")
    electroglas.query("?C")
    print electroglas.query("?C")
    electroglas.write("PC")
    print "profile wafer progress....."
    
    ########################## Electroglas.query("$?WFPF")
    
    ################### Print electroglas.query("$?WFPF")
    
    time.sleep(80)
    
    ################# while electroglas.query("$?WFPF")[0:5]!=u'WFPFT':
    while electroglas.query("$?WFPF")[0:1]!=u'W':
            electroglas.query("$?WFPF")
    electroglas.query("$?WFPF")
    electroglas.query("$?WFPF")
    electroglas.query("$?WFPF")
    #time.sleep(80) 
        
    print electroglas.query("$?WFPF")
    
    ############################### Auto alignment du wafer ############################## 
    electroglas.write("AA")
    print"alignement progres....."
    time.sleep(70)
    
    ############################ Positionement sur la puce de reference###################
    
    ################################## attente du positionement ##########################
    while electroglas.query("?P")!=u'X1Y1\r\n':
        electroglas.query("?P")
    electroglas.query("?P")
    electroglas.query("?P")
##    
##        
##    ################################# Confirmation du positionement ######################
    print electroglas.query("?P")

    barrette=str(linecache.getline('DUT.txt', 1))
    barrette=barrette[0:5]
    #chaine = "D-A26" Texte a rechercher
    fichier = open("barrette.txt","r")
    for ligne in fichier:
        if barrette in ligne:
            print ligne
            a=ligne.split(",")
            subx=a[1]
            suby=a[2]
            print subx
            print suby
            subsite="FM"+" "+subx+" "+suby
            electroglas.write(subsite)             
            while electroglas.query("?H")[0:1]!=u'H':
                electroglas.query("?H")
            print electroglas.query("?H")
    fichier.close()
    electroglas.write("SP19 0")
    ########### recuperation des coordonnees X et Y de chaque die + boucle ##############
    for i in range (2,linecount+1) :
        die=linecache.getline('DUT.txt', i)
        x = str(int(die[0:2]))
        y = str(int(die[3:]))
        
        toto="MO"+" "+x+" "+y+";SP1000"
        electroglas.write(toto)
    
        adresse="X"+x+"Y"+y+"\r\n"
        while electroglas.query("?P")!=adresse:
            electroglas.query("?P")       
        
        print electroglas.query("?P")
        
        mon_fichier_info = open("Informations.txt", "r")
        lotname=linecache.getline('Informations.txt', 2)
        lotname=lotname.replace("lot name=","")
        lotname=lotname.replace("\n","")

        size_of_memory=linecache.getline('Informations.txt', 1)
        size_of_memory=size_of_memory.replace("size of memory=","")
        size_of_memory=size_of_memory.replace("\n","")
        if size_of_memory=='4kbit NNN' or size_of_memory=='4kbit KTT' or size_of_memory=='4kbit PRKN':
            size_of_memory='4K'
        if size_of_memory=='256bit' or size_of_memory=='256bit Kelvin':
            size_of_memory='256'
        if size_of_memory=='64kbit panache':
            size_of_memory='64K'
        if size_of_memory=='1Mbit simple' or size_of_memory=='VRAM':
            size_of_memory='64K'
        #['256bit','256bit Kelvin','4kbit NNN','4kbit KTT','4kbit PRKN','64kbit panache','1Mbit simple','VRAM']
        # {'256': 0, '4K':1, '64K':2, '1M':3} 
        wafernumber=linecache.getline('Informations.txt', 3)
        wafernumber=wafernumber.replace('wafer name = ',"")
        wafernumber=wafernumber.replace("\n","")

        mon_fichier_info.close()
        test_die( lotname , wafernumber , x , y , size_of_memory ,1 )

        
        while electroglas.query("?D")!=u'DT'+str(i-1)+'ID:default\r\n':
            electroglas.query("?D")
        electroglas.query("?D")
        electroglas.query("?D")
        print electroglas.query("?D")
        while electroglas.query("?C")[0:1]!=u'C':
          electroglas.query("?C")
        electroglas.query("?C")
        print electroglas.query("?C")
##            
##        electroglas.write("ZD")
##        while electroglas.query("?Z")[0:3]!=down:
##            electroglas.query("?Z")
    
##        print electroglas.query("?Z")
    
    print ("prepare unload wafer.....")
    while electroglas.query("?C")[0:1]!=u'C':
          electroglas.query("?C")
    print electroglas.query("?C")
    while electroglas.query("?P")[0:1]!=u'X':
          electroglas.query("?P")
    print electroglas.query("?P")
    while electroglas.query("?C")[0:1]!=u'C':
          electroglas.query("?C")
    while electroglas.query("?P")[0:1]!=u'X':
          electroglas.query("?P")
    print electroglas.query("?P")
##    electroglas.query("?C")
##    for i in range (linecount+50):
##          electroglas.query("?C")
##    electroglas.query("?C")
##    electroglas.query("?C")
##    print electroglas.query("?C")
    electroglas.write("UL")
    print "unload wafer....."
    time.sleep(50)
    while electroglas.query("?C")[0:1]!=u'C':
           electroglas.query("?C")
    electroglas.query("?C")
    electroglas.query("?C")
    electroglas.query("?C")
    print electroglas.query("?C")
    print "it is finish....."
    print "load a new wafer wait ready an profile and align....."
    
    dies.close()
    electroglas.close()

def load_from_cassette():
    #r=200
    align=0
    
    wafers = open('Wafer.txt', 'r')
    #compter le nombre de lignes
    wafercount = len(open('Wafer.txt', 'rU').readlines())
    wafers.close()
    dies = open('DUT.txt', 'r')
    #compter le nombre de lignes
    linecount = len(open('DUT.txt', 'rU').readlines())
    dies.close()
    ########################### Ouverture de connection avec le prober ################### 
    rm=visa.ResourceManager()
    electroglas=rm.open_resource("GPIB::2")
    ################################### Effacement du buffer #############################
    electroglas.clear()
    ################################### Etat de la cassette1 #############################
    electroglas.write("SM70 1")
    while electroglas.query("?SM70")!=u'SM70C1\r\n':
        electroglas.query("?SM70")
    electroglas.query("?SM70")
    electroglas.query("?SM70")
    print electroglas.query("?SM70")
    ##################################### charger wafer##################################
    for w in range (1,wafercount+1) :   
        wafers = open('Wafer.txt', 'r')
        waf=linecache.getline('wafer.txt', w)
        print (waf)
        electroglas.write("LO")
        print "wafer load..."
        time.sleep(70)
        if w==wafercount:
            Cquerystart=u'CP0L0S0R0W'+str(int(waf))+'\r\n'
        elif w==wafercount-1:
            Cquerystart=u'CP0L1S0R0W'+str(int(waf))+'\r\n'
        else:
            Cquerystart=u'CP0L1S1R1W'+str(int(waf))+'\r\n'
        while electroglas.query("?C")!=Cquerystart :
          electroglas.query("?C")
        electroglas.query("?C")
        electroglas.query("?C")
        print electroglas.query("?C")
        while electroglas.query("?W0")!=u''+str(int(waf))+'\r\n':
            electroglas.query("?W0")
        electroglas.query("?W0")
        electroglas.query("?W0")
        print electroglas.query("?W0")
        ###########################profile wafer mesure d epaisseur ##########################
        electroglas.write("PC")
        print "profile wafer progress....."
        
        ########################## Electroglas.query("$?WFPF")
        
        ################### Print electroglas.query("$?WFPF")
        
        time.sleep(80)
        
        ################# while electroglas.query("$?WFPF")[0:5]!=u'WFPFT':
        while electroglas.query("$?WFPF")[0:1]!=u'W':
                electroglas.query("$?WFPF")
        electroglas.query("$?WFPF")
        electroglas.query("$?WFPF")
        electroglas.query("$?WFPF")
        #time.sleep(80) 
            
        print electroglas.query("$?WFPF")
        
        ############################### Auto alignment du wafer ############################## 
        electroglas.write("AA")
        print"alignement progres....."
        time.sleep(70)
        
        ############################ Positionement sur la puce de reference###################
        
        ################################## attente du positionement ##########################
        while electroglas.query("?P")!=u'X1Y1\r\n':
            electroglas.query("?P")
        electroglas.query("?P")
        electroglas.query("?P")
    ##    
    ##        
    ##    ################################# Confirmation du positionement ######################
        print electroglas.query("?P")
    
        barrette=str(linecache.getline('DUT.txt', 1))
        barrette=barrette[0:5]
        #chaine = "D-A26" Texte a rechercher
        fichier = open("barrette.txt","r")
        for ligne in fichier:
            if barrette in ligne:
                print ligne
                a=ligne.split(",")
                subx=a[1]
                suby=a[2]
                print subx
                print suby
                subsite="FM"+" "+subx+" "+suby
                electroglas.write(subsite)             
                while electroglas.query("?H")[0:1]!=u'H':
                    electroglas.query("?H")
                print electroglas.query("?H")
        fichier.close()
        electroglas.write("SP19 0")
        ########### recuperation des coordonnees X et Y de chaque die + boucle ##############
        for i in range (2,linecount+1) :
            die=linecache.getline('DUT.txt', i)
            x = str(int(die[0:2]))
            y = str(int(die[3:]))
            
            toto="MO"+" "+x+" "+y+";SP1000"
            electroglas.write(toto)
        
            adresse="X"+x+"Y"+y+"\r\n"
            while electroglas.query("?P")!=adresse:
                electroglas.query("?P")       
            
            print electroglas.query("?P")
            
            mon_fichier_info = open("Informations.txt", "r")
            lotname=linecache.getline('Informations.txt', 2)
            lotname=lotname.replace("lot name=","")
            lotname=lotname.replace("\n","")
    
            size_of_memory=linecache.getline('Informations.txt', 1)
            size_of_memory=size_of_memory.replace("size of memory=","")
            size_of_memory=size_of_memory.replace("\n","")
            if size_of_memory=='4kbit NNN' or size_of_memory=='4kbit KTT' or size_of_memory=='4kbit PRKN':
                size_of_memory='4K'
            if size_of_memory=='256bit' or size_of_memory=='256bit Kelvin':
                size_of_memory='256'
            if size_of_memory=='64kbit panache':
                size_of_memory='64K'
            if size_of_memory=='1Mbit simple' or size_of_memory=='VRAM':
                size_of_memory='64K'
            #['256bit','256bit Kelvin','4kbit NNN','4kbit KTT','4kbit PRKN','64kbit panache','1Mbit simple','VRAM']
            # {'256': 0, '4K':1, '64K':2, '1M':3} 
            wafernumber=str(int(waf))
            
            
    
            mon_fichier_info.close()
            test_die( lotname , wafernumber , x , y , size_of_memory ,1 )
    
            
            while electroglas.query("?D")!=u'DT'+str(i-1)+'ID:default\r\n':
                electroglas.query("?D")
            electroglas.query("?D")
            electroglas.query("?D")
            print electroglas.query("?D")
            while electroglas.query("?C")[0:1]!=u'C':
              electroglas.query("?C")
            electroglas.query("?C")
            print electroglas.query("?C")
    ##            
    ##        electroglas.write("ZD")
    ##        while electroglas.query("?Z")[0:3]!=down:
    ##            electroglas.query("?Z")
        
    ##        print electroglas.query("?Z")
        
        print ("prepare unload wafer.....")
        while electroglas.query("?C")[0:1]!=u'C':
              electroglas.query("?C")
        print electroglas.query("?C")
        while electroglas.query("?P")[0:1]!=u'X':
              electroglas.query("?P")
        print electroglas.query("?P")
        while electroglas.query("?C")[0:1]!=u'C':
              electroglas.query("?C")
        while electroglas.query("?P")[0:1]!=u'X':
              electroglas.query("?P")
        print electroglas.query("?P")
    ##    electroglas.query("?C")
    ##    for i in range (linecount+50):
    ##          electroglas.query("?C")
    ##    electroglas.query("?C")
    ##    electroglas.query("?C")
    ##    print electroglas.query("?C")
        electroglas.write("UL")
        print "unload wafer....."
        time.sleep(50)
        while electroglas.query("?C")[0:1]!=u'C':
               electroglas.query("?C")
        electroglas.query("?C")
        electroglas.query("?C")
        electroglas.query("?C")
        print electroglas.query("?C")
        print "it is finish....."
        print "load a new wafer wait ready an profile and align....."
        if w==wafercount:
            Cquerystop=u'CP0L0S0R0W\r\n'
        elif w==wafercount-1:
            Cquerystop=u'CP0L1S0R0W\r\n'
        else:
            Cquerystop=u'CP0L1S1R1W\r\n'
        while electroglas.query("?C")!=Cquerystop :
          electroglas.query("?C")
        print electroglas.query("?C")
        status="SM69 1 "+str(int(waf))+" 2"
        print "status="+status
        electroglas.write(status)
        while electroglas.query("?SM70")!=u'SM70C1\r\n':
            electroglas.query("?SM70")
        print electroglas.query("?SM70")

    ###################### decharger le chuck ################################
    
    #electroglas.write("UL")
    #print "unload wafer....."
    #time.sleep(50)
    print "it is finish....."
    wafers.close()
    dies.close()
