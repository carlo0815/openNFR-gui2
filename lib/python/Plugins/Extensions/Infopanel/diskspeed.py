from boxbranding import getMachineProcModel, getMachineBuild, getBoxType, getMachineName 
from Screens.Screen import Screen
from Plugins.Extensions.Infopanel.Console import Console
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.Button import Button
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.Input import Input
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Components.Pixmap import Pixmap, MultiPixmap
from Components.config import *
from Components.ConfigList import ConfigListScreen
import Components.Harddisk
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
from Components.ProgressBar import ProgressBar

import os
import re
from skin import parseColor
from boxbranding import getImageDistro
PLUGINVERSION = '1.00'
Disk_Speed_Skin = '\n\t\t<screen name="Disk_Speed" position="center,center" size="902,380" title="Disk Speed Test" >\n\t\t      <widget name="label1" position="10,10" size="840,30" zPosition="1" halign="center" font="Regular;25" backgroundColor="#9f1313" transparent="1"/>\n\t\t      <widget name="label2" position="10,80" size="840,290" zPosition="1" halign="center" font="Regular;20" backgroundColor="#9f1313" transparent="1"/>\n\t\t      <widget name="config" position="10,160" size="840,200" scrollbarMode="showOnDemand" transparent="1"/>\n\t\t      <ePixmap pixmap="skin_default/buttons/red.png" position="10,290" size="140,40" alphatest="on" />\n\t\t      <ePixmap pixmap="skin_default/buttons/green.png" position="150,290" size="140,40" alphatest="on" />\n\t\t      <ePixmap pixmap="skin_default/buttons/blue.png" position="300,290" size="140,40" alphatest="on" />\n\t\t      <widget name="key_red" position="10,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t      <widget name="key_green" position="150,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t      <widget name="key_blue" position="300,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t</screen>'
Disk_Speed1_Skin = '\n\t\t<screen name="Disk_Speed" position="center,center" size="902,380" title="Disk Speed Test">\n\t\t<widget name="label1" position="10,10" size="840,30" zPosition="1" halign="center" font="Regular;25" backgroundColor="un9f1313" transparent="1" />\n\t\t<widget name="label2" position="10,39" size="840,120" zPosition="1" halign="center" font="Regular;20" backgroundColor="un9f1313" transparent="1" />\n\t\t<widget name="config" position="10,159" size="840,200" scrollbarMode="showOnDemand" transparent="1" />\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="10,320" size="140,40" alphatest="on" />\n\t\t<widget name="key_red" position="9,318" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="un9f1313" transparent="1" />\n\t\t<ePixmap pixmap="skin_default/disk_speed1.png" position="50,200" size="800,40" alphatest="on" />\n\t\t<eLabel name="spaceused" text=" 1 SD" position="25,175" size="40,20" font="Regular; 12" halign="left" backgroundColor="black" transparent="1" zPosition="5" />\n\t\t<eLabel name="spaceused1" text=" 1 HD" position="65,175" size="40,20" font="Regular; 12" halign="left" backgroundColor="black" transparent="1" zPosition="5" />\n\t\t<eLabel name="spaceused2" text=" 2 HD" position="105,175" size="40,20" font="Regular; 12" halign="left" backgroundColor="black" transparent="1" zPosition="5" />\n\t\t<eLabel name="spaceused3" text=" More then 2 HD" position="438,175" size="120,20" font="Regular; 12" halign="left" backgroundColor="black" transparent="1" zPosition="5" />\n\t\t<widget name="spaceused" position="50,245" size="800,20" foregroundColor="unf2e000" backgroundColor="blue" zPosition="3" />\n\t\t</screen>'

global mysel
global label1
global label2        
global percUsed 


