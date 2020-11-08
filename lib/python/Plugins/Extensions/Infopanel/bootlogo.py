from __future__ import print_function
from boxbranding import getMachineBrand, getMachineName
from os import path
from Screens.MessageBox import MessageBox
from Components.Console import Console
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.config import ConfigSubsection, ConfigYesNo, config, ConfigSelection, ConfigText, ConfigNumber, ConfigSet, ConfigLocations, NoSave, ConfigClock, ConfigInteger, ConfigBoolean, ConfigPassword, ConfigIP, ConfigSlider, ConfigSelectionNumber, getConfigListEntry, KEY_LEFT, KEY_RIGHT, configfile
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Plugins.Extensions.Infopanel.outofflash import MoveBootlogos_int, MoveBootlogos, MoveRadiologos_int, MoveRadiologos
from enigma import *
from Tools.LoadPixmap import LoadPixmap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from glob import glob
import os
import time

config.bootlogo = ConfigSubsection()
config.bootlogo.booting = ConfigText(default = "NFRbootlogo.mvi")
config.radiologo = ConfigSubsection()
config.radiologo.booting = ConfigText(default = "NFRradiologo.mvi")

class PanelList(MenuList):
	if (getDesktop(0).size().width() == 1920):
		def __init__(self, list, font0 = 32, font1 = 24, itemHeight = 92, enableWrapAround = True):
			MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
			self.l.setFont(0, gFont("Regular", font0))
			self.l.setFont(1, gFont("Regular", font1))
			self.l.setItemHeight(itemHeight)
	else:
		def __init__(self, list, font0 = 24, font1 = 16, itemHeight = 92, enableWrapAround = True):
			MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
			self.l.setFont(0, gFont("Regular", font0))
			self.l.setFont(1, gFont("Regular", font1))
			self.l.setItemHeight(itemHeight)

def MenuEntryItem(entry):
	if (getDesktop(0).size().width() == 1920):
		res = [entry]
		res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 5), size=(200, 80), png=entry[0]))  # png vorn
		res.append(MultiContentEntryText(pos=(210, 30), size=(690, 80), font=0, text=entry[1]))  # menupunkt
		return res
	else:
		res = [entry]
		res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 5), size=(200, 80), png=entry[0]))  # png vorn
		res.append(MultiContentEntryText(pos=(210, 30), size=(440, 80), font=0, text=entry[1]))  # menupunkt
		return res

def InfoEntryComponent(file):
	png = LoadPixmap("/usr/share/enigma2/bootlogos/" + file + ".png")
	if png == None:
		png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/default_logo.png")
	res = (png)
	return res

def InfoEntryComponent1(file):
	png = LoadPixmap("/usr/share/enigma2/radiologos/" + file + ".png")
	if png == None:
		png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/default_logo.png")
	res = (png)
	return res

class BootlogoSetupScreen(Screen):
	skin = """<screen name="BootlogoSetupScreen" position="center,center" size="950,520" title="BootlogoSetupScreen">
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/redlogo.png" position="0,380" size="950,84" alphatest="on" zPosition="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/alliance.png" position="670,255" size="100,67" alphatest="on" zPosition="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/opennfr_info.png" position="510,11" size="550,354" alphatest="on" zPosition="1" />
				<widget source="global.CurrentTime" render="Label" position="450, 340" size="500,24" font="Regular;20" foregroundColor="white" halign="right" transparent="1" zPosition="5">
				<convert type="ClockToText">&gt;Format%H:%M:%S</convert>
				</widget>
				<eLabel backgroundColor="un56c856" position="0,330" size="950,1" zPosition="0" />
				<widget name="Mlist" position="10,10" size="480,300" zPosition="1" scrollbarMode="showOnDemand" backgroundColor="un251e1f20" transparent="1" />
				<widget name="label1" position="10,340" size="490,25" font="Regular;20" transparent="1" foregroundColor="#f2e000" halign="left" />
 				<ePixmap pixmap="skin_default/buttons/red.png" position="10,480" size="30,30" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/green.png" position="190,480" size="30,30" alphatest="blend" />
				<widget source="key_red" render="Label" position="45,482" size="140,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />
				<widget source="key_green" render="Label" position="225,483" size="140,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />
				<widget source="session.VideoPicture" render="Pig" position="510,11" size="420,236" backgroundColor="transparent" zPosition="2" />
		</screen>"""	
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		Screen.setTitle(self, _("BootlogoSetupScreen"))
		self.Console = Console()
		self.onShown.append(self.setWindowTitle)
		aktbootlogo = config.bootlogo.booting.value
		self["label1"] = Label(_("now Using Bootlogo: %s") % aktbootlogo)
		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Save"))
		vpath = "/usr/share/enigma2/bootlogos/"	
		ulogo=[]
		ulogo = os.listdir(vpath)
		bootlogo = []
		for xlogo in ulogo:
			if xlogo.endswith(".mvi"):
				bootlogo.append(xlogo)

		self.list = []
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions"],
			{
				"cancel": self.Exit,
				"exit": self.Exit,
				"red": self.Exit,
				"ok": self.ok,
				"green": self.ok,
			}, 1)
			
		self.Mlist = []
		self.Mlist.append(MenuEntryItem((InfoEntryComponent('NFRbootlogo'), _("NFRbootlogo"), 'defaultbootlogo')))
		for logo in bootlogo:
			xname = logo.strip(".mvi")
			if logo == "NFRbootlogo.mvi":
				print("deaultbootlogo found")
			else:
				self.Mlist.append(MenuEntryItem((InfoEntryComponent('%s' % xname), _('%s' % xname), '%s' % logo)))

		self.onChangedEntry = []
		if (getDesktop(0).size().width() == 1920):
			self["Mlist"] = PanelList([], font0=36, font1=28, itemHeight=92)
		else:
		        self["Mlist"] = PanelList([])
		self["Mlist"].l.setList(self.Mlist)
		self["Mlist"].onSelectionChanged.append(self.selectionChanged) 	

	def KeyYellow(self):
		self.session.open(MoveBootlogos)
		
	def KeyBlue(self):
		self.session.open(MoveBootlogos_int)


	def setWindowTitle(self):
		self.setTitle('%s' % (_('Bootlogo Setup')))
		
	
	def getCurrentEntry(self):
		if self['Mlist'].l.getCurrentSelection():
			menuv = self['Mlist'].getCurrent()[2]
			menuv1 = list(menuv)[7]
			selection = self['Mlist'].l.getCurrentSelection()[0]
			if (selection[0] is not None):
				return selection[0]

	def selectionChanged(self):
		item = self.getCurrentEntry()

		
	def Exit(self):
		self.close()
 

	def ok(self):
		menu = self['Mlist'].getCurrent()[2]
		menu1 = list(menu)[7]
		os.system("rm /usr/share/bootlogo.mvi")
		os.system("cp /usr/share/enigma2/bootlogos/%s.mvi /usr/share/bootlogo.mvi" %menu1)
		config.bootlogo.booting.value = menu1
		config.bootlogo.booting.save()	
		configfile.save()
		self.close()

