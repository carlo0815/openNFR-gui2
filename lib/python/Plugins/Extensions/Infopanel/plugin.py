from Plugins.Plugin import PluginDescriptor
from Screens.PluginBrowser import *
from Screens.Ipkg import Ipkg
from Components.Console import Console
from Components.About import about
from Components.Sources.List import List
from Components.SelectionList import SelectionList
from Screens.NetworkSetup import *
from enigma import *
from Screens.Standby import *
from Screens.LogManager import *
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap 
from Screens.Screen import Screen
from GlobalActions import globalActionMap
from Screens.ChoiceBox import ChoiceBox
from Tools.BoundFunction import boundFunction
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from Components.MenuList import MenuList
from Components.FileList import FileList
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Components.config import ConfigSubsection, ConfigInteger, ConfigText, getConfigListEntry, ConfigSelection,  ConfigIP, ConfigYesNo, ConfigSequence, ConfigNumber, NoSave, ConfigEnableDisable, configfile
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.Sources.StaticText import StaticText 
from Components.Sources.Progress import Progress
from Components.Button import Button
from Components.ActionMap import ActionMap
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.Hotkey import HotkeySetup
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from boxbranding import getBoxType, getMachineName, getMachineBrand, getBrandOEM  
from __init__ import _
from enigma import getDesktop
from Screens.OpenNFR_wizard import OpenNFRWizardSetup, OpenNFRWizardupdatecheck
from Screens.InputBox import PinInput
import string
from random import Random

if path.exists("/usr/lib/enigma2/python/Plugins/Extensions/dFlash"):
	from Plugins.Extensions.dFlash.plugin import dFlash
	DFLASH = True
else:
	DFLASH = False
import os
import sys
import re
font = "Regular;16"
import ServiceReference
import time
import datetime
inINFOPanel = None

config.NFRSoftcam = ConfigSubsection()
config.NFRSoftcam.actcam = ConfigText(visible_width = 200)
config.NFRSoftcam.actCam2 = ConfigText(visible_width = 200)
config.NFRSoftcam.waittime = ConfigSelection([('0',_("dont wait")),('1',_("1 second")), ('5',_("5 seconds")),('10',_("10 seconds")),('15',_("15 seconds")),('20',_("20 seconds")),('30',_("30 seconds"))], default='15')
config.VolumeSetup = ConfigSubsection()
config.VolumeSetup.steps = ConfigSelection([('default',_("default")),('1',_("1")),('2',_("2")), ('3',_("3")),('4',_("4")),('5',_("5"))], default='default')
config.plugins.infopanel_redkey = ConfigSubsection()
config.plugins.infopanel_redkey.list = ConfigSelection([('0',_("Default (Softcam Panel)")),('1',_("HBBTV")),('2',_("Quickmenu")),('3',_("Infopanel"))])
config.plugins.infopanel_redkeylong = ConfigSubsection()
config.plugins.infopanel_redkeylong.list = ConfigSelection([('0',_("Default (HBBTV)")),('1',_("Softcam Panel")),('2',_("Quickmenu")),('3',_("Infopanel"))])
config.plugins.infopanel_bluekey = ConfigSubsection()
config.plugins.infopanel_bluekey.list = ConfigSelection([('0',_("Default (Quickmenu)")),('1',_("HBBTV")),('2',_("Softcam Panel")),('3',_("Infopanel"))])
config.plugins.infopanel_bluekeylong = ConfigSubsection()
config.plugins.infopanel_bluekeylong.list = ConfigSelection([('0',_("Default (Infopanel)")),('1',_("HBBTV")),('2',_("Quickmenu")),('3',_("Softcam Panel"))])
config.plugins.infopanel_greenkeylong = ConfigSubsection()
config.plugins.infopanel_greenkeylong.list = ConfigSelection([('0',_("Default (Softcam Panel)")),('1',_("HBBTV")),('2',_("Quickmenu")),('3',_("Infopanel"))])
config.plugins.infopanel_yellowkeylong = ConfigSubsection()
config.plugins.infopanel_yellowkeylong.list = ConfigSelection([('0',_("Default (Softcam Panel)")),('1',_("HBBTV")),('2',_("Quickmenu")),('3',_("Infopanel"))])
config.plugins.showinfopanelextensions = ConfigYesNo(default=False)
config.plugins.infopanel_frozencheck = ConfigSubsection()
config.plugins.infopanel_frozencheck.list = ConfigSelection([('0',_("Off")),('1',_("1 min.")), ('5',_("5 min.")),('10',_("10 min.")),('15',_("15 min.")),('30',_("30 min."))])
	
if os.path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/plugin.pyo") is True:
	try:
		from Plugins.Extensions.MultiQuickButton.plugin import *
	except:
		pass

from Screens.CronTimer import *
from Plugins.Extensions.Infopanel.skin_setup import NfrHD_Config, DefaulSkinchange
from Plugins.Extensions.Infopanel.UserMainMenu import UserMainMenuConfig
from Plugins.Extensions.Infopanel.ScriptRunner import *
from Plugins.Extensions.Infopanel.bootvideo import BootvideoSetupScreen
from Plugins.Extensions.Infopanel.bootlogo import BootlogoSetupScreen, RadiologoSetupScreen
from Plugins.Extensions.Infopanel.diskspeed import Disk_Speed
from Plugins.Extensions.Infopanel.iptv_convert import IPTV
from Plugins.Extensions.Infopanel.easy_setup import EasySetup
from Screens.HddSetup import HddSetup
from Screens.HddMount import HddFastRemove
from Screens.Swap import SwapOverviewScreen
from Plugins.Extensions.Infopanel.Manager import *
from Plugins.Extensions.Infopanel.Softcam import *
from Plugins.Extensions.Infopanel.Flash_local import FlashOnline
from Plugins.Extensions.Infopanel.QuickMenu import QuickMenu
from Plugins.Extensions.Infopanel.SoftwarePanel import SoftwarePanel
from Plugins.SystemPlugins.SoftwareManager.BackupRestore import BackupScreen, RestoreScreen, BackupSelection, getBackupPath, getBackupFilename
from Plugins.SystemPlugins.SoftwareManager.ImageBackup import ImageBackup, TimerImageManager, AutoImageManagerTimer
from Plugins.Extensions.Infopanel.PluginWizard import PluginInstall
#from Plugins.Extensions.Infopanel.ImageManager import VIXImageManager, AutoImageManagerTimer, ImageBackup, ImageManagerDownload, ImageManagerautostart 
from Plugins.Extensions.Infopanel.PluginWizard import PluginDeinstall
from Plugins.Extensions.Infopanel.SpinnerSelector import SpinnerSelector
from os import popen, system, remove, listdir, chdir, getcwd, statvfs, mkdir, path, walk
from Components.ProgressBar import ProgressBar
from urllib import urlopen
import socket

