#----------------------------------------------------------------------
# SurfShark VPN GUI
# by Jake Day
# v1.0
# Basic GUI for connecting to surfshark vpn
#----------------------------------------------------------------------

import requests, os, subprocess, wx, zipfile, json

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, size=(300, 420))

        self.CreateStatusBar()

        self.panel = wx.Panel(self)

        config_path = os.path.expanduser('~/.surfshark/configs')

        my_path = os.path.abspath(os.path.dirname(__file__))

        with open(os.path.join(my_path, 'assets/servers.json')) as s:
            self.serverdata = json.load(s)

        servers = list(self.serverdata.keys())

        self.servercmb = wx.ComboBox(self.panel, choices=servers)
        self.protocmb = wx.ComboBox(self.panel, value='udp', choices=['udp', 'tcp'], size=(80, -1))

        self.credentialsbtn = wx.Button(self.panel, -1, "Enter Credentials")
        self.credentialsbtn.SetBackgroundColour('#ffffff')
        self.credentialsbtn.SetForegroundColour('#00d18a')

        self.connectbtn = wx.Button(self.panel, -1, "Quick Connect")
        self.connectbtn.SetBackgroundColour('#00d18a')
        self.connectbtn.SetForegroundColour('#ffffff')

        self.disconnectbtn = wx.Button(self.panel, -1, "Disconnect")
        self.disconnectbtn.SetBackgroundColour('#ffffff')
        self.disconnectbtn.SetForegroundColour('#00d18a')

        logoimg = wx.Image(os.path.join(my_path, 'assets/surfsharkgui.png'), wx.BITMAP_TYPE_ANY)
        logoimgBmp = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(logoimg))

        self.Bind(wx.EVT_BUTTON, self.OnCredentials, self.credentialsbtn)
        self.Bind(wx.EVT_BUTTON, self.OnConnect, self.connectbtn)
        self.Bind(wx.EVT_BUTTON, self.OnDisconnect, self.disconnectbtn)
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.AddSpacer(10)
        sizer.Add(self.credentialsbtn, 0, wx.ALIGN_CENTER, 10)

        sizer.Add(logoimgBmp, 0, wx.ALIGN_CENTER, 10)
        sizer.AddSpacer(10)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.servercmb, 1, wx.ALIGN_LEFT, 10)
        hsizer.Add(self.protocmb, 0, wx.ALIGN_RIGHT, 10)

        sizer.Add(hsizer, 0, wx.ALIGN_CENTER, 10)
        sizer.AddSpacer(10)

        sizer.Add(self.connectbtn, 0, wx.ALIGN_CENTER, 10)
        sizer.Add(self.disconnectbtn, 0, wx.ALIGN_CENTER, 10)

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
        credentials_file = os.path.join(config_path, 'credentials')

        config_file = os.path.join(config_path, self.serverdata[self.servercmb.GetValue()] + '_' + self.protocmb.GetValue() + '.ovpn')

        subprocess.Popen(['pkexec', 'sysctl', '-w', 'net.ipv6.conf.all.disable_ipv6=1'])

        self.ovpn = subprocess.Popen(['pkexec', 'openvpn', '--auth-nocache', '--config', config_file, '--auth-user-pass', credentials_file], preexec_fn=os.setpgrp)

    def OnDisconnect(self, evt):
        self.connectbtn.Show()
        self.disconnectbtn.Hide()
        self.panel.Layout()

        pgid = os.getpgid(self.ovpn.pid)
        subprocess.check_call(['pkexec', 'kill', str(pgid)])

        subprocess.Popen(['pkexec', 'sysctl', '-w', 'net.ipv6.conf.all.disable_ipv6=0'])

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

        if not os.path.exists(os.path.join(config_path, 'configurations')):
            confs_url = 'https://my.surfshark.com/vpn/api/v1/server/configurations'
            fileConfs = requests.get(confs_url)
            open(os.path.join(config_path, 'configurations'), 'wb').write(fileConfs.content)
            with zipfile.ZipFile(os.path.join(config_path, 'configurations'), 'r') as zip_conf:
                zip_conf.extractall(config_path)

app = MyApp()
app.MainLoop()
