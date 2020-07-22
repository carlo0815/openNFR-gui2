# -*- coding: utf-8 -*-

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

from __future__ import print_function
from enigma import eTimer, ePicLoad, getDesktop, loadPic
from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry, ConfigSubsection, ConfigSelection, ConfigYesNo, NoSave, ConfigNothing, ConfigNumber, configfile, ConfigBoolean
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.SkinSelector import SkinSelector
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import *
from Tools.LoadPixmap import LoadPixmap
from Tools.WeatherID import get_woeid_from_yahoo
from Tools import Notifications
from os import listdir, remove, rename, system, path, symlink, chdir, makedirs
from Components.AVSwitch import AVSwitch
import shutil
import glob

from __init__ import _


cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
if cur_skin == "skin.xml":
        cur_skin = "skin_default"

# Atile
config.plugins.NfrHD = ConfigSubsection()
config.plugins.NfrHD.refreshInterval = ConfigNumber(default=10)
config.plugins.NfrHD.woeid = ConfigNumber(default = 638242)
config.plugins.NfrHD.tempUnit = ConfigSelection(default="Celsius", choices = [
				("Celsius", _("Celsius")),
				("Fahrenheit", _("Fahrenheit"))
				])

def isInteger(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

class WeatherLocationChoiceList(Screen):
	skin = """
		<screen name="WeatherLocationChoiceList" position="center,center" size="1280,720" title="Location list" >
			<widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" transparent="1" />
			<widget name="choicelist" position="70,115" size="700,480" scrollbarMode="showOnDemand" scrollbarWidth="6" transparent="1" />
			<eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="red" />
			<eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="green" />
			<eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="yellow" />
			<eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="blue" />
			<widget name="key_red" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_green" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
		</screen>
		"""

	def __init__(self, session, location_list):
		self.session = session
		self.location_list = location_list
		list = []
		Screen.__init__(self, session)
		self.title = _("Location list")
		self["choicelist"] = MenuList(list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))
		self["myActionMap"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"ok": self.keyOk,
			"green": self.keyOk,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
		}, -1)
		self.createChoiceList()

	def createChoiceList(self):
		list = []
		for x in self.location_list:
			list.append((str(x[1]), str(x[0])))
		self["choicelist"].l.setList(list)

	def keyOk(self):
		returnValue = self["choicelist"].l.getCurrentSelection()[1]
		if returnValue is not None:
			self.close(returnValue)
		else:
			self.keyCancel()

	def keyCancel(self):
		self.close(None)