# Hide Softcam-Panel Setup when no softcams installed
if (config.plugins.showinfopanelextensions.value):
	config.plugins.showinfopanelextensions.setValue(False)
	config.plugins.showinfopanelextensions.save()

# Hide Keymap selection when no other keymaps installed.
if config.usage.keymap.value != eEnv.resolve("${datadir}/enigma2/keymap.xml"):
	if not os.path.isfile(eEnv.resolve("${datadir}/enigma2/keymap.usr")) and config.usage.keymap.value == eEnv.resolve("${datadir}/enigma2/keymap.usr"):
		setDefaultKeymap()
	if not os.path.isfile(eEnv.resolve("${datadir}/enigma2/keymap.ntr")) and config.usage.keymap.value == eEnv.resolve("${datadir}/enigma2/keymap.ntr"):
		setDefaultKeymap()
	if not os.path.isfile(eEnv.resolve("${datadir}/enigma2/keymap.u80")) and config.usage.keymap.value == eEnv.resolve("${datadir}/enigma2/keymap.u80"):
		setDefaultKeymap()

def getVarSpaceKb():
    try:
        s = statvfs('/')
    except OSError:
        return (0, 0)

    return (float(s.f_bfree * (s.f_bsize / 1024)), float(s.f_blocks * (s.f_bsize / 1024)))
		
def setDefaultKeymap():
	print "[Info-Panel] Set Keymap to Default"
	config.usage.keymap.setValue(eEnv.resolve("${datadir}/enigma2/keymap.xml"))
	config.save()

# edit bb , touch commands.getouput with this def #
def command(comandline, strip=1):
  comandline = comandline + " >/tmp/command.txt"
  os.system(comandline)
  text = ""
  if os.path.exists("/tmp/command.txt") is True:
    file = open("/tmp/command.txt", "r")
    if strip == 1:
      for line in file:
        text = text + line.strip() + '\n'
    else:
      for line in file:
        text = text + line
        if text[-1:] != '\n': text = text + "\n"
    file.close()
  # if one or last line then remove linefeed
  if text[-1:] == '\n': text = text[:-1]
  comandline = text
  os.system("rm /tmp/command.txt")
  return comandline

INFO_Panel_Version = 'Info-Panel V2.0 (mod by OpenNFR)'
boxversion = getBoxType()
print "[Info-Panel] boxversion: %s"  % (boxversion)
panel = open("/tmp/infopanel.ver", "w")
panel.write(INFO_Panel_Version + '\n')
panel.write("Boxversion: %s " % (boxversion)+ '\n')
try:
	panel.write("Keymap: %s " % (config.usage.keymap.value)+ '\n')
except:
	panel.write("Keymap: keymap file not found !!" + '\n')
panel.close()

ExitSave = "[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save")


class ConfigPORT(ConfigSequence):
	def __init__(self, default):
		ConfigSequence.__init__(self, seperator = ".", limits = [(1,65535)], default = default)

def main(session, **kwargs):
		session.open(Infopanel)

def Apanel(menuid, **kwargs):
	if menuid == "mainmenu":
		return [("Info Panel", main, "Infopanel", 11)]
	else:
		return []
		
def startcam(reason, **kwargs):
        from Components.Console import Console
	if config.NFRSoftcam.actcam.value != "none":
		if reason == 0: # Enigma start
			system("sleep 2")
			try:
				if "mgcamd" in config.NFRSoftcam.actcam.value:
	                        	os.system("rm /dev/dvb/adapter0/ca1")
	                        	os.system("ln -sf 'ca0' '/dev/dvb/adapter0/ca1'") 
				cmd = Softcam.getcamcmd(config.NFRSoftcam.actcam.value)
				Console().ePopen(cmd)
				print "[OpenNFR SoftCam Manager] ", cmd
			except:
				pass
		elif reason == 1: # Enigma stop
			try:
				Softcam.stopcam(config.NFRSoftcam.actcam.value)
			except:
				pass 		

#def camstart(reason, **kwargs):
#	if config.NFRSoftcam.actcam.value != "none":
#		if reason == 0: # Enigma start
#			sleep(2)
#			try:
#				if "mgcamd" in config.NFRSoftcam.actcam.value:
#	                        	os.system("rm /dev/dvb/adapter0/ca1")
#	                        	os.system("ln -sf 'ca0' '/dev/dvb/adapter0/ca1'") 
#				cmd = Softcam.getcamcmd(config.NFRSoftcam.actcam.value)
#				Console().ePopen(cmd)
#				print "[OpenNFR SoftCam Manager] ", cmd
#			except:
#				pass
#		elif reason == 1: # Enigma stop
#			try:
#				Softcam.stopcam(config.NFRSoftcam.actcam.value)
#			except:
#				pass 

