import visa
import time 
import linecache
import os
import wx
import numpy as np
import sys
from driver_electroglas import load_from_cassette
from driver_electroglas import manual_load

import driver_electroglas

sizeMemory='256bit\n'
lotName=' \n'

class RedirectText(object):
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        self.out.WriteText(string)


class MyFrameName(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self,parent,id,'Electroglas',size=(730,1000))
        wx.StaticText(self, -1, 'lot name', (10, 15))
        wx.StaticText(self, -1, 'size of memory', (10, 40))
        
        filemenu= wx.Menu()

        menuAbout = filemenu.Append(wx.ID_ABOUT,  "&About"," Information about this program")
        menuSave = filemenu.Append(wx.ID_SAVE,    "&Save"," Save this file") 
        menuExit = filemenu.Append(wx.ID_EXIT,    "E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")    # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)            # Adding the MenuBar to the Frame content.
        # Set events.  
        self.memoryList = ['256bit','256bit Kelvin','4kbit NNN','4kbit KTT','4kbit PRKN','64kbit panache','1Mbit simple','VRAM']
        self.sizeMemory = wx.ComboBox(self,wx.ID_ANY, pos=(110, 40), size=(120, -1), choices=self.memoryList, style=wx.CB_DROPDOWN)
        self.lotName = wx.TextCtrl(self, -1, '', (110, 10), (120, -1))
        
        self.button1=wx.Button (self,wx.ID_ANY,label="PRODUCTION ",pos=(50,80),size=(200,30))
        self.button2=wx.Button (self,wx.ID_ANY,label="MANUAL LOAD",pos=(250,80),size=(200,30))
        self.button3=wx.Button (self,wx.ID_ANY,label="DEBUGGER ",pos=(450,80),size=(200,30)) 

        self.Bind(wx.EVT_BUTTON, self.onglet1,self.button1)
        self.Bind(wx.EVT_BUTTON, self.onglet2,self.button2)
        self.Bind(wx.EVT_BUTTON, self.onglet3,self.button3)            
                
        self.panel =wx.Panel (self,wx.ID_ANY,size =self.GetClientSize ())
        self.noteBook =wx.Notebook (self.panel,wx.ID_ANY,pos=(05,120), size=(700,600))
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnSave, menuSave)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        wx.StaticText(self, -1, 'Console', (300, 720))
        log = wx.TextCtrl(self.panel, wx.ID_ANY,pos=(05,740), size=(700,200),
                          style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        redir=RedirectText(log)
        sys.stdout=redir
        #sys.stderr = redir        
        self.Show(True)   

    def onglet1(self,event):
            mon_fichier_info = open("Informations.txt", "w") 
            global sizeMemory
            sizeMemory = self.sizeMemory.GetValue()
            print ("size of memory=" + self.sizeMemory.GetValue())
            global lotName
            print ("lot name=" + str(self.lotName.GetValue()))
            lotName = str(self.lotName.GetValue())
            mon_fichier_info.write("size of memory=" + self.sizeMemory.GetValue())
            mon_fichier_info.write("\n")
            mon_fichier_info.write("lot name=" + self.lotName.GetValue())
            mon_fichier_info.write("\n")
            mon_fichier_info.close()
            page1 = pageOne (self.noteBook)
            self.noteBook.DeleteAllPages()
            self.noteBook.AddPage (page1,"Production")          
            
    def onglet2(self,event):
            mon_fichier_info = open("Informations.txt", "w") 
            global sizeMemory
            sizeMemory = self.sizeMemory.GetValue()
            print ("size of memory=" + self.sizeMemory.GetValue())
            global lotName
            print ("lot name=" + str(self.lotName.GetValue()))
            lotName = str(self.lotName.GetValue())
            mon_fichier_info.write("size of memory=" + self.sizeMemory.GetValue())
            mon_fichier_info.write("\n")
            mon_fichier_info.write("lot name=" + self.lotName.GetValue())
            mon_fichier_info.write("\n")
            mon_fichier_info.close()
            page2 = pageTwo (self.noteBook)
            self.noteBook.DeleteAllPages()
            self.noteBook.AddPage (page2,"Manual load")

    def onglet3(self,event):
            mon_fichier_info = open("Informations.txt", "w") 
            global sizeMemory
            sizeMemory = self.sizeMemory.GetValue()
            print ("size of memory=" + self.sizeMemory.GetValue())
            global lotName
            print ("lot name=" + str(self.lotName.GetValue()))
            lotName = str(self.lotName.GetValue())
            mon_fichier_info.write("size of memory=" + self.sizeMemory.GetValue())
            mon_fichier_info.write("\n")
            mon_fichier_info.write("lot name=" + self.lotName.GetValue())
            mon_fichier_info.write("\n")
            mon_fichier_info.close()
            page3 = pageThree(self.noteBook)
            self.noteBook.DeleteAllPages()
            self.noteBook.AddPage (page3,"Debugger")


    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "A small text editor", "About Sample Editor", wx.OK)
        dlg.ShowModal()                    # Show it
        dlg.Destroy()                      # finally destroy it when finished.

    def OnSave(self,e):
        mon_fichier = open("fichier.txt", "w")     # Argh j'ai tout écrasé !
        #mon_fichier.write(str(self.pos))
        mon_fichier.write(str(self.b))
        mon_fichier.close()
    def OnExit(self,e):
        self.Close(True)                   # Close the frame.