class NfrHD_Config(Screen, ConfigListScreen):

	skin = """
		<screen name="NfrHD_Config" position="center,center" size="1280,720" title="NfrHD Setup" >
			<widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" transparent="1" />
			<widget name="config" position="70,115" size="700,480" scrollbarMode="showOnDemand" scrollbarWidth="6" transparent="1" />
			<widget name="Picture" position="808,342" size="400,225" alphatest="on" />
			<eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="red" />
			<eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="green" />
			<eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="yellow" />
			<eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="blue" />
			<widget name="key_red" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_green" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_yellow" position="660,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_blue" position="955,635" size="260,25" zPosition="0" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
		</screen>
	"""

	def __init__(self, session, args = 0):
		self.session = session
		self.skin_lines = []
		self.changed_screens = False
		Screen.__init__(self, session)
		global cur_skin
		global color_test
		global background_test
		global infobar_test
		global sib_test
		global sb_test
		global ul_test
		global ch_se_test                
		global ev_test
                global clock_test                
		color_test = True
		background_test = True
		infobar_test = True
		sib_test = True
		ch_se_test = True
		ev_test = True		
		sb_test = True				
		ul_test = True
		clock_test = True                				
		self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
		if glob.glob(self.skin_base_dir + 'colors_*') == True:
			color_test = False                
		if glob.glob(self.skin_base_dir + 'background_*') == True:
			background_test = False                
		if glob.glob(self.skin_base_dir + 'infobar_*') == True:
			infobar_test = False                
		if glob.glob(self.skin_base_dir + 'sib_*') == True:			
			sib_test = False
		if glob.glob(self.skin_base_dir + 'ch_se_*') == True:			
			ch_se_test = False                            
		if glob.glob(self.skin_base_dir + 'ev_*') == True:			
			ev_test = False  
		if glob.glob(self.skin_base_dir + 'sb_*') == True:			
			sb_test = False 
		if glob.glob(self.skin_base_dir + 'ul_*') == True:			
			ul_test = False
		if glob.glob(self.skin_base_dir + 'clock_*') == True:			
			ul_test = False                          			
                		
		self.start_skin = config.skin.primary_skin.value
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self['Preview'] = Pixmap()
	        self.getInitConfig()
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))
		self["key_yellow"] = Label()
		self["key_blue"] = Label(_("About"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.keyGreen,
				"red": self.cancel,
				"yellow": self.keyYellow,
				"blue": self.about,
				"cancel": self.cancel,
				"ok": self.keyOk,
				"menu": self.weather
			}, -2)
			
		self["Picture"] = Pixmap()
		
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.createConfigList()
		
	def weather(self):
		try:
                	from Plugins.Extensions.WeatherPlugin.plugin import MSNWeatherPlugin#
			self.session.open(MSNWeatherPlugin)
		except Exception as e:
			self.session.open(MessageBox, _("The Weather plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
		
	def getInitConfig(self):
		self.title = _("%s - Setup") % cur_skin
		self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
		self.default_background_file = "background_Original.xml"
		self.default_color_file = "colors_Original.xml"
		self.default_infobar_file = "infobar_Original.xml"
		self.default_sib_file = "sib_Original.xml"
		self.default_ch_se_file = "ch_se_Original.xml"		
		self.default_ev_file = "ev_Original.xml"		
		self.default_sb_file = "sb_Original.xml"				
		self.default_ul_file = "ul_Original.xml"
		self.default_clock_file = "clock_Original.xml"				
		self.color_file = "skin_user_colors.xml"
		self.background_file = "skin_user_header.xml"
		self.infobar_file = "skin_user_infobar.xml"
		self.sib_file = "skin_user_sib.xml"
		self.ch_se_file = "skin_user_ch_se.xml"
		self.ev_file = "skin_user_ev.xml"
		self.sb_file = "skin_user_sb.xml"
		self.ul_file = "skin_user_ul.xml"
		self.clock_file = "skin_user_clock.xml"
		if color_test == True:
			current_color = self.getCurrentColor()
			color_choices = self.getPossibleColor()
			default_color = ("default")
			config.myNfrHD_style = ConfigSelection(default=default_color, choices = color_choices)
			if current_color is None:
				current_color = default_color
			if default_color not in color_choices:
				color_choices.append(default_color)
			current_color = current_color
		if background_test == True:
			current_background = self.getCurrentBackground() 
			background_choices = self.getPossibleBackground()
			default_background = ("default")
			config.myNfrHD_background = ConfigSelection(default=default_background, choices = background_choices)		
			if current_background is None:
				current_background = default_background
			if default_background not in background_choices:
				background_choices.append(default_background)
			current_background = current_background
		if infobar_test == True:
			current_infobar = self.getCurrentInfobar()
			infobar_choices = self.getPossibleInfobar()
			default_infobar = ("default")
			config.myNfrHD_infobar = ConfigSelection(default=default_infobar, choices = infobar_choices)		
			if current_infobar is None:
				current_infobar = default_infobar
			if default_infobar not in infobar_choices:
				infobar_choices.append(default_infobar)
			current_infobar = current_infobar
		if sib_test == True:
			current_sib = self.getCurrentSib() 
			sib_choices = self.getPossibleSib()
			default_sib = ("default")
			config.myNfrHD_sib = ConfigSelection(default=default_sib, choices = sib_choices)		
			if current_sib is None:
				current_sib = default_sib
			if default_sib not in sib_choices:
				sib_choices.append(default_sib)
			current_sib = current_sib
		if ch_se_test == True:
			current_ch_se = self.getCurrentCh_se() 
			ch_se_choices = self.getPossibleCh_se()
			default_ch_se = ("default")
			config.myNfrHD_ch_se = ConfigSelection(default=default_ch_se, choices = ch_se_choices)		
			if current_ch_se is None:
				current_ch_se = default_ch_se
			if default_ch_se not in ch_se_choices:
				ch_se_choices.append(default_ch_se)
			current_ch_se = current_ch_se			
		if ev_test == True:
			current_ev = self.getCurrentEV() 
			ev_choices = self.getPossibleEV()
			default_ev = ("default")
			config.myNfrHD_ev = ConfigSelection(default=default_ev, choices = ev_choices)		
			if current_ev is None:
				current_ev = default_ev
			if default_ev not in ev_choices:
				ev_choices.append(default_ev)
			current_ev = current_ev
		if sb_test == True:
			current_sb = self.getCurrentSB() 
			sb_choices = self.getPossibleSB()
			default_sb = ("default")
			config.myNfrHD_sb = ConfigSelection(default=default_sb, choices = sb_choices)		
			if current_sb is None:
				current_sb = default_sb
			if default_sb not in sb_choices:
				sb_choices.append(default_sb)
			current_sb = current_sb
		if ul_test == True:
			current_ul = self.getCurrentUL() 
			ul_choices = self.getPossibleUL()
			default_ul = ("default")
			config.myNfrHD_ul = ConfigSelection(default=default_ul, choices = ul_choices)		
			if current_ul is None:
				current_ul = default_ul
			if default_ul not in ul_choices:
				ul_choices.append(default_ul)
			current_ul = current_ul
		if clock_test == True:
			current_clock = self.getCurrentCLOCK() 
			clock_choices = self.getPossibleCLOCK()
			default_clock = ("default")
			config.myNfrHD_clock = ConfigSelection(default=default_clock, choices = clock_choices)		
			if current_clock is None:
				current_clock = default_clock
			if default_clock not in clock_choices:
				clock_choices.append(default_clock)
			current_clock = current_clock	                        						
		
		myatile_active = self.getmyAtileState()
		config.myNfrHD_active = ConfigYesNo(default=myatile_active)
		#choices = self.getPossibleFont()
		self.myNfrHD_fake_entry = ConfigNothing()		

	def createConfigList(self):
		self.set_myatile = getConfigListEntry(_("Enable %s pro:") % cur_skin, config.myNfrHD_active)
		self.set_new_skin = getConfigListEntry(_("Change skin"), ConfigNothing())
		#self.find_woeid = getConfigListEntry(_("Search weather location ID"), ConfigNothing())
		self.list = []
		self.list.append(self.set_myatile)
		if color_test == True:
                	self.set_color = getConfigListEntry(_("Style:"), config.myNfrHD_style)	
			self.list.append(self.set_color)
		if background_test == True:
                	self.set_background = getConfigListEntry(_("Background:"), config.myNfrHD_background)	
			self.list.append(self.set_background)
		if infobar_test == True:
                	self.set_infobar = getConfigListEntry(_("Infobar:"), config.myNfrHD_infobar)	
			self.list.append(self.set_infobar)
		if sib_test == True:
		        self.set_sib = getConfigListEntry(_("Secondinfobar:"), config.myNfrHD_sib)
			self.list.append(self.set_sib)
		if ch_se_test == True:
		        self.set_ch_se = getConfigListEntry(_("Channelselection:"), config.myNfrHD_ch_se)
			self.list.append(self.set_ch_se)			
		if ev_test == True:
		        self.set_ev = getConfigListEntry(_("Eventview:"), config.myNfrHD_ev)
			self.list.append(self.set_ev)
		if sb_test == True:
		        self.set_sb = getConfigListEntry(_("ColorSelectedBackground:"), config.myNfrHD_sb)
			self.list.append(self.set_sb)
		if ul_test == True:
		        self.set_ul = getConfigListEntry(_("Userlogo:"), config.myNfrHD_ul)
			self.list.append(self.set_ul)
		if clock_test == True:
		        self.set_clock = getConfigListEntry(_("Clock:"), config.myNfrHD_clock)
			self.list.append(self.set_clock)			
		self.list.append(self.set_new_skin)
		#self.list.append(getConfigListEntry(_("---Weather---"), self.myNfrHD_fake_entry))
		##self.list.append(getConfigListEntry(_("Refresh interval in minutes:"), config.plugins.NfrHD.refreshInterval))
		#self.list.append(getConfigListEntry(_("Temperature unit:"), config.plugins.NfrHD.tempUnit))
		#self.list.append(self.find_woeid)
		#self.list.append(getConfigListEntry(_("Location # (http://weather.yahoo.com/):"), config.plugins.NfrHD.woeid))
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		if config.myNfrHD_active.value:
		        if cur_skin == "skin_default":
			        self["key_yellow"].setText("skin_default Pro")
			else:
                                self["key_yellow"].setText("%s Pro" % cur_skin)
		else:
			self["key_yellow"].setText("")

	def changedEntry(self):
		if color_test == True:
                	if self["config"].getCurrent() == self.set_color:
				self.setPicture(config.myNfrHD_style.value)
		if background_test == True:		
			if self["config"].getCurrent() == self.set_background:
				self.setPicture(config.myNfrHD_background.value)
		if infobar_test == True:		
			if self["config"].getCurrent() == self.set_infobar:
				self.setPicture(config.myNfrHD_infobar.value)
		if sib_test == True:		
			if self["config"].getCurrent() == self.set_sib:
				self.setPicture(config.myNfrHD_sib.value)
		if ch_se_test == True:		
			if self["config"].getCurrent() == self.set_ch_se:
				self.setPicture(config.myNfrHD_ch_se.value)				
		if ev_test == True:		
			if self["config"].getCurrent() == self.set_ev:
				self.setPicture(config.myNfrHD_ev.value)
		if sb_test == True:		
			if self["config"].getCurrent() == self.set_sb:
				self.setPicture(config.myNfrHD_sb.value)				
		if ul_test == True:		
			if self["config"].getCurrent() == self.set_ul:
				self.setPicture(config.myNfrHD_ul.value)
		if clock_test == True:		
			if self["config"].getCurrent() == self.set_clock:
				self.setPicture(config.myNfrHD_clock.value)                                								
		if self["config"].getCurrent() == self.set_myatile:
			if config.myNfrHD_active.value:
                if cur_skin == "skin_default":
                    self["key_yellow"].setText("skin_default Pro")
                else:
                    self["key_yellow"].setText("%s Pro" % cur_skin)
			else:
				self["key_yellow"].setText("")

	def selectionChanged(self):
		if color_test == True:	
			if self["config"].getCurrent() == self.set_color:
				self.setPicture(config.myNfrHD_style.value)
		if background_test == True:		
			if self["config"].getCurrent() == self.set_background:
				self.setPicture(config.myNfrHD_background.value)
		if infobar_test == True:		
			if self["config"].getCurrent() == self.set_infobar:
				self.setPicture(config.myNfrHD_infobar.value)
		if sib_test == True:		
			if self["config"].getCurrent() == self.set_sib:
				self.setPicture(config.myNfrHD_sib.value)
		if ch_se_test == True:		
			if self["config"].getCurrent() == self.set_ch_se:
				self.setPicture(config.myNfrHD_ch_se.value)
		if ev_test == True:		
			if self["config"].getCurrent() == self.set_ev:
				self.setPicture(config.myNfrHD_ev.value)
		if sb_test == True:		
			if self["config"].getCurrent() == self.set_sb:
				self.setPicture(config.myNfrHD_sb.value)				
		if ul_test == True:		
			if self["config"].getCurrent() == self.set_ul:
				self.setPicture(config.myNfrHD_ul.value)
		if clock_test == True:		
			if self["config"].getCurrent() == self.set_clock:
				self.setPicture(config.myNfrHD_clock.value)                                				
		else:
			self["Picture"].hide()

	def cancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), MessageBox.TYPE_YESNO, default = False)
		else:
			for x in self["config"].list:
				x[1].cancel()
			if self.changed_screens:
				self.restartGUI()
			else:
				self.close()

	def cancelConfirm(self, result):
		if result is None or result is False:
			print("[%s]: Cancel confirmed." % cur_skin)
		else:
			print("[%s]: Cancel confirmed. Config changes will be lost." % cur_skin)
			for x in self["config"].list:
				x[1].cancel()
			self.close()

	def getPossibleColor(self):
		color_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'colors_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				color_list.append(f)
		color_list.append("default")
                return color_list

	def getPossibleBackground(self):
		background_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'background_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				background_list.append(f)
		background_list.append("default")
                return background_list
		
	def getPossibleInfobar(self):
		infobar_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'infobar_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				infobar_list.append(f)
		infobar_list.append("default")
                return infobar_list

	def getPossibleSib(self):
		sib_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'sib_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				sib_list.append(f)
		sib_list.append("default")
                return sib_list
                
	def getPossibleCh_se(self):
		ch_se_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'ch_se_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				ch_se_list.append(f)
		ch_se_list.append("default")
                return ch_se_list                
                
	def getPossibleEV(self):
		ev_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'ev_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				ev_list.append(f)
		ev_list.append("default")
                return ev_list
				
	def getPossibleSB(self):
		sb_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'sb_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				sb_list.append(f)
		sb_list.append("default")
                return sb_list
				
	def getPossibleUL(self):
		ul_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'ul_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				ul_list.append(f)
		ul_list.append("default")
                return ul_list
                
	def getPossibleCLOCK(self):
		clock_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'clock_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				clock_list.append(f)
		clock_list.append("default")
                return clock_list	                				
                
	def getmyAtileState(self):
		chdir(self.skin_base_dir)
		if path.exists("mySkin"):
			return True
		else:
			return False

	def getCurrentColor(self):
		myfile = self.skin_base_dir + self.color_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_color_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_color_file, self.color_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'colors_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)

	def getCurrentBackground(self):
		myfile = self.skin_base_dir + self.background_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_background_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_background_file, self.background_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'background_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)
		
	def getCurrentInfobar(self):
		myfile = self.skin_base_dir + self.infobar_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_infobar_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_infobar_file, self.infobar_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'infobar_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)

	def getCurrentSib(self):
		myfile = self.skin_base_dir + self.sib_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_sib_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_sib_file, self.sib_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'sib_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)
		
	def getCurrentCh_se(self):
		myfile = self.skin_base_dir + self.ch_se_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_ch_se_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_ch_se_file, self.ch_se_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'ch_se_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)
                
	def getCurrentEV(self):
		myfile = self.skin_base_dir + self.ev_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_ev_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_ev_file, self.ev_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'ev_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)

	def getCurrentSB(self):
		myfile = self.skin_base_dir + self.sb_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_sb_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_sb_file, self.sb_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'sb_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename) 

	def getCurrentUL(self):
		myfile = self.skin_base_dir + self.ul_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_ul_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_ul_file, self.ul_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'ul_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename) 
                
	def getCurrentCLOCK(self):
		myfile = self.skin_base_dir + self.clock_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_clock_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_clock_file, self.clock_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'clock_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)                 		

	def setPicture(self, f):
		try:
            pic = f.replace(".xml", ".png")
		except:
            pic = "default.png"                        
		preview = self.skin_base_dir + "preview/preview_" + pic
		if path.exists(preview):
			self["Picture"].instance.setPixmapFromFile(preview)
			self["Picture"].show()
		else:
			self["Picture"].hide()

	def keyYellow(self):
		if config.myNfrHD_active.value:
			self.session.openWithCallback(self.NfrHDScreenCB, NfrHDScreens)
		else:
			self["config"].setCurrentIndex(0)

	def keyOk(self):
		sel =  self["config"].getCurrent()
		if sel is not None and sel == self.set_new_skin:
			self.openSkinSelector()
		else:
			self.keyGreen()

	def openSkinSelector(self):
		self.session.openWithCallback(self.skinChanged, SkinSelector)


	def openSkinSelectorDelayed(self):
		self.delaytimer = eTimer()
		self.delaytimer.callback.append(self.openSkinSelector)
		self.delaytimer.start(200, True)

	def search_weather_id_callback(self, res):
		if res:
			id_dic = get_woeid_from_yahoo(res)
			if id_dic.has_key('error'):
				error_txt = id_dic['error']
				self.session.open(MessageBox, _("Sorry, there was a problem:") + "\n%s" % error_txt, MessageBox.TYPE_ERROR)
			elif id_dic.has_key('count'):
				result_no = int(id_dic['count'])
				location_list = []
				for i in list(range(0, result_no)):
					location_list.append(id_dic[i])
				self.session.openWithCallback(self.select_weather_id_callback, WeatherLocationChoiceList, location_list)

	def select_weather_id_callback(self, res):
		if res and isInteger(res):
			config.plugins.NfrHD.woeid.value = int(res)

	def skinChanged(self, ret = None):
		global cur_skin
		cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
		if cur_skin == "skin.xml":
        		cur_skin = "skin_default"
		else:
			self.getInitConfig()
			self.createConfigList()

	def keyGreen(self):
		if self["config"].isChanged():
			for x in self["config"].list:
				x[1].save()
			chdir(self.skin_base_dir)
			if path.exists(self.background_file):
				remove(self.background_file)
			elif path.islink(self.background_file):
				remove(self.background_file)
			if config.myNfrHD_background.value != 'default':
				symlink(config.myNfrHD_background.value, self.background_file)
			if path.exists(self.color_file):
				remove(self.color_file)
			elif path.islink(self.color_file):
				remove(self.color_file)
			if config.myNfrHD_style.value != 'default':
				symlink(config.myNfrHD_style.value, self.color_file)
			if path.exists(self.infobar_file):
				remove(self.infobar_file)
			elif path.islink(self.infobar_file):
				remove(self.infobar_file)
			if config.myNfrHD_infobar.value != 'default':
				symlink(config.myNfrHD_infobar.value, self.infobar_file)
			if path.exists(self.sib_file):
				remove(self.sib_file)
			elif path.islink(self.sib_file):
				remove(self.sib_file)
			if config.myNfrHD_sib.value != 'default':
				symlink(config.myNfrHD_sib.value, self.sib_file)
			if path.exists(self.ch_se_file):
				remove(self.ch_se_file)
			elif path.islink(self.ch_se_file):
				remove(self.ch_se_file)
			if config.myNfrHD_ch_se.value != 'default':
				symlink(config.myNfrHD_ch_se.value, self.ch_se_file)
			if path.exists(self.ev_file):
				remove(self.ev_file)
			elif path.islink(self.ev_file):
				remove(self.ev_file)
			if config.myNfrHD_ev.value != 'default':
				symlink(config.myNfrHD_ev.value, self.ev_file)
			if path.exists(self.sb_file):
				remove(self.sb_file)
			elif path.islink(self.sb_file):
				remove(self.sb_file)
			if config.myNfrHD_sb.value != 'default':
				symlink(config.myNfrHD_sb.value, self.sb_file)				
			if path.exists(self.ul_file):
				remove(self.ul_file)
			elif path.islink(self.ul_file):
				remove(self.ul_file)
			if config.myNfrHD_ul.value != 'default':
				symlink(config.myNfrHD_ul.value, self.ul_file)
			if path.exists(self.clock_file):
				remove(self.clock_file)
			elif path.islink(self.clock_file):
				remove(self.clock_file)
			if config.myNfrHD_clock.value != 'default':
				symlink(config.myNfrHD_clock.value, self.clock_file)                                				
			config.myNfrHD_background.save()
			config.myNfrHD_style.save()
			config.myNfrHD_infobar.save()
			config.myNfrHD_sib.save()
			config.myNfrHD_ch_se.save()
			config.myNfrHD_ev.save()
			config.myNfrHD_sb.save()			
			config.myNfrHD_ul.save()
			config.myNfrHD_clock.save()                        			
			configfile.save()
                        
			if config.myNfrHD_active.value:
				if not path.exists("mySkin") and path.exists("mySkin_off"):
					symlink("mySkin_off","mySkin")
			else:
				if path.exists("mySkin"):
					if path.exists("mySkin_off"):
						if path.islink("mySkin"):
							remove("mySkin")
						else:
							shutil.rmtree("mySkin")
					else:
						rename("mySkin", "mySkin_off")
			self.restartGUI()
		elif  config.skin.primary_skin.value != self.start_skin:
			self.restartGUI()
		else:
			if self.changed_screens:
				self.restartGUI()
			else:
				self.close()

	def NfrHDScreenCB(self):
		self.changed_screens = True
		self["config"].setCurrentIndex(0)

	def restartGUI(self):
		restartbox = self.session.openWithCallback(self.restartGUIcb,MessageBox, _("Restart necessary, restart GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Message"))

	def about(self):
		self.session.open(NfrHD_About)

	def restartGUIcb(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()
			
class NfrHD_Config1(Screen, ConfigListScreen):

	skin = """
		<screen name="NfrHD_Config" position="center,center" size="1280,720" title="NfrHD Setup" >
			<widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" transparent="1" />
			<widget name="config" position="70,115" size="700,480" scrollbarMode="showOnDemand" scrollbarWidth="6" transparent="1" />
			<widget name="Picture" position="808,342" size="400,225" alphatest="on" />
			<eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="red" />
			<eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="green" />
			<eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="yellow" />
			<eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="blue" />
			<widget name="key_red" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_green" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_yellow" position="660,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_blue" position="955,635" size="260,25" zPosition="0" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
		</screen>
	"""

	def __init__(self, session, args = 0):
		self.session = session
		self.skin_lines = []
		self.changed_screens = False
		Screen.__init__(self, session)
                global cur_skin
                global color_test
                global font_test
                global infobar_test
                global sib_test
                global ch_se_test                
                global ev_test                
		color_test = True
		font_test = True
		infobar_test = True
		sib_test = True
		ch_se_test = True
		ev_test = True		
                self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
                if glob.glob(self.skin_base_dir + 'colors_*') == True:
                        color_test = False                
                if glob.glob(self.skin_base_dir + 'font_*') == True:
                	font_test = False                
                if glob.glob(self.skin_base_dir + 'infobar_*') == True:
                	infobar_test = False                
                if glob.glob(self.skin_base_dir + 'sib_*') == True:			
			sib_test = False
                if glob.glob(self.skin_base_dir + 'ch_se_*') == True:			
			ch_se_test = False                            
                if glob.glob(self.skin_base_dir + 'ev_*') == True:			
			ev_test = False                                            
                		
		self.start_skin = config.skin.primary_skin.value
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self['Preview'] = Pixmap()
	        self.getInitConfig()
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))
		self["key_yellow"] = Label()
		self["key_blue"] = Label(_("About"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.keyGreen,
				"red": self.cancel,
				"yellow": self.keyYellow,
				"blue": self.about,
				"cancel": self.cancel,
				"ok": self.keyOk,
				"menu": self.weather				
			}, -2)
			
		self["Picture"] = Pixmap()
		
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.createConfigList()


	def weather(self):
		try:
			from Plugins.Extensions.WeatherPlugin.plugin import MSNWeatherPlugin#
			self.session.open(MSNWeatherPlugin)
		except Exception as e:
			self.session.open(MessageBox, _("The Weather plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )

	def getInitConfig(self):
		self.title = _("%s - Setup") % cur_skin
		self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin

		self.default_font_file = "font_Original.xml"
		self.default_color_file = "colors_Original.xml"
		self.default_infobar_file = "infobar_Original.xml"
		self.default_sib_file = "sib_Original.xml"
		self.default_ch_se_file = "ch_se_Original.xml"		
		self.default_ev_file = "ev_Original.xml"		
		self.color_file = "skin_user_colors.xml"
		self.font_file = "skin_user_header.xml"
		self.infobar_file = "skin_user_infobar.xml"
		self.sib_file = "skin_user_sib.xml"
		self.ch_se_file = "skin_user_ch_se.xml"
		self.ev_file = "skin_user_ev.xml"		
                if color_test == True:
			current_color = self.getCurrentColor()
			color_choices = self.getPossibleColor()
			default_color = ("default")
			config.myNfrHD_style = ConfigSelection(default=default_color, choices = color_choices)
			if current_color is None:
				current_color = default_color
			if default_color not in color_choices:
				color_choices.append(default_color)
			current_color = current_color
                if font_test == True:
			current_font = self.getCurrentFont() 
			font_choices = self.getPossibleFont()
			default_font = ("default")
			config.myNfrHD_font = ConfigSelection(default=default_font, choices = font_choices)		
			if current_font is None:
				current_font = default_font
			if default_font not in font_choices:
				font_choices.append(default_font)
			current_font = current_font
		if infobar_test == True:
			current_infobar = self.getCurrentInfobar()
			infobar_choices = self.getPossibleInfobar()
			default_infobar = ("default")
			config.myNfrHD_infobar = ConfigSelection(default=default_infobar, choices = infobar_choices)		
			if current_infobar is None:
				current_infobar = default_infobar
			if default_infobar not in infobar_choices:
				infobar_choices.append(default_infobar)
			current_infobar = current_infobar
		if sib_test == True:
			current_sib = self.getCurrentSib() 
			sib_choices = self.getPossibleSib()
			default_sib = ("default")
			config.myNfrHD_sib = ConfigSelection(default=default_sib, choices = sib_choices)		
			if current_sib is None:
				current_sib = default_sib
			if default_sib not in sib_choices:
				sib_choices.append(default_sib)
			current_sib = current_sib
		if ch_se_test == True:
                        current_ch_se = self.getCurrentCh_se() 
			ch_se_choices = self.getPossibleCh_se()
			default_ch_se = ("default")
			config.myNfrHD_ch_se = ConfigSelection(default=default_ch_se, choices = ch_se_choices)		
			if current_ch_se is None:
				current_ch_se = default_ch_se
			if default_ch_se not in ch_se_choices:
				ch_se_choices.append(default_ch_se)
			current_ch_se = current_ch_se			
		if ev_test == True:
			current_ev = self.getCurrentEV() 
			ev_choices = self.getPossibleEV()
			default_ev = ("default")
			config.myNfrHD_ev = ConfigSelection(default=default_ev, choices = ev_choices)		
			if current_ev is None:
				current_ev = default_ev
			if default_ev not in ev_choices:
				ev_choices.append(default_ev)
			current_ev = current_ev			
		
		myatile_active = self.getmyAtileState()
		config.myNfrHD_active = ConfigYesNo(default=myatile_active)
		#choices = self.getPossibleFont()
		self.myNfrHD_fake_entry = ConfigNothing()		

	def createConfigList(self):
		self.set_myatile = getConfigListEntry(_("Enable %s pro:") % cur_skin, config.myNfrHD_active)
		self.set_new_skin = getConfigListEntry(_("Change skin"), ConfigNothing())
		self.find_woeid = getConfigListEntry(_("Search weather location ID"), ConfigNothing())
		self.list = []
		self.list.append(self.set_myatile)
		if color_test == True:
                	self.set_color = getConfigListEntry(_("Style:"), config.myNfrHD_style)	
			self.list.append(self.set_color)
		if font_test == True:
                	self.set_font = getConfigListEntry(_("Font:"), config.myNfrHD_font)	
			self.list.append(self.set_font)
		if infobar_test == True:
                	self.set_infobar = getConfigListEntry(_("Infobar:"), config.myNfrHD_infobar)	
			self.list.append(self.set_infobar)
		if sib_test == True:
		        self.set_sib = getConfigListEntry(_("Secondinfobar:"), config.myNfrHD_sib)
			self.list.append(self.set_sib)
		if ch_se_test == True:
		        self.set_ch_se = getConfigListEntry(_("Channelselection:"), config.myNfrHD_ch_se)
			self.list.append(self.set_ch_se)			
		if ev_test == True:
		        self.set_ev = getConfigListEntry(_("Eventview:"), config.myNfrHD_ev)
			self.list.append(self.set_ev)			
		self.list.append(self.set_new_skin)
		self.list.append(getConfigListEntry(_("---Weather---"), self.myNfrHD_fake_entry))
		self.list.append(getConfigListEntry(_("Refresh interval in minutes:"), config.plugins.NfrHD.refreshInterval))
		self.list.append(getConfigListEntry(_("Temperature unit:"), config.plugins.NfrHD.tempUnit))
		self.list.append(self.find_woeid)
		self.list.append(getConfigListEntry(_("Location # (http://weather.yahoo.com/):"), config.plugins.NfrHD.woeid))
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		if config.myNfrHD_active.value:
			if cur_skin == "skin_default":
                self["key_yellow"].setText("skin_default Pro")
			else:
                self["key_yellow"].setText("%s Pro" % cur_skin)
		else:
			self["key_yellow"].setText("")

	def changedEntry(self):
		if color_test == True:
			if self["config"].getCurrent() == self.set_color:
				self.setPicture(config.myNfrHD_style.value)
		if font_test == True:		
			if self["config"].getCurrent() == self.set_font:
				self.setPicture(config.myNfrHD_font.value)
		if infobar_test == True:		
			if self["config"].getCurrent() == self.set_infobar:
				self.setPicture(config.myNfrHD_infobar.value)
		if sib_test == True:		
			if self["config"].getCurrent() == self.set_sib:
				self.setPicture(config.myNfrHD_sib.value)
		if ch_se_test == True:		
			if self["config"].getCurrent() == self.set_ch_se:
				self.setPicture(config.myNfrHD_ch_se.value)				
		if ev_test == True:		
			if self["config"].getCurrent() == self.set_ev:
				self.setPicture(config.myNfrHD_ev.value)				
		if self["config"].getCurrent() == self.set_myatile:
			if config.myNfrHD_active.value:
				if cur_skin == "skin_default":
                    self["key_yellow"].setText("skin_default Pro")
				else:
                    self["key_yellow"].setText("%s Pro" % cur_skin)
			else:
				self["key_yellow"].setText("")

	def selectionChanged(self):
		if color_test == True:	
			if self["config"].getCurrent() == self.set_color:
				self.setPicture(config.myNfrHD_style.value)
		if font_test == True:		
			if self["config"].getCurrent() == self.set_font:
				self.setPicture(config.myNfrHD_font.value)
		if infobar_test == True:		
			if self["config"].getCurrent() == self.set_infobar:
				self.setPicture(config.myNfrHD_infobar.value)
		if sib_test == True:		
			if self["config"].getCurrent() == self.set_sib:
				self.setPicture(config.myNfrHD_sib.value)
		if ch_se_test == True:		
			if self["config"].getCurrent() == self.set_ch_se:
				self.setPicture(config.myNfrHD_ch_se.value)
		if ev_test == True:		
			if self["config"].getCurrent() == self.set_ev:
				self.setPicture(config.myNfrHD_ev.value)
		else:
			self["Picture"].hide()

	def cancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), MessageBox.TYPE_YESNO, default = False)
		else:
			for x in self["config"].list:
				x[1].cancel()
			if self.changed_screens:
				self.restartGUI()
			else:
				self.close()

	def cancelConfirm(self, result):
		if result is None or result is False:
			print("[%s]: Cancel confirmed." % cur_skin)
		else:
			print("[%s]: Cancel confirmed. Config changes will be lost." % cur_skin)
			for x in self["config"].list:
				x[1].cancel()
			self.close()

	def getPossibleColor(self):
		color_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'colors_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				color_list.append(f)
		color_list.append("default")
                return color_list

	def getPossibleFont(self):
		font_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'font_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				font_list.append(f)
		font_list.append("default")
                return font_list
		
	def getPossibleInfobar(self):
		infobar_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'infobar_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				infobar_list.append(f)
		infobar_list.append("default")
                return infobar_list

	def getPossibleSib(self):
		sib_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'sib_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				sib_list.append(f)
		sib_list.append("default")
                return sib_list
                
	def getPossibleCh_se(self):
		ch_se_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'ch_se_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				ch_se_list.append(f)
		ch_se_list.append("default")
                return ch_se_list                
                
	def getPossibleEV(self):
		ev_list = []
		for f in sorted(listdir(self.skin_base_dir), key=str.lower):
			search_str = 'ev_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				ev_list.append(f)
		ev_list.append("default")
                return ev_list
                
	def getmyAtileState(self):
		chdir(self.skin_base_dir)
		if path.exists("mySkin"):
			return True
		else:
			return False

	def getCurrentColor(self):
		myfile = self.skin_base_dir + self.color_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_color_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_color_file, self.color_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'colors_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)

	def getCurrentFont(self):
		myfile = self.skin_base_dir + self.font_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_font_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_font_file, self.font_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'font_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)
		
	def getCurrentInfobar(self):
		myfile = self.skin_base_dir + self.infobar_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_infobar_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_infobar_file, self.infobar_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'infobar_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)

	def getCurrentSib(self):
		myfile = self.skin_base_dir + self.sib_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_sib_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_sib_file, self.sib_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'sib_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)
		
	def getCurrentCh_se(self):
		myfile = self.skin_base_dir + self.ch_se_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_ch_se_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_ch_se_file, self.ch_se_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'ch_se_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)
                
	def getCurrentEV(self):
		myfile = self.skin_base_dir + self.ev_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_ev_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir)
				symlink(self.default_ev_file, self.ev_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'ev_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)                		

	def setPicture(self, f):
                try:
                        pic = f.replace(".xml", ".png")
                except:
                        pic = "default.png"                        
		preview = self.skin_base_dir + "preview/preview_" + pic
		if path.exists(preview):
			self["Picture"].instance.setPixmapFromFile(preview)
			self["Picture"].show()
		else:
			self["Picture"].hide()

	def keyYellow(self):
		if config.myNfrHD_active.value:
			self.session.openWithCallback(self.NfrHDScreenCB, NfrHDScreens)
		else:
			self["config"].setCurrentIndex(0)

	def keyOk(self):
		sel =  self["config"].getCurrent()
		if sel is not None and sel == self.set_new_skin:
			self.openSkinSelector()
		elif sel is not None and sel == self.find_woeid:
			self.session.openWithCallback(self.search_weather_id_callback, VirtualKeyBoard, title = _('Please enter search string for your location'), text = "")
		else:
			self.keyGreen()

	def openSkinSelector(self):
		self.session.openWithCallback(self.skinChanged, SkinSelector)


	def openSkinSelectorDelayed(self):
		self.delaytimer = eTimer()
		self.delaytimer.callback.append(self.openSkinSelector)
		self.delaytimer.start(200, True)

	def search_weather_id_callback(self, res):
		if res:
			id_dic = get_woeid_from_yahoo(res)
			if id_dic.has_key('error'):
				error_txt = id_dic['error']
				self.session.open(MessageBox, _("Sorry, there was a problem:") + "\n%s" % error_txt, MessageBox.TYPE_ERROR)
			elif id_dic.has_key('count'):
				result_no = int(id_dic['count'])
				location_list = []
				for i in list(range(0, result_no)):
					location_list.append(id_dic[i])
				self.session.openWithCallback(self.select_weather_id_callback, WeatherLocationChoiceList, location_list)

	def select_weather_id_callback(self, res):
		if res and isInteger(res):
			config.plugins.NfrHD.woeid.value = int(res)

	def skinChanged(self, ret = None):
		global cur_skin
		cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
		if cur_skin == "skin.xml":
        		cur_skin = "skin_default"
		else:
			self.getInitConfig()
			self.createConfigList()

	def keyGreen(self):
		if self["config"].isChanged():
			for x in self["config"].list:
				x[1].save()
			chdir(self.skin_base_dir)
			if path.exists(self.font_file):
				remove(self.font_file)
			elif path.islink(self.font_file):
				remove(self.font_file)
			if config.myNfrHD_font.value != 'default':
				symlink(config.myNfrHD_font.value, self.font_file)
			if path.exists(self.color_file):
				remove(self.color_file)
			elif path.islink(self.color_file):
				remove(self.color_file)
			if config.myNfrHD_style.value != 'default':
				symlink(config.myNfrHD_style.value, self.color_file)
			if path.exists(self.infobar_file):
				remove(self.infobar_file)
			elif path.islink(self.infobar_file):
				remove(self.infobar_file)
			if config.myNfrHD_infobar.value != 'default':
				symlink(config.myNfrHD_infobar.value, self.infobar_file)
			if path.exists(self.sib_file):
				remove(self.sib_file)
			elif path.islink(self.sib_file):
				remove(self.sib_file)
			if config.myNfrHD_sib.value != 'default':
				symlink(config.myNfrHD_sib.value, self.sib_file)
			if path.exists(self.ch_se_file):
				remove(self.ch_se_file)
			elif path.islink(self.ch_se_file):
				remove(self.ch_se_file)
			if config.myNfrHD_ch_se.value != 'default':
				symlink(config.myNfrHD_ch_se.value, self.ch_se_file)
			if path.exists(self.ev_file):
				remove(self.ev_file)
			elif path.islink(self.ev_file):
				remove(self.ev_file)
			if config.myNfrHD_ev.value != 'default':
				symlink(config.myNfrHD_ev.value, self.ev_file)                                                                		
                        config.myNfrHD_font.save()
                        config.myNfrHD_style.save()
                        config.myNfrHD_infobar.save()
                        config.myNfrHD_sib.save()
                        config.myNfrHD_ch_se.save()
                        config.myNfrHD_ev.save()
                        configfile.save()
                        
                        if config.myNfrHD_active.value:
				if not path.exists("mySkin") and path.exists("mySkin_off"):
					symlink("mySkin_off","mySkin")
			else:
				if path.exists("mySkin"):
					if path.exists("mySkin_off"):
						if path.islink("mySkin"):
							remove("mySkin")
						else:
							shutil.rmtree("mySkin")
					else:
						rename("mySkin", "mySkin_off")
			self.restartGUI()
		elif  config.skin.primary_skin.value != self.start_skin:
			self.restartGUI()
		else:
			if self.changed_screens:
				self.restartGUI()
			else:
				self.close()

	def NfrHDScreenCB(self):
		self.changed_screens = True
		self["config"].setCurrentIndex(0)

	def restartGUI(self):
		restartbox = self.session.openWithCallback(self.restartGUIcb, MessageBox, _("Restart necessary, restart GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Message"))

	def about(self):
		self.session.open(NfrHD_About)

	def restartGUIcb(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()			
			
class NfrHD_Config2(Screen, ConfigListScreen):

	skin = """
		<screen name="NfrHD_Config" position="center,center" size="1280,720" title="NfrHD Setup" >
			<widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" transparent="1" />
			<widget name="config" position="70,115" size="700,480" scrollbarMode="showOnDemand" scrollbarWidth="6" transparent="1" />
			<widget name="Picture" position="808,342" size="400,225" alphatest="on" />
			<eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="red" />
			<eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="green" />
			<eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="yellow" />
			<eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="blue" />
			<widget name="key_red" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_green" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_yellow" position="660,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_blue" position="955,635" size="260,25" zPosition="0" font="Regular;20" halign="left" foregroundColor="foreground" transparent="1" />
		</screen>
	"""

	def __init__(self, session, args = 0):
		self.session = session
		self.skin_lines = []
		self.changed_screens = False
		Screen.__init__(self, session)
		global cur_skin
		global color_test
		global center_test
		global infobar_test
		global sib_test
		global ch_se_test
		global ev_test
		global sb_test
		global frame_test
		global lines_test
		global sbar_test
		global wget_test
		global emc_test
		global volume_test
		global movsel_test

		color_test = True
		center_test = True
		infobar_test = True
		sib_test = True
		ch_se_test = True
		ev_test = True
		sb_test = True
		frame_test = True
		lines_test = True
		sbar_test = True
		wget_test = True
		emc_test = True
		volume_test = True
		movsel_test = True                  		

		self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
		if glob.glob(self.skin_base_dir + 'allScreens/Colors/colors_*') == True:
			color_test = False
		if glob.glob(self.skin_base_dir + 'allScreens/Center/skin_center_*') == True:
			center_test = False
		if glob.glob(self.skin_base_dir + 'allScreens/Infobar/infobar_*') == True:
			infobar_test = False
		if glob.glob(self.skin_base_dir + 'allScreens/Sib/sib_*') == True:
			sib_test = False
		if glob.glob(self.skin_base_dir + 'allScreens/CH_se/ch_se_*') == True:
			ch_se_test = False
		if glob.glob(self.skin_base_dir + 'allScreens/EV/ev_*') == True:
			ev_test = False
		if glob.glob(self.skin_base_dir + 'allScreens/SB/skin_Selected_Background_*') == True:
			sb_test = False
		if glob.glob(self.skin_base_dir + 'allScreens/FRAME/skin_frame_*') == True:
			frame_test = False
		if glob.glob(self.skin_base_dir + 'allScreens/LINES/skin_lines_*') == True:
			lines_test = False
		if glob.glob(self.skin_base_dir + 'allScreens/SBAR/skin_Scrollbar_*') == True:
			sbar_test = False
		if glob.glob(self.skin_base_dir + 'allScreens/WGET/skin_widget_*') == True:
			wget_test = False
		if glob.glob(self.skin_base_dir + 'allScreens/EMC/skin_EMC_*') == True:
			emc_test = False			
		if glob.glob(self.skin_base_dir + 'allScreens/VOLUME/skin_Volume_*') == True:
			volume_test = False			
		if glob.glob(self.skin_base_dir + 'allScreens/MOVSEL/skin_Movie_Selection_*') == True:
			movsel_test = False			

                		
		self.start_skin = config.skin.primary_skin.value
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self['Preview'] = Pixmap()
	        self.getInitConfig()
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))
		self["key_yellow"] = Label()
		self["key_blue"] = Label(_("About"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"green": self.keyGreen,
				"red": self.cancel,
				"yellow": self.keyYellow,
				"blue": self.about,
				"cancel": self.cancel,
				"ok": self.keyOk,
				"menu": self.weather				
			}, -2)
			
		self["Picture"] = Pixmap()
		
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.createConfigList()
		
	def weather(self):
		try:
			from Plugins.Extensions.WeatherPlugin.plugin import MSNWeatherPlugin#
			self.session.open(MSNWeatherPlugin)
		except Exception as e:
			self.session.open(MessageBox, _("The Weather plugin is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )		

	def getInitConfig(self):
		self.title = _("%s - Setup") % cur_skin
		self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
		self.skin_base_dir1 = "/usr/share/enigma2/%s/allScreens/" % cur_skin
		self.default_center_file = "center_Original.xml"
		self.default_color_file = "colors_Original.xml"
		self.default_infobar_file = "infobar_Original.xml"
		self.default_sib_file = "sib_Original.xml"
		self.default_ch_se_file = "ch_se_Original.xml"
		self.default_ev_file = "ev_Original.xml"
		self.default_sb_file = "sb_Original.xml"
		self.default_frame_file = "frame_Original.xml"
		self.default_lines_file = "lines_Original.xml"
		self.default_sbar_file = "sbar_Original.xml"
		self.default_wget_file = "wget_Original.xml"
		self.default_emc_file = "emc_selection_Original.xml"
		self.default_volume_file = "volume_Original.xml"
		self.default_movsel_file = "movie_selection_Original.xml"
		self.color_file = "skin_user_colors.xml"
		self.center_file = "skin_user_center.xml"
		self.infobar_file = "skin_user_infobar.xml"
		self.sib_file = "skin_user_sib.xml"
		self.ch_se_file = "skin_user_ch_se.xml"
		self.ev_file = "skin_user_ev.xml"
		self.sb_file = "skin_user_sb.xml"
		self.frame_file = "skin_user_frame.xml"
		self.lines_file = "skin_user_lines.xml"
		self.sbar_file = "skin_user_sbar.xml"
		self.wget_file = "skin_user_wget.xml"
		self.emc_file = "skin_user_emc.xml"
		self.volume_file = "skin_user_volume.xml"
		self.movsel_file = "skin_user_movieselection.xml"	
		
		if color_test == True:
			current_color = self.getCurrentColor()
			color_choices = self.getPossibleColor()
			default_color = ("default")
			config.myNfrHD_style = ConfigSelection(default=default_color, choices = color_choices)
			if current_color is None:
				current_color = default_color
			if default_color not in color_choices:
				color_choices.append(default_color)
			current_color = current_color
		if center_test == True:
			current_center = self.getCurrentCenter() 
			center_choices = self.getPossibleCenter()
			default_center = ("default")
			config.myNfrHD_center = ConfigSelection(default=default_center, choices = center_choices)		
			if current_center is None:
				current_center = default_center
			if default_center not in center_choices:
				center_choices.append(default_center)
			current_center = current_center
		if infobar_test == True:
			current_infobar = self.getCurrentInfobar()
			infobar_choices = self.getPossibleInfobar()
			default_infobar = ("default")
			config.myNfrHD_infobar = ConfigSelection(default=default_infobar, choices = infobar_choices)		
			if current_infobar is None:
				current_infobar = default_infobar
			if default_infobar not in infobar_choices:
				infobar_choices.append(default_infobar)
			current_infobar = current_infobar
		if sib_test == True:
			current_sib = self.getCurrentSib() 
			sib_choices = self.getPossibleSib()
			default_sib = ("default")
			config.myNfrHD_sib = ConfigSelection(default=default_sib, choices = sib_choices)		
			if current_sib is None:
				current_sib = default_sib
			if default_sib not in sib_choices:
				sib_choices.append(default_sib)
			current_sib = current_sib
		if ch_se_test == True:
			current_ch_se = self.getCurrentCh_se() 
			ch_se_choices = self.getPossibleCh_se()
			default_ch_se = ("default")
			config.myNfrHD_ch_se = ConfigSelection(default=default_ch_se, choices = ch_se_choices)		
			if current_ch_se is None:
				current_ch_se = default_ch_se
			if default_ch_se not in ch_se_choices:
				ch_se_choices.append(default_ch_se)
			current_ch_se = current_ch_se			
		if ev_test == True:
			current_ev = self.getCurrentEV() 
			ev_choices = self.getPossibleEV()
			default_ev = ("default")
			config.myNfrHD_ev = ConfigSelection(default=default_ev, choices = ev_choices)		
			if current_ev is None:
				current_ev = default_ev
			if default_ev not in ev_choices:
				ev_choices.append(default_ev)
			current_ev = current_ev			
		if sb_test  == True:
			current_sb = self.getCurrentSB() 
			sb_choices = self.getPossibleSB()
			default_sb = ("default")
			config.myNfrHD_sb = ConfigSelection(default=default_sb, choices = sb_choices)		
			if current_sb is None:
				current_sb = default_sb
			if default_sb not in sb_choices:
				sb_choices.append(default_sb)
			current_ev = current_ev			
		if frame_test  == True:
			current_frame = self.getCurrentFRAME() 
			frame_choices = self.getPossibleFRAME()
			default_frame = ("default")
			config.myNfrHD_frame = ConfigSelection(default=default_frame, choices = frame_choices)		
			if current_frame is None:
				current_frame = default_frame
			if default_frame not in frame_choices:
				frame_choices.append(default_frame)
			current_frame = current_frame			
		if lines_test == True:
			current_lines = self.getCurrentLINES() 
			lines_choices = self.getPossibleLINES()
			default_lines = ("default")
			config.myNfrHD_lines = ConfigSelection(default=default_lines, choices = lines_choices)		
			if current_lines is None:
				current_lines = default_lines
			if default_lines not in lines_choices:
				lines_choices.append(default_lines)
			current_lines = current_lines			
		if sbar_test == True:
			current_sbar = self.getCurrentSBAR() 
			sbar_choices = self.getPossibleSBAR()
			default_sbar = ("default")
			config.myNfrHD_sbar = ConfigSelection(default=default_sbar, choices = sbar_choices)		
			if current_sbar is None:
				current_sbar = default_sbar
			if default_sbar not in sbar_choices:
				sbar_choices.append(default_sbar)
			current_sbar = current_sbar			
		if wget_test == True:
			current_wget = self.getCurrentWGET() 
			wget_choices = self.getPossibleWGET()
			default_wget = ("default")
			config.myNfrHD_wget = ConfigSelection(default=default_wget, choices = wget_choices)		
			if current_wget is None:
				current_wget = default_wget
			if default_wget not in wget_choices:
				wget_choices.append(default_wget)
			current_wget = current_wget
		if emc_test == True:
			current_emc = self.getCurrentEMC() 
			emc_choices = self.getPossibleEMC()
			default_emc = ("default")
			config.myNfrHD_emc = ConfigSelection(default=default_emc, choices = emc_choices)		
			if current_emc is None:
				current_emc = default_emc
			if default_emc not in emc_choices:
				emc_choices.append(default_emc)
			current_emc = current_emc                        
		if volume_test == True:
			current_volume = self.getCurrentVOLUME() 
			volume_choices = self.getPossibleVOLUME()
			default_volume = ("default")
			config.myNfrHD_volume = ConfigSelection(default=default_volume, choices = volume_choices)		
			if current_volume is None:
				current_volume = default_volume
			if default_volume not in volume_choices:
				volume_choices.append(default_volume)
			current_volume = current_volume                        
		if movsel_test == True:
			current_movsel = self.getCurrentMOVSEL() 
			movsel_choices = self.getPossibleMOVSEL()
			default_movsel = ("default")
			config.myNfrHD_movsel = ConfigSelection(default=default_movsel, choices = movsel_choices)		
			if current_movsel is None:
				current_movsel = default_movsel
			if default_movsel not in movsel_choices:
				movsel_choices.append(default_movsel)
			current_movsel = current_movsel                        
		
		myatile_active = self.getmyAtileState()
		config.myNfrHD_active = ConfigYesNo(default=myatile_active)
		#choices = self.getPossibleFont()
		self.myNfrHD_fake_entry = ConfigNothing()		

	def createConfigList(self):
		self.set_myatile = getConfigListEntry(_("Enable %s pro:") % cur_skin, config.myNfrHD_active)
		self.set_new_skin = getConfigListEntry(_("Change skin"), ConfigNothing())
		self.find_woeid = getConfigListEntry(_("Search weather location ID"), ConfigNothing())
		self.list = []
		self.list.append(self.set_myatile)
		if color_test == True:
                	self.set_color = getConfigListEntry(_("Style:"), config.myNfrHD_style)	
			self.list.append(self.set_color)
		if center_test == True:
                	self.set_center = getConfigListEntry(_("Center:"), config.myNfrHD_center)	
			self.list.append(self.set_center)
		if infobar_test == True:
                	self.set_infobar = getConfigListEntry(_("Infobar:"), config.myNfrHD_infobar)	
			self.list.append(self.set_infobar)
		if sib_test == True:
		        self.set_sib = getConfigListEntry(_("Secondinfobar:"), config.myNfrHD_sib)
			self.list.append(self.set_sib)
		if ch_se_test == True:
		        self.set_ch_se = getConfigListEntry(_("Channelselection:"), config.myNfrHD_ch_se)
			self.list.append(self.set_ch_se)			
		if ev_test == True:
		        self.set_ev = getConfigListEntry(_("Eventview:"), config.myNfrHD_ev)
			self.list.append(self.set_ev)			
		if sb_test == True:
		        self.set_sb = getConfigListEntry(_("ColorSelectedBackground:"), config.myNfrHD_sb)
			self.list.append(self.set_sb)
		if frame_test == True:
		        self.set_frame = getConfigListEntry(_("Frame:"), config.myNfrHD_frame)
			self.list.append(self.set_frame)
		if lines_test == True:
		        self.set_lines = getConfigListEntry(_("Lines:"), config.myNfrHD_lines)
			self.list.append(self.set_lines)
		if sbar_test == True:
		        self.set_sbar = getConfigListEntry(_("Scrollbar:"), config.myNfrHD_sbar)
			self.list.append(self.set_sbar)
		if wget_test == True:
		        self.set_wget = getConfigListEntry(_("Clock_Widget:"), config.myNfrHD_wget)
			self.list.append(self.set_wget)
		if emc_test == True:
		        self.set_emc = getConfigListEntry(_("EMC:"), config.myNfrHD_emc)
			self.list.append(self.set_emc)			
		if volume_test == True:
		        self.set_volume = getConfigListEntry(_("Volume:"), config.myNfrHD_volume)
			self.list.append(self.set_volume)			
		if movsel_test == True:
		        self.set_movsel = getConfigListEntry(_("Movie_Selection:"), config.myNfrHD_movsel)
			self.list.append(self.set_movsel)			
		self.list.append(self.set_new_skin)
		self.list.append(getConfigListEntry(_("---Weather---"), self.myNfrHD_fake_entry))
		self.list.append(getConfigListEntry(_("Refresh interval in minutes:"), config.plugins.NfrHD.refreshInterval))
		self.list.append(getConfigListEntry(_("Temperature unit:"), config.plugins.NfrHD.tempUnit))
		self.list.append(self.find_woeid)
		self.list.append(getConfigListEntry(_("Location # (http://weather.yahoo.com/):"), config.plugins.NfrHD.woeid))
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		if config.myNfrHD_active.value:
		        if cur_skin == "skin_default":
			        self["key_yellow"].setText("skin_default Pro")
			else:
                                self["key_yellow"].setText("%s Pro" % cur_skin)
		else:
			self["key_yellow"].setText("")

	def changedEntry(self):
		if color_test == True:
                	if self["config"].getCurrent() == self.set_color:
				self.setPicture(config.myNfrHD_style.value)
		if center_test == True:		
			if self["config"].getCurrent() == self.set_center:
				self.setPicture(config.myNfrHD_center.value)
		if infobar_test == True:		
			if self["config"].getCurrent() == self.set_infobar:
				self.setPicture(config.myNfrHD_infobar.value)
		if sib_test == True:		
			if self["config"].getCurrent() == self.set_sib:
				self.setPicture(config.myNfrHD_sib.value)
		if ch_se_test == True:		
			if self["config"].getCurrent() == self.set_ch_se:
				self.setPicture(config.myNfrHD_ch_se.value)				
		if ev_test == True:		
			if self["config"].getCurrent() == self.set_ev:
				self.setPicture(config.myNfrHD_ev.value)				
		if sb_test == True:		
			if self["config"].getCurrent() == self.set_sb:
				self.setPicture(config.myNfrHD_sb.value)				
		if frame_test == True:		
			if self["config"].getCurrent() == self.set_frame:
				self.setPicture(config.myNfrHD_frame.value)				
		if lines_test == True:		
			if self["config"].getCurrent() == self.set_lines:
				self.setPicture(config.myNfrHD_lines.value)				
		if sbar_test == True:		
			if self["config"].getCurrent() == self.set_sbar:
				self.setPicture(config.myNfrHD_sbar.value)				
		if wget_test == True:		
			if self["config"].getCurrent() == self.set_wget:
				self.setPicture(config.myNfrHD_wget.value)
		if emc_test == True:		
			if self["config"].getCurrent() == self.set_emc:
				self.setPicture(config.myNfrHD_emc.value)                                
		if volume_test == True:		
			if self["config"].getCurrent() == self.set_volume:
				self.setPicture(config.myNfrHD_volume.value)                                
		if movsel_test == True:		
			if self["config"].getCurrent() == self.set_movsel:
				self.setPicture(config.myNfrHD_movsel.value)                                				
		if self["config"].getCurrent() == self.set_myatile:
			if config.myNfrHD_active.value:
				if cur_skin == "skin_default":
                    self["key_yellow"].setText("skin_default Pro")
				else:
                    self["key_yellow"].setText("%s Pro" % cur_skin)
			else:
				self["key_yellow"].setText("")

	def selectionChanged(self):
		if color_test == True:	
			if self["config"].getCurrent() == self.set_color:
				self.setPicture(config.myNfrHD_style.value)
		if center_test == True:		
			if self["config"].getCurrent() == self.set_center:
				self.setPicture(config.myNfrHD_center.value)
		if infobar_test == True:		
			if self["config"].getCurrent() == self.set_infobar:
				self.setPicture(config.myNfrHD_infobar.value)
		if sib_test == True:		
			if self["config"].getCurrent() == self.set_sib:
				self.setPicture(config.myNfrHD_sib.value)
		if ch_se_test == True:		
			if self["config"].getCurrent() == self.set_ch_se:
				self.setPicture(config.myNfrHD_ch_se.value)
		if ev_test == True:		
			if self["config"].getCurrent() == self.set_ev:
				self.setPicture(config.myNfrHD_ev.value)
		if sb_test == True:		
			if self["config"].getCurrent() == self.set_sb:
				self.setPicture(config.myNfrHD_sb.value)
		if frame_test == True:		
			if self["config"].getCurrent() == self.set_frame:
				self.setPicture(config.myNfrHD_frame.value)
		if lines_test == True:		
			if self["config"].getCurrent() == self.set_lines:
				self.setPicture(config.myNfrHD_lines.value)
		if sbar_test == True:		
			if self["config"].getCurrent() == self.set_sbar:
				self.setPicture(config.myNfrHD_sbar.value)
		if wget_test == True:		
			if self["config"].getCurrent() == self.set_wget:
				self.setPicture(config.myNfrHD_wget.value)
		if emc_test == True:		
			if self["config"].getCurrent() == self.set_emc:
				self.setPicture(config.myNfrHD_emc.value)				
		if volume_test == True:		
			if self["config"].getCurrent() == self.set_volume:
				self.setPicture(config.myNfrHD_volume.value)				
		if movsel_test == True:		
			if self["config"].getCurrent() == self.set_movsel:
				self.setPicture(config.myNfrHD_movsel.value)				
		else:
			self["Picture"].hide()

	def cancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), MessageBox.TYPE_YESNO, default = False)
		else:
			for x in self["config"].list:
				x[1].cancel()
			if self.changed_screens:
				self.restartGUI()
			else:
				self.close()

	def cancelConfirm(self, result):
		if result is None or result is False:
			print("[%s]: Cancel confirmed." % cur_skin)
		else:
			print("[%s]: Cancel confirmed. Config changes will be lost." % cur_skin)
			for x in self["config"].list:
				x[1].cancel()
			self.close()

	def getPossibleColor(self):
		color_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/Colors/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'colors_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				color_list.append(f)
		color_list.append("default")
                return color_list

	def getPossibleCenter(self):
		center_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/Center/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'skin_center_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				center_list.append(f)
		center_list.append("default")
                return center_list
		
	def getPossibleInfobar(self):
		infobar_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/Infobar/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'infobar_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				infobar_list.append(f)
		infobar_list.append("default")
                return infobar_list

	def getPossibleSib(self):
		sib_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/Sib/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'sib_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				sib_list.append(f)
		sib_list.append("default")
                return sib_list
                
	def getPossibleCh_se(self):
		ch_se_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/CH_se/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'ch_se_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				ch_se_list.append(f)
		ch_se_list.append("default")
                return ch_se_list                
                
	def getPossibleEV(self):
		ev_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/EV/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'ev_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				ev_list.append(f)
		ev_list.append("default")
                return ev_list
				
	def getPossibleSB(self):
		sb_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/SB/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'skin_Selected_Background_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				sb_list.append(f)
		sb_list.append("default")
                return sb_list
				
	def getPossibleFRAME(self):
		frame_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/FRAME/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'skin_Frame_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				frame_list.append(f)
		frame_list.append("default")
                return frame_list
				
	def getPossibleLINES(self):
		lines_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/LINES/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'skin_lines_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				lines_list.append(f)
		lines_list.append("default")
                return lines_list
				
	def getPossibleSBAR(self):
		sbar_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/SBAR/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'skin_Scrollbar_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				sbar_list.append(f)
		sbar_list.append("default")
                return sbar_list
				
	def getPossibleWGET(self):
		wget_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/WGET/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'skin_widget_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				wget_list.append(f)
		wget_list.append("default")
                return wget_list
                
	def getPossibleEMC(self):
		emc_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/EMC/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'skin_EMC_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				emc_list.append(f)
		emc_list.append("default")
                return emc_list                
                
	def getPossibleVOLUME(self):
		volume_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/VOLUME/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'skin_Volume_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				volume_list.append(f)
		volume_list.append("default")
                return volume_list                
                
	def getPossibleMOVSEL(self):
		movsel_list = []
		self.skin_base_dir1 = self.skin_base_dir + "allScreens/MOVSEL/"
		for f in sorted(listdir(self.skin_base_dir1), key=str.lower):
			search_str = 'skin_Movie_Selection_'
			if f.endswith('.xml') and f.startswith(search_str):
				friendly_name = f.replace(search_str, "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				movsel_list.append(f)
		movsel_list.append("default")
                return movsel_list                
                
	def getmyAtileState(self):
		chdir(self.skin_base_dir)
		if path.exists("mySkin"):
			return True
		else:
			return False

	def getCurrentColor(self):
		myfile = self.skin_base_dir1 + self.color_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir + self.default_color_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_color_file, self.color_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'colors_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)

	def getCurrentCenter(self):
		myfile = self.skin_base_dir1 + self.center_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_center_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_center_file, self.center_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'skin_center_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)
		
	def getCurrentInfobar(self):
		myfile = self.skin_base_dir1 + self.infobar_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_infobar_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_infobar_file, self.infobar_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'infobar_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)

	def getCurrentSib(self):
		myfile = self.skin_base_dir1 + self.sib_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_sib_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_sib_file, self.sib_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'sib_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)
		
	def getCurrentCh_se(self):
		myfile = self.skin_base_dir1 + self.ch_se_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_ch_se_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_ch_se_file, self.ch_se_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'ch_se_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)
                
	def getCurrentEV(self):
		myfile = self.skin_base_dir1 + self.ev_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_ev_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_ev_file, self.ev_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'ev_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)
		
	def getCurrentSB(self):
		myfile = self.skin_base_dir1 + self.sb_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_sb_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_sb_file, self.sb_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'skin_Selected_Background_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)		

	def getCurrentFRAME(self):
		myfile = self.skin_base_dir1 + self.frame_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_frame_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_frame_file, self.frame_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'skin_Frame_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)

	def getCurrentLINES(self):
		myfile = self.skin_base_dir1 + self.lines_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_lines_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_lines_file, self.lines_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'skin_lines_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)

	def getCurrentSBAR(self):
		myfile = self.skin_base_dir1 + self.sbar_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_sbar_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_sbar_file, self.sbar_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'skin_Scrollbar_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)

	def getCurrentWGET(self):
		myfile = self.skin_base_dir1 + self.wget_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_wget_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_wget_file, self.wget_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'skin_widget_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)
                
	def getCurrentEMC(self):
		myfile = self.skin_base_dir1 + self.emc_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_emc_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_emc_file, self.emc_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'skin_EMC_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)                
                
	def getCurrentVOLUME(self):
		myfile = self.skin_base_dir1 + self.volume_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_volume_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_volume_file, self.volume_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'skin_Volume_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)                
                
	def getCurrentMOVSEL(self):
		myfile = self.skin_base_dir1 + self.movsel_file
		if not path.exists(myfile):
			if path.exists(self.skin_base_dir1 + self.default_movsel_file):
				if path.islink(myfile):
					remove(myfile)
				chdir(self.skin_base_dir1)
				symlink(self.default_movsel_file, self.movsel_file)
			else:
				return None
		filename = path.realpath(myfile)
		filename = path.basename(filename)
		search_str = 'skin_Movie_Selection_'
		friendly_name = filename.replace(search_str, "")
		friendly_name = friendly_name.replace(".xml", "")
		friendly_name = friendly_name.replace("_", " ")
		return (filename)                		

	def setPicture(self, f):
		try:
            pic = f.replace(".xml", ".png")
		except:
            pic = "default.png"                        
		preview = self.skin_base_dir + "preview/preview_" + pic
		if path.exists(preview):
			self["Picture"].instance.setPixmapFromFile(preview)
			self["Picture"].show()
		else:
			self["Picture"].hide()

	def keyYellow(self):
		if config.myNfrHD_active.value:
			self.session.openWithCallback(self.NfrHDScreenCB, NfrHDScreens)
		else:
			self["config"].setCurrentIndex(0)

	def keyOk(self):
		sel =  self["config"].getCurrent()
		if sel is not None and sel == self.set_new_skin:
			self.openSkinSelector()
		elif sel is not None and sel == self.find_woeid:
			self.session.openWithCallback(self.search_weather_id_callback, VirtualKeyBoard, title = _('Please enter search string for your location'), text = "")
		else:
			self.keyGreen()

	def openSkinSelector(self):
		self.session.openWithCallback(self.skinChanged, SkinSelector)


	def openSkinSelectorDelayed(self):
		self.delaytimer = eTimer()
		self.delaytimer.callback.append(self.openSkinSelector)
		self.delaytimer.start(200, True)

	def search_weather_id_callback(self, res):
		if res:
			id_dic = get_woeid_from_yahoo(res)
			if id_dic.has_key('error'):
				error_txt = id_dic['error']
				self.session.open(MessageBox, _("Sorry, there was a problem:") + "\n%s" % error_txt, MessageBox.TYPE_ERROR)
			elif id_dic.has_key('count'):
				result_no = int(id_dic['count'])
				location_list = []
				for i in list(range(0, result_no)):
					location_list.append(id_dic[i])
				self.session.openWithCallback(self.select_weather_id_callback, WeatherLocationChoiceList, location_list)

	def select_weather_id_callback(self, res):
		if res and isInteger(res):
			config.plugins.NfrHD.woeid.value = int(res)

	def skinChanged(self, ret = None):
		global cur_skin
		cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
		if cur_skin == "skin.xml":
        		cur_skin = "skin_default"
		else:
			self.getInitConfig()
			self.createConfigList()

	def keyGreen(self):
		if self["config"].isChanged():
			for x in self["config"].list:
				x[1].save()
			chdir(self.skin_base_dir)
			if path.exists(self.center_file):
				remove(self.center_file)
			elif path.islink(self.center_file):
				remove(self.center_file)
			if config.myNfrHD_center.value != 'default':
				symlink(self.skin_base_dir + "allScreens/Center/" + config.myNfrHD_center.value, self.center_file)
			if path.exists(self.color_file):
				remove(self.color_file)
			elif path.islink(self.color_file):
				remove(self.color_file)
			if config.myNfrHD_style.value != 'default':
				symlink(self.skin_base_dir + "allScreens/Colors/" + config.myNfrHD_style.value, self.color_file)
			if path.exists(self.infobar_file):
				remove(self.infobar_file)
			elif path.islink(self.infobar_file):
				remove(self.infobar_file)
			if config.myNfrHD_infobar.value != 'default':
				symlink(self.skin_base_dir + "allScreens/Infobar/" + config.myNfrHD_infobar.value, self.infobar_file)
			if path.exists(self.sib_file):
				remove(self.sib_file)
			elif path.islink(self.sib_file):
				remove(self.sib_file)
			if config.myNfrHD_sib.value != 'default':
				symlink(self.skin_base_dir + "allScreens/Sib/" + config.myNfrHD_sib.value, self.sib_file)
			if path.exists(self.ch_se_file):
				remove(self.ch_se_file)
			elif path.islink(self.ch_se_file):
				remove(self.ch_se_file)
			if config.myNfrHD_ch_se.value != 'default':
				symlink(self.skin_base_dir + "allScreens/CH_se/" + config.myNfrHD_ch_se.value, self.ch_se_file)
			if path.exists(self.ev_file):
				remove(self.ev_file)
			elif path.islink(self.ev_file):
				remove(self.ev_file)
			if config.myNfrHD_ev.value != 'default':
				symlink(self.skin_base_dir + "allScreens/EV/" + config.myNfrHD_ev.value, self.ev_file) 
			if path.exists(self.sb_file):
				remove(self.sb_file)
			elif path.islink(self.sb_file):
				remove(self.sb_file)
			if config.myNfrHD_sb.value != 'default':
				symlink(self.skin_base_dir + "allScreens/SB/" + config.myNfrHD_sb.value, self.sb_file)
			if path.exists(self.frame_file):
				remove(self.frame_file)
			elif path.islink(self.frame_file):
				remove(self.frame_file)
			if config.myNfrHD_frame.value != 'default':
				symlink(self.skin_base_dir + "allScreens/FRAME/" + config.myNfrHD_frame.value, self.frame_file)
			if path.exists(self.lines_file):
				remove(self.lines_file)
			elif path.islink(self.lines_file):
				remove(self.lines_file)
			if config.myNfrHD_lines.value != 'default':
				symlink(self.skin_base_dir + "allScreens/LINES/" + config.myNfrHD_lines.value, self.lines_file)
			if path.exists(self.sbar_file):
				remove(self.sbar_file)
			elif path.islink(self.sbar_file):
				remove(self.sbar_file)
			if config.myNfrHD_sbar.value != 'default':
				symlink(self.skin_base_dir + "allScreens/SBAR/" + config.myNfrHD_sbar.value, self.sbar_file)
			if path.exists(self.wget_file):
				remove(self.wget_file)
			elif path.islink(self.wget_file):
				remove(self.wget_file)
			if config.myNfrHD_wget.value != 'default':
				symlink(self.skin_base_dir + "allScreens/WGET/" + config.myNfrHD_wget.value, self.wget_file)
			if path.exists(self.emc_file):
				remove(self.emc_file)
			elif path.islink(self.emc_file):
				remove(self.emc_file)
			if config.myNfrHD_emc.value != 'default':
				symlink(self.skin_base_dir + "allScreens/EMC/" + config.myNfrHD_emc.value, self.emc_file)				
			if path.exists(self.volume_file):
				remove(self.volume_file)
			elif path.islink(self.volume_file):
				remove(self.volume_file)
			if config.myNfrHD_volume.value != 'default':
				symlink(self.skin_base_dir + "allScreens/VOLUME/" + config.myNfrHD_volume.value, self.volume_file)				
			if path.exists(self.movsel_file):
				remove(self.movsel_file)
			elif path.islink(self.movsel_file):
				remove(self.movsel_file)
			if config.myNfrHD_movsel.value != 'default':
				symlink(self.skin_base_dir + "allScreens/MOVSEL/" + config.myNfrHD_movsel.value, self.movsel_file)				
                        config.myNfrHD_center.save()
                        config.myNfrHD_style.save()
                        config.myNfrHD_infobar.save()
                        config.myNfrHD_sib.save()
                        config.myNfrHD_ch_se.save()
                        config.myNfrHD_ev.save()
                        config.myNfrHD_sb.save()
                        config.myNfrHD_frame.save()
                        config.myNfrHD_lines.save()
                        config.myNfrHD_sbar.save()
                        config.myNfrHD_wget.save()
                        config.myNfrHD_emc.save()                        
                        config.myNfrHD_volume.save()                        
                        config.myNfrHD_movsel.save()                        
                        configfile.save()
                        
                        if config.myNfrHD_active.value:
				if not path.exists("mySkin") and path.exists("mySkin_off"):
					symlink("mySkin_off","mySkin")
			else:
				if path.exists("mySkin"):
					if path.exists("mySkin_off"):
						if path.islink("mySkin"):
							remove("mySkin")
						else:
							shutil.rmtree("mySkin")
					else:
						rename("mySkin", "mySkin_off")
			self.restartGUI()
		elif  config.skin.primary_skin.value != self.start_skin:
			self.restartGUI()
		else:
			if self.changed_screens:
				self.restartGUI()
			else:
				self.close()

	def NfrHDScreenCB(self):
		self.changed_screens = True
		self["config"].setCurrentIndex(0)

	def restartGUI(self):
		restartbox = self.session.openWithCallback(self.restartGUIcb, MessageBox,_("Restart necessary, restart GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Message"))

	def about(self):
		self.session.open(NfrHD_About)

	def restartGUIcb(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()						

class NfrHD_About(Screen):

	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.keyOk,
			}, -2)

	def keyOk(self):
		self.close()

	def cancel(self):
		self.close()