def Plugins(**kwargs):
	return [

	#// show Infopanel in Main Menu
	PluginDescriptor(name="Info Panel", description="Info panel GUI 22/05/2014", where = PluginDescriptor.WHERE_MENU, fnc = Apanel),
	#// autostart
	PluginDescriptor(where=PluginDescriptor.WHERE_AUTOSTART,	needsRestart=True, fnc=startcam),
	#PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART,PluginDescriptor.WHERE_AUTOSTART],fnc = camstart),
	#// SwapAutostart
	#PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART,PluginDescriptor.WHERE_AUTOSTART],fnc = SwapAutostart),
	#// show Infopanel in EXTENSIONS Menu
	PluginDescriptor(name="Info Panel", description="Info panel GUI 22/05/2014", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc = main) ]



#############------- SKINS --------############################

MENU_SKIN = """<screen position="center,center" size="950,470" title="INFO Panel">
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/redlogo.png" position="0,380" size="950,84" alphatest="on" zPosition="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/alliance.png" position="670,255" size="100,67" alphatest="on" zPosition="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/opennfr_info.png" position="510,11" size="550,354" alphatest="on" zPosition="1" />
				<widget source="global.CurrentTime" render="Label" position="450, 340" size="500,24" font="Regular;20" foregroundColor="white" halign="right" transparent="1" zPosition="5">
				<convert type="ClockToText">&gt;Format%H:%M:%S</convert>
				</widget>
				<eLabel backgroundColor="un56c856" position="0,330" size="950,1" zPosition="0" />
				<widget name="Mlist" position="10,10" size="480,300" zPosition="1" scrollbarMode="showOnDemand" backgroundColor="un251e1f20" transparent="1" />
				<widget name="label1" position="10,340" size="490,25" font="Regular;20" transparent="1" foregroundColor="unf2e000" halign="left" />
				<eLabel name="spaceused" text="% Flash Used..." position="12,390" size="150,20" font="Regular;19" halign="left" foregroundColor="white" backgroundColor="black" transparent="1" zPosition="5" />
				<widget name="spaceused" position="171,390" size="751,20" foregroundColor="white" backgroundColor="blue" zPosition="3" />
			</screen>"""

CONFIG_SKIN = """<screen position="center,center" size="600,440" title="PANEL Config" >
	<widget name="config" position="10,10" size="580,377" enableWrapAround="1" scrollbarMode="showOnDemand" />
	<widget name="labelExitsave" position="90,410" size="420,25" halign="center" font="Regular;20" transparent="1" foregroundColor="#f2e000" />
</screen>"""

INFO_SKIN =  """<screen name="Panel-Info"  position="center,center" size="730,400" title="PANEL-Info" >
	<widget name="label2" position="0,10" size="730,25" font="Regular;20" transparent="1" halign="center" foregroundColor="#f2e000" />
	<widget name="label1" position="10,45" size="710,350" font="Console;20" zPosition="1" backgroundColor="#251e1f20" transparent="1" />
</screen>"""

INFO_SKIN2 =  """<screen name="PANEL-Info2"  position="center,center" size="530,400" title="PANEL-Info" backgroundColor="#251e1f20">
	<widget name="label1" position="10,50" size="510,340" font="Regular;15" zPosition="1" backgroundColor="#251e1f20" transparent="1" />
</screen>"""


###################  Max Test ###################
class PanelList(MenuList):
        if (getDesktop(0).size().width() == 1920):
	        def __init__(self, list, font0 = 38, font1 = 28, itemHeight = 60, enableWrapAround = True):
		        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		        self.l.setFont(0, gFont("Regular", font0))
		        self.l.setFont(1, gFont("Regular", font1))
		        self.l.setItemHeight(itemHeight)
	else:
                def __init__(self, list, font0 = 24, font1 = 16, itemHeight = 50, enableWrapAround = True):	        
		        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
                        self.l.setFont(0, gFont("Regular", font0))
		        self.l.setFont(1, gFont("Regular", font1))
		        self.l.setItemHeight(itemHeight)
		        
def MenuEntryItem(entry):
        if (getDesktop(0).size().width() == 1920):
	   res = [entry]
	   res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 10), size=(100, 50), png=entry[0]))  # png vorn
	   res.append(MultiContentEntryText(pos=(110, 5), size=(690, 50), font=0, text=entry[1]))  # menupunkt
	   return res
	else:
	   res = [entry]
	   res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 5), size=(100, 40), png=entry[0]))  # png vorn
       	   res.append(MultiContentEntryText(pos=(110, 10), size=(440, 40), font=0, text=entry[1]))  # menupunkt
	   return res
           
###################  Max Test ###################

#g
from Screens.PiPSetup import PiPSetup
from Screens.InfoBarGenerics import InfoBarPiP
#g

def InfoEntryComponent(file):
	png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/" + file + ".png")
	if png == None:
		png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/default.png")

	res = (png)
	return res

class Infopanel(Screen, InfoBarPiP):
	servicelist = None
	def __init__(self, session, services = None):
		Screen.__init__(self, session)
		self.session = session
		self.skin = MENU_SKIN
		global check_update
		check_update = 0
		self.onShown.append(self.checkTraficLight)
		self.onShown.append(self.setWindowTitle)
                self.service = None
		self['spaceused'] = ProgressBar()			
		global pluginlist
		global videomode
		global infook
		global INFOCONF
		global menu
		INFOCONF = 0
		pluginlist="False"
		try:
			print '[INFO-Panel] SHOW'
			global inINFOPanel
			inINFOPanel = self
		except:
			print '[INFO-Panel] Error Hide'