class pageOne (wx.Panel):
    def __init__ (self,parent):
                wx.Panel.__init__ (self,parent,wx.ID_ANY,size=(1,1))
                wx.StaticText(self, -1, '<-- Electrical Test Program', (220, 5))
                self.m_filePicker1 = wx.FilePickerCtrl(self,1)
                self.m_filePicker1.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnFileChange)


                ######################         sizer =wx.BoxSizer (wx.HORIZONTAL) ###########################################
                delta=60                
                Width=120
                Width1=Width+delta        #160
                Width2=Width1+delta       #200
                Width3=Width2+delta       #240
                Width4=Width3+delta       #280
                Width5=Width4+delta       #320
                Width6=Width5+delta       #360
                Width7=Width6+delta       #400

                self.panel = wx.Panel(self)
                self.wafer = wx.StaticText(self,wx.ID_ANY, label="wafer to test?", pos=(20, 45))   
                              
                self.myCheckBox01 = wx.CheckBox (self,wx.ID_ANY,label="1",pos=  (20 ,  60), size=(-1,-1))
                self.myCheckBox02 = wx.CheckBox (self,wx.ID_ANY,label="2",pos=  (20 ,  80), size=(-1,-1))       
                self.myCheckBox03 = wx.CheckBox (self,wx.ID_ANY,label="3",pos=  (20 , 100), size=(-1,-1))
                self.myCheckBox04 = wx.CheckBox (self,wx.ID_ANY,label="4",pos=  (20 , 120), size=(-1,-1))
                self.myCheckBox05 = wx.CheckBox (self,wx.ID_ANY,label="5",pos=  (20 , 140), size=(-1,-1))       
                self.myCheckBox06 = wx.CheckBox (self,wx.ID_ANY,label="6",pos=  (20 , 160), size=(-1,-1))
                self.myCheckBox07 = wx.CheckBox (self,wx.ID_ANY,label="7",pos=  (20 , 180), size=(-1,-1))
                self.myCheckBox08 = wx.CheckBox (self,wx.ID_ANY,label="8",pos=  (20 , 200), size=(-1,-1))     
                self.myCheckBox09 = wx.CheckBox (self,wx.ID_ANY,label="9",pos=  (20 , 220), size=(-1,-1))
                self.myCheckBox10 = wx.CheckBox (self,wx.ID_ANY,label="10",pos= (20 , 240), size=(-1,-1))
                self.myCheckBox11 = wx.CheckBox (self,wx.ID_ANY,label="11",pos= (20 , 260), size=(-1,-1))      
                self.myCheckBox12 = wx.CheckBox (self,wx.ID_ANY,label="12",pos= (20 , 280), size=(-1,-1))
                self.myCheckBox13 = wx.CheckBox (self,wx.ID_ANY,label="13",pos= (20 , 300), size=(-1,-1))
                self.myCheckBox14 = wx.CheckBox (self,wx.ID_ANY,label="14",pos= (20 , 320), size=(-1,-1))      
                self.myCheckBox15 = wx.CheckBox (self,wx.ID_ANY,label="15",pos= (20 , 340), size=(-1,-1))
                self.myCheckBox16 = wx.CheckBox (self,wx.ID_ANY,label="16",pos= (20 , 360), size=(-1,-1))
                self.myCheckBox17 = wx.CheckBox (self,wx.ID_ANY,label="17",pos= (20 , 380), size=(-1,-1))       
                self.myCheckBox18 = wx.CheckBox (self,wx.ID_ANY,label="18",pos= (20 , 400), size=(-1,-1))
                self.myCheckBox19 = wx.CheckBox (self,wx.ID_ANY,label="19",pos= (20 , 420), size=(-1,-1))
                self.myCheckBox20 = wx.CheckBox (self,wx.ID_ANY,label="20",pos= (20 , 440), size=(-1,-1))       
                self.myCheckBox21 = wx.CheckBox (self,wx.ID_ANY,label="21",pos= (20 , 460), size=(-1,-1))
                self.myCheckBox22 = wx.CheckBox (self,wx.ID_ANY,label="22",pos= (20 , 480), size=(-1,-1))
                self.myCheckBox23 = wx.CheckBox (self,wx.ID_ANY,label="23",pos= (20 , 500), size=(-1,-1))       
                self.myCheckBox24 = wx.CheckBox (self,wx.ID_ANY,label="24",pos= (20 , 520), size=(-1,-1))
                self.myCheckBox25 = wx.CheckBox (self,wx.ID_ANY,label="25",pos= (20 , 540), size=(-1,-1)) 
                
                self.wafer = wx.StaticText(self,wx.ID_ANY, label="Dies to test?", pos=(Width2, 180))    
                
                self.myCheckBox26 = wx.CheckBox (self,wx.ID_ANY,label="2  1",pos= (Width2 , 340), size=(-1,-1))       
                self.myCheckBox27 = wx.CheckBox (self,wx.ID_ANY,label="3  1",pos= (Width3 , 340), size=(-1,-1))
                self.myCheckBox28 = wx.CheckBox (self,wx.ID_ANY,label="4  1",pos= (Width4 , 340), size=(-1,-1))
                self.myCheckBox29 = wx.CheckBox (self,wx.ID_ANY,label="5  1",pos= (Width5 , 340), size=(-1,-1))       
                self.myCheckBox30 = wx.CheckBox (self,wx.ID_ANY,label="1  2",pos= (Width1 , 320), size=(-1,-1))     
                self.myCheckBox31 = wx.CheckBox (self,wx.ID_ANY,label="2  2",pos= (Width2 , 320), size=(-1,-1))
                self.myCheckBox32 = wx.CheckBox (self,wx.ID_ANY,label="3  2",pos= (Width3 , 320), size=(-1,-1))
                self.myCheckBox33 = wx.CheckBox (self,wx.ID_ANY,label="4  2",pos= (Width4 , 320), size=(-1,-1))      
                self.myCheckBox34 = wx.CheckBox (self,wx.ID_ANY,label="5  2",pos= (Width5 , 320), size=(-1,-1))
                self.myCheckBox35 = wx.CheckBox (self,wx.ID_ANY,label="6  2",pos= (Width6 , 320), size=(-1,-1))      
                self.myCheckBox36 = wx.CheckBox (self,wx.ID_ANY,label="-1  3",pos= (Width , 300), size=(-1,-1))
                self.myCheckBox37 = wx.CheckBox (self,wx.ID_ANY,label="1  3",pos= (Width1 , 300), size=(-1,-1))     
                self.myCheckBox38 = wx.CheckBox (self,wx.ID_ANY,label="2  3",pos= (Width2 , 300), size=(-1,-1))
                self.myCheckBox39 = wx.CheckBox (self,wx.ID_ANY,label="3  3",pos= (Width3 , 300), size=(-1,-1))
                self.myCheckBox40 = wx.CheckBox (self,wx.ID_ANY,label="4  3",pos= (Width4 , 300), size=(-1,-1))      
                self.myCheckBox41 = wx.CheckBox (self,wx.ID_ANY,label="5  3",pos= (Width5 , 300), size=(-1,-1))
                self.myCheckBox42 = wx.CheckBox (self,wx.ID_ANY,label="6  3",pos= (Width6 , 300), size=(-1,-1))
                self.myCheckBox43 = wx.CheckBox (self,wx.ID_ANY,label="7  3",pos= (Width7 , 300), size=(-1,-1)) 
                self.myCheckBox44 = wx.CheckBox (self,wx.ID_ANY,label="-1  4",pos= (Width , 280), size=(-1,-1))
                self.myCheckBox45 = wx.CheckBox (self,wx.ID_ANY,label="1  4",pos= (Width1 , 280), size=(-1,-1))     
                self.myCheckBox46 = wx.CheckBox (self,wx.ID_ANY,label="2  4",pos= (Width2 , 280), size=(-1,-1))
                self.myCheckBox47 = wx.CheckBox (self,wx.ID_ANY,label="3  4",pos= (Width3 , 280), size=(-1,-1))
                self.myCheckBox48 = wx.CheckBox (self,wx.ID_ANY,label="4  4",pos= (Width4 , 280), size=(-1,-1))      
                self.myCheckBox49 = wx.CheckBox (self,wx.ID_ANY,label="5  4",pos= (Width5 , 280), size=(-1,-1))
                self.myCheckBox50 = wx.CheckBox (self,wx.ID_ANY,label="6  4",pos= (Width6 , 280), size=(-1,-1))
                self.myCheckBox51 = wx.CheckBox (self,wx.ID_ANY,label="7  4",pos= (Width7 , 280), size=(-1,-1)) 
                self.myCheckBox52 = wx.CheckBox (self,wx.ID_ANY,label="-1  5",pos= (Width , 260), size=(-1,-1))
                self.myCheckBox53 = wx.CheckBox (self,wx.ID_ANY,label="1  5",pos= (Width1 , 260), size=(-1,-1))     
                self.myCheckBox54 = wx.CheckBox (self,wx.ID_ANY,label="2  5",pos= (Width2 , 260), size=(-1,-1))
                self.myCheckBox55 = wx.CheckBox (self,wx.ID_ANY,label="3  5",pos= (Width3 , 260), size=(-1,-1))
                self.myCheckBox56 = wx.CheckBox (self,wx.ID_ANY,label="4  5",pos= (Width4 , 260), size=(-1,-1))      
                self.myCheckBox57 = wx.CheckBox (self,wx.ID_ANY,label="5  5",pos= (Width5 , 260), size=(-1,-1))
                self.myCheckBox58 = wx.CheckBox (self,wx.ID_ANY,label="6  5",pos= (Width6 , 260), size=(-1,-1))
                self.myCheckBox59 = wx.CheckBox (self,wx.ID_ANY,label="7  5",pos= (Width7 , 260), size=(-1,-1)) 
                self.myCheckBox60 = wx.CheckBox (self,wx.ID_ANY,label="-1  6",pos= (Width , 240), size=(-1,-1))
                self.myCheckBox61 = wx.CheckBox (self,wx.ID_ANY,label="1  6",pos= (Width1 , 240), size=(-1,-1))     
                self.myCheckBox62 = wx.CheckBox (self,wx.ID_ANY,label="2  6",pos= (Width2 , 240), size=(-1,-1))
                self.myCheckBox63 = wx.CheckBox (self,wx.ID_ANY,label="3  6",pos= (Width3 , 240), size=(-1,-1))
                self.myCheckBox64 = wx.CheckBox (self,wx.ID_ANY,label="4  6",pos= (Width4 , 240), size=(-1,-1))      
                self.myCheckBox65 = wx.CheckBox (self,wx.ID_ANY,label="5  6",pos= (Width5 , 240), size=(-1,-1))
                self.myCheckBox66 = wx.CheckBox (self,wx.ID_ANY,label="6  6",pos= (Width6 , 240), size=(-1,-1))
                self.myCheckBox67 = wx.CheckBox (self,wx.ID_ANY,label="7  6",pos= (Width7 , 240), size=(-1,-1)) 
                self.myCheckBox68 = wx.CheckBox (self,wx.ID_ANY,label="1  7",pos= (Width1 , 220), size=(-1,-1))     
                self.myCheckBox69 = wx.CheckBox (self,wx.ID_ANY,label="2  7",pos= (Width2 , 220), size=(-1,-1))
                self.myCheckBox70 = wx.CheckBox (self,wx.ID_ANY,label="3  7",pos= (Width3 , 220), size=(-1,-1))
                self.myCheckBox71 = wx.CheckBox (self,wx.ID_ANY,label="4  7",pos= (Width4 , 220), size=(-1,-1))      
                self.myCheckBox72 = wx.CheckBox (self,wx.ID_ANY,label="5  7",pos= (Width5 , 220), size=(-1,-1))
                self.myCheckBox73 = wx.CheckBox (self,wx.ID_ANY,label="6  7",pos= (Width6 , 220), size=(-1,-1))     
                self.myCheckBox74 = wx.CheckBox (self,wx.ID_ANY,label="2  8",pos= (Width2 , 200), size=(-1,-1))
                self.myCheckBox75 = wx.CheckBox (self,wx.ID_ANY,label="3  8",pos= (Width3 , 200), size=(-1,-1))
                self.myCheckBox76 = wx.CheckBox (self,wx.ID_ANY,label="4  8",pos= (Width4 , 200), size=(-1,-1))      
                self.myCheckBox77 = wx.CheckBox (self,wx.ID_ANY,label="5  8",pos= (Width5 , 200), size=(-1,-1))

                self.button1=wx.Button (self,wx.ID_ANY,label="Create Wafer list and Die List ",pos=(200,400),size=(200,30)) 
                self.button2=wx.Button (self,wx.ID_ANY,label="Select all dies ",pos=(200,430),size=(200,30)) 
                self.button4=wx.Button (self,wx.ID_ANY,label="UnSelect all dies ",pos=(400,430),size=(200,30)) 
                self.button3=wx.Button (self,wx.ID_ANY,label="launch test",pos=(200,465),size=(400,100))
                
                print (sizeMemory)

                if sizeMemory=='256bit':          
                    self.sampleList = ['A-D26','A-D27','A-D28','A-D29','D-D26','D-D27','D-D28','D-D29']

                if sizeMemory=='256bit Kelvin':          
                    self.sampleList = ['A-C01','A-C02','D-C01','D-C02']

                if sizeMemory=='4kbit NNN':          
                    self.sampleList = ['A-D09','A-D10','A-D11','A-D12','A-D13','A-D14','A-D15','A-D16','A-D17','A-D18','A-D19','A-D20','D-D09','D-D10','D-D11','D-D12','D-D13','D-D14','D-D15','D-D16','D-D17','D-D18','D-D19','D-D20']

                if sizeMemory=='4kbit KTT':          
                    self.sampleList = ['A-D01','A-D02','A-D03','A-D04','A-D05','A-D06','A-D07','A-D08','D-D01','D-D02','D-D03','D-D04','D-D05','D-D06','D-D07','D-D08']

                if sizeMemory=='4kbit PRKN':          
                    self.sampleList = ['A-D21','A-D22','A-D23','A-D24','A-D25','D-D21','D-D22','D-D23','D-D24','D-D25']

                if sizeMemory=='64kbit panache':          
                    self.sampleList = ['A-C03','A-C03bis','D-C03','D-C03bis']

                if sizeMemory=='1Mbit simple':          
                    self.sampleList = ['A-C04','A-C05','D-C04','D-C05']

                if sizeMemory=='VRAM':          
                    self.sampleList = ['A-A55','A-A56','A-A57','A-A58','A-A59','A-A60','A-A61','A-A62','A-A63','A-A64','D-A55','D-A56','D-A57','D-A58','D-A59','D-A60','D-A61','D-A62','D-A63','D-A64']

                self.button3.Hide()
                self.lblhear = wx.StaticText(self,wx.ID_ANY, label="scribe to test?", pos=(300, 20))
                self.edithear =wx.ComboBox(self,wx.ID_ANY, pos=(300, 50), size=(95, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)

                self.Bind(wx.EVT_BUTTON, self.checkfunction_wafer,self.button1)
                self.Bind(wx.EVT_BUTTON, self.select_all_dies_wafer,self.button2)
                self.Bind(wx.EVT_BUTTON, self.unselect_all_dies_wafer,self.button4)
                self.Bind(wx.EVT_BUTTON, self.launch_test,self.button3)
                
    def OnFileChange( self, event):
                event.Skip()
                global TestFile
                TestFile=self.m_filePicker1.GetPath()           
                print TestFile
                
    def select_all_dies_wafer(self,event):
                self.myCheckBox26.SetValue(True)
                self.myCheckBox27.SetValue(True)
                self.myCheckBox28.SetValue(True)
                self.myCheckBox29.SetValue(True)
                self.myCheckBox30.SetValue(True)
                self.myCheckBox31.SetValue(True)
                self.myCheckBox32.SetValue(True)
                self.myCheckBox33.SetValue(True)
                self.myCheckBox34.SetValue(True)
                self.myCheckBox35.SetValue(True)
                self.myCheckBox36.SetValue(True)
                self.myCheckBox37.SetValue(True)
                self.myCheckBox38.SetValue(True)
                self.myCheckBox39.SetValue(True)
                self.myCheckBox40.SetValue(True)
                self.myCheckBox41.SetValue(True)
                self.myCheckBox42.SetValue(True)
                self.myCheckBox43.SetValue(True)
                self.myCheckBox44.SetValue(True)
                self.myCheckBox45.SetValue(True)
                self.myCheckBox46.SetValue(True)
                self.myCheckBox47.SetValue(True)
                self.myCheckBox48.SetValue(True)
                self.myCheckBox49.SetValue(True)
                self.myCheckBox50.SetValue(True)
                self.myCheckBox51.SetValue(True)
                self.myCheckBox52.SetValue(True)
                self.myCheckBox53.SetValue(True)
                self.myCheckBox54.SetValue(True)
                self.myCheckBox55.SetValue(True)
                self.myCheckBox56.SetValue(True)
                self.myCheckBox57.SetValue(True)
                self.myCheckBox58.SetValue(True)
                self.myCheckBox59.SetValue(True)
                self.myCheckBox60.SetValue(True)
                self.myCheckBox61.SetValue(True)
                self.myCheckBox62.SetValue(True)
                self.myCheckBox63.SetValue(True)                
                self.myCheckBox52.SetValue(True)
                self.myCheckBox53.SetValue(True)
                self.myCheckBox54.SetValue(True)
                self.myCheckBox55.SetValue(True)
                self.myCheckBox56.SetValue(True)
                self.myCheckBox57.SetValue(True)
                self.myCheckBox58.SetValue(True)
                self.myCheckBox59.SetValue(True)
                self.myCheckBox60.SetValue(True)
                self.myCheckBox61.SetValue(True)
                self.myCheckBox62.SetValue(True)
                self.myCheckBox63.SetValue(True)                 
                self.myCheckBox64.SetValue(True)
                self.myCheckBox65.SetValue(True)
                self.myCheckBox66.SetValue(True)
                self.myCheckBox67.SetValue(True)
                self.myCheckBox68.SetValue(True)
                self.myCheckBox69.SetValue(True)
                self.myCheckBox70.SetValue(True)
                self.myCheckBox71.SetValue(True)
                self.myCheckBox72.SetValue(True)
                self.myCheckBox73.SetValue(True)
                self.myCheckBox74.SetValue(True)               
                self.myCheckBox75.SetValue(True)
                self.myCheckBox76.SetValue(True)
                self.myCheckBox77.SetValue(True)
                
    def unselect_all_dies_wafer(self,event):
                self.myCheckBox26.SetValue(False)
                self.myCheckBox27.SetValue(False)
                self.myCheckBox28.SetValue(False)
                self.myCheckBox29.SetValue(False)
                self.myCheckBox30.SetValue(False)
                self.myCheckBox31.SetValue(False)
                self.myCheckBox32.SetValue(False)
                self.myCheckBox33.SetValue(False)
                self.myCheckBox34.SetValue(False)
                self.myCheckBox35.SetValue(False)
                self.myCheckBox36.SetValue(False)
                self.myCheckBox37.SetValue(False)
                self.myCheckBox38.SetValue(False)
                self.myCheckBox39.SetValue(False)
                self.myCheckBox40.SetValue(False)
                self.myCheckBox41.SetValue(False)
                self.myCheckBox42.SetValue(False)
                self.myCheckBox43.SetValue(False)
                self.myCheckBox44.SetValue(False)
                self.myCheckBox45.SetValue(False)
                self.myCheckBox46.SetValue(False)
                self.myCheckBox47.SetValue(False)
                self.myCheckBox48.SetValue(False)
                self.myCheckBox49.SetValue(False)
                self.myCheckBox50.SetValue(False)
                self.myCheckBox51.SetValue(False)
                self.myCheckBox52.SetValue(False)
                self.myCheckBox53.SetValue(False)
                self.myCheckBox54.SetValue(False)
                self.myCheckBox55.SetValue(False)
                self.myCheckBox56.SetValue(False)
                self.myCheckBox57.SetValue(False)
                self.myCheckBox58.SetValue(False)
                self.myCheckBox59.SetValue(False)
                self.myCheckBox60.SetValue(False)
                self.myCheckBox61.SetValue(False)
                self.myCheckBox62.SetValue(False)
                self.myCheckBox63.SetValue(False)                
                self.myCheckBox52.SetValue(False)
                self.myCheckBox53.SetValue(False)
                self.myCheckBox54.SetValue(False)
                self.myCheckBox55.SetValue(False)
                self.myCheckBox56.SetValue(False)
                self.myCheckBox57.SetValue(False)
                self.myCheckBox58.SetValue(False)
                self.myCheckBox59.SetValue(False)
                self.myCheckBox60.SetValue(False)
                self.myCheckBox61.SetValue(False)
                self.myCheckBox62.SetValue(False)
                self.myCheckBox63.SetValue(False)
                self.myCheckBox64.SetValue(False)
                self.myCheckBox65.SetValue(False)
                self.myCheckBox66.SetValue(False)
                self.myCheckBox67.SetValue(False)
                self.myCheckBox68.SetValue(False)
                self.myCheckBox69.SetValue(False)
                self.myCheckBox70.SetValue(False)
                self.myCheckBox71.SetValue(False)
                self.myCheckBox72.SetValue(False)
                self.myCheckBox73.SetValue(False)
                self.myCheckBox74.SetValue(False)
                self.myCheckBox75.SetValue(False)
                self.myCheckBox76.SetValue(False)
                self.myCheckBox77.SetValue(False)
                
    def checkfunction_wafer(self,event):   
        mon_fichier = open("wafer.txt", "w") 
        if self.myCheckBox01.IsChecked()==True :
            print "1"
            mon_fichier.write("1\n")
        if self.myCheckBox02.IsChecked()==True :
            print "2"
            mon_fichier.write("2\n")
        if self.myCheckBox03.IsChecked()==True :
            print "3"
            mon_fichier.write("3\n")
        if self.myCheckBox04.IsChecked()==True :
            print "4"
            mon_fichier.write("4\n")
        if self.myCheckBox05.IsChecked()==True :
            print "5"
            mon_fichier.write("5\n")
        if self.myCheckBox06.IsChecked()==True :
            print "6"
            mon_fichier.write("6\n")
        if self.myCheckBox07.IsChecked()==True :
            print "7"
            mon_fichier.write("7\n")
        if self.myCheckBox08.IsChecked()==True :
            print "8"
            mon_fichier.write("8\n")
        if self.myCheckBox09.IsChecked()==True :
            print "9" 
            mon_fichier.write("9\n")
        if self.myCheckBox10.IsChecked()==True :
            print "10"
            mon_fichier.write("10\n")
        if self.myCheckBox11.IsChecked()==True :
            print "11"
            mon_fichier.write("11\n")
        if self.myCheckBox12.IsChecked()==True :
            print "12"
            mon_fichier.write("12\n")
        if self.myCheckBox13.IsChecked()==True :
            print "13"
            mon_fichier.write("13\n")
        if self.myCheckBox14.IsChecked()==True :
            print "14"
            mon_fichier.write("14\n")
        if self.myCheckBox15.IsChecked()==True :
            print "15"
            mon_fichier.write("15\n")
        if self.myCheckBox16.IsChecked()==True :
            print "16"
            mon_fichier.write("16\n")
        if self.myCheckBox17.IsChecked()==True :
            print "17"
            mon_fichier.write("17\n")
        if self.myCheckBox18.IsChecked()==True :
            print "18"
            mon_fichier.write("18\n")
        if self.myCheckBox19.IsChecked()==True :
            print "19"
            mon_fichier.write("19\n")
        if self.myCheckBox20.IsChecked()==True :
            print "20"
            mon_fichier.write("20\n")            
        if self.myCheckBox21.IsChecked()==True :
            print "21"
            mon_fichier.write("21\n")
        if self.myCheckBox22.IsChecked()==True :
            print "22"
            mon_fichier.write("22\n")
        if self.myCheckBox23.IsChecked()==True :
            print "23"
            mon_fichier.write("23\n")
        if self.myCheckBox24.IsChecked()==True :
            print "24"
            mon_fichier.write("24\n")
        if self.myCheckBox25.IsChecked()==True :        
            print "25"
            mon_fichier.write("25\n")
        mon_fichier.close()
        
        mon_fichier_die = open("DUT.txt", "w") 
        self.barrette = self.edithear.GetValue()
        print self.barrette
        mon_fichier_die.write(self.barrette)
        mon_fichier_die.write("\n")
        
        if self.myCheckBox26.IsChecked()==True :
            print "2   1"
            mon_fichier_die.write("2   1\n")
        if self.myCheckBox27.IsChecked()==True :
            print "3   1"
            mon_fichier_die.write("3   1\n")
        if self.myCheckBox28.IsChecked()==True :
            print "4   1"
            mon_fichier_die.write("4   1\n")
        if self.myCheckBox29.IsChecked()==True :
            print "5   1"
            mon_fichier_die.write("5   1\n")
        if self.myCheckBox30.IsChecked()==True :
            print "1   2"
            mon_fichier_die.write("\n 1   2")
        if self.myCheckBox31.IsChecked()==True :
            print "2   2"
            mon_fichier_die.write("2   2\n")
        if self.myCheckBox32.IsChecked()==True :
            print "3   2"
            mon_fichier_die.write("3   2\n")
        if self.myCheckBox33.IsChecked()==True :
            print "4   2"
            mon_fichier_die.write("4   2\n")
        if self.myCheckBox34.IsChecked()==True :
            print "5   2" 
            mon_fichier_die.write("5   2\n")
        if self.myCheckBox35.IsChecked()==True :
            print "6   2"
            mon_fichier_die.write("6   2\n")
        if self.myCheckBox36.IsChecked()==True :
            print "-1  3"
            mon_fichier_die.write("-1   3\n")
        if self.myCheckBox37.IsChecked()==True :
            print "1   3"
            mon_fichier_die.write("1   3\n")
        if self.myCheckBox38.IsChecked()==True :
            print "2   3"
            mon_fichier_die.write("2   3\n")
        if self.myCheckBox39.IsChecked()==True :
            print "3   3"
            mon_fichier_die.write("3   3\n")
        if self.myCheckBox40.IsChecked()==True :
            print "4   3"
            mon_fichier_die.write("4   3\n")
        if self.myCheckBox41.IsChecked()==True :
            print "5   3"
            mon_fichier_die.write("5   3\n")
        if self.myCheckBox42.IsChecked()==True :
            print "6   3"
            mon_fichier_die.write("6   3\n")
        if self.myCheckBox43.IsChecked()==True :
            print "7   3"
            mon_fichier_die.write("7   3\n")
        if self.myCheckBox44.IsChecked()==True :
            print "-1  4"
            mon_fichier_die.write("-1   4\n")
        if self.myCheckBox45.IsChecked()==True :
            print "1   4"
            mon_fichier_die.write("1   4\n")            
        if self.myCheckBox46.IsChecked()==True :
            print "2   4"
            mon_fichier_die.write("2   4\n")
        if self.myCheckBox47.IsChecked()==True :
            print "3   4"
            mon_fichier_die.write("3   4\n")
        if self.myCheckBox48.IsChecked()==True :
            print "4   4"
            mon_fichier_die.write("4   4\n")
        if self.myCheckBox49.IsChecked()==True :
            print "5   4"
            mon_fichier_die.write("5   4\n")
        if self.myCheckBox50.IsChecked()==True :        
            print "6   4"
            mon_fichier_die.write("6   4\n")
        if self.myCheckBox51.IsChecked()==True :        
            print "7   4"            
            mon_fichier_die.write("7   4\n")
        if self.myCheckBox52.IsChecked()==True :        
            print "-1  5"            
            mon_fichier_die.write("-1   5\n")
        if self.myCheckBox53.IsChecked()==True :        
            print "1   5"            
            mon_fichier_die.write("1   5\n")
        if self.myCheckBox54.IsChecked()==True :        
            print "2   5"            
            mon_fichier_die.write("2   5\n")
        if self.myCheckBox55.IsChecked()==True :        
            print "3   5"            
            mon_fichier_die.write("3   5\n")
        if self.myCheckBox56.IsChecked()==True :        
            print "4   5"            
            mon_fichier_die.write("4   5\n")
        if self.myCheckBox57.IsChecked()==True :        
            print "5   5"            
            mon_fichier_die.write("5   5\n")
        if self.myCheckBox58.IsChecked()==True :        
            print "6   5"            
            mon_fichier_die.write("6   5\n")
        if self.myCheckBox59.IsChecked()==True :        
            print "7   5"            
            mon_fichier_die.write("7   5\n")
        if self.myCheckBox60.IsChecked()==True :        
            print "-1   6"            
            mon_fichier_die.write("-1   6\n")
        if self.myCheckBox61.IsChecked()==True :        
            print "1    6"            
            mon_fichier_die.write("1   6\n")
        if self.myCheckBox62.IsChecked()==True :        
            print "2   6"            
            mon_fichier_die.write("2   6\n")
        if self.myCheckBox63.IsChecked()==True :        
            print "3   6"            
            mon_fichier_die.write("3   6\n")
        if self.myCheckBox64.IsChecked()==True :        
            print "4   6"            
            mon_fichier_die.write("4   6\n")
        if self.myCheckBox65.IsChecked()==True :        
            print "5   6"            
            mon_fichier_die.write("5   6\n")
        if self.myCheckBox66.IsChecked()==True :        
            print "6   6"            
            mon_fichier_die.write("6   6\n")
        if self.myCheckBox67.IsChecked()==True :        
            print "7   6"            
            mon_fichier_die.write("7   6\n")
        if self.myCheckBox68.IsChecked()==True :        
            print "1   7"            
            mon_fichier_die.write("1   7\n")
        if self.myCheckBox69.IsChecked()==True :        
            print "2   7"            
            mon_fichier_die.write("2   7\n")
        if self.myCheckBox70.IsChecked()==True :        
            print "3   7"            
            mon_fichier_die.write("3   7\n")
        if self.myCheckBox71.IsChecked()==True :        
            print "4   7"            
            mon_fichier_die.write("4   7\n")
        if self.myCheckBox72.IsChecked()==True :        
            print "5   7"            
            mon_fichier_die.write("5   7\n")
        if self.myCheckBox73.IsChecked()==True :        
            print "6   7"            
            mon_fichier_die.write("6   7\n")
        if self.myCheckBox74.IsChecked()==True :        
            print "2   8"            
            mon_fichier_die.write("2   8\n")
        if self.myCheckBox75.IsChecked()==True :        
            print "3   8"            
            mon_fichier_die.write("3   8\n")
        if self.myCheckBox76.IsChecked()==True :        
            print "4   8"            
            mon_fichier_die.write("4   8\n")
        if self.myCheckBox77.IsChecked()==True :        
            print "5   8"            
            mon_fichier_die.write("5   8\n")

        if self.edithear.GetValue()!="":            
            if self.myCheckBox26.GetValue()|self.myCheckBox27.GetValue()|self.myCheckBox28.GetValue()|self.myCheckBox29.GetValue()|self.myCheckBox30.IsChecked()|self.myCheckBox31.IsChecked()|self.myCheckBox32.IsChecked()|self.myCheckBox33.IsChecked()|self.myCheckBox34.IsChecked()|self.myCheckBox35.IsChecked()|self.myCheckBox36.IsChecked()|self.myCheckBox37.IsChecked()|self.myCheckBox38.IsChecked()|self.myCheckBox39.IsChecked()|self.myCheckBox40.IsChecked()|self.myCheckBox41.IsChecked()|self.myCheckBox42.IsChecked()|self.myCheckBox43.IsChecked()|self.myCheckBox44.IsChecked()|self.myCheckBox45.IsChecked()|self.myCheckBox46.IsChecked()|self.myCheckBox47.IsChecked()|self.myCheckBox48.IsChecked()|self.myCheckBox49.IsChecked()|self.myCheckBox50.IsChecked()|self.myCheckBox51.IsChecked()|self.myCheckBox52.IsChecked()|self.myCheckBox53.IsChecked()|self.myCheckBox54.IsChecked()|self.myCheckBox55.IsChecked()|self.myCheckBox56.IsChecked()|self.myCheckBox57.IsChecked()|self.myCheckBox58.IsChecked()|self.myCheckBox59.IsChecked()|self.myCheckBox60.IsChecked()|self.myCheckBox61.IsChecked()|self.myCheckBox62.IsChecked()|self.myCheckBox63.IsChecked()|self.myCheckBox64.IsChecked()|self.myCheckBox65.IsChecked()|self.myCheckBox66.IsChecked()|self.myCheckBox67.IsChecked()|self.myCheckBox68.IsChecked()|self.myCheckBox69.IsChecked()|self.myCheckBox70.IsChecked()|self.myCheckBox71.IsChecked()|self.myCheckBox72.IsChecked()|self.myCheckBox73.IsChecked()|self.myCheckBox74.IsChecked()|self.myCheckBox75.IsChecked()|self.myCheckBox76.IsChecked()|self.myCheckBox77.IsChecked()==True:
                self.button3.Show()
        mon_fichier_die.close()
        
    def launch_test(self,event):        
        driver_electroglas.load_from_cassette ()
        print "test en mode production"
        
class pageTwo (wx.Panel):

    def __init__ (self,parent):
                wx.Panel.__init__ (self,parent,wx.ID_ANY,size=(1,1))
                wx.FutureCall(5000, self.ShowMessage)
                delta=60                
                Width=120
                Width1=Width+delta        #160
                Width2=Width1+delta       #200
                Width3=Width2+delta       #240
                Width4=Width3+delta       #280
                Width5=Width4+delta       #320
                Width6=Width5+delta       #360
                Width7=Width6+delta       #400

                self.panel = wx.Panel(self)
                                         
                self.wafer = wx.StaticText(self,wx.ID_ANY, label="Dies to test?", pos=(Width2, 180))             
                self.myCheckBox26 = wx.CheckBox (self,wx.ID_ANY,label="2  1",pos= (Width2 , 340), size=(-1,-1))       
                self.myCheckBox27 = wx.CheckBox (self,wx.ID_ANY,label="3  1",pos= (Width3 , 340), size=(-1,-1))
                self.myCheckBox28 = wx.CheckBox (self,wx.ID_ANY,label="4  1",pos= (Width4 , 340), size=(-1,-1))
                self.myCheckBox29 = wx.CheckBox (self,wx.ID_ANY,label="5  1",pos= (Width5 , 340), size=(-1,-1))       
                self.myCheckBox30 = wx.CheckBox (self,wx.ID_ANY,label="1  2",pos= (Width1 , 320), size=(-1,-1))     
                self.myCheckBox31 = wx.CheckBox (self,wx.ID_ANY,label="2  2",pos= (Width2 , 320), size=(-1,-1))
                self.myCheckBox32 = wx.CheckBox (self,wx.ID_ANY,label="3  2",pos= (Width3 , 320), size=(-1,-1))
                self.myCheckBox33 = wx.CheckBox (self,wx.ID_ANY,label="4  2",pos= (Width4 , 320), size=(-1,-1))      
                self.myCheckBox34 = wx.CheckBox (self,wx.ID_ANY,label="5  2",pos= (Width5 , 320), size=(-1,-1))
                self.myCheckBox35 = wx.CheckBox (self,wx.ID_ANY,label="6  2",pos= (Width6 , 320), size=(-1,-1))      
                self.myCheckBox36 = wx.CheckBox (self,wx.ID_ANY,label="-1  3",pos= (Width , 300), size=(-1,-1))
                self.myCheckBox37 = wx.CheckBox (self,wx.ID_ANY,label="1  3",pos= (Width1 , 300), size=(-1,-1))     
                self.myCheckBox38 = wx.CheckBox (self,wx.ID_ANY,label="2  3",pos= (Width2 , 300), size=(-1,-1))
                self.myCheckBox39 = wx.CheckBox (self,wx.ID_ANY,label="3  3",pos= (Width3 , 300), size=(-1,-1))
                self.myCheckBox40 = wx.CheckBox (self,wx.ID_ANY,label="4  3",pos= (Width4 , 300), size=(-1,-1))      
                self.myCheckBox41 = wx.CheckBox (self,wx.ID_ANY,label="5  3",pos= (Width5 , 300), size=(-1,-1))
                self.myCheckBox42 = wx.CheckBox (self,wx.ID_ANY,label="6  3",pos= (Width6 , 300), size=(-1,-1))
                self.myCheckBox43 = wx.CheckBox (self,wx.ID_ANY,label="7  3",pos= (Width7 , 300), size=(-1,-1)) 
                self.myCheckBox44 = wx.CheckBox (self,wx.ID_ANY,label="-1  4",pos= (Width , 280), size=(-1,-1))
                self.myCheckBox45 = wx.CheckBox (self,wx.ID_ANY,label="1  4",pos= (Width1 , 280), size=(-1,-1))     
                self.myCheckBox46 = wx.CheckBox (self,wx.ID_ANY,label="2  4",pos= (Width2 , 280), size=(-1,-1))
                self.myCheckBox47 = wx.CheckBox (self,wx.ID_ANY,label="3  4",pos= (Width3 , 280), size=(-1,-1))
                self.myCheckBox48 = wx.CheckBox (self,wx.ID_ANY,label="4  4",pos= (Width4 , 280), size=(-1,-1))      
                self.myCheckBox49 = wx.CheckBox (self,wx.ID_ANY,label="5  4",pos= (Width5 , 280), size=(-1,-1))
                self.myCheckBox50 = wx.CheckBox (self,wx.ID_ANY,label="6  4",pos= (Width6 , 280), size=(-1,-1))
                self.myCheckBox51 = wx.CheckBox (self,wx.ID_ANY,label="7  4",pos= (Width7 , 280), size=(-1,-1)) 
                self.myCheckBox52 = wx.CheckBox (self,wx.ID_ANY,label="-1  5",pos= (Width , 260), size=(-1,-1))
                self.myCheckBox53 = wx.CheckBox (self,wx.ID_ANY,label="1  5",pos= (Width1 , 260), size=(-1,-1))     
                self.myCheckBox54 = wx.CheckBox (self,wx.ID_ANY,label="2  5",pos= (Width2 , 260), size=(-1,-1))
                self.myCheckBox55 = wx.CheckBox (self,wx.ID_ANY,label="3  5",pos= (Width3 , 260), size=(-1,-1))
                self.myCheckBox56 = wx.CheckBox (self,wx.ID_ANY,label="4  5",pos= (Width4 , 260), size=(-1,-1))      
                self.myCheckBox57 = wx.CheckBox (self,wx.ID_ANY,label="5  5",pos= (Width5 , 260), size=(-1,-1))
                self.myCheckBox58 = wx.CheckBox (self,wx.ID_ANY,label="6  5",pos= (Width6 , 260), size=(-1,-1))
                self.myCheckBox59 = wx.CheckBox (self,wx.ID_ANY,label="7  5",pos= (Width7 , 260), size=(-1,-1)) 
                self.myCheckBox60 = wx.CheckBox (self,wx.ID_ANY,label="-1  6",pos= (Width , 240), size=(-1,-1))
                self.myCheckBox61 = wx.CheckBox (self,wx.ID_ANY,label="1  6",pos= (Width1 , 240), size=(-1,-1))     
                self.myCheckBox62 = wx.CheckBox (self,wx.ID_ANY,label="2  6",pos= (Width2 , 240), size=(-1,-1))
                self.myCheckBox63 = wx.CheckBox (self,wx.ID_ANY,label="3  6",pos= (Width3 , 240), size=(-1,-1))
                self.myCheckBox64 = wx.CheckBox (self,wx.ID_ANY,label="4  6",pos= (Width4 , 240), size=(-1,-1))      
                self.myCheckBox65 = wx.CheckBox (self,wx.ID_ANY,label="5  6",pos= (Width5 , 240), size=(-1,-1))
                self.myCheckBox66 = wx.CheckBox (self,wx.ID_ANY,label="6  6",pos= (Width6 , 240), size=(-1,-1))
                self.myCheckBox67 = wx.CheckBox (self,wx.ID_ANY,label="7  6",pos= (Width7 , 240), size=(-1,-1)) 
                self.myCheckBox68 = wx.CheckBox (self,wx.ID_ANY,label="1  7",pos= (Width1 , 220), size=(-1,-1))     
                self.myCheckBox69 = wx.CheckBox (self,wx.ID_ANY,label="2  7",pos= (Width2 , 220), size=(-1,-1))
                self.myCheckBox70 = wx.CheckBox (self,wx.ID_ANY,label="3  7",pos= (Width3 , 220), size=(-1,-1))
                self.myCheckBox71 = wx.CheckBox (self,wx.ID_ANY,label="4  7",pos= (Width4 , 220), size=(-1,-1))      
                self.myCheckBox72 = wx.CheckBox (self,wx.ID_ANY,label="5  7",pos= (Width5 , 220), size=(-1,-1))
                self.myCheckBox73 = wx.CheckBox (self,wx.ID_ANY,label="6  7",pos= (Width6 , 220), size=(-1,-1))     
                self.myCheckBox74 = wx.CheckBox (self,wx.ID_ANY,label="2  8",pos= (Width2 , 200), size=(-1,-1))
                self.myCheckBox75 = wx.CheckBox (self,wx.ID_ANY,label="3  8",pos= (Width3 , 200), size=(-1,-1))
                self.myCheckBox76 = wx.CheckBox (self,wx.ID_ANY,label="4  8",pos= (Width4 , 200), size=(-1,-1))      
                self.myCheckBox77 = wx.CheckBox (self,wx.ID_ANY,label="5  8",pos= (Width5 , 200), size=(-1,-1))

                self.button1=wx.Button (self,wx.ID_ANY,label="Create Die List only ",pos=(200,400),size=(200,30)) 
                self.button2=wx.Button (self,wx.ID_ANY,label="Select all dies ",pos=(200,430),size=(200,30)) 
                self.button4=wx.Button (self,wx.ID_ANY,label="UnSelect all dies ",pos=(400,430),size=(200,30)) 
                self.button3=wx.Button (self,wx.ID_ANY,label="launch test",pos=(200,465),size=(400,100))
 
                print (sizeMemory)

                if sizeMemory=='256bit':          
                    self.sampleList = ['A-D26','A-D27','A-D28','A-D29','D-D26','D-D27','D-D28','D-D29']

                if sizeMemory=='256bit Kelvin':          
                    self.sampleList = ['A-C01','A-C02','D-C01','D-C02']

                if sizeMemory=='4kbit NNN':          
                    self.sampleList = ['A-D09','A-D10','A-D11','A-D12','A-D13','A-D14','A-D15','A-D16','A-D17','A-D18','A-D19','A-D20','D-D09','D-D10','D-D11','D-D12','D-D13','D-D14','D-D15','D-D16','D-D17','D-D18','D-D19','D-D20']

                if sizeMemory=='4kbit KTT':          
                    self.sampleList = ['A-D01','A-D02','A-D03','A-D04','A-D05','A-D06','A-D07','A-D08','D-D01','D-D02','D-D03','D-D04','D-D05','D-D06','D-D07','D-D08']

                if sizeMemory=='4kbit PRKN':          
                    self.sampleList = ['A-D21','A-D22','A-D23','A-D24','A-D25','D-D21','D-D22','D-D23','D-D24','D-D25']

                if sizeMemory=='64kbit panache':          
                    self.sampleList = ['A-C03','A-C03bis','D-C03','D-C03bis']

                if sizeMemory=='1Mbit simple':          
                    self.sampleList = ['A-C04','A-C05','D-C04','D-C05']

                if sizeMemory=='VRAM':          
                    self.sampleList = ['A-A55','A-A56','A-A57','A-A58','A-A59','A-A60','A-A61','A-A62','A-A63','A-A64','D-A55','D-A56','D-A57','D-A58','D-A59','D-A60','D-A61','D-A62','D-A63','D-A64']
           
                
#                self.sampleList = ['A-A01','A-A02','A-A03','A-A04','A-A05','A-A06','A-A07','A-A08','A-A09','A-A10','A-A11','A-A12','A-A13','A-A14','A-A15','A-A16','A-A17','A-A18','A-A19','A-A20','A-A21','A-A22','A-A23','A-A24','A-A25','A-A26','A-A27','A-A28','A-A29','A-A30','A-A31','A-A32','A-A33','A-A34','A-A35','A-A36','A-A37','A-A38','A-A39','A-A40','A-A41','A-A42','A-A43','A-A44','A-A45','A-A46','A-A47','A-A48','A-A49','A-A50','A-A51','A-A52','A-A53','A-A54','A-A55','A-A56','A-A57','A-A58','A-A59','A-A60','A-A61','A-A62','A-A63','A-A64','A-B01','A-B02','A-B03','A-B04','A-B05','A-B06','A-B07','A-B08','A-B09','A-B10','A-B11','A-B12','A-B13','A-B14','A-B15','A-B16','A-B17','A-B18','A-B19','A-B20','A-B21','A-B22','A-B23','A-B24','A-B25','A-B26','A-B27','A-B28','A-B29','A-B30','A-B31','A-B32','A-B33','A-B34','A-B35','A-B36','A-B37','A-B38','A-B39','A-B40','A-B41','A-B42','A-B43','A-B44','A-B45','A-B46','A-B47','A-B48','A-B49','A-B50','A-B51','A-B52','A-B53','A-B54','A-B55','A-B56','A-B57','A-B58','A-B59','A-B60','A-B61','A-B62','A-B63','A-B64','A-B65','A-B66','A-C01','A-C02','A-C03','A-C04','A-C05','A-D01','A-D02','A-D03','A-D04','A-D05','A-D06','A-D07','A-D08','A-D09','A-D10','A-D11','A-D12','A-D13','A-D14','A-D15','A-D16','A-D17','A-D18','A-D19','A-D20','A-D21','A-D22','A-D23','A-D24','A-D25','A-D26','A-D27','A-D28','A-D29','A-E01','A-E02','A-E03','A-E04','A-E05','A-E06','A-E07','A-E08','A-E09','A-E10','A-E11','A-E12','A-E13','A-E14','A-E15','A-E16','A-E17','A-E18','A-E19','A-E20','A-E21','A-E22','A-E23','A-E24','A-E25','A-E26','A-E27','A-E28','A-E29','A-E30','A-E31','A-F01','A-F02','A-F03','A-F04','A-F05','A-F06','A-F07','A-F08','A-F09','A-F10','A-F11','A-F12','A-F13','A-F14','A-F15','A-F16','A-F17','A-F18','A-F19','A-F20','A-F21','D-A01','D-A02','D-A03','D-A04','D-A05','D-A06','D-A07','D-A08','D-A09','D-A10','D-A11','D-A12','D-A13','D-A14','D-A15','D-A16','D-A17','D-A18','D-A19','D-A20','D-A21','D-A22','D-A23','D-A24','D-A25','D-A26','D-A27','D-A28','D-A29','D-A30','D-A31','D-A32','D-A33','D-A34','D-A35','D-A36','D-A37','D-A38','D-A39','D-A40','D-A41','D-A42','D-A43','D-A44','D-A45','D-A46','D-A47','D-A48','D-A49','D-A50','D-A51','D-A52','D-A53','D-A54','D-A55','D-A56','D-A57','D-A58','D-A59','D-A60','D-A61','D-A62','D-A63','D-A64','D-A65','D-B01','D-B02','D-B03','D-B04','D-B05','D-B06','D-B07','D-B08','D-B09','D-B10','D-B11','D-B12','D-B13','D-B14','D-B15','D-B16','D-B17','D-B18','D-B19','D-B20','D-B21','D-B22','D-B23','D-B24','D-B25','D-B26','D-B27','D-B28','D-B29','D-B30','D-B31','D-B32','D-B33','D-B34','D-B35','D-B36','D-B37','D-B38','D-B39','D-B40','D-B41','D-B42','D-B43','D-B44','D-B45','D-B46','D-B47','D-B48','D-B49','D-B50','D-B51','D-B52','D-B53','D-B54','D-B55','D-B56','D-B57','D-B58','D-B59','D-B60','D-B61','D-B62','D-B63','D-B64','D-B65','D-B66','D-C01','D-C02','D-C03','D-C04','D-C05','D-D01','D-D02','D-D03','D-D04','D-D05','D-D06','D-D07','D-D08','D-D09','D-D10','D-D11','D-D12','D-D13','D-D14','D-D15','D-D16','D-D17','D-D18','D-D19','D-D20','D-D21','D-D22','D-D23','D-D24','D-D25','D-D26','D-D27','D-D28','D-D29','D-E01','D-E02','D-E03','D-E04','D-E05','D-E06','D-E07','D-E08','D-E09','D-E10','D-E11','D-E12','D-E13','D-E14','D-E15','D-E16','D-E17','D-E18','D-E19','D-E20','D-E21','D-E22','D-E23','D-E24','D-E25','D-E26','D-E27','D-E28','D-E29','D-E30','D-E31','D-F01','D-F02','D-F03','D-F04','D-F05','D-F06','D-F07','D-F08','D-F09','D-F10','D-F11','D-F12','D-F13','D-F14','D-F15','D-F16','D-F17','D-F18','D-F19','D-F20','D-F21']
                self.button3.Hide()
                self.lblhear = wx.StaticText(self,wx.ID_ANY, label="scribe to test?", pos=(500, 20))
                self.edithear =wx.ComboBox(self,wx.ID_ANY, pos=(500, 50), size=(95, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
                self.Bind(wx.EVT_BUTTON, self.checkfunction_die,self.button1)
                self.Bind(wx.EVT_BUTTON, self.select_all_dies_only,self.button2)
                self.Bind(wx.EVT_BUTTON, self.unselect_all_dies_only,self.button4)
                self.Bind(wx.EVT_BUTTON, self.launch_test,self.button3)
                wx.StaticText(self, -1, 'wafer name', (200, 20))
                self.waferList = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25']
                self.wafername = wx.ComboBox(self,wx.ID_ANY, pos=(200, 50), size=(95, -1), choices=self.waferList, style=wx.CB_DROPDOWN)
                self.Bind(wx.EVT_COMBOBOX, self.wafer_decl,self.wafername)

    def wafer_decl(self,event):
                mon_fichier_info = open("Informations.txt", "a")
                mon_fichier_info.write('wafer name = '+ self.wafername.GetValue())
                mon_fichier_info.write("\n")
                mon_fichier_info.close()
                
    def select_all_dies_only(self,event):
                self.myCheckBox26.SetValue(True)
                self.myCheckBox27.SetValue(True)
                self.myCheckBox28.SetValue(True)
                self.myCheckBox29.SetValue(True)
                self.myCheckBox30.SetValue(True)
                self.myCheckBox31.SetValue(True)
                self.myCheckBox32.SetValue(True)
                self.myCheckBox33.SetValue(True)
                self.myCheckBox34.SetValue(True)
                self.myCheckBox35.SetValue(True)
                self.myCheckBox36.SetValue(True)
                self.myCheckBox37.SetValue(True)
                self.myCheckBox38.SetValue(True)
                self.myCheckBox39.SetValue(True)
                self.myCheckBox40.SetValue(True)
                self.myCheckBox41.SetValue(True)
                self.myCheckBox42.SetValue(True)
                self.myCheckBox43.SetValue(True)
                self.myCheckBox44.SetValue(True)
                self.myCheckBox45.SetValue(True)
                self.myCheckBox46.SetValue(True)
                self.myCheckBox47.SetValue(True)
                self.myCheckBox48.SetValue(True)
                self.myCheckBox49.SetValue(True)
                self.myCheckBox50.SetValue(True)
                self.myCheckBox51.SetValue(True)
                self.myCheckBox52.SetValue(True)
                self.myCheckBox53.SetValue(True)
                self.myCheckBox54.SetValue(True)
                self.myCheckBox55.SetValue(True)
                self.myCheckBox56.SetValue(True)
                self.myCheckBox57.SetValue(True)
                self.myCheckBox58.SetValue(True)
                self.myCheckBox59.SetValue(True)
                self.myCheckBox60.SetValue(True)
                self.myCheckBox61.SetValue(True)
                self.myCheckBox62.SetValue(True)
                self.myCheckBox63.SetValue(True)                
                self.myCheckBox52.SetValue(True)
                self.myCheckBox53.SetValue(True)
                self.myCheckBox54.SetValue(True)
                self.myCheckBox55.SetValue(True)
                self.myCheckBox56.SetValue(True)
                self.myCheckBox57.SetValue(True)
                self.myCheckBox58.SetValue(True)
                self.myCheckBox59.SetValue(True)
                self.myCheckBox60.SetValue(True)
                self.myCheckBox61.SetValue(True)
                self.myCheckBox62.SetValue(True)
                self.myCheckBox63.SetValue(True)                 
                self.myCheckBox64.SetValue(True)
                self.myCheckBox65.SetValue(True)
                self.myCheckBox66.SetValue(True)
                self.myCheckBox67.SetValue(True)
                self.myCheckBox68.SetValue(True)
                self.myCheckBox69.SetValue(True)
                self.myCheckBox70.SetValue(True)
                self.myCheckBox71.SetValue(True)
                self.myCheckBox72.SetValue(True)
                self.myCheckBox73.SetValue(True)
                self.myCheckBox74.SetValue(True)               
                self.myCheckBox75.SetValue(True)
                self.myCheckBox76.SetValue(True)
                self.myCheckBox77.SetValue(True)
                
    def unselect_all_dies_only(self,event):
                self.myCheckBox26.SetValue(False)
                self.myCheckBox27.SetValue(False)
                self.myCheckBox28.SetValue(False)
                self.myCheckBox29.SetValue(False)
                self.myCheckBox30.SetValue(False)
                self.myCheckBox31.SetValue(False)
                self.myCheckBox32.SetValue(False)
                self.myCheckBox33.SetValue(False)
                self.myCheckBox34.SetValue(False)
                self.myCheckBox35.SetValue(False)
                self.myCheckBox36.SetValue(False)
                self.myCheckBox37.SetValue(False)
                self.myCheckBox38.SetValue(False)
                self.myCheckBox39.SetValue(False)
                self.myCheckBox40.SetValue(False)
                self.myCheckBox41.SetValue(False)
                self.myCheckBox42.SetValue(False)
                self.myCheckBox43.SetValue(False)
                self.myCheckBox44.SetValue(False)
                self.myCheckBox45.SetValue(False)
                self.myCheckBox46.SetValue(False)
                self.myCheckBox47.SetValue(False)
                self.myCheckBox48.SetValue(False)
                self.myCheckBox49.SetValue(False)
                self.myCheckBox50.SetValue(False)
                self.myCheckBox51.SetValue(False)
                self.myCheckBox52.SetValue(False)
                self.myCheckBox53.SetValue(False)
                self.myCheckBox54.SetValue(False)
                self.myCheckBox55.SetValue(False)
                self.myCheckBox56.SetValue(False)
                self.myCheckBox57.SetValue(False)
                self.myCheckBox58.SetValue(False)
                self.myCheckBox59.SetValue(False)
                self.myCheckBox60.SetValue(False)
                self.myCheckBox61.SetValue(False)
                self.myCheckBox62.SetValue(False)
                self.myCheckBox63.SetValue(False)                
                self.myCheckBox52.SetValue(False)
                self.myCheckBox53.SetValue(False)
                self.myCheckBox54.SetValue(False)
                self.myCheckBox55.SetValue(False)
                self.myCheckBox56.SetValue(False)
                self.myCheckBox57.SetValue(False)
                self.myCheckBox58.SetValue(False)
                self.myCheckBox59.SetValue(False)
                self.myCheckBox60.SetValue(False)
                self.myCheckBox61.SetValue(False)
                self.myCheckBox62.SetValue(False)
                self.myCheckBox63.SetValue(False)
                self.myCheckBox64.SetValue(False)
                self.myCheckBox65.SetValue(False)
                self.myCheckBox66.SetValue(False)
                self.myCheckBox67.SetValue(False)
                self.myCheckBox68.SetValue(False)
                self.myCheckBox69.SetValue(False)
                self.myCheckBox70.SetValue(False)
                self.myCheckBox71.SetValue(False)
                self.myCheckBox72.SetValue(False)
                self.myCheckBox73.SetValue(False)
                self.myCheckBox74.SetValue(False)
                self.myCheckBox75.SetValue(False)
                self.myCheckBox76.SetValue(False)
                self.myCheckBox77.SetValue(False)
                                
    def checkfunction_die(self,event):
        mon_fichier_die = open("DUT.txt", "w") 
        self.barrette = self.edithear.GetValue()
        print self.barrette
        mon_fichier_die.write(self.barrette)
        mon_fichier_die.write("\n")
################          Mon_fichier_die = open("DUT.txt", "w")                  #############################################
        if self.myCheckBox26.IsChecked()==True :
            print "2   1"
            mon_fichier_die.write("2   1\n")            
        if self.myCheckBox27.IsChecked()==True :
            print "3   1"
            mon_fichier_die.write("3   1\n")
        if self.myCheckBox28.IsChecked()==True :
            print "4   1"
            mon_fichier_die.write("4   1\n")
        if self.myCheckBox29.IsChecked()==True :
            print "5   1"
            mon_fichier_die.write("5   1\n")
        if self.myCheckBox30.IsChecked()==True :
            print "1   2"
            mon_fichier_die.write("1   2\n")
        if self.myCheckBox31.IsChecked()==True :
            print "2   2"
            mon_fichier_die.write("2   2\n")
        if self.myCheckBox32.IsChecked()==True :
            print "3   2"
            mon_fichier_die.write("3   2\n")
        if self.myCheckBox33.IsChecked()==True :
            print "4   2"
            mon_fichier_die.write("4   2\n")
        if self.myCheckBox34.IsChecked()==True :
            print "5   2" 
            mon_fichier_die.write("5   2\n")
        if self.myCheckBox35.IsChecked()==True :
            print "6   2"
            mon_fichier_die.write("6   2\n")
        if self.myCheckBox36.IsChecked()==True :
            print "-1  3"
            mon_fichier_die.write("-1   3\n")
        if self.myCheckBox37.IsChecked()==True :
            print "1   3"
            mon_fichier_die.write("1   3\n")
        if self.myCheckBox38.IsChecked()==True :
            print "2   3"
            mon_fichier_die.write("2   3\n")
        if self.myCheckBox39.IsChecked()==True :
            print "3   3"
            mon_fichier_die.write("3   3\n")
        if self.myCheckBox40.IsChecked()==True :
            print "4   3"
            mon_fichier_die.write("4   3\n")
        if self.myCheckBox41.IsChecked()==True :
            print "5   3"
            mon_fichier_die.write("5   3\n")
        if self.myCheckBox42.IsChecked()==True :
            print "6   3"
            mon_fichier_die.write("6   3\n")
        if self.myCheckBox43.IsChecked()==True :
            print "7   3"
            mon_fichier_die.write("7   3\n")
        if self.myCheckBox44.IsChecked()==True :
            print "-1  4"
            mon_fichier_die.write("-1   4\n")
        if self.myCheckBox45.IsChecked()==True :
            print "1   4"
            mon_fichier_die.write("1   4\n")            
        if self.myCheckBox46.IsChecked()==True :
            print "2   4"
            mon_fichier_die.write("2   4\n")
        if self.myCheckBox47.IsChecked()==True :
            print "3   4"
            mon_fichier_die.write("3   4\n")
        if self.myCheckBox48.IsChecked()==True :
            print "4   4"
            mon_fichier_die.write("4   4\n")
        if self.myCheckBox49.IsChecked()==True :
            print "5   4"
            mon_fichier_die.write("5   4\n")
        if self.myCheckBox50.IsChecked()==True :        
            print "6   4"
            mon_fichier_die.write("6   4\n")
        if self.myCheckBox51.IsChecked()==True :        
            print "7   4"            
            mon_fichier_die.write("7   4\n")
        if self.myCheckBox52.IsChecked()==True :        
            print "-1  5"            
            mon_fichier_die.write("-1   5\n")
        if self.myCheckBox53.IsChecked()==True :        
            print "1   5"            
            mon_fichier_die.write("1   5\n")
        if self.myCheckBox54.IsChecked()==True :        
            print "2   5"            
            mon_fichier_die.write("2   5\n")
        if self.myCheckBox55.IsChecked()==True :        
            print "3   5"            
            mon_fichier_die.write("3   5\n")
        if self.myCheckBox56.IsChecked()==True :        
            print "4   5"            
            mon_fichier_die.write("4   5\n")
        if self.myCheckBox57.IsChecked()==True :        
            print "5   5"            
            mon_fichier_die.write("5   5\n")
        if self.myCheckBox58.IsChecked()==True :        
            print "6   5"            
            mon_fichier_die.write("6   5\n")
        if self.myCheckBox59.IsChecked()==True :        
            print "7   5"            
            mon_fichier_die.write("7   5\n")
        if self.myCheckBox60.IsChecked()==True :        
            print "-1   6"            
            mon_fichier_die.write("-1   6\n")
        if self.myCheckBox61.IsChecked()==True :        
            print "1    6"            
            mon_fichier_die.write("1   6\n")
        if self.myCheckBox62.IsChecked()==True :        
            print "2   6"            
            mon_fichier_die.write("2   6\n")
        if self.myCheckBox63.IsChecked()==True :        
            print "3   6"            
            mon_fichier_die.write("3   6\n")
        if self.myCheckBox64.IsChecked()==True :        
            print "4   6"            
            mon_fichier_die.write("4   6\n")
        if self.myCheckBox65.IsChecked()==True :        
            print "5   6"            
            mon_fichier_die.write("5   6\n")
        if self.myCheckBox66.IsChecked()==True :        
            print "6   6"            
            mon_fichier_die.write("6   6\n")
        if self.myCheckBox67.IsChecked()==True :        
            print "7   6"            
            mon_fichier_die.write("7   6\n")
        if self.myCheckBox68.IsChecked()==True :        
            print "1   7"            
            mon_fichier_die.write("1   7\n")
        if self.myCheckBox69.IsChecked()==True :        
            print "2   7"            
            mon_fichier_die.write("2   7\n")
        if self.myCheckBox70.IsChecked()==True :        
            print "3   7"            
            mon_fichier_die.write("3   7\n")
        if self.myCheckBox71.IsChecked()==True :        
            print "4   7"            
            mon_fichier_die.write("4   7\n")
        if self.myCheckBox72.IsChecked()==True :        
            print "5   7"            
            mon_fichier_die.write("5   7\n")
        if self.myCheckBox73.IsChecked()==True :        
            print "6   7"            
            mon_fichier_die.write("6   7\n")
        if self.myCheckBox74.IsChecked()==True :        
            print "2   8"            
            mon_fichier_die.write("2   8\n")
        if self.myCheckBox75.IsChecked()==True :        
            print "3   8"            
            mon_fichier_die.write("3   8\n")
        if self.myCheckBox76.IsChecked()==True :        
            print "4   8"            
            mon_fichier_die.write("4   8\n")
        if self.myCheckBox77.IsChecked()==True :        
            print "5   8"            
            mon_fichier_die.write("5   8\n")
        if self.edithear.GetValue()!=""        :
            if self.wafername.GetValue()!=""        :
                if self.myCheckBox26.GetValue()|self.myCheckBox27.GetValue()|self.myCheckBox28.GetValue()|self.myCheckBox29.GetValue()|self.myCheckBox30.IsChecked()|self.myCheckBox31.IsChecked()|self.myCheckBox32.IsChecked()|self.myCheckBox33.IsChecked()|self.myCheckBox34.IsChecked()|self.myCheckBox35.IsChecked()|self.myCheckBox36.IsChecked()|self.myCheckBox37.IsChecked()|self.myCheckBox38.IsChecked()|self.myCheckBox39.IsChecked()|self.myCheckBox40.IsChecked()|self.myCheckBox41.IsChecked()|self.myCheckBox42.IsChecked()|self.myCheckBox43.IsChecked()|self.myCheckBox44.IsChecked()|self.myCheckBox45.IsChecked()|self.myCheckBox46.IsChecked()|self.myCheckBox47.IsChecked()|self.myCheckBox48.IsChecked()|self.myCheckBox49.IsChecked()|self.myCheckBox50.IsChecked()|self.myCheckBox51.IsChecked()|self.myCheckBox52.IsChecked()|self.myCheckBox53.IsChecked()|self.myCheckBox54.IsChecked()|self.myCheckBox55.IsChecked()|self.myCheckBox56.IsChecked()|self.myCheckBox57.IsChecked()|self.myCheckBox58.IsChecked()|self.myCheckBox59.IsChecked()|self.myCheckBox60.IsChecked()|self.myCheckBox61.IsChecked()|self.myCheckBox62.IsChecked()|self.myCheckBox63.IsChecked()|self.myCheckBox64.IsChecked()|self.myCheckBox65.IsChecked()|self.myCheckBox66.IsChecked()|self.myCheckBox67.IsChecked()|self.myCheckBox68.IsChecked()|self.myCheckBox69.IsChecked()|self.myCheckBox70.IsChecked()|self.myCheckBox71.IsChecked()|self.myCheckBox72.IsChecked()|self.myCheckBox73.IsChecked()|self.myCheckBox74.IsChecked()|self.myCheckBox75.IsChecked()|self.myCheckBox76.IsChecked()|self.myCheckBox77.IsChecked()==True:
                    self.button3.Show()
                
        mon_fichier_die.close()        
        
        
        
    def launch_test(self,event):
        driver_electroglas.manual_load()
        print "Test en mode manuel"
    def ShowMessage(self):
        wx.MessageBox('Load Manually Wafer On Tray and wait until it is READY!!!!', 'WARNING!!!', wx.OK | wx.ICON_INFORMATION) 

class pageThree (wx.Panel):
        def __init__ (self,parent):
                wx.Panel.__init__ (self,parent,wx.ID_ANY,size=(1,1))
                wx.FutureCall(5000, self.ShowMessage)
                self.sizememorytext = wx.StaticText(self, -1, 'size of memory', (100, 20))
                self.memoryList2 = ['256bit','256bit Kelvin','4kbit NNN','4kbit KTT','4kbit PRKN','64kbit panache','1Mbit simple','VRAM']
                self.sizeMemory2 = wx.ComboBox(self,wx.ID_ANY, pos=(100, 50), size=(120, -1), choices=self.memoryList2, style=wx.CB_DROPDOWN)

                delta=60                
                Width=120
                Width1=Width+delta        #160
                Width2=Width1+delta       #200
                Width3=Width2+delta       #240
                Width4=Width3+delta       #280
                Width5=Width4+delta       #320
                Width6=Width5+delta       #360
                Width7=Width6+delta       #400

                self.panel = wx.Panel(self)
                                         
                self.wafer = wx.StaticText(self,wx.ID_ANY, label="SELECT ONLY ONE DIE TO TEST(the other ones are not probed)", pos=(Width2, 180))             
                self.myCheckBox26 = wx.RadioButton (self,wx.ID_ANY,label="2  1",pos= (Width2 , 340), size=(-1,-1),style = wx.RB_GROUP)       
                self.myCheckBox27 = wx.RadioButton (self,wx.ID_ANY,label="3  1",pos= (Width3 , 340), size=(-1,-1))
                self.myCheckBox28 = wx.RadioButton (self,wx.ID_ANY,label="4  1",pos= (Width4 , 340), size=(-1,-1))
                self.myCheckBox29 = wx.RadioButton (self,wx.ID_ANY,label="5  1",pos= (Width5 , 340), size=(-1,-1))       
                self.myCheckBox30 = wx.RadioButton (self,wx.ID_ANY,label="1  2",pos= (Width1 , 320), size=(-1,-1))     
                self.myCheckBox31 = wx.RadioButton (self,wx.ID_ANY,label="2  2",pos= (Width2 , 320), size=(-1,-1))
                self.myCheckBox32 = wx.RadioButton (self,wx.ID_ANY,label="3  2",pos= (Width3 , 320), size=(-1,-1))
                self.myCheckBox33 = wx.RadioButton (self,wx.ID_ANY,label="4  2",pos= (Width4 , 320), size=(-1,-1))      
                self.myCheckBox34 = wx.RadioButton (self,wx.ID_ANY,label="5  2",pos= (Width5 , 320), size=(-1,-1))
                self.myCheckBox35 = wx.RadioButton (self,wx.ID_ANY,label="6  2",pos= (Width6 , 320), size=(-1,-1))      
                self.myCheckBox36 = wx.RadioButton (self,wx.ID_ANY,label="-1  3",pos= (Width , 300), size=(-1,-1))
                self.myCheckBox37 = wx.RadioButton (self,wx.ID_ANY,label="1  3",pos= (Width1 , 300), size=(-1,-1))     
                self.myCheckBox38 = wx.RadioButton (self,wx.ID_ANY,label="2  3",pos= (Width2 , 300), size=(-1,-1))
                self.myCheckBox39 = wx.RadioButton (self,wx.ID_ANY,label="3  3",pos= (Width3 , 300), size=(-1,-1))
                self.myCheckBox40 = wx.RadioButton (self,wx.ID_ANY,label="4  3",pos= (Width4 , 300), size=(-1,-1))      
                self.myCheckBox41 = wx.RadioButton (self,wx.ID_ANY,label="5  3",pos= (Width5 , 300), size=(-1,-1))
                self.myCheckBox42 = wx.RadioButton (self,wx.ID_ANY,label="6  3",pos= (Width6 , 300), size=(-1,-1))
                self.myCheckBox43 = wx.RadioButton (self,wx.ID_ANY,label="7  3",pos= (Width7 , 300), size=(-1,-1)) 
                self.myCheckBox44 = wx.RadioButton (self,wx.ID_ANY,label="-1  4",pos= (Width , 280), size=(-1,-1))
                self.myCheckBox45 = wx.RadioButton (self,wx.ID_ANY,label="1  4",pos= (Width1 , 280), size=(-1,-1))     
                self.myCheckBox46 = wx.RadioButton (self,wx.ID_ANY,label="2  4",pos= (Width2 , 280), size=(-1,-1))
                self.myCheckBox47 = wx.RadioButton (self,wx.ID_ANY,label="3  4",pos= (Width3 , 280), size=(-1,-1))
                self.myCheckBox48 = wx.RadioButton (self,wx.ID_ANY,label="4  4",pos= (Width4 , 280), size=(-1,-1))      
                self.myCheckBox49 = wx.RadioButton (self,wx.ID_ANY,label="5  4",pos= (Width5 , 280), size=(-1,-1))
                self.myCheckBox50 = wx.RadioButton (self,wx.ID_ANY,label="6  4",pos= (Width6 , 280), size=(-1,-1))
                self.myCheckBox51 = wx.RadioButton (self,wx.ID_ANY,label="7  4",pos= (Width7 , 280), size=(-1,-1)) 
                self.myCheckBox52 = wx.RadioButton (self,wx.ID_ANY,label="-1  5",pos= (Width , 260), size=(-1,-1))
                self.myCheckBox53 = wx.RadioButton (self,wx.ID_ANY,label="1  5",pos= (Width1 , 260), size=(-1,-1))     
                self.myCheckBox54 = wx.RadioButton (self,wx.ID_ANY,label="2  5",pos= (Width2 , 260), size=(-1,-1))
                self.myCheckBox55 = wx.RadioButton (self,wx.ID_ANY,label="3  5",pos= (Width3 , 260), size=(-1,-1))
                self.myCheckBox56 = wx.RadioButton (self,wx.ID_ANY,label="4  5",pos= (Width4 , 260), size=(-1,-1))      
                self.myCheckBox57 = wx.RadioButton (self,wx.ID_ANY,label="5  5",pos= (Width5 , 260), size=(-1,-1))
                self.myCheckBox58 = wx.RadioButton (self,wx.ID_ANY,label="6  5",pos= (Width6 , 260), size=(-1,-1))
                self.myCheckBox59 = wx.RadioButton (self,wx.ID_ANY,label="7  5",pos= (Width7 , 260), size=(-1,-1)) 
                self.myCheckBox60 = wx.RadioButton (self,wx.ID_ANY,label="-1  6",pos= (Width , 240), size=(-1,-1))
                self.myCheckBox61 = wx.RadioButton (self,wx.ID_ANY,label="1  6",pos= (Width1 , 240), size=(-1,-1))     
                self.myCheckBox62 = wx.RadioButton (self,wx.ID_ANY,label="2  6",pos= (Width2 , 240), size=(-1,-1))
                self.myCheckBox63 = wx.RadioButton (self,wx.ID_ANY,label="3  6",pos= (Width3 , 240), size=(-1,-1))
                self.myCheckBox64 = wx.RadioButton (self,wx.ID_ANY,label="4  6",pos= (Width4 , 240), size=(-1,-1))      
                self.myCheckBox65 = wx.RadioButton (self,wx.ID_ANY,label="5  6",pos= (Width5 , 240), size=(-1,-1))
                self.myCheckBox66 = wx.RadioButton (self,wx.ID_ANY,label="6  6",pos= (Width6 , 240), size=(-1,-1))
                self.myCheckBox67 = wx.RadioButton (self,wx.ID_ANY,label="7  6",pos= (Width7 , 240), size=(-1,-1)) 
                self.myCheckBox68 = wx.RadioButton (self,wx.ID_ANY,label="1  7",pos= (Width1 , 220), size=(-1,-1))     
                self.myCheckBox69 = wx.RadioButton (self,wx.ID_ANY,label="2  7",pos= (Width2 , 220), size=(-1,-1))
                self.myCheckBox70 = wx.RadioButton (self,wx.ID_ANY,label="3  7",pos= (Width3 , 220), size=(-1,-1))
                self.myCheckBox71 = wx.RadioButton (self,wx.ID_ANY,label="4  7",pos= (Width4 , 220), size=(-1,-1))      
                self.myCheckBox72 = wx.RadioButton (self,wx.ID_ANY,label="5  7",pos= (Width5 , 220), size=(-1,-1))
                self.myCheckBox73 = wx.RadioButton (self,wx.ID_ANY,label="6  7",pos= (Width6 , 220), size=(-1,-1))     
                self.myCheckBox74 = wx.RadioButton (self,wx.ID_ANY,label="2  8",pos= (Width2 , 200), size=(-1,-1))
                self.myCheckBox75 = wx.RadioButton (self,wx.ID_ANY,label="3  8",pos= (Width3 , 200), size=(-1,-1))
                self.myCheckBox76 = wx.RadioButton (self,wx.ID_ANY,label="4  8",pos= (Width4 , 200), size=(-1,-1))      
                self.myCheckBox77 = wx.RadioButton (self,wx.ID_ANY,label="5  8",pos= (Width5 , 200), size=(-1,-1))

                self.button1=wx.Button (self,wx.ID_ANY,label="SELECT BARETTE & DIE",pos=(200,400),size=(200,30)) 
                self.button5=wx.Button (self,wx.ID_ANY,label="UNLOAD WAFER",pos=(400,400),size=(200,30))
                self.button2=wx.Button (self,wx.ID_ANY,label="CHUCK UP",pos=(200,430),size=(200,30)) 
                self.button4=wx.Button (self,wx.ID_ANY,label="CHUCK DOWN",pos=(400,430),size=(200,30)) 
                self.button3=wx.Button (self,wx.ID_ANY,label="GO TO DIE AND BARRETTE",pos=(200,460),size=(200,30))
                self.button6=wx.Button (self,wx.ID_ANY,label="PROFILE and ALIGNEMENT",pos=(200,490),size=(200,30))
                #self.button6=wx.Button (self,wx.ID_ANY,label="ALIGNEMENT",pos=(200,490),size=(200,30))
           
                
#                self.sampleList = ['A-A01','A-A02','A-A03','A-A04','A-A05','A-A06','A-A07','A-A08','A-A09','A-A10','A-A11','A-A12','A-A13','A-A14','A-A15','A-A16','A-A17','A-A18','A-A19','A-A20','A-A21','A-A22','A-A23','A-A24','A-A25','A-A26','A-A27','A-A28','A-A29','A-A30','A-A31','A-A32','A-A33','A-A34','A-A35','A-A36','A-A37','A-A38','A-A39','A-A40','A-A41','A-A42','A-A43','A-A44','A-A45','A-A46','A-A47','A-A48','A-A49','A-A50','A-A51','A-A52','A-A53','A-A54','A-A55','A-A56','A-A57','A-A58','A-A59','A-A60','A-A61','A-A62','A-A63','A-A64','A-B01','A-B02','A-B03','A-B04','A-B05','A-B06','A-B07','A-B08','A-B09','A-B10','A-B11','A-B12','A-B13','A-B14','A-B15','A-B16','A-B17','A-B18','A-B19','A-B20','A-B21','A-B22','A-B23','A-B24','A-B25','A-B26','A-B27','A-B28','A-B29','A-B30','A-B31','A-B32','A-B33','A-B34','A-B35','A-B36','A-B37','A-B38','A-B39','A-B40','A-B41','A-B42','A-B43','A-B44','A-B45','A-B46','A-B47','A-B48','A-B49','A-B50','A-B51','A-B52','A-B53','A-B54','A-B55','A-B56','A-B57','A-B58','A-B59','A-B60','A-B61','A-B62','A-B63','A-B64','A-B65','A-B66','A-C01','A-C02','A-C03','A-C04','A-C05','A-D01','A-D02','A-D03','A-D04','A-D05','A-D06','A-D07','A-D08','A-D09','A-D10','A-D11','A-D12','A-D13','A-D14','A-D15','A-D16','A-D17','A-D18','A-D19','A-D20','A-D21','A-D22','A-D23','A-D24','A-D25','A-D26','A-D27','A-D28','A-D29','A-E01','A-E02','A-E03','A-E04','A-E05','A-E06','A-E07','A-E08','A-E09','A-E10','A-E11','A-E12','A-E13','A-E14','A-E15','A-E16','A-E17','A-E18','A-E19','A-E20','A-E21','A-E22','A-E23','A-E24','A-E25','A-E26','A-E27','A-E28','A-E29','A-E30','A-E31','A-F01','A-F02','A-F03','A-F04','A-F05','A-F06','A-F07','A-F08','A-F09','A-F10','A-F11','A-F12','A-F13','A-F14','A-F15','A-F16','A-F17','A-F18','A-F19','A-F20','A-F21','D-A01','D-A02','D-A03','D-A04','D-A05','D-A06','D-A07','D-A08','D-A09','D-A10','D-A11','D-A12','D-A13','D-A14','D-A15','D-A16','D-A17','D-A18','D-A19','D-A20','D-A21','D-A22','D-A23','D-A24','D-A25','D-A26','D-A27','D-A28','D-A29','D-A30','D-A31','D-A32','D-A33','D-A34','D-A35','D-A36','D-A37','D-A38','D-A39','D-A40','D-A41','D-A42','D-A43','D-A44','D-A45','D-A46','D-A47','D-A48','D-A49','D-A50','D-A51','D-A52','D-A53','D-A54','D-A55','D-A56','D-A57','D-A58','D-A59','D-A60','D-A61','D-A62','D-A63','D-A64','D-A65','D-B01','D-B02','D-B03','D-B04','D-B05','D-B06','D-B07','D-B08','D-B09','D-B10','D-B11','D-B12','D-B13','D-B14','D-B15','D-B16','D-B17','D-B18','D-B19','D-B20','D-B21','D-B22','D-B23','D-B24','D-B25','D-B26','D-B27','D-B28','D-B29','D-B30','D-B31','D-B32','D-B33','D-B34','D-B35','D-B36','D-B37','D-B38','D-B39','D-B40','D-B41','D-B42','D-B43','D-B44','D-B45','D-B46','D-B47','D-B48','D-B49','D-B50','D-B51','D-B52','D-B53','D-B54','D-B55','D-B56','D-B57','D-B58','D-B59','D-B60','D-B61','D-B62','D-B63','D-B64','D-B65','D-B66','D-C01','D-C02','D-C03','D-C04','D-C05','D-D01','D-D02','D-D03','D-D04','D-D05','D-D06','D-D07','D-D08','D-D09','D-D10','D-D11','D-D12','D-D13','D-D14','D-D15','D-D16','D-D17','D-D18','D-D19','D-D20','D-D21','D-D22','D-D23','D-D24','D-D25','D-D26','D-D27','D-D28','D-D29','D-E01','D-E02','D-E03','D-E04','D-E05','D-E06','D-E07','D-E08','D-E09','D-E10','D-E11','D-E12','D-E13','D-E14','D-E15','D-E16','D-E17','D-E18','D-E19','D-E20','D-E21','D-E22','D-E23','D-E24','D-E25','D-E26','D-E27','D-E28','D-E29','D-E30','D-E31','D-F01','D-F02','D-F03','D-F04','D-F05','D-F06','D-F07','D-F08','D-F09','D-F10','D-F11','D-F12','D-F13','D-F14','D-F15','D-F16','D-F17','D-F18','D-F19','D-F20','D-F21']
                self.button1.Hide()
                self.button3.Hide()
                self.button5.Hide()
                self.button2.Hide()
                self.button4.Hide()
                self.sizememorytext.Hide()
                self.sizeMemory2.Hide()
#                self.lblhear = wx.StaticText(self,wx.ID_ANY, label="scribe to test?", pos=(300, 20))
#                self.edithear =wx.ComboBox(self,wx.ID_ANY, pos=(300, 50), size=(95, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)

                self.Bind(wx.EVT_BUTTON, self.checkfunction_die,self.button1)
                self.Bind(wx.EVT_BUTTON, self.unload_wafer,self.button5)
                self.Bind(wx.EVT_BUTTON, self.chuck_up,self.button2)
                self.Bind(wx.EVT_BUTTON, self.chuck_down,self.button4)
                self.Bind(wx.EVT_BUTTON, self.go_to_subsite,self.button3)
                self.Bind(wx.EVT_BUTTON, self.align_and_profile,self.button6)
                
                self.Bind(wx.EVT_COMBOBOX,self.refresh_selection,self.sizeMemory2)

                print (self.sizeMemory2.GetValue())

                self.selectscribe = wx.StaticText(self, -1, 'Select Scribe', (400, 20))
                self.sampleList = ['A-D26','A-D27','A-D28','A-D29','D-D26','D-D27','D-D28','D-D29']
                self.edithear =wx.ComboBox(self ,wx.ID_ANY, pos=(400, 50), size=(95, -1), choices=self.sampleList, style=wx.CB_DROPDOWN) 
                self.Bind(wx.EVT_COMBOBOX,self.checkfunction_die,self.edithear)
                self.selectscribe.Hide()
                self.edithear.Hide()

        def refresh_selection(self,event):
                self.button1.Hide()
                self.button3.Hide()
                self.button5.Hide()
                self.button2.Hide()
                self.button4.Hide()
                
                print (self.sizeMemory2.GetValue())
                self.edithear.Clear()
                if self.sizeMemory2.GetValue()=='256bit':
                    self.edithear.Clear()
                    self.edithear.Append('A-D26')
                    self.edithear.Append('A-D27')
                    self.edithear.Append('A-D28')
                    self.edithear.Append('A-D29')                    
                    self.edithear.Append('D-D26')
                    self.edithear.Append('D-D27')                    
                    self.edithear.Append('D-D28')
                    self.edithear.Append('D-D29')   
              
                    
                if self.sizeMemory2.GetValue()=='256bit Kelvin':
                    self.edithear.Clear()
                    self.edithear.Append('A-C01')
                    self.edithear.Append('A-C02')
                    self.edithear.Append('D-C01')
                    self.edithear.Append('D-C02')
                    
                if self.sizeMemory2.GetValue()=='4kbit NNN':                    
                    self.edithear.Clear()
                    self.edithear.Append('A-D09')
                    self.edithear.Append('A-D10')
                    self.edithear.Append('A-D11')
                    self.edithear.Append('A-D12')                    
                    self.edithear.Append('A-D13')
                    self.edithear.Append('A-D14')
                    self.edithear.Append('A-D15')
                    self.edithear.Append('A-D16')                    
                    self.edithear.Append('A-D17')
                    self.edithear.Append('A-D18')
                    self.edithear.Append('A-A19')
                    self.edithear.Append('A-A20')   
                    self.edithear.Append('D-D10')
                    self.edithear.Append('D-D11')
                    self.edithear.Append('D-D12')                    
                    self.edithear.Append('D-D13')
                    self.edithear.Append('D-D14')
                    self.edithear.Append('D-D15')
                    self.edithear.Append('D-D16')                    
                    self.edithear.Append('D-D17')
                    self.edithear.Append('D-D18')
                    self.edithear.Append('D-A19')
                    self.edithear.Append('D-A20') 
                    
                if self.sizeMemory2.GetValue()=='4kbit KTT':                    
                    self.edithear.Clear()
                    self.edithear.Append('A-D01')
                    self.edithear.Append('A-D02')
                    self.edithear.Append('A-D03')
                    self.edithear.Append('A-D04')                    
                    self.edithear.Append('A-D05')
                    self.edithear.Append('A-D06')
                    self.edithear.Append('A-D07')
                    self.edithear.Append('A-D08')                    
                    self.edithear.Append('D-D01')
                    self.edithear.Append('D-D02')
                    self.edithear.Append('D-D03')
                    self.edithear.Append('D-D04')                    
                    self.edithear.Append('D-D05')
                    self.edithear.Append('D-D06')
                    self.edithear.Append('D-D07')
                    self.edithear.Append('D-D08')

                if self.sizeMemory2.GetValue()=='4kbit PRKN':
                    self.edithear.Clear()
                    self.edithear.Append('A-D21')
                    self.edithear.Append('A-D22')
                    self.edithear.Append('A-D23')
                    self.edithear.Append('A-D24')                    
                    self.edithear.Append('A-D25')                   
                    self.edithear.Append('D-D21')
                    self.edithear.Append('D-D22')
                    self.edithear.Append('D-D23')
                    self.edithear.Append('D-D24')                    
                    self.edithear.Append('D-D25')
                    self.edithear.Append('D-D26')
                    self.edithear.Append('D-D27')
                    self.edithear.Append('D-D28')

                if self.sizeMemory2.GetValue()=='64kbit panache':
                    self.edithear.Clear()
                    self.edithear.Append('A-C03')
                    self.edithear.Append('A-C03bis')
                    self.edithear.Append('D-C03')
                    self.edithear.Append('D-C03bis')                    

                if self.sizeMemory2.GetValue()=='1Mbit simple':
                    self.edithear.Clear()
                    self.edithear.Append('A-C04')
                    self.edithear.Append('A-C05')
                    self.edithear.Append('D-C04')
                    self.edithear.Append('D-C05')

                if self.sizeMemory2.GetValue()=='VRAM':
                    self.edithear.Clear()
                    self.edithear.Append('A-A55')
                    self.edithear.Append('A-A56')
                    self.edithear.Append('A-A57')
                    self.edithear.Append('A-A58')
                    self.edithear.Append('A-A59')
                    self.edithear.Append('A-A60')
                    self.edithear.Append('A-A61')
                    self.edithear.Append('A-A62')
                    self.edithear.Append('A-A63')
                    self.edithear.Append('A-A64')
                    self.edithear.Append('A-D55')                    
                    self.edithear.Append('A-D56')
                    self.edithear.Append('A-D57')
                    self.edithear.Append('A-D58')
                    self.edithear.Append('A-D59')
                    self.edithear.Append('A-D60')
                    self.edithear.Append('A-D61')
                    self.edithear.Append('A-D62')
                    self.edithear.Append('A-D63')
                    self.edithear.Append('A-D64')                

        def checkfunction_die(self,event):
            
            self.barrette = self.edithear.GetValue()
            print self.barrette
    ################          Mon_fichier_die = open("DUT.txt", "w")                  #############################################
            if self.myCheckBox26.GetValue()==True :
                print "2   1"
                self.x = 2
                self.y = 1                               
            if self.myCheckBox27.GetValue()==True :
                print "3   1"
                self.x = 3
                self.y = 1

            if self.myCheckBox28.GetValue()==True :
                print "4   1"
                self.x = 4
                self.y = 1
                
            if self.myCheckBox29.GetValue()==True :
                print "5   1"
                self.x = 5
                self.y = 1
                
            if self.myCheckBox30.GetValue()==True :
                print "1   2"
                self.x = 1
                self.y = 2

            if self.myCheckBox31.GetValue()==True :
                print "2   2"
                self.x = 2
                self.y = 2
                
            if self.myCheckBox32.GetValue()==True :
                print "3   2"
                self.x = 3
                self.y = 2
                
            if self.myCheckBox33.GetValue()==True :
                print "4   2"
                self.x = 4
                self.y = 2
                
            if self.myCheckBox34.GetValue()==True :
                print "5   2" 
                self.x = 5
                self.y = 2
                
            if self.myCheckBox35.GetValue()==True :
                print "6   2"
                self.x = 6
                self.y = 2
                
            if self.myCheckBox36.GetValue()==True :
                print "-1  3"
                self.x = -1
                self.y = 3

            if self.myCheckBox37.GetValue()==True :
                print "1   3"
                self.x = 1
                self.y = 3
                
            if self.myCheckBox38.GetValue()==True :
                print "2   3"
                self.x = 2
                self.y = 3
                
            if self.myCheckBox39.GetValue()==True :
                print "3   3"
                self.x = 3
                self.y = 3
                
            if self.myCheckBox40.GetValue()==True :
                print "4   3"
                self.x = 4
                self.y = 3
                
            if self.myCheckBox41.GetValue()==True :
                print "5   3"
                self.x = 5
                self.y = 3
                
            if self.myCheckBox42.GetValue()==True :
                print "6   3"
                self.x = 6
                self.y = 3
                
            if self.myCheckBox43.GetValue()==True :
                print "7   3"
                self.x = 7
                self.y = 3
                
            if self.myCheckBox44.GetValue()==True :
                print "-1  4"
                self.x = -1
                self.y = 4
                
            if self.myCheckBox45.GetValue()==True :
                print "1   4"
                self.x = 1
                self.y = 4
          
            if self.myCheckBox46.GetValue()==True :
                print "2   4"
                self.x = 2
                self.y = 4

            if self.myCheckBox47.GetValue()==True :
                print "3   4"
                self.x = 3
                self.y = 4

            if self.myCheckBox48.GetValue()==True :
                print "4   4"
                self.x = 4
                self.y = 4

            if self.myCheckBox49.GetValue()==True :
                print "5   4"
                self.x = 5
                self.y = 4
                
            if self.myCheckBox50.GetValue()==True :        
                print "6   4"
                self.x = 6
                self.y = 4

            if self.myCheckBox51.GetValue()==True :        
                print "7   4"            
                self.x = 7
                self.y = 4
                
            if self.myCheckBox52.GetValue()==True :        
                print "-1  5"            
                self.x = -1
                self.y = 5
                
            if self.myCheckBox53.GetValue()==True :        
                print "1   5"            
                self.x = 1
                self.y = 5

            if self.myCheckBox54.GetValue()==True :        
                print "2   5"            
                self.x = 2
                self.y = 5

            if self.myCheckBox55.GetValue()==True :        
                print "3   5"            
                self.x = 3
                self.y = 5

            if self.myCheckBox56.GetValue()==True :        
                print "4   5"            
                self.x = 4
                self.y = 5

            if self.myCheckBox57.GetValue()==True :        
                print "5   5"            
                self.x = 5
                self.y = 5

            if self.myCheckBox58.GetValue()==True :        
                print "6   5"            
                self.x = 6
                self.y = 5

            if self.myCheckBox59.GetValue()==True :        
                print "7   5"            
                self.x = 7
                self.y = 5

            if self.myCheckBox60.GetValue()==True :        
                print "-1   6"            
                self.x = -1
                self.y = 6

            if self.myCheckBox61.GetValue()==True :        
                print "1    6"            
                self.x = 1
                self.y = 6

            if self.myCheckBox62.GetValue()==True :        
                print "2   6"            
                self.x = 2
                self.y = 6

            if self.myCheckBox63.GetValue()==True :        
                print "3   6"            
                self.x = 3
                self.y = 6

            if self.myCheckBox64.GetValue()==True :        
                print "4   6"            
                self.x = 4
                self.y = 6

            if self.myCheckBox65.GetValue()==True :        
                print "5   6"            
                self.x = 5
                self.y = 6

            if self.myCheckBox66.GetValue()==True :        
                print "6   6"            
                self.x = 6
                self.y = 6

            if self.myCheckBox67.GetValue()==True :        
                print "7   6"            
                self.x = 7
                self.y = 6

            if self.myCheckBox68.GetValue()==True :        
                print "1   7"            
                self.x = 1
                self.y = 7

            if self.myCheckBox69.GetValue()==True :        
                print "2   7"            
                self.x = 2
                self.y = 7

            if self.myCheckBox70.GetValue()==True :        
                print "3   7"            
                self.x = 3
                self.y = 7

            if self.myCheckBox71.GetValue()==True :        
                print "4   7"            
                self.x = 4
                self.y = 7

            if self.myCheckBox72.GetValue()==True :        
                print "5   7"            
                self.x = 5
                self.y = 7

            if self.myCheckBox73.GetValue()==True :        
                print "6   7"            
                self.x = 6
                self.y = 7

            if self.myCheckBox74.GetValue()==True :        
                print "2   8"            
                self.x = 2
                self.y = 8

            if self.myCheckBox75.GetValue()==True :        
                print "3   8"            
                self.x = 3
                self.y = 8

            if self.myCheckBox76.GetValue()==True :        
                print "4   8"            
                self.x = 4
                self.y = 8

            if self.myCheckBox77.GetValue()==True :        
                print "5   8"            
                self.x = 5
                self.y = 8

            self.button1.Show()
            self.button3.Show()
            self.button5.Show()
            #self.button2.Show()
            self.button4.Show()
      
            
            
            
        def go_to_subsite(self,event):
            import visa
            rm=visa.ResourceManager()
            electroglas=rm.open_resource("GPIB::2")
            print "barrette = "+ self.barrette
            print "x ="+ str(self.x)
            print "y ="+ str(self.y)
            electroglas.write("MF;SP10000")
            while electroglas.query("?P")!=u'X1Y1\r\n':
                electroglas.query("?P")
            electroglas.query("?P")
            electroglas.query("?P")
            barrette=self.barrette
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
                    electroglas.query("?H")
                    electroglas.query("?H")
                    print electroglas.query("?H")
            fichier.close()
            toto="MO"+" "+str(self.x)+" "+str(self.y)+";SP1000"
            electroglas.write(toto)
            self.adresse="X"+str(self.x)+"Y"+str(self.y)+"\r\n"
            while electroglas.query("?P")!=self.adresse:
                electroglas.query("?P")
            electroglas.query("?P")
            electroglas.query("?P")
            print electroglas.query("?P")
            while electroglas.query("?D")[0:2]!=u'DT':
                electroglas.query("?D")
            electroglas.query("?D")
            electroglas.query("?D")
            print electroglas.query("?D")
            print "debugger"            
            

        def unload_wafer(self,event):
            import visa
            rm=visa.ResourceManager()
            electroglas=rm.open_resource("GPIB::2")
            print "prepare unload wafer....."
            while electroglas.query("?C")[0:1]!=u'C':
                electroglas.query("?C")
            print electroglas.query("?C")
            while electroglas.query("?P")[0:1]!=u'X':
                electroglas.query("?P")
            print electroglas.query("?P")
            while electroglas.query("?C")[0:1]!=u'C':
                electroglas.query("?C")
            electroglas.query("?C")
            for i in range (100):
                electroglas.query("?C")
            electroglas.query("?C")
            electroglas.query("?C")
            print electroglas.query("?C")
            electroglas.write("UL")
            print "unload wafer....."
            time.sleep(50)
            for i in range (20):
                electroglas.query("?C")
            print electroglas.query("?C")
            print "it is finish....."
            print "load a new wafer wait ready an profile and align....."
            self.button6.Show()
            
        def align_and_profile(self,event):
            import visa
            rm=visa.ResourceManager()
            electroglas=rm.open_resource("GPIB::2")
            while electroglas.query("?C")[0:1]!=u'C':
                electroglas.query("?C")
            electroglas.query("?C")
            electroglas.query("?C")
            electroglas.query("?C")
            print electroglas.query("?C")
            electroglas.write("PC")
            print "profile wafer progress....."
            ################### Print electroglas.query("$?WFPF")           
            time.sleep(80)         
            ################# while electroglas.query("$?WFPF")[0:5]!=u'WFPFT':
            while (electroglas.query("$?WFPF")[0:1])!=u'W':
                electroglas.query("$?WFPF")
            electroglas.query("$?WFPF")
            electroglas.query("$?WFPF")
            #time.sleep(80) 
                
            print electroglas.query("$?WFPF")
            ############################### Auto alignment du wafer ############################## 
            electroglas.write("AA")
            
            print"alignement progress....."
            time.sleep(70)
            while electroglas.query("?Z")[0:1]!=u'Z':
                electroglas.query("?Z")
            electroglas.query("?Z")
            electroglas.query("?Z")
            electroglas.query("?Z")
            print electroglas.query("?Z")
            self.up=electroglas.query("?Z")[0:3]

            ################################## attente du positionement ##########################
            while electroglas.query("?H")[0:1]!=u'H':
                electroglas.query("?H")
            print electroglas.query("?H")
            while electroglas.query("?P")!=u'X1Y1\r\n':
                electroglas.query("?P")
            print electroglas.query("?P")
            print "wafer ready to test"
 #           self.button1.Show()
            self.button6.Hide()
            self.selectscribe.Show()
            self.sizememorytext.Show()
            self.sizeMemory2.Show()
            self.edithear.Show()
            
        def chuck_up(self,event):
            import visa
            rm=visa.ResourceManager()
            electroglas=rm.open_resource("GPIB::2")
            electroglas.write("ZU")
            print "Chuck Up..."
            while electroglas.query("?Z")[0:3]!=self.up:
                electroglas.query("?Z")
            electroglas.query("?Z")
            electroglas.query("?Z")
            print electroglas.query("?Z")
            self.button2.Hide()


        def chuck_down(self,event):
            import visa
            rm=visa.ResourceManager()
            electroglas=rm.open_resource("GPIB::2")
            electroglas.write("ZD")
            print "Chuck Down..."
            while electroglas.query("?Z")[0:1]!=u'Z':
                electroglas.query("?Z")
            electroglas.query("?Z")
            electroglas.query("?Z")
            print electroglas.query("?Z")
            self.button2.Show()
        def ShowMessage(self):
            wx.MessageBox('Load Manually Wafer On Tray and wait until it is READY!!!!', 'WARNING!!!', wx.OK | wx.ICON_INFORMATION) 
            
if __name__=='__main__':    
    app= wx.App(False)
    frame=MyFrameName(parent=None, id=-1, title="Test")
    frame.Show()
    app.MainLoop()
