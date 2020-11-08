# -*-coding:Latin-1 -*
#------------------------------------------------------------------------------
# Name:        ErrorModule
# Purpose:     v 0.1
#
# Author:      AV242852
#
# Created:     23/09/2014
# Copyright:   (c) AV242852 2014
# Licence:     <your licence>
#------------------------------------------------------------------------------
"""
Module to print some error informations in a pop-up windows and close the
program.
"""
import wx
import sys              # Exit from Python. used to interrupt the program

errorCode = 0
errorDescription = ''
functionName = ''
lineError = 0

sizeWindowX = 450
sizeWindowY = 200

class MyDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, u'error', wx.DefaultPosition,
                           wx.Size(sizeWindowX, sizeWindowY))
        
        verticalSizer = wx.BoxSizer(wx.VERTICAL)

        errorSizer = wx.GridBagSizer(hgap = 5, vgap = 5)

        errorSizer.Add(wx.StaticText(self, -1, u'Error Code :'), pos=(0, 0))
        errorSizer.Add(wx.StaticText(self, -1, str(errorCode)), pos=(0, 1))
        errorSizer.Add(wx.StaticText(self, -1, u'Error description :'),
                       pos=(1, 0))
        descriptionLabel = wx.StaticText(self, -1, errorDescription)
        descriptionLabel.Wrap(sizeWindowX-120)
        errorSizer.Add(descriptionLabel, pos=(1, 1))
        errorSizer.Add(wx.StaticText(self, -1, u'Function name :'), pos=(2, 0))
        errorSizer.Add(wx.StaticText(self, -1, functionName), pos=(2, 1))
        errorSizer.Add(wx.StaticText(self, -1, u'Error line :'), pos=(3, 0))
        errorSizer.Add(wx.StaticText(self, -1, str(lineError)), pos=(3, 1))
        errorSizer.AddGrowableCol(1)
        verticalSizer.Add(errorSizer, 0, wx.ALL|wx.EXPAND, 10)
        clear_btn = wx.Button(self, 1, u'Close')
        verticalSizer.Add(clear_btn, 0, wx.ALL|wx.EXPAND, 10)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.SetSizer(verticalSizer)

    def OnClose(self, event):
        self.Destroy()
        sys.exit()

class MyApp(wx.App):
    def OnInit(self):
        dlg = MyDialog(None)
        dlg.Show(True)
        dlg.Centre()
        return True

def callError(eC, eD, fN, lE):
    global errorCode
    global errorDescription
    global functionName
    global lineError
    errorCode = eC
    errorDescription = eD
    functionName = fN
    lineError = lE
    app = MyApp(0)
    app.MainLoop()