#		global servicelist
		if services is not None:
			self.servicelist = services
		else:
			self.servicelist = None
		self.list = []
		#// get the remote buttons
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions"],
			{
				"cancel": self.Exit,
				"upUp": self.up,
				"downUp": self.down,
				"ok": self.ok,
			}, 1)
		
		self["label1"] = Label(INFO_Panel_Version)
		self["summary_description"] = StaticText("")

		self.Mlist = []
		self.Mlist.append(MenuEntryItem((InfoEntryComponent('SoftcamManager'), _("Softcam-Manager"), 'SoftcamManager')))
		self.Mlist.append(MenuEntryItem((InfoEntryComponent ("ImageManager" ), _("Image-Manager"), ("image-manager"))))
		self.Mlist.append(MenuEntryItem((InfoEntryComponent ("RemoteManager" ), _("Image/Remote-Setup"), ("remote-manager"))))
		self.Mlist.append(MenuEntryItem((InfoEntryComponent ("PluginManager" ), _("Plugin-Manager"), ("plugin-manager"))))
		self.Mlist.append(MenuEntryItem((InfoEntryComponent ("QuickMenu" ), _("Quick-Menu"), ("QuickMenu"))))
		self.Mlist.append(MenuEntryItem((InfoEntryComponent('Extras'), _("Extras"), 'Extras')))
		self.Mlist.append(MenuEntryItem((InfoEntryComponent('easy-setup'), _("EasySetup"), 'easy-setup')))		
		self.Mlist.append(MenuEntryItem((InfoEntryComponent('Infos'), _("Infos"), 'Infos')))

		self.onChangedEntry = []
		self["Mlist"] = PanelList([])
		self["Mlist"].l.setList(self.Mlist)
		menu = 0
		self["Mlist"].onSelectionChanged.append(self.selectionChanged)
		if self.isProtected() and config.ParentalControl.servicepin[0].value:
			self.onFirstExecBegin.append(boundFunction(self.session.openWithCallback, self.pinEntered, PinInput, pinList=[x.value for x in config.ParentalControl.servicepin], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the correct pin code"), windowTitle=_("Enter pin code")))

	def checkTraficLight(self):
                global check_update
                if config.opennfrupdate.enablecheckupdate.value is True:
                	if check_update == 0:
                		check_update = 1
				currentTimeoutDefault = socket.getdefaulttimeout()
				socket.setdefaulttimeout(3)
				try:
					if os.path.isfile("/tmp/lastrelease.txt"):
                                		os.system("rm -f /tmp/lastrelease.txt")
					import urllib
					urllib.urlretrieve('http://dev.nachtfalke.biz/nfr/feeds/lastrelease.txt', '/tmp/lastrelease.txt')
                                        d = os.popen("/tmp/lastrelease.txt").read()
					tmpOnlineStatus = open("/tmp/lastrelease.txt", "r").read()
                                	tmpFlashStatus = open("/etc/version", "r").read()
					if int(tmpOnlineStatus) > int(tmpFlashStatus):
						message = _("new Release avaible")
						self.session.openWithCallback(self.setWindowTitle(), MessageBox, _("New Releaseimage on Server, read more about it by http://www.nachtfalke.biz/f742-opennfr-images.html"), MessageBox.TYPE_INFO, timeout=5)
                        		else:
                        			print "no new Release avaible"                                                                	
				except:
					print "no internetconnection to check imageupdates"

				socket.setdefaulttimeout(currentTimeoutDefault)
                	else:
                		pass        	

                else:
                	check_update = 1
                        self.setWindowTitle()
                	
	def isProtected(self):
		return config.ParentalControl.setuppinactive.value and config.ParentalControl.config_sections.infopanel.value

	def pinEntered(self, result):
		if result is None:
			self.closeProtectedScreen()
		elif not result:
			self.session.openWithCallback(self.close(), MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR, timeout=3)

	def closeProtectedScreen(self, result=None):
		self.close(None)
		
	def ConvertSize(self, size):
		size = int(size)
		if size >= 1073741824:
			Size = '%0.2f TB' % (size / 1073741824.0)
		elif size >= 1048576:
			Size = '%0.2f GB' % (size / 1048576.0)
		elif size >= 1024:
			Size = '%0.2f MB' % (size / 1024.0)
		else:
			Size = '%0.2f KB' % size
		return str(Size)

	def setWindowTitle(self):
		diskSpace = getVarSpaceKb()
		percFree = int(diskSpace[0] / diskSpace[1] * 100)
		percUsed = int((diskSpace[1] - diskSpace[0]) / diskSpace[1] * 100)
		self.setTitle('%s - %s: %s (%d%%)' % (_('Info Panel'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)

		
	def getCurrentEntry(self):
		if self['Mlist'].l.getCurrentSelection():
			selection = self['Mlist'].l.getCurrentSelection()[0]
			self["summary_description"].text = selection[1]
			if (selection[0] is not None):
				return selection[0]

	def selectionChanged(self):
		item = self.getCurrentEntry()


	def up(self):
		#self["Mlist"].up()
		pass

	def down(self):
		#self["Mlist"].down()
		pass

	def left(self):
		pass

	def right(self):
		pass

	def Red(self):
		self.showExtensionSelection1(Parameter="run")
		pass

	def Green(self):
		#// Not used
		pass

	def yellow(self):
		#// Not used
		pass

	def blue(self):
		#// Not used
		pass

	def Exit(self):
		#// Exit Infopanel when pressing the EXIT button or go back to the MainMenu
		global menu
		if menu == 0:
			try:
				self.service = self.session.nav.getCurrentlyPlayingServiceReference()
				service = self.service.toCompareString()
				servicename = ServiceReference.ServiceReference(service).getServiceName().replace('\xc2\x87', '').replace('\xc2\x86', '').ljust(16)
				print '[INFO-Panel] HIDE'
				global inINFOPanel
				inINFOPanel = None
			except:
				print '[INFO-Panel] Error Hide'
			self.close()
		elif menu == 1:
			self["Mlist"].moveToIndex(0)
			self["Mlist"].l.setList(self.oldmlist)
			menu = 0
			self["label1"].setText(INFO_Panel_Version)
		elif menu == 2:
			self["Mlist"].moveToIndex(0)
			self["Mlist"].l.setList(self.oldmlist1)
			menu = 1
			self["label1"].setText("Infos")
		else:
			pass

	def ok(self):
		#// Menu Selection
#		menu = self["Mlist"].getCurrent()
		global INFOCONF
		menu = self['Mlist'].l.getCurrentSelection()[0][2]
		print '[INFO-Panel] MenuItem: ' + menu
		if menu == "Extras":
			self.Extras()
		elif menu == "Pluginbrowser":
			self.session.open(PluginBrowser)
		elif menu == "Infos":
			self.Infos()
		elif menu == "InfoPanel":
			self.session.open(Info, "InfoPanel")
		elif menu == "Info":
			self.session.open(Info, "Sytem_info")
		elif menu == "FreeSpace":
			self.session.open(Info, "FreeSpace")
		elif menu == "Network":
			self.session.open(Info, "Network")
		elif menu == "Mounts":
			self.session.open(Info, "Mounts")
		elif menu == "Kernel":
			self.session.open(Info, "Kernel")
		elif menu == "Ram":
			self.session.open(Info, "Free")
		elif menu == "Cpu":
			self.session.open(Info, "Cpu")
		elif menu == "Top":
			self.session.open(Info, "Top")
		elif menu == "MemInfo":
			self.session.open(Info, "MemInfo")
		elif menu == "Module":
			self.session.open(Info, "Module")
		elif menu == "Mtd":
			self.session.open(Info, "Mtd")
		elif menu == "Partitions":
			self.session.open(Info, "Partitions")
		elif menu == "Swap":
			self.session.open(Info, "Swap")
		elif menu == "DiskSpeed":
			self.session.open(Disk_Speed)
		elif menu == "m3u-convert":
			self.session.open(IPTV)
		elif menu == "easy-setup":
			self.session.open(EasySetup)                        			
		elif menu == "PasswordChange":
			self.session.open(NFRPasswdScreen)
		elif menu == "UserMainMenu":
		        plugin_path = None
			self.session.open(UserMainMenuConfig, plugin_path)                                                				
		elif menu == "System_Info":
			self.System()
		elif menu == "JobManager":
			self.session.open(ScriptRunner)
		elif menu == "SoftcamManager":
			self.session.open(NFRCamManager)
		elif menu == "image-manager":
			self.Image_Manager()
		elif menu == "remote-manager":
			self.Remote_Manager()
		elif menu == "plugin-manager":
			self.Plugin_Manager()
		elif menu == "software-update":
			self.session.open(SoftwarePanel)
		elif menu == "backup-image":
			if DFLASH == True:
				self.session.open(dFlash)
			else:
				self.session.open(TimerImageManager)
		elif menu == "backup-settings":
			self.session.openWithCallback(self.backupDone,BackupScreen, runBackup = True)
		elif menu == "restore-settings":
			self.backuppath = getBackupPath()
			self.backupfile = getBackupFilename()
			self.fullbackupfilename = self.backuppath + "/" + self.backupfile
			if os_path.exists(self.fullbackupfilename):
				self.session.openWithCallback(self.startRestore, MessageBox, _("Are you sure you want to restore your STB backup?\nSTB will restart after the restore"))
			else:
				self.session.open(MessageBox, _("Sorry no backups found!"), MessageBox.TYPE_INFO, timeout = 10)
		elif menu == "bootvideomanager":
			self.session.open(BootvideoSetupScreen)
		elif menu == "bootlogomanager":
			self.session.open(BootlogoSetupScreen)	
		elif menu == "radiologomanager":
			self.session.open(RadiologoSetupScreen) 
		elif menu == "spinnermanager":
			SpinnerSelector(self.session) 			
		elif menu == "backup-files":
			self.session.openWithCallback(self.backupfiles_choosen,BackupSelection)
		elif menu == "flash-local":
			self.session.open(FlashOnline)
		elif menu == "MultiQuickButton":
			self.session.open(MultiQuickButton)
		elif menu == "MountManager":
			self.session.open(HddSetup)
		elif menu == "SwapManager":
			self.session.open(SwapOverviewScreen)
		elif menu == "DefaulteSkin-Steps":
			self.session.open(DefaulSkinchange)				
		elif menu == "Volume-Steps":
			self.session.open(VolumeSteps)			
		elif menu == "Red-Key-Action":
			self.session.open(RedPanel)
		elif menu == "Red-Key-Action-Long":
			self.session.open(RedPanelLong)				
		elif menu == "Blue-Key-Action":
			self.session.open(BluePanel)
		elif menu == "Blue-Key-Action-Long":
			self.session.open(BluePanelLong)		
		elif menu == "Green-Key-Action-Long":
			self.session.open(GreenPanelLong)		
		elif menu == "Yellow-Key-Action-Long":
			self.session.open(YellowPanelLong)					
		elif menu == "Multi-Key-Action":
			self.session.open(HotkeySetup)			
		elif menu == "KeymapSel":
			self.session.open(KeymapSel)
		elif menu == "QuickMenu":
			self.session.open(QuickMenu)
		elif menu == "LogManager":
			self.session.open(LogManager)
		elif menu == "PluginInstallwizard":
			self.session.open(PluginInstall)
		elif menu == "PluginDeinstallwizard":
			self.session.open(PluginDeinstall)
		elif menu == "OpenNFRWizard":
			self.session.open(OpenNFRWizardSetup)
		elif menu == "SkinSetup":
			self.session.open(NfrHD_Config)
		elif menu == "ImageUpdateCheck": 
			self.session.open(OpenNFRWizardupdatecheck)                        	
		elif menu == "PluginReLoad":
                        if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/PluginReLoad.pyo") or fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/PluginReLoad.py"):    
                            from Plugins.Extensions.Infopanel.PluginReLoad import PluginReLoadConfig
                            self.session.open(PluginReLoadConfig)      				
		else:
			pass

	def Extras(self):
		#// Create Extras Menu
		global menu
		menu = 1
		self["label1"].setText(_("Extras"))
		self.tlist = []
		self.oldmlist = []
		self.oldmlist = self.Mlist
		self.tlist.append(MenuEntryItem((InfoEntryComponent('MountManager'), _("MountManager"), 'MountManager')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('JobManager'), _("JobManager"), 'JobManager')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('SwapManager'), _("SwapManager"), 'SwapManager')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent ("LogManager" ), _("Log-Manager"), ("LogManager"))))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('DiskSpeed'), _("Disk-Speed"), 'DiskSpeed')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('m3u-convert'), _("m3u-convert"), 'm3u-convert')))
		if os.path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/plugin.pyo") is True:
			self.tlist.append(MenuEntryItem((InfoEntryComponent('MultiQuickButton'), _("MultiQuickButton"), 'MultiQuickButton')))
		self["Mlist"].moveToIndex(0)
		self["Mlist"].l.setList(self.tlist)

	def Infos(self):
		#// Create Infos Menu
		global menu
		menu = 1
		self["label1"].setText(_("Infos"))
		self.tlist = []
		self.oldmlist = []
		self.oldmlist1 = []
		self.oldmlist = self.Mlist
		self.tlist.append(MenuEntryItem((InfoEntryComponent('InfoPanel'), _("InfoPanel"), 'InfoPanel')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('FreeSpace'), _("FreeSpace"), 'FreeSpace')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Kernel'), _("Kernel"), 'Kernel')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Mounts'), _("Mounts"), 'Mounts')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Network'), _("Network"), 'Network')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Ram'), _("Ram"), 'Ram')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('System_Info'), _("System_Info"), 'System_Info')))
		self["Mlist"].moveToIndex(0)
		self["Mlist"].l.setList(self.tlist)
		self.oldmlist1 = self.tlist

	def System(self):
		#// Create System Menu
		global menu
		menu = 2
		self["label1"].setText(_("System Info"))
		self.tlist = []
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Cpu'), _("Cpu"), 'Cpu')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('MemInfo'), _("MemInfo"), 'MemInfo')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Mtd'), _("Mtd"), 'Mtd')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Module'), _("Module"), 'Module')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Partitions'), _("Partitions"), 'Partitions')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Swap'), _("Swap"), 'Swap')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Top'), _("Top"), 'Top')))
		self["Mlist"].moveToIndex(0)
		self["Mlist"].l.setList(self.tlist)

	def System_main(self):
		#// Create System Main Menu
		global menu
		menu = 1
		self["label1"].setText(_("System"))
		self.tlist = []
		self.oldmlist = []
		self.oldmlist = self.Mlist
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Info'), _("Info"), 'Info')))
		self["Mlist"].moveToIndex(0)
		self["Mlist"].l.setList(self.tlist)

	def Image_Manager(self):
		#// Create Image Manager Menu
		global menu
		menu = 1
		self["label1"].setText(_("Image Manager"))
		self.tlist = []
		self.oldmlist = []
		self.oldmlist = self.Mlist
                self.tlist.append(MenuEntryItem((InfoEntryComponent('ImageUpdateCheck'), _("ImageUpdateCheck"), 'ImageUpdateCheck')))
                #self.tlist.append(MenuEntryItem((InfoEntryComponent ("SoftwareManager" ), _("Software update"), ("software-update"))))
		self.tlist.append(MenuEntryItem((InfoEntryComponent ("ImageBackup" ), _("Software Backup"), ("backup-image"))))
		self.tlist.append(MenuEntryItem((InfoEntryComponent ("Flash_local" ), _("Flash local online"), ("flash-local"))))
		self.tlist.append(MenuEntryItem((InfoEntryComponent ("BackupFiles" ), _("Choose backup files"), ("backup-files"))))
		self.tlist.append(MenuEntryItem((InfoEntryComponent ("BackupSettings" ), _("Backup Settings"), ("backup-settings"))))
		self.tlist.append(MenuEntryItem((InfoEntryComponent ("RestoreSettings" ), _("Restore Settings"), ("restore-settings"))))
		self["Mlist"].moveToIndex(0)
		self["Mlist"].l.setList(self.tlist)

	def Remote_Manager(self):
		#// Create Keymap Menu
		global menu
		menu = 1
		self["label1"].setText(_("Image/Remote Setup"))
		self.tlist = []
		self.oldmlist = []
		self.oldmlist = self.Mlist
		self.tlist.append(MenuEntryItem((InfoEntryComponent('SkinSetup'), _("SkinSetup"), 'SkinSetup')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('DefaulteSkin-Steps'), _("DefaulteSkin-Steps"), 'DefaulteSkin-Steps')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Volume-Steps'), _("VolumeSteps"), 'Volume-Steps')))		
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Red-Key-Action'), _("Red Panel"), 'Red-Key-Action')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Red-Key-Action-Long'), _("Red Panel Long"), 'Red-Key-Action-Long')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Blue-Key-Action'), _("Blue Panel"), 'Blue-Key-Action')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Blue-Key-Action-Long'), _("Blue Panel Long"), 'Blue-Key-Action-Long')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Green-Key-Action-Long'), _("Green Panel Long"), 'Green-Key-Action-Long')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Yellow-Key-Action-Long'), _("Yellow Panel Long"), 'Yellow-Key-Action-Long')))		
		self.tlist.append(MenuEntryItem((InfoEntryComponent('Multi-Key-Action'), _("Edit remote buttons"), 'Multi-Key-Action')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('KeymapSel'), _("Keymap-Selection"), 'KeymapSel')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent ("BootvideoManager" ), _("BootvideoManager"), ("bootvideomanager"))))
		self.tlist.append(MenuEntryItem((InfoEntryComponent ("BootlogoManager" ), _("BootlogoManager"), ("bootlogomanager")))) 
		self.tlist.append(MenuEntryItem((InfoEntryComponent ("RadiologoManager" ), _("RadiologoManager"), ("radiologomanager")))) 
		self.tlist.append(MenuEntryItem((InfoEntryComponent ("SpinnerManager" ), _("SpinnerManager"), ("spinnermanager"))))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('PasswordChange'), _("PasswordChange"), 'PasswordChange')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('UserMainMenu'), _("UserMainMenu"), 'UserMainMenu')))                		
		self["Mlist"].moveToIndex(0)
		self["Mlist"].l.setList(self.tlist)

	def Plugin_Manager(self):
		#// Create Plugin Menu
		global menu
		menu = 1
		self["label1"].setText(_("Plugin Manager"))
		self.tlist = []
		self.oldmlist = []
		self.oldmlist = self.Mlist
		self.tlist.append(MenuEntryItem((InfoEntryComponent('PluginInstallwizard'), _("PluginInstallwizard"), 'PluginInstallwizard')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('PluginDeinstallwizard'), _("PluginDeinstallwizard"), 'PluginDeinstallwizard')))
		self.tlist.append(MenuEntryItem((InfoEntryComponent('OpenNFRWizard'), _("OpenNFRWizard"), 'OpenNFRWizard')))
		self["Mlist"].moveToIndex(0)
		self["Mlist"].l.setList(self.tlist)

	def backupfiles_choosen(self, ret):
		#self.backupdirs = ' '.join( config.plugins.configurationbackup.backupdirs.value )
		config.plugins.configurationbackup.backupdirs.save()
		config.plugins.configurationbackup.save()
		config.save()

	def backupDone(self,retval = None):
		if retval is True:
			self.session.open(MessageBox, _("Backup done."), MessageBox.TYPE_INFO, timeout = 10)
		else:
			self.session.open(MessageBox, _("Backup failed."), MessageBox.TYPE_INFO, timeout = 10)

	def startRestore(self, ret = False):
		if (ret == True):
			self.exe = True
			self.session.open(RestoreScreen, runRestore = True)

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
		self.session.openWithCallback(self.ExecuteRestart, MessageBox, _("Keymap changed, you need to restart the GUI") +"\n"+_("Do you want to restart now?"), MessageBox.TYPE_YESNO)
		self.close()

	def ExecuteRestart(self, result):
		if result:
			quitMainloop(3)
		else:
			self.close()
			
