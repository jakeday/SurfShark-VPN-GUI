#----------------------------------------------------------------------
# SurfShark VPN GUI
# by Jake Day
# v1.0
# Basic GUI for connecting to surfshark vpn
#----------------------------------------------------------------------

import requests, os, sys, subprocess, time, wx, zipfile, glob, fnmatch

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, pos=(150, 150), size=(300, 400))

        menuBar = wx.MenuBar()
        menu = wx.Menu()

        menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit SurfShark VPN GUI")
        menu.Append(wx.ID_PREFERENCES, "Enter &Credentials\tAlt-C", "Enter SurfShark Credentials")

        self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnCredentials, id=wx.ID_PREFERENCES)

        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

        self.CreateStatusBar()

        self.panel = wx.Panel(self)

        config_path = os.path.expanduser('~/.surfshark/configs')
        servers = [os.path.basename(x).split('.ovpn', 1)[0] for x in glob.glob(config_path + '/*.ovpn')]

        self.combo = wx.ComboBox(self.panel, choices = servers)

        self.connectbtn = wx.Button(self.panel, -1, "Quick Connect")
        self.connectbtn.SetBackgroundColour('#00d18a')
        self.connectbtn.SetForegroundColour('#ffffff')

        self.disconnectbtn = wx.Button(self.panel, -1, "Disconnect")
        self.disconnectbtn.SetBackgroundColour('#ffffff')
        self.disconnectbtn.SetForegroundColour('#00d18a')

        logoimg = wx.Image('logo.png', wx.BITMAP_TYPE_ANY)
        logoimgBmp = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(logoimg))

        self.Bind(wx.EVT_BUTTON, self.OnConnect, self.connectbtn)
        self.Bind(wx.EVT_BUTTON, self.OnDisconnect, self.disconnectbtn)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(logoimgBmp, 0, wx.CENTER, 10)
        sizer.AddSpacer(10)
        sizer.Add(self.combo, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 10)
        sizer.Add(self.connectbtn, 0, wx.CENTER, 10)
        sizer.Add(self.disconnectbtn, 0, wx.CENTER, 10)

        self.disconnectbtn.Hide()

        self.panel.SetSizerAndFit(sizer)
        self.panel.Layout()

    def OnClose(self, evt):
        self.Close()

    def OnCredentials(self, evt):
        dlg = wx.MessageDialog(self,
            'Please generate your credentials first at https://account.surfshark.com/setup/manual.',
            'Generate Credentials', wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        dlg = wx.TextEntryDialog(self, 'Enter Your Username','SurfShark Credentials')
        save = True

        if dlg.ShowModal() == wx.ID_OK:
            username = dlg.GetValue()
        else:
            save = False
        dlg.Destroy()

        dlg = wx.TextEntryDialog(self, 'Enter Your Password','SurfShark Credentials') 

        if dlg.ShowModal() == wx.ID_OK:
            password = dlg.GetValue()
        else:
            save = False
        dlg.Destroy()

        if save:
            credentials_file = os.path.expanduser('~/.surfshark/configs/credentials')
            with open(credentials_file, 'w') as fw:
                fw.write(username + '\n' + password + '\n')

    def OnConnect(self, evt):
        self.disconnectbtn.Show()
        self.connectbtn.Hide()
        self.panel.Layout()

        config_path = os.path.expanduser('~/.surfshark/configs')
        config_file = config_path + '/' + self.combo.GetValue() + '.ovpn'
        credentials_file = config_path + '/credentials'

        self.ovpn = subprocess.Popen(['sudo', 'openvpn', '--auth-nocache', '--config', config_file, '--auth-user-pass', credentials_file], preexec_fn=os.setpgrp)

    def OnDisconnect(self, evt):
        self.connectbtn.Show()
        self.disconnectbtn.Hide()
        self.panel.Layout()

        pgid = os.getpgid(self.ovpn.pid)
        subprocess.check_call(['sudo', 'kill', str(pgid)])

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "SurfShark VPN GUI")
        self.SetTopWindow(frame)

        frame.Show(True)

        self.Prep()
        return True

    def Prep(self):
        config_path = os.path.expanduser('~/.surfshark/configs')

        if not os.path.exists(config_path):
            os.makedirs(config_path)

        if not os.path.exists(config_path + '/configurations'):
            confs_url = 'https://account.surfshark.com/api/v1/server/configurations'
            fileConfs = requests.get(confs_url)
            open(config_path + '/configurations', 'wb').write(fileConfs.content)
            with zipfile.ZipFile(config_path + '/configurations', 'r') as zip_conf:
                zip_conf.extractall(config_path)

app = MyApp()
app.MainLoop()
