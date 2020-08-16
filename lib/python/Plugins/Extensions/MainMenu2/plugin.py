from __future__ import print_function
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Button import Button
from Components.ConfigList import ConfigList
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
import os
import commands
from enigma import getDesktop
from Plugins.SystemPlugins.SoftwareManager.ImageBackup import ImageBackup
from Plugins.Extensions.Infopanel.Flash_local import FlashOnline
from Plugins.Extensions.Infopanel.plugin import RedPanel, BluePanel, KeymapSel
from Plugins.Extensions.MainMenu2.usemenu import User_MainMenu, UserMainMenuSetup
from Screens.ScanSetup import ScanSimple, ScanSetup
from Screens.VideoMode import VideoSetup
from Screens.SkinSelector import SkinSelector
from Screens.Setup import Setup
global mmpath
global XIndex

#change to FullHD
if getDesktop(0).size().width() == 1920:
	loadSkin("/usr/lib/enigma2/python/Plugins/Extensions/MainMenu2/skins/defaultHD/skinHD.xml")
	mmpath = '/usr/lib/enigma2/python/Plugins/Extensions/MainMenu2/skins/defaultHD/images/'	
else:
	loadSkin("/usr/lib/enigma2/python/Plugins/Extensions/MainMenu2/skins/defaultHD/skin.xml")
	mmpath = '/usr/lib/enigma2/python/Plugins/Extensions/MainMenu2/skins/defaultHD/images/default/'
class MM_MainMenu(Screen):
	def __init__(self, session):
		Screen.__init__(self, session) 
		self["text"] = Label(_("Infopanel"))
		self["left"] = Pixmap()
		self["middle"] = Pixmap()
		self["right"] = Pixmap()
		self.Console = Console()
		list = []
		list.append((_("InfoPanel"), "2MM_Infopanel", "menu_infopanel", "50"))
		list.append((_("InfoPanel"), "2MM_Infopanel", "menu_infopanel", "50"))
		list.append((_("Setup"), "2MM_Setup", "menu_setup", "50"))
		list.append((_("Plugins"), "2MM_Plugins", "menu_plugins", "50"))
		list.append((_("UserMenu"), "2MM_UserMenu", "menu_UserMenu", "50"))
		list.append(("Exit", "Exit", "menu_exit", "50"))
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
			"left": self.prev
		}, -1)
              
	def next(self):
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(1)	
		self["menu"].selectNext()
		if self["menu"].getIndex() == 5:
			self["menu"].setIndex(1)
		self.update()
	def prev(self):
		self["menu"].selectPrevious()
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(4)
		self.update()
	def update(self):
		if self["menu"].getIndex() == 1:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconSetupsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconInfopanel.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconUserMenusw.png")
		elif self["menu"].getIndex() == 2:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconPluginssw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconSetup.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconInfopanelsw.png")
		elif self["menu"].getIndex() == 3:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconUserMenusw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconPlugins.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconSetupsw.png")
		elif self["menu"].getIndex() == 4:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconInfopanelsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconUserMenu.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconPluginssw.png")			
		self["text"].setText(self["menu"].getCurrent()[0])
	def okbuttonClick(self):
		from Screens.MessageBox import MessageBox
		selection = self["menu"].getCurrent()
		if selection is not None:
			if selection[1] == "2MM_Infopanel":
				self.session.openWithCallback(self.update, Infopanel_MainMenu)
			elif selection[1] == "2MM_Setup":
				self.session.openWithCallback(self.update, Setup_MainMenu)
			elif selection[1] == "2MM_Plugins":
				self.session.openWithCallback(self.update, PluginBrowser)
			elif selection[1] == "2MM_UserMenu":
				self.session.openWithCallback(self.update, User_MainMenu)				

	def error(self, error):
		from Screens.MessageBox import MessageBox
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)
	def Exit(self):
		self.close()
		
class Infopanel_MainMenu(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self["text"] = Label(_("ImageManager"))
		self["left"] = Pixmap()
		self["middle"] = Pixmap()
		self["right"] = Pixmap()
		self.Console = Console()
		list = []
		list.append((_("ImageManager"), "2MM_ImageManager", "menu_imagemanager", "50"))
		list.append((_("ImageManager"), "2MM_ImageManager", "menu_imagemanager", "50"))
		list.append((_("RemoteManager"), "2MM_RemoteManager", "menu_remotemanager", "50"))
		list.append(("Exit", "Exit", "menu_exit", "50"))
		self["menu"] = List(list)
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
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
			"left": self.prev
		}, -1)
                
	def next(self):
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(1)	
		self["menu"].selectNext()
		if self["menu"].getIndex() == 3:
			self["menu"].setIndex(1)
		self.update()
	def prev(self):
		self["menu"].selectPrevious()
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(2)
		self.update()
	def update(self):
		if self["menu"].getIndex() == 1:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconRemotemanagersw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconImagemanager.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconRemotemanagersw.png")
		elif self["menu"].getIndex() == 2:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconImagemanagersw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconRemotemanager.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconImagemanagersw.png")
		self["text"].setText(self["menu"].getCurrent()[0])
	def okbuttonClick(self):
		from Screens.MessageBox import MessageBox
		selection = self["menu"].getCurrent()
		if selection is not None:
			if selection[1] == "2MM_ImageManager":
				self.session.openWithCallback(self.update, ImageManager_MainMenu)
			elif selection[1] == "2MM_RemoteManager":
				self.session.openWithCallback(self.update, RemoteManager_MainMenu)

	def error(self, error):
		from Screens.MessageBox import MessageBox
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)
	def Exit(self):
		self.close()
		
