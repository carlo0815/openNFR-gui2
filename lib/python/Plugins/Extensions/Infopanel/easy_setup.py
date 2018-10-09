# -*- coding: utf-8 -*-
from Components.ActionMap import *
from Components.config import *
from Components.ConfigList import *
from Components.UsageConfig import *
from Components.Label import Label
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.Network import iNetwork
from Components.Ipkg import IpkgComponent
from Plugins.Plugin import PluginDescriptor
from Components.Pixmap import Pixmap
from Components.PluginComponent import plugins
from Screens.Console import Console
from Tools.Directories import fileExists, resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from os import popen, system, remove, listdir, chdir, getcwd, statvfs, mkdir, path, walk
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
import shutil
import string
from random import Random
from Screens.VirtualKeyBoard import VirtualKeyBoard
from traceback import print_exc
from Tools.Import import my_import
from Screens.Setup import Setup, getSetupTitle
from Screens.HddSetup import HddSetup
from Screens.Recordings import RecordingSettings
from Screens.Hotkey import HotkeySetup
from Plugins.Extensions.Infopanel.QuickMenu import QuickMenu
from Plugins.Extensions.Infopanel.iptv_convert import IPTV
from Screens.OpenNFR_wizard import OpenNFRWizardSetup
from Screens.WizardUserInterfacePositioner import UserInterfacePositionerWizard
from Plugins.Extensions.OpenWebif.plugin import OpenWebifConfig
if os.path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/MenuSort/plugin.pyo") is True:
	try:
		from Plugins.Extensions.MenuSort.plugin import *
	except:
		pass		
from Screens.Menu import Menu, mdom
if os.path.isfile("/usr/lib/enigma2/python/Plugins/SystemPlugins/HdmiCEC/plugin.pyo") is True:
	try:
		from Plugins.SystemPlugins.HdmiCEC.plugin import HdmiCECSetupScreen
	except:
		pass
from Plugins.SystemPlugins.SoftwareManager.ImageBackup import ImageBackup, TimerImageManager, AutoImageManagerTimer
from enigma import *
from Screens.PluginBrowser import *
from Screens.Ipkg import Ipkg
from Components.Console import Console
from Components.About import about
from Components.Sources.List import List
from Components.SelectionList import SelectionList
from Screens.NetworkSetup import *
from Screens.Standby import *
from Screens.LogManager import *
from GlobalActions import globalActionMap
from Screens.ChoiceBox import ChoiceBox
from Tools.BoundFunction import boundFunction
from Tools.LoadPixmap import LoadPixmap
from Components.FileList import FileList
from Components.Sources.Progress import Progress
from Components.Button import Button
from boxbranding import getBoxType, getMachineName, getMachineBrand, getBrandOEM  
from __init__ import _
from enigma import getDesktop
from Screens.OpenNFR_wizard import OpenNFRWizardSetup, OpenNFRWizardupdatecheck
from Screens.InputBox import PinInput
import os
import sys
import re
import ServiceReference
import time
import datetime
from Screens.CronTimer import *
from Plugins.Extensions.Infopanel.skin_setup import NfrHD_Config, DefaulSkinchange
from Plugins.Extensions.Infopanel.UserMainMenu import UserMainMenuConfig
from Plugins.Extensions.Infopanel.ScriptRunner import *
from Plugins.Extensions.Infopanel.bootvideo import BootvideoSetupScreen
from Plugins.Extensions.Infopanel.bootlogo import BootlogoSetupScreen, RadiologoSetupScreen
from Plugins.Extensions.Infopanel.diskspeed import Disk_Speed
from Screens.HddMount import HddFastRemove
from Screens.Swap import SwapOverviewScreen
from Plugins.Extensions.Infopanel.Manager import *
from Plugins.Extensions.Infopanel.Softcam import *
from Plugins.Extensions.Infopanel.Flash_local import FlashOnline
from Plugins.Extensions.Infopanel.SoftwarePanel import SoftwarePanel
from Plugins.SystemPlugins.SoftwareManager.BackupRestore import BackupScreen, RestoreScreen, BackupSelection, getBackupPath, getBackupFilename
from Plugins.Extensions.Infopanel.PluginWizard import PluginInstall
from Plugins.Extensions.Infopanel.PluginWizard import PluginDeinstall
from Plugins.Extensions.Infopanel.SpinnerSelector import SpinnerSelector
from os import popen, system, remove, listdir, chdir, getcwd, statvfs, mkdir, path, walk
from urllib import urlopen
import socket