class VolumeSteps(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = "Setup"
		Screen.setTitle(self, _("Volume Step Setup") + "...")
		self.setup_title = _("Volume Step Setup") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label("")
		self["labelExitsave"] = Label("[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save"))

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
		self.list.append(getConfigListEntry(_("Volume Step Setup"), config.VolumeSetup.steps))
		
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
		for x in self["config"].list:
			x[1].save()
		configfile.save()

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

class RedPanel(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = "Setup"
		Screen.setTitle(self, _("Red Key Action") + "...")
		self.setup_title = _("Red Key Action") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label("")
		self["labelExitsave"] = Label("[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save"))

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
		self.list.append(getConfigListEntry(_("Red Key Action"), config.plugins.infopanel_redkey.list))
		
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
		for x in self["config"].list:
			x[1].save()
		configfile.save()

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

class RedPanelLong(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = "Setup"
		Screen.setTitle(self, _("Red Key Long Action") + "...")
		self.setup_title = _("Red Key Long Action") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label("")
		self["labelExitsave"] = Label("[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save"))

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
		self.list.append(getConfigListEntry(_("Red Key Long Action"), config.plugins.infopanel_redkeylong.list))
		
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
		for x in self["config"].list:
			x[1].save()
		configfile.save()

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
			
class BluePanel(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = "Setup"
		Screen.setTitle(self, _("Blue Key Action") + "...")
		self.setup_title = _("Blue Key Action") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label("")
		self["labelExitsave"] = Label("[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save"))

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
		self.list.append(getConfigListEntry(_("Blue Key Action"), config.plugins.infopanel_bluekey.list))
		
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
		for x in self["config"].list:
			x[1].save()
		configfile.save()

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

