#----------------------------------------------------------------------
# SurfShark VPN GUI
# by Jake Day
# v1.0
# Basic GUI for connecting to surfshark vpn
#----------------------------------------------------------------------

import requests, os, subprocess, wx, zipfile, json

config_path = os.path.expanduser('~/.surfshark/configs')

surfshark_setup = 'https://my.surfshark.com/vpn/manual-setup/main'
clusters_url = 'https://my.surfshark.com/vpn/api/v1/server/clusters'
configurations_url = 'https://my.surfshark.com/vpn/api/v1/server/configurations'

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, size=(320, 460))

        self.CreateStatusBar()

        self.panel = wx.Panel(self)

        with open(os.path.join(config_path, 'clusters.json')) as s:
            self.jsondata = json.load(s)
            self.serverdata = {x["location"] + " · " + x["country"]: x["connectionName"] for x in self.jsondata}

        self.servers = list(self.serverdata.keys())

        self.servercmb = wx.ComboBox(self.panel, choices=self.servers)
        # Every text input filters the list of servers
        self.servercmb.Bind(wx.EVT_TEXT, self.OnText)
        self.ignore_evt_text = False
        # Custom input handler to acts like a real cursor for text edition
        self.servercmb.Bind(wx.EVT_KEY_DOWN, self.OnComboKey)
        self.intersection_point = 0

        self.protocmb = wx.ComboBox(self.panel, value='udp', choices=['udp', 'tcp'], size=(80, -1))

        credentials_file = os.path.join(config_path, 'credentials')

        if os.path.isfile(credentials_file):
            self.credentialsbtn = wx.Button(self.panel, -1, 'Modify Credentials')
        else:
            self.credentialsbtn = wx.Button(self.panel, -1, 'Enter Credentials')
        self.credentialsbtn.SetBackgroundColour('#ffffff')
        self.credentialsbtn.SetForegroundColour('#00d18a')

        self.updatebtn = wx.Button(self.panel, -1, '🔄', size=(28, 28))
        self.updatebtn.SetBackgroundColour('#ffffff')

        self.connectbtn = wx.Button(self.panel, -1, 'Quick Connect')
        self.connectbtn.SetBackgroundColour('#00d18a')
        self.connectbtn.SetForegroundColour('#ffffff')

        self.disconnectbtn = wx.Button(self.panel, -1, 'Disconnect')
        self.disconnectbtn.SetBackgroundColour('#ffffff')
        self.disconnectbtn.SetForegroundColour('#00d18a')

        self.info = wx.StaticText(self.panel, -1, size=(320, 20), style=wx.ALIGN_CENTRE)
        self.info.SetForegroundColour('#ff7f00')

        logoimg = wx.Image(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets/surfsharkgui.png'), wx.BITMAP_TYPE_ANY)
        logoimgBmp = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(logoimg))

        self.Bind(wx.EVT_BUTTON, self.OnCredentials, self.credentialsbtn)
        self.Bind(wx.EVT_BUTTON, self.OnConnect, self.connectbtn)
        self.Bind(wx.EVT_BUTTON, self.OnDisconnect, self.disconnectbtn)
        self.Bind(wx.EVT_BUTTON, self.OnUpdate, self.updatebtn)

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.AddSpacer(10)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.credentialsbtn, 0, wx.ALIGN_CENTER, 10)
        hsizer.AddSpacer(40)
        hsizer.Add(self.updatebtn, 0, wx.ALIGN_CENTER, 10)
        sizer.Add(hsizer, 0, wx.ALIGN_CENTER, 10)

        sizer.Add(logoimgBmp, 0, wx.ALIGN_CENTER, 10)
        sizer.AddSpacer(10)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.servercmb, 1, wx.ALIGN_LEFT, 10)
        hsizer.Add(self.protocmb, 0, wx.ALIGN_LEFT, 10)

        sizer.Add(hsizer, 0, wx.ALIGN_CENTER, 10)
        sizer.AddSpacer(10)

        sizer.Add(self.info, 0, wx.ALIGN_CENTER, 10)
        sizer.AddSpacer(10)

        sizer.Add(self.connectbtn, 0, wx.ALIGN_CENTER, 10)
        sizer.Add(self.disconnectbtn, 0, wx.ALIGN_CENTER, 10)

        self.disconnectbtn.Hide()

        self.panel.SetSizerAndFit(sizer)
        self.panel.Layout()

    def OnClose(self, evt):
        self.Close()

    def OnComboKey(self, evt):
        # Backspace key, shift index to previous
        if evt.GetKeyCode() == 8:
            self.intersection_point = self.servercmb.GetInsertionPoint() - 1
        # Delete key, keep current index
        elif evt.GetKeyCode() == 127:
            self.intersection_point = self.servercmb.GetInsertionPoint()
        # Any other key, increase length
        else:
            self.intersection_point = self.servercmb.GetInsertionPoint() + 1
        # Continue event
        evt.Skip()

    def OnText(self, evt):
        current_text = evt.GetString()
        if self.ignore_evt_text:
            self.ignore_evt_text = False
            return

        # Cancel double event triggered by single key
        self.ignore_evt_text = True

        if current_text:
            matching = [x for x in self.servers if current_text.lower() in x.lower()]
            self.servercmb.Set(matching)
            # Cancel incoming event from servercmb update
            self.ignore_evt_text = True
            self.servercmb.SetValue(current_text)
            self.servercmb.SetInsertionPoint(self.intersection_point)
        elif len(current_text) == 0:
            self.servercmb.Set(self.servers)

    def OnCredentials(self, evt):
        dlg = wx.MessageDialog(self,
                               f'Please generate your credentials first at {surfshark_setup}.',
                               'Generate Credentials', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        dlg = wx.TextEntryDialog(self, 'Enter Your Email/Username', 'SurfShark Credentials')
        save = True

        if dlg.ShowModal() == wx.ID_OK:
            username = dlg.GetValue()
        else:
            save = False
        dlg.Destroy()

        dlg = wx.TextEntryDialog(self, 'Enter Your Password', 'SurfShark Credentials')

        if dlg.ShowModal() == wx.ID_OK:
            password = dlg.GetValue()
        else:
            save = False
        dlg.Destroy()

        if save:
            credentials_file = os.path.join(config_path, 'credentials')
            with open(credentials_file, 'w') as fw:
                fw.write(username + '\n' + password + '\n')

    def OnConnect(self, evt):
        credentials_file = os.path.join(config_path, 'credentials')

        if self.servercmb.GetValue() in self.serverdata.keys():
            locations_path = os.path.join(config_path, 'locations')
            config_file = os.path.join(locations_path, self.serverdata[self.servercmb.GetValue()] + '_' + self.protocmb.GetValue() + '.ovpn')

            self.disconnectbtn.Show()
            self.connectbtn.Hide()
            self.info.SetLabel('')
            self.panel.Layout()

            subprocess.Popen(['pkexec', 'sysctl', '-w', 'net.ipv6.conf.all.disable_ipv6=1'])

            self.ovpn = subprocess.Popen(['pkexec', 'openvpn', '--auth-nocache', '--config', config_file, '--auth-user-pass', credentials_file], preexec_fn=os.setpgrp)
        else:
            self.info.SetLabel('Unknown server, please select a valid one in the list')

    def OnDisconnect(self, evt):
        self.connectbtn.Show()
        self.disconnectbtn.Hide()
        self.panel.Layout()

        pgid = os.getpgid(self.ovpn.pid)
        subprocess.check_call(['pkexec', 'kill', str(pgid)])

        subprocess.Popen(['pkexec', 'sysctl', '-w', 'net.ipv6.conf.all.disable_ipv6=0'])

    def OnUpdate(self, evt):
        self.info.SetLabel('Updating files, please wait')
        self.Update()

        clusters = requests.get(clusters_url)
        clusters_path = os.path.join(config_path, 'clusters.json')
        with open(clusters_path, 'wb') as file:
            file.write(clusters.content)

        configurations = requests.get(configurations_url)
        configurations_path = os.path.join(config_path, 'configurations.zip')
        locations_path = os.path.join(config_path, 'locations')
        with open(configurations_path, 'wb') as file:
            file.write(configurations.content)
        with zipfile.ZipFile(configurations_path, 'r') as zip_conf:
            zip_conf.extractall(locations_path)

        with open(os.path.join(config_path, 'clusters.json')) as s:
            self.jsondata = json.load(s)
            self.serverdata = {x["location"] + " · " + x["country"]: x["connectionName"] for x in self.jsondata}

        self.servers = list(self.serverdata.keys())
        self.servercmb.Set(self.servers)

        self.info.SetLabel('')

class MyApp(wx.App):
    def OnInit(self):
        self.Prep()

        frame = MyFrame(None, 'SurfShark VPN GUI')
        self.SetTopWindow(frame)

        frame.Show(True)

        return True

    def Prep(self):
        if not os.path.exists(config_path):
            os.makedirs(config_path)

        clusters_path = os.path.join(config_path, 'clusters.json')
        if not os.path.isfile(clusters_path):
            clusters = requests.get(clusters_url)
            with open(clusters_path, 'wb') as file:
                file.write(clusters.content)

        configurations_path = os.path.join(config_path, 'configurations.zip')
        locations_path = os.path.join(config_path, 'locations')
        if not os.path.isfile(configurations_path) or not os.path.exists(locations_path):
            configurations = requests.get(configurations_url)
            with open(configurations_path, 'wb') as file:
                file.write(configurations.content)
            with zipfile.ZipFile(configurations_path, 'r') as zip_conf:
                zip_conf.extractall(locations_path)

app = MyApp()
app.MainLoop()
