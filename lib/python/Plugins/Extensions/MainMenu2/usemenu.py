from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.ConfigList import ConfigList
from Components.Network import iNetwork
from Screens.NetworkSetup import *
from Components.config import *
from Components.Console import Console
from skin import loadSkin
from Components.Label import Label
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
from Plugins.Plugin import PluginDescriptor
from Tools.Directories import pathExists, fileExists
from Screens.PluginBrowser import PluginDownloadBrowser, PluginBrowser
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from __init__ import _
from Components.Button import Button
import os
import commands
from enigma import getDesktop
from Plugins.SystemPlugins.SoftwareManager.ImageBackup import ImageBackup
from Plugins.Extensions.Infopanel.Flash_local import FlashOnline
from Plugins.Extensions.Infopanel.plugin import RedPanel, BluePanel, KeymapSel
from Screens.ScanSetup import ScanSimple, ScanSetup
from Screens.VideoMode import VideoSetup
from Screens.SkinSelector import SkinSelector
from Screens.Setup import Setup

from Plugins.Extensions.BMediaCenter.Weather import *
from Plugins.Extensions.BMediaCenter.plugin import DMC_MainMenu    
from Plugins.Extensions.Infopanel.TelnetCommand import TelnetCommand
from Plugins.Extensions.Infopanel.SoftwarePanel import SoftwarePanel
from Plugins.SystemPlugins.SoftwareManager.plugin import SoftwareManagerSetup
global mmpath
global XIndex
#change to FullHD
if getDesktop(0).size().width() == 1920:
	loadSkin("/usr/lib/enigma2/python/Plugins/Extensions/MainMenu2/skins/defaultHD/skinHD.xml")
	mmpath = '/usr/lib/enigma2/python/Plugins/Extensions/MainMenu2/skins/defaultHD/images/'	
else:
	loadSkin("/usr/lib/enigma2/python/Plugins/Extensions/MainMenu2/skins/defaultHD/skin.xml")
	mmpath = '/usr/lib/enigma2/python/Plugins/Extensions/MainMenu2/skins/defaultHD/images/default/'