class NfrHDScreens(Screen):

	skin = """
		<screen name="NfrHDScreens" position="center,center" size="1280,720" title="NfrHD Setup">
			<widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" transparent="1" />
			<widget source="menu" render="Listbox" position="70,115" size="700,480" scrollbarMode="showOnDemand" scrollbarWidth="6" scrollbarSliderBorderWidth="1" enableWrapAround="1" transparent="1">
				<convert type="TemplatedMultiContent">
					{"template":
						[
							MultiContentEntryPixmapAlphaTest(pos = (2, 2), size = (25, 24), png = 2),
							MultiContentEntryText(pos = (35, 4), size = (500, 24), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),
						],
						"fonts": [gFont("Regular", 22),gFont("Regular", 16)],
						"itemHeight": 30
					}
				</convert>
			</widget>
			<widget name="Picture" position="808,342" size="400,225" alphatest="on" />
			<eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="red" />
			<eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="green" />
			<widget source="key_red" render="Label" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" transparent="1" />
			<widget source="key_green" render="Label" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" transparent="1" />
		</screen>
	"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		
		global cur_skin
		if cur_skin == "skin_default":
			self.title = _("skin_default additional screens")
		else:
			self.title = _("%s additional screens") % cur_skin		
		
		try:
			self["title"]=StaticText(self.title)
		except:
			print('self["title"] was not found in skin')
		
		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("on"))
		
		self["Picture"] = Pixmap()
		
		menu_list = []
		self["menu"] = List(menu_list)
		
		self["shortcuts"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
		{
			"ok": self.runMenuEntry,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.runMenuEntry,
		}, -2)
		
		if cur_skin == "skin_default":
            self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
		else:
            self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
		self.screen_dir = "allScreens"
		self.file_dir = "mySkin_off"
		my_path = resolveFilename(SCOPE_SKIN, "%s/icons/input_info.png" % cur_skin)
		if not path.exists(my_path):
			my_path = resolveFilename(SCOPE_SKIN, "skin_default/icons/lock_on.png")
		self.enabled_pic = LoadPixmap(cached = True, path = my_path)
		my_path = resolveFilename(SCOPE_SKIN, "%s/icons/input_error.png" % cur_skin)
		if not path.exists(my_path):
			my_path = resolveFilename(SCOPE_SKIN, "skin_default/icons/lock_off.png")
		self.disabled_pic = LoadPixmap(cached = True, path = my_path)
		
		if not self.selectionChanged in self["menu"].onSelectionChanged:
			self["menu"].onSelectionChanged.append(self.selectionChanged)
		
		self.onLayoutFinish.append(self.createMenuList)

	def selectionChanged(self):
		sel = self["menu"].getCurrent()
		if sel is not None:
			self.setPicture(sel[0])
			if sel[2] == self.enabled_pic:
				self["key_green"].setText(_("off"))
			elif sel[2] == self.disabled_pic:
				self["key_green"].setText(_("on"))

	def createMenuList(self):
		chdir(self.skin_base_dir)
		f_list = []
		dir_path = self.skin_base_dir + self.screen_dir
		if not path.exists(dir_path):
			makedirs(dir_path)
		file_dir_path = self.skin_base_dir + self.file_dir
		if not path.exists(file_dir_path):
			makedirs(file_dir_path)
		list_dir = sorted(listdir(dir_path), key=str.lower)
		for f in list_dir:
			if f.endswith('.xml') and f.startswith('skin_'):
				friendly_name = f.replace("skin_", "")
				friendly_name = friendly_name.replace(".xml", "")
				friendly_name = friendly_name.replace("_", " ")
				linked_file = file_dir_path + "/" + f
				if path.exists(linked_file):
					if path.islink(linked_file):
						pic = self.enabled_pic
					else:
						remove(linked_file)
						symlink(dir_path + "/" + f, file_dir_path + "/" + f)
						pic = self.enabled_pic
				else:
					pic = self.disabled_pic
				f_list.append((f, friendly_name, pic))
		menu_list = [ ]
		for entry in f_list:
			menu_list.append((entry[0], entry[1], entry[2]))
		self["menu"].updateList(menu_list)
		self.selectionChanged()

	def setPicture(self, f):
		pic = f.replace(".xml", ".png")
		preview = self.skin_base_dir + "preview/preview_" + pic
		if path.exists(preview):
			self["Picture"].instance.setPixmapFromFile(preview)
			self["Picture"].show()
		else:
			self["Picture"].hide()
	
	def keyCancel(self):
		self.close()

	def runMenuEntry(self):
		sel = self["menu"].getCurrent()
		if sel is not None:
			if sel[2] == self.enabled_pic:
				remove(self.skin_base_dir + self.file_dir + "/" + sel[0])
			elif sel[2] == self.disabled_pic:
				symlink(self.skin_base_dir + self.screen_dir + "/" + sel[0], self.skin_base_dir + self.file_dir + "/" + sel[0])
			self.createMenuList()
			
class DefaulSkinchange(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = "Setup"
		Screen.setTitle(self, _("Default Skin Setup") + "...After selection and ok click box reboot!")
		self.setup_title = _("Default Skin Setup") + "..."
		config.defaultskinSetup = ConfigSubsection()
		config.defaultskinSetup.steps = ConfigSelection([('default Utopia', _("default Utopia")), ('default SmokeR', _("default SmokeR"))],  default='nothing')

                self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("testtesttest")
                self["description"] = StaticText("now Using Bootlogo: ")
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
		self.list.append(getConfigListEntry(_("Default Skin Setup"), config.defaultskinSetup.steps))
		
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
                config.misc.skindefaultwizardenabled.value = False
		config.misc.skindefaultwizardenabled.save()
		configfile.save()
                if config.defaultskinSetup.steps.value == "nothing":
                        self.session.open(MessageBox,_("nothing selected Utopia will be used without reboot!"), MessageBox.TYPE_INFO, timeout=5)
                        self.close()
                else:        
		        self.session.open(MessageBox,_("Box will reboot to activated selected Defaultskin"), MessageBox.TYPE_INFO, timeout=5)
                        os.system("reboot")

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
                	if config.defaultskinSetup.steps.value == "nothing":
                		configfile.save()
                		config.misc.skindefaultwizardenabled.value = False
				config.misc.skindefaultwizardenabled.save()
				configfile.save() 			
			self.close() 			