class ImageManager_MainMenu(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self["text"] = Label(_("Backup"))
		self["left"] = Pixmap()
		self["middle"] = Pixmap()
		self["right"] = Pixmap()
		self.Console = Console()
		list = []
		list.append((_("Backup"), "2MM_Backup", "menu_backup", "50"))
		list.append((_("Backup"), "2MM_Backup", "menu_backup", "50"))
		list.append((_("FlashLocal"), "2MM_FlashLocal", "menu_flashlocal", "50"))
		list.append(("Exit", "Exit", "menu_exit", "50"))
		self["menu"] = List(list)
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
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
			"left": self.prev
		}, -1)
                
	def next(self):
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(1)	
		self["menu"].selectNext()
		if self["menu"].getIndex() == 3:
			self["menu"].setIndex(1)
		self.update()
	def prev(self):
		self["menu"].selectPrevious()
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(2)
		self.update()
	def update(self):
		if self["menu"].getIndex() == 1:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconFlashlocalsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconBackup.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconFlashlocalsw.png")
		elif self["menu"].getIndex() == 2:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconBackupsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconFlashlocal.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconBackupsw.png")
		self["text"].setText(self["menu"].getCurrent()[0])
	def okbuttonClick(self):
		from Screens.MessageBox import MessageBox
		selection = self["menu"].getCurrent()
		if selection is not None:
			if selection[1] == "2MM_Backup":
				self.session.openWithCallback(self.update, ImageBackup)
			elif selection[1] == "2MM_FlashLocal":
				self.session.openWithCallback(self.update, FlashOnline)

	def error(self, error):
		from Screens.MessageBox import MessageBox
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)
	def Exit(self):
		self.close()
                
class RemoteManager_MainMenu(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self["text"] = Label(_("RedPanel"))
		self["left"] = Pixmap()
		self["middle"] = Pixmap()
		self["right"] = Pixmap()
		self.Console = Console()
		list = []
		list.append((_("RedPanel"), "2MM_RedPanel", "menu_redpanel", "50"))
		list.append((_("RedPanel"), "2MM_RedPanel", "menu_redpanel", "50"))
		list.append((_("BluePanel"), "2MM_BluePanel", "menu_bluepanel", "50"))
		list.append((_("KeymapPanel"), "2MM_KeymapPanel", "menu_keymappanel", "50"))
		list.append(("Exit", "Exit", "menu_exit", "50"))
		self["menu"] = List(list)
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
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
			"left": self.prev
		}, -1)
                
	def next(self):
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(1)	
		self["menu"].selectNext()
		if self["menu"].getIndex() == 4:
			self["menu"].setIndex(1)
		self.update()
	def prev(self):
		self["menu"].selectPrevious()
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(3)
		self.update()
	def update(self):
		if self["menu"].getIndex() == 1:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconBluepanelsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconRedpanel.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconKeymappanalsw.png")
		elif self["menu"].getIndex() == 2:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconKeymappanalsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconBluepanel.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconRedpanelsw.png")
		elif self["menu"].getIndex() == 3:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconRedpanelsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconKeymappanel.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconBluepanelsw.png")
		self["text"].setText(self["menu"].getCurrent()[0])
	def okbuttonClick(self):
		from Screens.MessageBox import MessageBox
		selection = self["menu"].getCurrent()
		if selection is not None:
			if selection[1] == "2MM_RedPanel":
				self.session.openWithCallback(self.update, RedPanel)
			elif selection[1] == "2MM_BluePanel":
				self.session.openWithCallback(self.update, BluePanel)
			elif selection[1] == "2MM_KeymapPanel":
				self.session.openWithCallback(self.update, KeymapSel)

	def error(self, error):
		from Screens.MessageBox import MessageBox
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)
	def Exit(self):
		self.close()                		
		