class Disk_Speed(Screen):
    def __init__(self, session):
        self.skin = Disk_Speed_Skin
        Screen.__init__(self, session)
        self.list = []
        self['config'] = MenuList(self.list)
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Start Test'))
        self['key_blue'] = Label(_('Devices Panel'))
        self['label1'] = Label(_('Welcome to Device Speed Test.'))
        self['label2'] = Label(_('Here is the list of mounted devices in Your STB\n\nPlease choose a device where You would like to test the Speed:'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.close,
         'green': self.start_test,
         'ok': self.start_test,         
         'back': self.close,
         'blue': self.devpanel})
        self.updateList()

    def updateList(self):
        if fileExists('/tmp/writebufferhdd'):
           os.system("rm /tmp/writebufferhdd")      
        myusb, myhdd = ('', '')
        myoptions = []
        if fileExists('/proc/mounts'):
            fileExists('/proc/mounts')
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/media/usb') != -1:
                    myusb = '/media/usb'
                    continue
                if line.find('/media/hdd') != -1:
                    myhdd = '/media/hdd'
                    continue

            f.close()
        else:
            self['label2'].setText(_('Sorry it seems that there are not Linux formatted devices mounted on your STB. To install NFR4XBoot you need a Linux formatted part1 device. Click on the blue button to open NFR Devices Panel'))
            fileExists('/proc/mounts')
        if myusb:
            self.list.append(myusb)
        else:
            myusb
        if myhdd:
            myhdd
            self.list.append(myhdd)
        else:
            myhdd
        self['config'].setList(self.list)

    def devpanel(self):
        try:
            from Screens.HddSetup import HddSetup
            self.session.open(HddSetup)
        except:
            self.session.open(MessageBox, _('You are not running NFR Image. You must mount devices Your self.'), MessageBox.TYPE_INFO)

    def myclose(self):
        self.close()

    def start_test(self):
        check = False
        self.mysel = self['config'].getCurrent()
        global mysel
        mysel = self.mysel
        if fileExists('/proc/mounts'):
            fileExists('/proc/mounts')
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find(self.mysel) != -1:
                    check = True
                    continue
            f.close()
        else:
            fileExists('/proc/mounts')
        if check == False:
            self.session.open(MessageBox, _('Sorry, there is not any connected devices in your STB.\nPlease connect HDD or USB to test the Speed!'), MessageBox.TYPE_INFO)
        else:
           self.install2()

    def install2(self):
        os.system("echo 3 >/proc/sys/vm/drop_caches")
        os.popen("time dd if=/dev/zero of=%s/blanks2 bs=1024k count=50 2>/tmp/writebufferhdd" % self.mysel)
        f = open('/tmp/writebufferhdd', 'r')
        for line in f.readlines():
            if "MB/s" in line:
                    model = line.split(' ')[6]
		    speed = re.findall("[-+]?\d+[\.]?\d*", model)
        f.close()
        label1 = Label(_('Your Disk-Speed is:%s') %model)
        percUsed = int(float(speed[0]) / 1.6) 
        if float(speed[0]) <= 1.5:
            label2 = Label(_('With this Speed you can Record 1 SD Channel!\n'))
        elif float(speed[0]) > 1.5 and float(speed[0]) <= 10:
            label2 = Label(_('With this Speed you can Record 1 HD Channel!\n'))
        elif float(speed[0]) > 10 and float(speed[0]) <= 15:
            label2 = Label(_('With this Speed you can Record 2 HD Channel!\n'))
        else:
            label2 = Label(_('With this Speed you can Record more then 2 HD Channel!\n'))
        os.system("rm %s/blank2" % mysel)
        self.session.open(Disk_Test, percUsed, label1, label2)
        os.system("rm /tmp/writebufferhdd")
            
class Disk_Test(Screen):
    def __init__(self, session, percUsed, label1, label2):
        Screen.__init__(self, session)
        global percUsed1
        percUsed1 = percUsed
        label1 = label1
        label2 = label2        
        self.skin = Disk_Speed1_Skin
        self.onShown.append(self.setWindowTitle)
        self['label1'] = label1        
        self['label2'] = label2         
        self['key_red'] = Label(_('Exit'))
        self['spaceused'] = ProgressBar()        
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.close,
         'back': self.close})
        
    def setWindowTitle(self):	        
        self['spaceused'].setValue(percUsed1)