class BluePanelLong(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = "Setup"
		Screen.setTitle(self, _("Blue Key Long Action") + "...")
		self.setup_title = _("Blue Key Long Action") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label("")
		self["labelExitsave"] = Label("[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save"))

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
		self.list.append(getConfigListEntry(_("Blue Key Long Action"), config.plugins.infopanel_bluekeylong.list))
		
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
		for x in self["config"].list:
			x[1].save()
		configfile.save()

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
						
class GreenPanelLong(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = "Setup"
		Screen.setTitle(self, _("Green Key Long Action") + "...")
		self.setup_title = _("Green Key Long Action") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label("")
		self["labelExitsave"] = Label("[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save"))

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
		self.list.append(getConfigListEntry(_("Green Key Long Action"), config.plugins.infopanel_greenkeylong.list))
		
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
		for x in self["config"].list:
			x[1].save()
		configfile.save()

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
						
class YellowPanelLong(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = "Setup"
		Screen.setTitle(self, _("Yellow Key Long Action") + "...")
		self.setup_title = _("Yellow Key Long Action") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label("")
		self["labelExitsave"] = Label("[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save"))

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
		self.list.append(getConfigListEntry(_("Yellow Key Long Action"), config.plugins.infopanel_yellowkeylong.list))
		
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
		for x in self["config"].list:
			x[1].save()
		configfile.save()

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
						
