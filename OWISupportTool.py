"""
OWISupportTool

This program is to act as a GUI interface to the OWIBridge application. This can be used by support staff to perform
specific tasks on a GR that is currently connected to a CP
"""

import time
import webhook_listener
import requests
import json
import sys
#import socket
import os.path
#import pdb

# Insert the path of SmartNet Python Library modules folder to the "sys.path" variable
sys.path.insert(0, "..\\SN-PyLib")

import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

# This is the list of 'Actions' that the OWIBridge can take
SN_OWIWebHookAction = {
    0: "Configure",
    1: "Reboot",
    2: "UploadFWFile",
    3: "UploadOptionsFile",
    4: "InstallFWFile",
    5: "InstallOptionsFile",
    6: "GetSystemInfo",
    7: "GetCoordinates"
}

g_SiteInfoDict = {
    "Action": "Reboot",
    "SiteCode": "UNKN",
    "SiteIP": "",
    "SitePort": 5004,
    "ResultsIP": "127.0.0.1",
    "ResultsPort": 8091
}

ActionList = ('GetSystemInfo', "UploadFWFile", "UploadOptionsFile")

class CStatusBar(ttk.Frame):
    def __init__(self, MasterFrame):
        ttk.Frame.__init(self, MasterFrame)
        self.TitleLabel = ttk.Label(self, text="Status: ")
        self.TitleLabel = ttk.Label.pack (side-LEFT)

        self.StatusLabel = ttk.Label(self)
        self.StatusLabel.pack(side=LEFT)

        self.pack(side=BOTTOM, fill=X)

    def SetLabel (p_String):
        self.StatusLabel.config(text=p_String)

    def ClearLabel (self):
        self.StatusLabel.config(text="Unknown")

class CUploadFileFrame (ttk.LabelFrame):

    def __init__(self, p_RootWindow, p_OWISupportFrame):

        ttk.LabelFrame.__init__(self, p_RootWindow)

        self.m_UploadFile = StringVar ()

        self.m_UploadFileField = ttk.Entry(self, width=40, textvariable=self.m_UploadFile)
        self.m_UploadFileField.grid(column=2, row=1, columnspan=3, sticky=(W, E))
        self.m_UploadFileBrowseButton = ttk.Button (self, text="Browse")
        self.m_UploadFileBrowseButton.grid (column=5, row=1)
        self.m_UploadFileBrowseButton.bind ('<ButonPress-1>', self.m_UploadFileBrowseButton.configure(command=self.BrowseFiles))

        self.m_UploadFileLabel = ttk.Label(self, text="Firmware File")
        self.m_UploadFileLabel.grid(column=1, row=1, sticky=E)

        #m_ButtonFrame = ttk.Frame (p_SupportFrame)
        # fillers for spacing buttons
        ttk.Label (self, text="    ").grid(column=3, row=2)
        ttk.Label (self, text="    ").grid(column=2, row=3, sticky=W)
        ttk.Label (self, text="    ").grid(column=4, row=3, sticky=E)

        self.m_UploadButton = ttk.Button(self)
        self.m_UploadButton.configure (text="Upload")
        self.m_UploadButton.bind ('<ButonPress-1>', self.m_UploadButton.configure(command=p_OWISupportFrame.UploadFile))
        self.m_UploadButton.grid (column=2, row=4)

        self.m_InstallButton = ttk.Button(self)
        self.m_InstallButton.configure (text="Install")
        self.m_InstallButton.bind ('<ButonPress-1>', self.m_InstallButton.configure(command=p_OWISupportFrame.InstallFile))
        self.m_InstallButton.grid (column=4, row=4)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def SetUploadLabel (self, p_LabelString):
        self.m_UploadFileLabel.configure (text=p_LabelString)

    def BrowseFiles (self):
        Filename = filedialog.askopenfile(initialdir='/', title="Select file to Upload",
                                                      filetypes=(("FW files as zip", "*.zip"), ("Option Files", "*.key"), ("all files", "*.*")))
        # if open dialog is 'canceled' it will return an empty
        if (Filename):
            print ("Fileopen dialog returned '%s'" % (Filename.name))
            self.m_UploadFile.set(Filename.name)