def getVarSpaceKb():
    try:
        s = statvfs('/')
    except OSError:
        return (0, 0)

    return (float(s.f_bfree * (s.f_bsize / 1024)), float(s.f_blocks * (s.f_bsize / 1024)))
    
if config.usage.keymap.value != eEnv.resolve("${datadir}/enigma2/keymap.xml"):
	if not os.path.isfile(eEnv.resolve("${datadir}/enigma2/keymap.usr")) and config.usage.keymap.value == eEnv.resolve("${datadir}/enigma2/keymap.usr"):
		setDefaultKeymap()
	if not os.path.isfile(eEnv.resolve("${datadir}/enigma2/keymap.ntr")) and config.usage.keymap.value == eEnv.resolve("${datadir}/enigma2/keymap.ntr"):
		setDefaultKeymap()
	if not os.path.isfile(eEnv.resolve("${datadir}/enigma2/keymap.u80")) and config.usage.keymap.value == eEnv.resolve("${datadir}/enigma2/keymap.u80"):
		setDefaultKeymap()

def setDefaultKeymap():
	print "[Info-Panel] Set Keymap to Default"
	config.usage.keymap.setValue(eEnv.resolve("${datadir}/enigma2/keymap.xml"))
	config.save()


panel = open("/tmp/infopanel.ver", "w")

try:
	panel.write("Keymap: %s " % (config.usage.keymap.value)+ '\n')
except:
	panel.write("Keymap: keymap file not found !!" + '\n')
panel.close()    