class Info(Screen):
	def __init__(self, session, info):
		self.service = None
		Screen.__init__(self, session)

		self.skin = INFO_SKIN

		self["label2"] = Label("INFO")
		self["label1"] =  ScrollLabel()
		if info == "InfoPanel":
			self.InfoPanel()
		if info == "Sytem_info":
			self.Sytem_info()
		elif info == "FreeSpace":
			self.FreeSpace()
		elif info == "Mounts":
			self.Mounts()
		elif info == "Network":
			self.Network()
		elif info == "Kernel":
			self.Kernel()
		elif info == "Free":
			self.Free()
		elif info == "Cpu":
			self.Cpu()
		elif info == "Top":
			self.Top()
		elif info == "MemInfo":
			self.MemInfo()
		elif info == "Module":
			self.Module()
		elif info == "Mtd":
			self.Mtd()
		elif info == "Partitions":
			self.Partitions()
		elif info == "Swap":
			self.Swap()

		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
		{
			"cancel": self.Exit,
			"ok": self.ok,
			"up": self.Up,
			"down": self.Down,
		}, -1)

	def Exit(self):
		self.close()

	def ok(self):
		self.close()

	def Down(self):
		self["label1"].pageDown()

	def Up(self):
		self["label1"].pageUp()

	def InfoPanel(self):
		try:
			self["label2"].setText("INFO")
			info1 = self.Do_cmd("cat", "/etc/motd", None)
			if info1.find('wElc0me') > -1:
				info1 = info1[info1.find('wElc0me'):len(info1)] + "\n"
				info1 = info1.replace('|','')
			else:
				info1 = info1[info1.find('INFO'):len(info1)] + "\n"
			info2 = self.Do_cmd("cat", "/etc/image-version", None)
			info3 = self.Do_cut(info1 + info2)
			self["label1"].setText(info3)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def Sytem_info(self):
		try:
			self["label2"].setText(_("Image Info"))
			info1 = self.Do_cmd("cat", "/etc/version", None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occur"))


	def FreeSpace(self):
		try:
			self["label2"].setText(_("FreeSpace"))
			info1 = self.Do_cmd("df", None, "-h")
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def Mounts(self):
		try:
			self["label2"].setText(_("Mounts"))
			info1 = self.Do_cmd("mount", None, None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def Network(self):
		try:
			self["label2"].setText(_("Network"))
			info1 = self.Do_cmd("ifconfig", None, None) + '\n'
			info2 = self.Do_cmd("route", None, "-n")
			info3 = self.Do_cut(info1 + info2)
			self["label1"].setText(info3)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def Kernel(self):
		try:
			self["label2"].setText(_("Kernel"))
			info0 = self.Do_cmd("cat", "/proc/version", None)
			info = info0.split('(')
			info1 = "Name = " + info[0] + "\n"
			info2 =  "Owner = " + info[1].replace(')','') + "\n"
			info3 =  "Mainimage = " + info[2][0:info[2].find(')')] + "\n"
			info4 = "Date = " + info[3][info[3].find('SMP')+4:len(info[3])]
			info5 = self.Do_cut(info1 + info2 + info3 + info4)
			self["label1"].setText(info5)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def Free(self):
		try:
			self["label2"].setText(_("Ram"))
			info1 = self.Do_cmd("free", None, None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def Cpu(self):
		try:
			self["label2"].setText(_("Cpu"))
			info1 = self.Do_cmd("cat", "/proc/cpuinfo", None, " | sed 's/\t\t/\t/'")
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def Top(self):
		try:
			self["label2"].setText(_("Top"))
			info1 = self.Do_cmd("top", None, "-b -n1")
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def MemInfo(self):
		try:
			self["label2"].setText(_("MemInfo"))
			info1 = self.Do_cmd("cat", "/proc/meminfo", None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def Module(self):
		try:
			self["label2"].setText(_("Module"))
			info1 = self.Do_cmd("cat", "/proc/modules", None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def Mtd(self):
		try:
			self["label2"].setText(_("Mtd"))
			info1 = self.Do_cmd("cat", "/proc/mtd", None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def Partitions(self):
		try:
			self["label2"].setText(_("Partitions"))
			info1 = self.Do_cmd("cat", "/proc/partitions", None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occur"))

	def Swap(self):
		try:
			self["label2"].setText(_("Swap"))
			info0 = self.Do_cmd("cat", "/proc/swaps", None, " | sed 's/\t/ /g; s/[ ]* / /g'")
			info0 = info0.split("\n");
			info1 = ""
			for l in info0[1:]:
				l1 = l.split(" ")
				info1 = info1 + "Name: " + l1[0] + '\n'
				info1 = info1 + "Type: " + l1[1] + '\n'
				info1 = info1 + "Size: " + l1[2] + '\n'
				info1 = info1 + "Used: " + l1[3] + '\n'
				info1 = info1 + "Prio: " + l1[4] + '\n\n'
			if info1[-1:] == '\n': info1 = info1[:-1]
			if info1[-1:] == '\n': info1 = info1[:-1]
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occur"))


	def Do_find(self, text, search):
		text = text + ' '
		ret = ""
		pos = text.find(search)
		pos1 = text.find(" ", pos)
		if pos > -1:
			ret = text[pos + len(search):pos1]
		return ret

	def Do_cut(self, text):
		text1 = text.split("\n")
		text = ""
		for line in text1:
			text = text + line[:95] + "\n"
		if text[-1:] == '\n': text = text[:-1]
		return text

	def Do_cmd(self, cmd , file, arg , pipe = ""):
		try:
			if file != None:
				if os.path.exists(file) is True:
					o = command(cmd + ' ' + file + pipe, 0)
				else:
					o = "File not found: \n" + file
			else:
				if arg == None:
					o = command(cmd, 0)
				else:
					o = command(cmd + ' ' + arg, 0)
			return o
		except:
			o = ''
			return o
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