class CSystemInfoFrame (ttk.LabelFrame):
    def __init__(self, p_MainWindow, p_OWISupportFrame):
        ttk.LabelFrame.__init__(self, p_MainWindow)

        self.m_RcvrType = StringVar ()
        self.m_RcvrSerialNum = StringVar ()
        self.m_RcvrFWVersion = StringVar ()
        self.m_RcvrMEVersion = StringVar ()
        self.m_RcvrBootloaderVersion = StringVar ()
        self.m_RcvrMaintDate = StringVar ()

        # define "system info" fields and labels
        self.m_RcvrTypeField = ttk.Label(self, textvariable=self.m_RcvrType).grid(column=2, row=1, sticky=(W, E))
        self.m_RcvrSerialNumField = ttk.Label(self, textvariable=self.m_RcvrSerialNum).grid(column=4, row=1, sticky=(W, E))
        self.m_RcvrFWVersionField = ttk.Label(self, textvariable=self.m_RcvrFWVersion).grid(column=2, row=2, sticky=(W, E))
        self.m_RcvrMEVersionField = ttk.Label(self, textvariable=self.m_RcvrMEVersion).grid(column=2, row=3, sticky=(W, E))
        self.m_RcvrBLVersionField = ttk.Label(self, textvariable=self.m_RcvrBootloaderVersion).grid(column=2, row=4, sticky=(W, E))
        self.m_RcvrMaintDateField = ttk.Label(self, textvariable=self.m_RcvrMaintDate).grid(column=2, row=5, sticky=(W, E))

        self.m_RcvrTypeLabel = ttk.Label(self, text="Receiver Type").grid(column=1, row=1, sticky=E)
        self.m_RcvrSerialNumLabel = ttk.Label(self, text="Receiver Serial").grid(column=3, row=1, sticky=W)
        self.m_RcvrFWVersionLabel = ttk.Label(self, text="Receiver FW Version").grid(column=1, row=2, sticky=E)
        self.m_RcvrMEVersionLabel = ttk.Label(self, text="Receiver ME Version").grid(column=1, row=3, sticky=W)
        self.m_RcvrBLVersionLabel = ttk.Label(self, text="Receiver BootLoader").grid(column=1, row=4, sticky=E)
        self.m_RcvrMaintDateLabel = ttk.Label(self, text="Receiver Maint Date").grid(column=1, row=5, sticky=W)

        self.m_GetSysButton = ttk.Button(self)
        self.m_GetSysButton.configure (text="Get System Info")
        self.m_GetSysButton.bind ('<ButonPress-1>', self.m_GetSysButton.configure(command=p_OWISupportFrame.SendToOWIBridge))
        self.m_GetSysButton.grid (column=2, row=6)

        self.m_RebootButton = ttk.Button(self)
        self.m_RebootButton.configure (text="Reboot GR")
        self.m_RebootButton.bind ('<ButonPress-1>', self.m_GetSysButton.configure(command=p_OWISupportFrame.RebootGR))
        self.m_RebootButton.grid (column=4, row=6)