class EasySetup(ConfigListScreen, Screen):
    __module__ = __name__
    def __init__(self, session, args = 0):
	Screen.__init__(self, session)
	self.skinName = ["Setup"]
	config.easysetup = ConfigSubsection()
	config.easysetup.restart = ConfigBoolean(default = False)	
	config.easysetup.backup = ConfigYesNo(default=True)	
	config.easysetup.hddsetup = ConfigYesNo(default=False)
	config.easysetup.records = ConfigYesNo(default=False)
	config.easysetup.timeshift = ConfigYesNo(default=False)
	config.easysetup.Keymap = ConfigYesNo(default=False)
	config.easysetup.Hotkey = ConfigYesNo(default=False)
	config.easysetup.channellist = ConfigYesNo(default=False)
	config.easysetup.m3u = ConfigYesNo(default=False)
	config.easysetup.menusort = ConfigYesNo(default=False)
       	config.easysetup.hdmicec = ConfigYesNo(default=False)
	config.easysetup.password = ConfigYesNo(default=False)
	config.easysetup.displaysetup = ConfigYesNo(default=False)
	config.wizardsetup.UserInterfacePositionerWizard = ConfigYesNo(default = False) 
	config.wizardsetup.OpenWebifConfig = ConfigYesNo(default = False)
	config.wizardsetup.OpenNFRaddonsWizardSetup = ConfigYesNo(default = False)
	config.wizardsetup.poweroffsetup = ConfigYesNo(default = False)	
	self.backup = '0'
	self.runed = '0'
        self['spaceused'] = ProgressBar()
        self["status"] = ScrollLabel()
        self.onShown.append(self.setWindowTitle)
        self["description"] = Label(_(""))
        			
        list = []
	list.append(getConfigListEntry(_('Enable Fullbackup after Easy-Setup?'), config.easysetup.backup, _("Default is enable and Fullbackup will start after all Setups are ready.")))        
	list.append(getConfigListEntry(_('Enable HDD/USB/SD Mounts Setup?'), config.easysetup.hddsetup, _("Choose your Device mounts (USB, HDD, others...).")))
	list.append(getConfigListEntry(_('Enable Records Setup?'), config.easysetup.records, _("Choose your recording config.")))		
	list.append(getConfigListEntry(_('Enable Timeshift Setup?'), config.easysetup.timeshift, _("Choose your timeshift config.")))
	list.append(getConfigListEntry(_('Enable Keymap Setup?'), config.easysetup.Keymap, _("Choose your keymap.")))
	list.append(getConfigListEntry(_('Enable Hotkey Setup?'), config.easysetup.Hotkey, _("Choose your remote buttons.")))
	list.append(getConfigListEntry(_('Enable Channellist Setup?'), config.easysetup.channellist, _("Choose your Channel selection config.")))		
	list.append(getConfigListEntry(_('Enable M3U Convert to Channellist Setup?'), config.easysetup.m3u, _("Install your IPTV-m3u-files into channellist.\nFirst you must coppy a M3U-List to /etc/enigma2")))
	if os.path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/MenuSort/plugin.pyo") is True:
        	list.append(getConfigListEntry(_('Enable Menusort Setup?'), config.easysetup.menusort, _("Choose your Mainmenu sorts.")))
	if os.path.isfile("/usr/lib/enigma2/python/Plugins/SystemPlugins/HdmiCEC/plugin.pyo") is True:
        	list.append(getConfigListEntry(_('Enable HDMI-CEC Setup?'), config.easysetup.hdmicec, _("Choose your HDMI-CEC config.")))
	list.append(getConfigListEntry(_('Enable Password change?'), config.easysetup.password, _("Change the rootpassword for login in ftp, telnet and webif.")))		
	list.append(getConfigListEntry(_('Enable Display Setup?'), config.easysetup.displaysetup, _("Choose your Display config.")))
	list.append(getConfigListEntry(_('Enable Position Setup?'), config.wizardsetup.UserInterfacePositionerWizard, _("Choose your OSD Position in TV")))		
	list.append(getConfigListEntry(_('Enable OpenWebif Setup?'), config.wizardsetup.OpenWebifConfig, _("Choose your Openwebif config.")))
	list.append(getConfigListEntry(_('Enable OpenNFR-Addons Setup?'), config.wizardsetup.OpenNFRaddonsWizardSetup, _("Install OpenNFR Plugins.")))		
	list.append(getConfigListEntry(_('Enable Power Off Menu Setup?'), config.wizardsetup.poweroffsetup, _("Choose your Powerbutton Funktion on Remotecontrol.")))                	
	
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Start Easy-Setup"))
        self['label1'] = Label(_(''))
        self['label2'] = Label(_('% Flash Used....'))
        self['label3'] = Label(_(''))
        
        ConfigListScreen.__init__(self, list) 
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions'], {'red': self.dontSaveAndExit, 'green' : self.run1,
         'cancel': self.dontSaveAndExit}, -1)

    def setWindowTitle(self):
		self.title = _('EasySetup')
	
    def run1(self):
        self.runed = '1'
        if config.easysetup.hddsetup.value is True:
            self.session.openWithCallback(self.run2, HddSetup)
        else:
            self.run2()

    def run2(self):
        self.runed = '2'
        if config.easysetup.records.value is True:
            self.openSetup("recording")
        else:
            self.run3()

    def run3(self):
        self.runed = '3'
        if config.easysetup.timeshift.value is True:
            self.openSetup("timeshift")
        else:
            self.run4()
            
    def run4(self):
        self.runed = '4'
        if config.easysetup.Keymap.value is True:
            self.session.openWithCallback(self.run5, KeymapSel)
        else:
            config.easysetup.restart.setValue(False)
	    config.easysetup.restart.save()
            self.run5()                        

    def run5(self):
        self.runed = "5"
        if config.easysetup.Hotkey.value is True:
            self.session.openWithCallback(self.run6,HotkeySetup)
        else:
            self.run6()
            
    def run6(self):
        self.runed = "6"
        if config.easysetup.channellist.value is True:
            self.openSetup("channelselection")
        else:
            self.run7()
            
    def run7(self):
        self.runed = "7"
        if config.easysetup.m3u.value is True:
            self.session.openWithCallback(self.run8,IPTV)
        else:
            self.run8()
            
    def run8(self):
        self.runed = "8"
        if config.easysetup.menusort.value is True and os.path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/MenuSort/plugin.pyo") is True:
            self.session.openWithCallback(self.run8a,SortableMenu, mdom.getroot())
        else:
            self.run9()
            
    def run8a(self, ret):
        self.run9()            
            
    def run9(self):
        self.runed = "9"
        if config.easysetup.hdmicec.value is True and os.path.isfile("/usr/lib/enigma2/python/Plugins/SystemPlugins/HdmiCEC/plugin.pyo") is True:
            self.session.openWithCallback(self.run10,HdmiCECSetupScreen)
        else:
            self.run10()
            
    def run10(self):
        self.runed = "10"
        if config.easysetup.password.value is True:
            self.session.openWithCallback(self.run11,NFRPasswdScreen)
        else:
            self.run11()
            
    def run11(self):
        self.runed = "11"
        if config.easysetup.displaysetup.value is True:
            self.openSetup("display")
        else:
            self.run11a()
            
    def run11a(self):
        self.runed = "11a"
        if config.wizardsetup.UserInterfacePositionerWizard.value is True:
            self.Console = Console()
            self.Console.ePopen('/usr/bin/showiframe /usr/share/enigma2/hd-testcard.mvi')			
            self.session.openWithCallback(self.run11b,UserInterfacePositionerWizard)  
        else:
            self.run11b()
            
    def run11b(self):
        self.runed = "11b"
        if config.wizardsetup.OpenWebifConfig.value is True:
            self.session.openWithCallback(self.run11c,OpenWebifConfig)
        else:
            self.run11c()
            
    def run11c(self):
        self.runed = "11c"
        if config.wizardsetup.OpenNFRaddonsWizardSetup.value is True:
            self.session.openWithCallback(self.run11d,OpenNFRWizardSetup)
        else:
            self.run11d()
            
    def run11d(self):
        self.runed = "11d"
        if config.wizardsetup.poweroffsetup.value is True:
            self.openSetup("remotesetup")
        else:
            self.run12()                                                
            
    def run12(self):
        self.runed = "12"
        if config.easysetup.backup.value is True:
            self.session.openWithCallback(self.closetest,ImageBackup)
        else:
            self.closetest()
            
    def closetest(self):            
	if config.easysetup.restart.value == True:
            config.easysetup.restart.setValue(False)
	    config.easysetup.restart.save()
            quitMainloop(3)
	else:
            config.easysetup.restart.setValue(False)
	    config.easysetup.restart.save()
            self.close()		
    def openSetup(self, dialog):
         self.session.openWithCallback(self.menuClosed, Setup, dialog)        

    def menuClosed(self, *res):
        if self.runed == "1":
            self.run2()
        elif self.runed == "2":
            self.run3()
        elif self.runed == "3":
            self.run4()
        elif self.runed == "4":
            self.run5()                 
        elif self.runed == "5":
            self.run6()                 
        elif self.runed == "6":
            self.run7()                 
        elif self.runed == "7":
            self.run8()                                         
        elif self.runed == "8":
            self.run9()     
        elif self.runed == "9":
            self.run10()                 
        elif self.runed == "10":
            self.run11()
        elif self.runed == "11":
            self.run11a()
        elif self.runed == "11a":
            self.run11b()
        elif self.runed == "11b":
            self.run11c()
        elif self.runed == "11c":
            self.run11d()
        elif self.runed == "11d":
            self.run12()                                                           
              
    def dontSaveAndExit(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()
        
   
class KeymapSel(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = ["SetupInfo", "Setup" ]
		Screen.setTitle(self, _("Keymap Selection") + "...")
		self.setup_title =  _("Keymap Selection") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label("")
		self["labelInfo"] = Label(_("Copy your keymap to\n/usr/share/enigma2/keymap.usr"))

		usrkey = eEnv.resolve("${datadir}/enigma2/keymap.usr")
		ntrkey = eEnv.resolve("${datadir}/enigma2/keymap.ntr")
		u80key = eEnv.resolve("${datadir}/enigma2/keymap.u80")
		
		self.actkeymap = self.getKeymap(config.usage.keymap.value)
		keySel = [ ('keymap.xml',_("Default  (keymap.xml)"))]
		if os.path.isfile(usrkey):
			keySel.append(('keymap.usr',_("User  (keymap.usr)")))
		if os.path.isfile(ntrkey):
			keySel.append(('keymap.ntr',_("Neut  (keymap.ntr)")))
		if os.path.isfile(u80key):
			keySel.append(('keymap.u80',_("UP80  (keymap.u80)")))			
		if self.actkeymap == usrkey and not os.path.isfile(usrkey):
			setDefaultKeymap()
		if self.actkeymap == ntrkey and not os.path.isfile(ntrkey):
			setDefaultKeymap()
		if self.actkeymap == u80key and not os.path.isfile(u80key):
			setDefaultKeymap()
		self.keyshow = ConfigSelection(keySel)
		self.keyshow.setValue(self.actkeymap)

		self.onChangedEntry = [ ]
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
		self.createSetup()

		self["actions"] = ActionMap(["SetupActions", 'ColorActions'],
		{
			"ok": self.keySave,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
			"menu": self.keyCancel,
		}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def createSetup(self):
		self.editListEntry = None
		self.list = []
		self.list.append(getConfigListEntry(_("Use Keymap"), self.keyshow))
		
		self["config"].list = self.list
		self["config"].setList(self.list)
		if config.usage.sort_settings.value:
			self["config"].list.sort()

	def selectionChanged(self):
		self["status"].setText(self["config"].getCurrent()[0])

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
		self.selectionChanged()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def getCurrentDescription(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or ""

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

	def saveAll(self):
		config.usage.keymap.setValue(eEnv.resolve("${datadir}/enigma2/" + self.keyshow.value))
		config.usage.keymap.save()
		configfile.save()
		if self.actkeymap != self.keyshow.value:
			self.changedFinished()

	def keySave(self):
		self.saveAll()
		self.close()

	def cancelConfirm(self, result):
		if not result:
			return
		for x in self["config"].list:
			x[1].cancel()
		self.close()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"))
		else:
			self.close()

	def getKeymap(self, file):
		return file[file.rfind('/') +1:]

	def changedFinished(self):
		self.session.openWithCallback(self.ExecuteRestart, MessageBox, _("Keymap changed, you need to restart the GUI after finish EasySetup") +"\n"+_("Do you want to restart after finish EasySetup?"), MessageBox.TYPE_YESNO)
		self.close()

	def ExecuteRestart(self, result):
		if result:
			config.easysetup.restart.setValue(True)
			config.easysetup.restart.save()
                        self.close()			
		else:
			config.easysetup.restart.setValue(False)
			config.easysetup.restart.save()			
                        self.close()
                        
class NFRPasswdScreen(Screen):

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        self.title = _('Change Root Password')
        try:
            self['title'] = StaticText(self.title)
        except:
            print 'self["title"] was not found in skin'

        self.user = 'root'
        self.output_line = ''
        self.list = []
        self['passwd'] = ConfigList(self.list)
        self['key_red'] = StaticText(_('Close'))
        self['key_green'] = StaticText(_('Set Password'))
        self['key_yellow'] = StaticText(_('new Random'))
        self['key_blue'] = StaticText(_('virt. Keyboard'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.close,
         'green': self.SetPasswd,
         'yellow': self.newRandom,
         'blue': self.bluePressed,
         'cancel': self.close}, -1)
        self.buildList(self.GeneratePassword())
        self.onShown.append(self.setWindowTitle)

    def newRandom(self):
        self.buildList(self.GeneratePassword())

    def buildList(self, password):
        self.password = password
        self.list = []
        self.list.append(getConfigListEntry(_('Enter new Password'), ConfigText(default=self.password, fixed_size=False)))
        self['passwd'].setList(self.list)

    def GeneratePassword(self):
        passwdChars = string.letters + string.digits
        passwdLength = 8
        return ''.join(Random().sample(passwdChars, passwdLength))

    def SetPasswd(self):
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self.container.dataAvail.append(self.processOutputLine)
        retval = self.container.execute('passwd %s' % self.user)
        if retval == 0:
            self.session.open(MessageBox, _('Sucessfully changed password for root user to:\n%s ' % self.password), MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, _('Unable to change/reset password for root user'), MessageBox.TYPE_ERROR)

    def dataAvail(self, data):
        self.output_line += data
        if self.output_line.find('password changed.') == -1:
            if self.output_line.endswith('new UNIX password: '):
                print '1password:%s\n' % self.password
                self.processOutputLine(self.output_line[:1])

    def processOutputLine(self, line):
        if line.find('new UNIX password: '):
            print '2password:%s\n' % self.password
            self.container.write('%s\n' % self.password)
            self.output_line = ''

    def runFinished(self, retval):
        del self.container.dataAvail[:]
        del self.container.appClosed[:]
        del self.container
        self.close()

    def bluePressed(self):
        self.session.openWithCallback(self.VirtualKeyBoardTextEntry, VirtualKeyBoard, title=_('Enter your password here:'), text=self.password)

    def VirtualKeyBoardTextEntry(self, callback = None):
        if callback is not None:
            self.buildList(callback)
        return

    def setWindowTitle(self, title = None):
        if not title:
            title = self.title
        try:
            self['title'] = StaticText(title)
        except:
            pass   
                                
                        