class RadiologoSetupScreen(Screen):
	skin = """<screen name="RadiologoSetupScreen" position="center,center" size="950,520" title="RadiologoSetupScreen">
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/redlogo.png" position="0,380" size="950,84" alphatest="on" zPosition="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/alliance.png" position="670,255" size="100,67" alphatest="on" zPosition="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/opennfr_info.png" position="510,11" size="550,354" alphatest="on" zPosition="1" />
				<widget source="global.CurrentTime" render="Label" position="450, 340" size="500,24" font="Regular;20" foregroundColor="white" halign="right" transparent="1" zPosition="5">
				<convert type="ClockToText">&gt;Format%H:%M:%S</convert>
				</widget>
				<eLabel backgroundColor="un56c856" position="0,330" size="950,1" zPosition="0" />
				<widget name="Mlist" position="10,10" size="480,300" zPosition="1" scrollbarMode="showOnDemand" backgroundColor="un251e1f20" transparent="1" />
				<widget name="label1" position="10,340" size="490,25" font="Regular;20" transparent="1" foregroundColor="#f2e000" halign="left" />
 				<ePixmap pixmap="skin_default/buttons/red.png" position="10,480" size="30,30" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/green.png" position="190,480" size="30,30" alphatest="blend" />
				<widget source="key_red" render="Label" position="45,482" size="140,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />
				<widget source="key_green" render="Label" position="225,483" size="140,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />
				<widget source="session.VideoPicture" render="Pig" position="510,11" size="420,236" backgroundColor="transparent" zPosition="2" />
		</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		Screen.setTitle(self, _("RadiologoSetupScreen"))
		self.Console = Console()
		self.onShown.append(self.setWindowTitle)
		aktradiologo = config.radiologo.booting.value
		self["label1"] = Label(_("now Using Radiologo: %s") % aktradiologo)
		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Save"))
		vpath = "/usr/share/enigma2/radiologos/"
		uradio=[]
		uradio = os.listdir(vpath)
		radiologo = []
		for xradio in uradio:
			if xradio.endswith(".mvi"):
				radiologo.append(xradio)
 
		self.list = []
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions"],
			{
				"cancel": self.Exit,
				"exit": self.Exit,
				"red": self.Exit,
				"ok": self.ok,
				"green": self.ok,
			}, 1)
			
		self.Mlist = []
		self.Mlist.append(MenuEntryItem((InfoEntryComponent1('NFRradiologo'), _("NFRradiologo"), 'defaultradiologo')))
		for logo in radiologo:
			yname = logo.strip(".mvi")
			if logo == "NFRradiologo.mvi":
				print("deaultradiologo found")
			else:
				self.Mlist.append(MenuEntryItem((InfoEntryComponent1('%s' % yname), _('%s' % yname), '%s' % logo)))

		self.onChangedEntry = []
		if (getDesktop(0).size().width() == 1920):
			self["Mlist"] = PanelList([], font0=36, font1=28, itemHeight=92)
		else:
			self["Mlist"] = PanelList([])
		self["Mlist"].l.setList(self.Mlist)
		self["Mlist"].onSelectionChanged.append(self.selectionChanged)

	def KeyYellow(self):
		self.session.open(MoveRadiologos)
		
	def KeyBlue(self):
		self.session.open(MoveRadiologos_int)

	def setWindowTitle(self):
		self.setTitle('%s' % (_('Radiologo Setup')))
	
	def getCurrentEntry(self):
		if self['Mlist'].l.getCurrentSelection():
			menuv = self['Mlist'].getCurrent()[2]
			menuv1 = list(menuv)[7]
			if menuv1 == "Default Radiologo":
				menuv1 = "NFRradiologo.mvi"
			selection = self['Mlist'].l.getCurrentSelection()[0]
			if (selection[0] is not None):
				return selection[0]

	def selectionChanged(self):
		item = self.getCurrentEntry()

	
	def Exit(self):
		self.close()

	def ok(self):
		menu = self['Mlist'].getCurrent()[2]
		menu1 = list(menu)[7]
		if menu1 == "Default Radiologo":
			menu1 = "NFRradiologo.mvi"
		os.system("rm /usr/share/enigma2/radio.mvi")
		os.system("cp /usr/share/enigma2/radiologos/%s.mvi /usr/share/enigma2/radio.mvi" %menu1)
		config.radiologo.booting.value = menu1
		config.radiologo.booting.save()	
		configfile.save()
		self.close() 