class COWISupportFrame (ttk.Frame):

    def __init__(self, p_RootWindow):

        ttk.Frame.__init__(self, p_RootWindow, padding="20 20 20 20")

        self.m_SiteCode = StringVar (value="FLME")
        self.m_SiteIP = StringVar(value="10.47.201.1")
        self.m_SitePort = StringVar(value="5004")
        self.m_Action = StringVar ()
        self.m_ResultsStatus = StringVar (value="Status: ")

        p_RootWindow.title ("Support Tool Using OWI")

        #mainframe = ttk.Frame(RootWindow, padding="30 30 30 30")
        #self.m_OWISupportFrame = ttk.Frame(p_RootWindow, padding="30 30 30 30")
        self.pack()
        p_RootWindow.columnconfigure (0, weight=1)
        p_RootWindow.rowconfigure (0, weight=1)

        p_RootWindow.protocol("WM_DELETE_WINDOW", self.Quit)

        self.m_Action.set (ActionList[0])
        self.m_PrevAction = self.m_Action.get()
        self.m_ActionCombo = ttk.Combobox (self, textvariable=self.m_Action, values=ActionList, state='readonly')
        self.m_ActionCombo.bind ('<<ComboboxSelected>>', self.ComboSelect)
        self.m_ActionCombo.grid(column=2, row=0, sticky=W)

        # set up Site required input edit fields
        SiteCodeEntry = ttk.Entry(self, width=7, textvariable=self.m_SiteCode)
        SiteCodeEntry.grid(column=2, row=1, sticky=(W, E))
        SiteIPEntry = ttk.Entry(self, width=14, textvariable=self.m_SiteIP)
        SiteIPEntry.grid(column=2, row=2, sticky=(W, E))
        SiteIPEntry.bind ('<FocusOut>', self.ClearStatus)
        SitePortEntry = ttk.Entry(self, width=4, textvariable=self.m_SitePort)
        SitePortEntry.grid(column=4, row=2, sticky=(W, E))
        SitePortEntry.bind ('<FocusOut>', self.ClearStatus)

        ttk.Label(self, text="Action").grid(column=1, row=0, sticky=W)
        ttk.Label(self, text="Site Code").grid(column=1, row=1, sticky=W)
        ttk.Label(self, text="Site IP").grid(column=1, row=2, sticky=W)
        ttk.Label(self, text="Site Port").grid(column=3, row=2, sticky=W)
        #ttk.Label(OWISupportFrame, text="Results Status:").grid (column=1, row=4)
        self.m_StatusLabel = ttk.Label (self, textvariable=self.m_ResultsStatus).grid (column=1, row=3, columnspan=3, sticky=W)

        #ttk.Label(self.m_OWISupportFrame, text=" ").grid(column=2, row=5, sticky=(W, E))

        # create space saver frame for action-related info
        self.SpaceSaverFrame = ttk.Frame (p_RootWindow)
        self.SpaceSaverFrame.pack (fill = tkinter.X)

        self.m_SysInfoFrame = CSystemInfoFrame (self.SpaceSaverFrame, self)
        #self.m_SysInfoFrame.grid (column=1, row=5)

        self.m_UploadFileFrame = CUploadFileFrame (self.SpaceSaverFrame, self)
        #self.m_UploadFileFrame.grid (column=1, row=5, columnspan = 3)
        #self.m_UploadFileFrame.grid_remove ()

        self.QuitButton = ttk.Button(p_RootWindow)
        self.QuitButton.configure (text="Quit")
        self.QuitButton.bind ('<ButonPress-1>', self.QuitButton.configure(command=self.Quit))
        self.QuitButton.pack(anchor='s', padx=10, pady=10)
        #self.QuitButton.pack ()


        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # initially show SysInfo frame
        self.ShowWidgets ()
        # set up status bar at bottom
        #self.m_StatusLabel = ttk.Label (m_OWISupportFrame, textvariable=self.m_ResultsStatus).pack (expand=True, fill=BOTH)

    def HideWidgets (self, *args):
        # hide widgets associated with previous action if Action has changes

        print ("Ready to hide frame for %s" % (self.m_PrevAction))
        if (self.m_PrevAction == self.m_Action.get()):
            # if actin did not change there no need to change anything
            return

        if (self.m_PrevAction == "GetSystemInfo"):
            #self.m_SysInfoFrame.grid_remove ()
            self.m_SysInfoFrame.pack_forget ()
        elif (self.m_PrevAction == "UploadFWFile" or self.m_PrevAction == "UploadOptionsFile"):
            #self.m_UploadFileFrame.grid_remove ()
            self.m_UploadFileFrame.pack_forget ()

    def ShowWidgets (self, *args):
        # show the widget associated with the Actin that was selected. Also, set the file name label if Upload

        print ("ready to show frame %s" % (self.m_Action.get()))
        #if (self.m_PrevAction == self.m_Action.get()):
            # if action did not change there no need to change anything
            #return

        if (self.m_Action.get() == "GetSystemInfo"):
            #self.m_SysInfoFrame.grid (column=1, row=6)
            self.m_SysInfoFrame.pack (pady=10, padx=20, fill=tkinter.X)
        elif (self.m_Action.get() == "UploadFWFile"):
            self.m_UploadFileFrame.SetUploadLabel("Firmware File")
            #self.m_UploadFileFrame.grid (column=1, row=6)
            self.m_UploadFileFrame.pack (pady=10,padx=20, fill=tkinter.X)
        elif (self.m_Action.get() == "UploadOptionsFile"):
            self.m_UploadFileFrame.SetUploadLabel("Options File")
            #self.m_UploadFileFrame.grid (column=1, row=6)
            self.m_UploadFileFrame.pack (pady=10, padx=20, fill=tkinter.X)

    def ComboSelect (self, *args):
        # hide and show widgets based on which Action was selected

        if (self.m_PrevAction == self.m_Action):
            # if action did not change there no need to change anything
            return

        self.HideWidgets ()
        self.ShowWidgets ()
        # save Action just selected as Previous to be used in next call to 'HideWidgets'
        self.m_PrevAction = self.m_Action.get()

    def UploadFile(self):
        self.SendToOWIBridge ("Upload")

    def InstallFile(self):
        self.SendToOWIBridge ("Install")

    def RebootGR (self):
        self.SendToOWIBridge("Reboot")

    def SendToOWIBridge (self, p_ActionString, *args):
        # create output JSON to be sent to OWIBridge
        SiteConfigDict = {
            "Action": p_ActionString,
            "SiteCode": self.m_SiteCode.get(),
            "SiteIP": self.m_SiteIP.get(),
            "SitePort": int(self.m_SitePort.get()),
            "ResultsIP": "http://127.0.0.1",
            "ResultsPort": 8091
        }
        if (p_ActionString == "Upload"):
            if (self.m_Action.get () == "UploadFWFile"):
                SiteConfigDict["Action"] = "UploadFWFile"
            if (self.m_Action.get() == "UploadOptionsFile"):
                SiteConfigDict["Action"] = "UploadOptionsFile"

        if (p_ActionString == "Install"):
            if (self.m_Action.get() == "UploadFWFile"):
                SiteConfigDict["Action"] = "InstallFWFile"
            if (self.m_Action.get() == "UploadOptionsFile"):
                SiteConfigDict["Action"] = "InstallOptionsFile"

        # if UploadFW or UploadOptions
        # Connect to server and send data
        print ("posting requests and/or data to OWIBridge")
        # use loopback address ("127.0.0.1") to send request to OWIBridge running on this same machine
        response = requests.post("http://127.0.0.1:8090", data=json.dumps(SiteConfigDict))
        print ("Results response is %d" % (response.status_code))
        self.UpdateStatus ()
        if ("Action" in g_SiteInfoDict):
            print ("Action was %s" % (g_SiteInfoDict["Action"]))
        else:
            print ("Action not found in Site Info Dict")
        if ("Action" in g_SiteInfoDict and g_SiteInfoDict["Action"] == "GetSystemInfo"):
            self.UpdateSysInfo()

    def UpdateStatus (self, *args):
        print ("Updating status results for var of type... ", (type (self.m_ResultsStatus)))
        #print ("Status current value is %s" % (self.ResultsStatus.get()))
        try:
            if ("Status" in g_SiteInfoDict):
                print ("Results are: %s" % (g_SiteInfoDict["Status"]))
                self.m_ResultsStatus.set (g_SiteInfoDict["Status"])
                """
                if ("Success" in g_SiteInfoDict["Status"]):
                    print ("Success")
                    #self.m_StatusLabel.config (text="Success")
                    self.ResultsStatus.set ("Success")
                elif ("Warning" in g_SiteInfoDict["Status"]):
                    print ("Warning")
                    #self.ResultsStatus.set ("Warning")
                elif ("Error" in g_SiteInfoDict["Status"]):
                    print ("Error")
                    self.m_StatusLabel.config (text="Error")
                    #self.ResultsStatus.set ("ERROR")
                else:
                    print ("unknown")
                    #self.ResultsStatus.set ("Unknown Results")
                """
            else:
                self.m_ResultsStatus.set ("Results Status: No results field found")
        #except _tkinter.Exception as err:
            #print ("Tcl Error: %s" % (err))
        except ValueError as err:
            print ("Value error: %s" % (err))
        except Exception as err:
            print ("Error trying to update status: %s" % (err))

    def ClearStatus (self, *args):
        print ("Clear Status was called")
        self.m_ResultsStatus.set ("Status: ")

    def UpdateSysInfo (self, *args):

        print ("Updating Sys Info with...", g_SiteInfoDict)
        # Update sys info fields with info form passed dictionary
        try:
            if ("Receiver" in g_SiteInfoDict):
                if ("ReceiverType" in g_SiteInfoDict["Receiver"]):
                    self.m_RcvrType.set (g_SiteInfoDict["Receiver"]["ReceiverType"])
                if ("SerialNum" in g_SiteInfoDict["Receiver"]):
                    self.m_RcvrSerialNum.set (int(g_SiteInfoDict["Receiver"]["SerialNum"]))
                if ("FWVersion" in g_SiteInfoDict["Receiver"]):
                    self.m_RcvrFWVersion.set (float(g_SiteInfoDict["Receiver"]["FWVersion"]))
                if ("MEVersion" in g_SiteInfoDict["Receiver"]):
                    self.m_RcvrMEVersion.set (float(g_SiteInfoDict["Receiver"]["MEVersion"]))
                if ("BootLoader" in g_SiteInfoDict["Receiver"]):
                    self.m_RcvrBootloaderVersion.set (float(g_SiteInfoDict["Receiver"]["BootLoader"]))
                if ("MaintDate" in g_SiteInfoDict["Receiver"]):
                    self.m_RcvrMaintDate.set (g_SiteInfoDict["Receiver"]["MaintDate"])
        #except tk.TclError as err:
            #print ("Tcl Error: %s" % (err))
        except ValueError as err:
            print ("Value error: %s" % (err))
        except Exception as err:
            print ("Exception trying to update Sys Info: %s" % (err))

    def Quit(self, *args):
        global MyMainWindow
        global webhooks

        print ("Attempting to quit ...")
        webhooks.stop ()
        MyMainWindow.destroy()