class UserMainMenuSetup(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.Console = Console()
		self["actions"] = ActionMap(["SetupActions","OkCancelActions"],
		{
			"ok": self.keyOK,
			"cancel": self.close,
			"left": self.keyLeft,
			"right": self.keyRight
		
		}, -1)
		self.list = []
		self["configlist"] = ConfigList(self.list)
		self.list.append(getConfigListEntry(_("Network Interface"), config.plugins.um_globalsettings.networkinterface))
		self.list.append(getConfigListEntry(_("Telnet Command"), config.plugins.um_globalsettings.telnetcommand))
		self.list.append(getConfigListEntry(_("Software Update"), config.plugins.um_globalsettings.softwareupdate))
		self.list.append(getConfigListEntry(_("Software Manager Setup"), config.plugins.um_globalsettings.softwaremanagersetup))
	        self.list.append(getConfigListEntry(_("Skin"), config.plugins.um_globalsettings.Skin))
	        self.list.append(getConfigListEntry(_("Media Center"), config.plugins.um_globalsettings.Mediacenter))
	        self.list.append(getConfigListEntry(_("Weather"), config.plugins.um_globalsettings.Weather))
        
        def keyLeft(self):
		self["configlist"].handleKey(KEY_LEFT)
	def keyRight(self):
		self["configlist"].handleKey(KEY_RIGHT)
	def keyNumber(self, number):
		self["configlist"].handleKey(KEY_0 + number)
	def keyOK(self):
		config.plugins.um_globalsettings.save()
		self.close()





class User_MainMenu(Screen):
	def __init__(self, session):
		Screen.__init__(self, session) 
		self["left"] = Pixmap()
		self["middle"] = Pixmap()
		self["right"] = Pixmap()		
		self.Console = Console()
		list = []
		testl = "0"
		if config.plugins.um_globalsettings.networkinterface.value == True:
		        list.append((_("Network Interface"), "NetworkAdapterSelection", "MenuIconNetwork.png", "MenuIconNetworksw.png"))
		        if testl == "0":
		                self["text"] = Label(_("Network Interface"))
		                list.append((_("Network Interface"), "NetworkAdapterSelection", "MenuIconNetwork.png", "MenuIconNetworksw.png"))
                                testl = "1"
		if config.plugins.um_globalsettings.telnetcommand.value == True:
		        list.append((_("Telnet Command"), "TelnetCommand", "MenuIconTelnet.png", "MenuIconTelnetsw.png"))
		        if testl == "0":
                                self["text"] = Label(_("Telnet Command"))
		                list.append((_("Telnet Command"), "TelnetCommand", "MenuIconTelnet.png", "MenuIconTelnetsw.png"))
                                testl = "1"
		if config.plugins.um_globalsettings.softwareupdate.value == True:
		        list.append((_("Software Update"), "SoftwarePanel", "MenuIconSoftwareUpdate.png", "MenuIconSoftwareUpdatesw.png"))
		        if testl == "0":
		                self["text"] = Label(_("Software Update"))
		                list.append((_("Software Update"), "SoftwarePanel", "MenuIconSoftwareUpdate.png", "MenuIconSoftwareUpdatesw.png"))
                                testl = "1"
		if config.plugins.um_globalsettings.softwaremanagersetup.value == True:
		        list.append((_("Software Manager Setup"), "SoftwareManagerSetup", "MenuIconSoftwareManager.png", "MenuIconSoftwareManagersw.png"))
		        if testl == "0":
		                self["text"] = Label(_("Software Manager Setup"))
		                list.append((_("Software Manager Setup"), "SoftwareManagerSetup", "SoftwareManagerSetup.png", "MenuIconSoftwareManagersw.png"))
                                testl = "1"
		if config.plugins.um_globalsettings.Skin.value == True:
		        list.append((_("skin selektor"), "SkinSelector", "MenuIconSkin.png", "MenuIconSkinsw.png"))
		        if testl == "0":
		                self["text"] = Label(_("Skin Selektor"))
		                list.append((_("skin selektor"), "SkinSelector", "MenuIconSkin.png", "MenuIconSkinsw.png"))
                                testl = "1"                                
		if config.plugins.um_globalsettings.Mediacenter.value == True:
		        list.append((_("Media Center"), "DMC_MainMenu", "MenuIconMC.png", "MenuIconMCsw.png"))
		        if testl == "0":
		                self["text"] = Label(_("Media Center"))
		                list.append((_("Media Center"), "DMC_MainMenu", "MenuIconMC.png", "MenuIconMCsw.png"))
                                testl = "1" 
		if config.plugins.um_globalsettings.Weather.value == True:
		        list.append((_("Weather"), "MeteoMain", "MenuIconWeather.png", "MenuIconWeathersw.png"))
		        if testl == "0":
		                self["text"] = Label(_("Yahoo Weather"))
		                list.append((_("Weather"), "MeteoMain", "MenuIconWeather.png", "MenuIconWeathersw.png"))
                                testl = "1"                                 
                if testl == "0":
                        self["text"] = Label(_("No UserMainMenuSetup"))                                                        		        
		        list.append((_("Exit"), "Exit", "MenuIconUserMenu.png", "MenuIconUserMenusw.png"))
		else:
                        list.append((_("Exit"), "Exit", "MenuIconUserMenu.png", "MenuIconUserMenusw.png"))        
		global Xlen
		Xlen = len(list)
		self['key_blue'] = Button(_('UserMenuSetup'))		
		self["menu"] = List(list)
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions"],
		{
			"cancel": self.Exit,
			"ok": self.okbuttonClick,
			"right": self.next,
			"upRepeated": self.prev,
			"down": self.next,
			"downRepeated": self.next,
			"leftRepeated": self.prev,
			"rightRepeated": self.next,
			"up": self.prev,
			"left": self.prev,
			"blue":self.User_MainMenuSetup,				
		}, -1)

                
	def User_MainMenuSetup(self):
	        from Screens.MessageBox import MessageBox
	        self.session.openWithCallback(self.update, UserMainMenuSetup)
		
	def prev(self):
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(1)	
		self["menu"].selectNext()
		if self["menu"].getIndex() == (Xlen-1):
			self["menu"].setIndex(1)
		self.update()
	def next(self):
		self["menu"].selectPrevious()
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(Xlen-2)
		self.update()
	def update(self):
	        self["middle"].instance.setPixmapFromFile(mmpath + self["menu"].getCurrent()[2])
		index = self["menu"].getIndex()
		if index == 1:
			newindex = Xlen-2
                else:
                	newindex = index-1
		self["menu"].setIndex(newindex)
		self["left"].instance.setPixmapFromFile(mmpath + self["menu"].getCurrent()[3])
		if index == Xlen-2:
			newindex = 1
                else:
                	newindex = index+1		
                self["menu"].setIndex(newindex)
                self["right"].instance.setPixmapFromFile(mmpath + self["menu"].getCurrent()[3])
		self["menu"].setIndex(index)
                self["text"].setText(self["menu"].getCurrent()[0])
	def okbuttonClick(self):
		from Screens.MessageBox import MessageBox
		selection = self["menu"].getCurrent()
		if selection is not None:
			if "Exit" in selection:
		        	self.Exit()
                        else:
                                xopen = eval(self["menu"].getCurrent()[1])
				self.session.openWithCallback(self.update, xopen)

	def error(self, error):
		from Screens.MessageBox import MessageBox
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)

		
	def Exit(self):
		self.close()