class Setup_MainMenu(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self["text"] = Label(_("ChannelSearch"))
		self["left"] = Pixmap()
		self["middle"] = Pixmap()
		self["right"] = Pixmap()
		self.Console = Console()
		list = []
		list.append((_("ChannelSearch"), "2MM_ChannelSearch", "menu_channelsearch", "50"))
		list.append((_("ChannelSearch"), "2MM_ChannelSearch", "menu_channelsearch", "50"))
		list.append((_("System"), "2MM_System", "menu_system", "50"))
		list.append(("Exit", "Exit", "menu_exit", "50"))
		self["menu"] = List(list)
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
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
			"left": self.prev
		}, -1)
                
	def next(self):
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(1)	
		self["menu"].selectNext()
		if self["menu"].getIndex() == 3:
			self["menu"].setIndex(1)
		self.update()
	def prev(self):
		self["menu"].selectPrevious()
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(2)
		self.update()
	def update(self):
		if self["menu"].getIndex() == 1:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconSystemsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconChannelsearch.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconSystemsw.png")
		elif self["menu"].getIndex() == 2:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconChannelsearchsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconSystem.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconChannelsearchsw.png")
		self["text"].setText(self["menu"].getCurrent()[0])
	def okbuttonClick(self):
		from Screens.MessageBox import MessageBox
		selection = self["menu"].getCurrent()
		if selection is not None:
			if selection[1] == "2MM_ChannelSearch":
				self.session.openWithCallback(self.update, ChannelSearch_MainMenu)
			elif selection[1] == "2MM_System":
				self.session.openWithCallback(self.update, System_MainMenu)

	def error(self, error):
		from Screens.MessageBox import MessageBox
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)
	def Exit(self):
		self.close()
		
class ChannelSearch_MainMenu(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self["text"] = Label(_("Automatic"))
		self["left"] = Pixmap()
		self["middle"] = Pixmap()
		self["right"] = Pixmap()
		self.Console = Console()
		list = []
		list.append((_("Automatic"), "2MM_Automatic", "menu_automatic", "50"))
		list.append((_("Automatic"), "2MM_Automatic", "menu_automatic", "50"))
		list.append((_("Manuell"), "2MM_Manuell", "menu_manuell", "50"))
		list.append(("Exit", "Exit", "menu_exit", "50"))
		self["menu"] = List(list)
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
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
			"left": self.prev
		}, -1)
                
	def next(self):
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(1)	
		self["menu"].selectNext()
		if self["menu"].getIndex() == 3:
			self["menu"].setIndex(1)
		self.update()
	def prev(self):
		self["menu"].selectPrevious()
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(2)
		self.update()
	def update(self):
		if self["menu"].getIndex() == 1:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconManuelsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconAutomatic.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconManuelsw.png")
		elif self["menu"].getIndex() == 2:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconAutomaticsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconManuel.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconAutomaticsw.png")
		self["text"].setText(self["menu"].getCurrent()[0])
	def okbuttonClick(self):
		from Screens.MessageBox import MessageBox
		selection = self["menu"].getCurrent()
		if selection is not None:
			if selection[1] == "2MM_Automatic":
				self.session.openWithCallback(self.update, ScanSimple)
			elif selection[1] == "2MM_Manuell":
				self.session.openWithCallback(self.update, ScanSetup)

	def error(self, error):
		from Screens.MessageBox import MessageBox
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)
	def Exit(self):
		self.close()
                
class System_MainMenu(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self["text"] = Label(_("AV"))
		self["left"] = Pixmap()
		self["middle"] = Pixmap()
		self["right"] = Pixmap()
		self.Console = Console()
		list = []
		list.append((_("AV"), "2MM_AV", "menu_av", "50"))
		list.append((_("AV"), "2MM_AV", "menu_av", "50"))
		list.append((_("Gui"), "2MM_Gui", "menu_gui", "50"))
		list.append(("Exit", "Exit", "menu_exit", "50"))
		self["menu"] = List(list)
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
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
			"left": self.prev
		}, -1)
                
	def next(self):
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(1)	
		self["menu"].selectNext()
		if self["menu"].getIndex() == 3:
			self["menu"].setIndex(1)
		self.update()
	def prev(self):
		self["menu"].selectPrevious()
		if self["menu"].getIndex() == 0:
			self["menu"].setIndex(2)
		self.update()
	def update(self):
		if self["menu"].getIndex() == 1:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconGuisw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconAV.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconGuisw.png")
		elif self["menu"].getIndex() == 2:
			self["left"].instance.setPixmapFromFile(mmpath +"MenuIconAVsw.png")
			self["middle"].instance.setPixmapFromFile(mmpath +"MenuIconGui.png")
			self["right"].instance.setPixmapFromFile(mmpath +"MenuIconAVsw.png")
		self["text"].setText(self["menu"].getCurrent()[0])
	def okbuttonClick(self):
		from Screens.MessageBox import MessageBox
		selection = self["menu"].getCurrent()
		if selection is not None:
			if selection[1] == "2MM_AV":
				self.session.openWithCallback(self.update, VideoSetup)
			elif selection[1] == "2MM_Gui":
				self.session.openWithCallback(self.update, User_MainMenu)

	def error(self, error):
		from Screens.MessageBox import MessageBox
		self.session.open(MessageBox,("UNEXPECTED ERROR:\n%s") % (error),  MessageBox.TYPE_INFO)
	def Exit(self):
		self.close()    

def sessionMainM(session, reason, **kwargs):
        print("EasyMenu Load")


def Plugins(**kwargs):
	plugin_list = [
		PluginDescriptor(
			where = PluginDescriptor.WHERE_SESSIONSTART,
			needsRestart = False,
			fnc = sessionMainM),
			]
	return plugin_list;