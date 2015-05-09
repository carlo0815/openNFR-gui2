from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.InfoBar import InfoBar
from Plugins.Extensions.Infopanel.Console import Console
from Components.ConfigList import ConfigListScreen
from Components.Sources.List import List
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.EventView import EventViewSimple
from Components.ActionMap import ActionMap
from Components.FileList import FileList
from Components.MenuList import MenuList
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Tools.LoadPixmap import LoadPixmap
from Components.config import config, ConfigSubsection, ConfigText, ConfigYesNo, ConfigSelection, getConfigListEntry, configfile
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_PLUGINS
from Tools.HardwareInfo import HardwareInfo
from ServiceReference import ServiceReference
from Screens.InputBox import InputBox
from enigma import eConsoleAppContainer, eServiceReference, ePicLoad, getDesktop, eServiceCenter
from os import system as os_system
from os import stat as os_stat
from os import walk as os_walk
from os import popen as os_popen
from os import rename as os_rename
from os import mkdir as os_mkdir
from os import path as os_path
from os import remove as os_remove
from os import listdir as os_listdir
from time import strftime as time_strftime
from time import localtime as time_localtime
import os
from Screens.VirtualKeyBoard import VirtualKeyBoard

class TelnetCommand(Screen, ConfigListScreen):
	skin = """
<screen name="TelnetCommand" position="center,center" size="820,180" title="TelnetCommand">
  <ePixmap pixmap="skin_default/buttons/key_red.png" position="9,128" size="30,30" alphatest="blend" />
  <ePixmap pixmap="skin_default/buttons/key_green.png" position="239,128" size="30,30" alphatest="blend" />
  <ePixmap pixmap="skin_default/buttons/key_blue.png" position="477,128" size="30,30" alphatest="blend" />
  <widget name="key_red" render="Label" position="43,131" size="160,25" zPosition="1" font="Regular;22" halign="left" backgroundColor="black" transparent="1" />
  <widget name="key_green" render="Label" position="276,131" size="160,25" zPosition="1" font="Regular;22" halign="left" backgroundColor="black" transparent="1" />
  <widget name="key_blue" render="Label" position="517,131" size="250,25" zPosition="1" font="Regular;22" halign="left" backgroundColor="black" transparent="1" />
  <widget name="config" position="6,10" size="800,100" zPosition="1" scrollbarMode="showOnDemand" transparent="1" />
</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("TelnetCommand"))
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Send Command"))
		self["key_blue"] = Label(_("Use VirtualKeyboard"))
		self.VirtualKeyBoard = VirtualKeyBoard 	
		global NFRTelnet_command
                global NFRTelnet_execute
                NFRTelnet_command = ConfigText(visible_width = 200, fixed_size=False)
                NFRTelnet_execute = ConfigYesNo(default = False) 
		self.list = []
		ConfigListScreen.__init__(self, self.list, session=session)
		self.createsetup()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"red": self.cancel,
				"ok": self.ok,
				"green": self.ok,
				"blue": self.blue, 				
			}, -2)

	def createsetup(self):
		self.list = []
		self.list.append(getConfigListEntry(_("Telnet Command: "),
			NFRTelnet_command))
		self.list.append(getConfigListEntry(_("Execute Command: "),
			NFRTelnet_execute))			
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		self.config = config

	def ok(self):
		if NFRTelnet_execute.value == True:
			NFRTelnet_command.value
			target = NFRTelnet_command.value
                	self.session.open(Console, title=_("Telnet Command."), cmdlist = [target], closeOnSuccess = False)
                else:
                        self.session.open(MessageBox, _('Your Choice is no Command execute!'), type=MessageBox.TYPE_INFO, timeout=10)

	def cancel(self):
	        self.close()
	        

	def blue(self):
		self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=_('Insert your Command!'), text=NFRTelnet_command.value)

	def VirtualKeyBoardCallback(self, callback = None):
		if callback is not None and len(callback):
			self["config"].getCurrent()[1].setValue(callback)
			self["config"].invalidate(self["config"].getCurrent()) 