def process_owibridge_results(request, *args, **kwargs):
    """
    This function is the handler function used to process a "POST" request from webhook_listener

    """
    global MainFrame
    global g_SiteInfoDict
    # Process the request!

    # ...
    print ("received some results ...")
    # If a JSON file is sent Load JSON input data into a dictionary tht could then be read for specific results
    try:
        RawJSON = request.body.read(int(request.headers['Content-Length'])) if int(request.headers.get('Content-Length', 0)) > 0 else '{}'
        JSONString = RawJSON.decode()
        ResultsDict = json.loads(JSONString)

        # if Action was "GetSystemInfo"
        if (ResultsDict["Action"] == SN_OWIWebHookAction[6]):
            print ("Sending sys info results to frame ...")
            # copy read results dictionary into global SiteInfo dictionary so can be used back in main thread
            g_SiteInfoDict = ResultsDict.copy()

    except Exception as err:
        print ("Response error '%s' trying to read response" % (err))

    print (ResultsDict)

    print("Action complete\n")

    return


webhooks = webhook_listener.Listener(handlers={"POST": process_owibridge_results}, port=8091)
webhooks.start()

MyMainWindow = tkinter.Tk()
MainFrame = COWISupportFrame(MyMainWindow)
#SystemInfoFrame = CSystemInfoFrame (MyMainWindow)
#UploadFileFrame = CUploadFileFrame (MyMainWindow)
MyMainWindow.mainloop()
