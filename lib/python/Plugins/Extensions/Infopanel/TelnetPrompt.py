from boxbranding import getMachineBrand, getMachineName
from os import path
from Components.Console import Console
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.config import ConfigSubsection, ConfigYesNo, config, ConfigSelection, ConfigText, ConfigNumber, ConfigSet, ConfigLocations, NoSave, ConfigClock, ConfigInteger, ConfigBoolean, ConfigPassword, ConfigIP, ConfigSlider, ConfigSelectionNumber, getConfigListEntry, KEY_LEFT, KEY_RIGHT, configfile
from Components.Sources.StaticText import StaticText
from Plugins.Extensions.Infopanel.outofflash import MoveVideos_int, MoveVideos
from Components.MenuList import MenuList
from enigma import *
from Tools.LoadPixmap import LoadPixmap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from glob import glob
import os

class PanelList(MenuList):
	if (getDesktop(0).size().width() == 1920):
		def __init__(self, list, font0 = 32, font1 = 24, itemHeight = 80, enableWrapAround = True):
			MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
			self.l.setFont(0, gFont("Regular", font0))
			self.l.setFont(1, gFont("Regular", font1))
			self.l.setItemHeight(itemHeight)
	else:
		def __init__(self, list, font0 = 24, font1 = 16, itemHeight = 80, enableWrapAround = True):
			MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
			self.l.setFont(0, gFont("Regular", font0))
			self.l.setFont(1, gFont("Regular", font1))
			self.l.setItemHeight(itemHeight)

def MenuEntryItem(entry):
	if (getDesktop(0).size().width() == 1920):
		res = [entry]
		res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 5), size=(142, 80), png=entry[0])) # png vorn
		res.append(MultiContentEntryText(pos=(152, 5), size=(690, 80), font=0, text=entry[1])) # menupunkt
		return res
	else:
		res = [entry]
		res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 5), size=(142, 80), png=entry[0])) # png vorn
		res.append(MultiContentEntryText(pos=(152, 10), size=(440, 80), font=0, text=entry[1])) # menupunkt
		return res


def InfoEntryComponent(file):
	png = LoadPixmap("/etc/profile_files/" + file + ".png")
	if png == None:
		png = LoadPixmap("/etc/profile_files/default.png")

	res = (png)
	return res

class TelnetPrompt(Screen):
	skin = """
	<screen name="TelnetPrompt" position="center,center" size="950,520" title="TelnetPrompt">
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/redlogo.png" position="0,380" size="950,84" alphatest="on" zPosition="1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/alliance.png" position="670,255" size="100,67" alphatest="on" zPosition="1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/opennfr_info.png" position="510,11" size="550,354" alphatest="on" zPosition="1" />
			<widget source="global.CurrentTime" render="Label" position="450, 340" size="500,24" font="Regular;20" foregroundColor="white" halign="right" transparent="1" zPosition="5">
			<convert type="ClockToText">&gt;Format%H:%M:%S</convert>
			</widget>
		<eLabel backgroundColor="un56c856" position="0,330" size="950,1" zPosition="0" />
			<widget name="Mlist" position="10,10" size="480,325" zPosition="1" scrollbarMode="showOnDemand" backgroundColor="un251e1f20" transparent="1" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,480" size="30,30" alphatest="blend" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="190,480" size="30,30" alphatest="blend" />
			<widget source="key_red" render="Label" position="45,482" size="140,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />
			<widget source="key_green" render="Label" position="225,483" size="140,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />
			<widget source="session.VideoPicture" render="Pig" position="510,11" size="420,236" backgroundColor="transparent" zPosition="2" />
	</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		Screen.setTitle(self, _("TelnetPrompt"))
		self.Console = Console()
		self.onShown.append(self.setWindowTitle)
		self.oldbmcService = self.session.nav.getCurrentlyPlayingServiceReference()
		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Save"))

		vpath = "/etc/profile_files/"
		if not os.path.exists(vpath):
			telnetprompt = []
		else:
			utelnetprompt=[]
			utelnetprompt = os.listdir(vpath)
			telnetprompt = []
			for xtelnetprompt in utelnetprompt:
				if "profile_" in xtelnetprompt and xtelnetprompt.endswith(".png"):
					print("png found")				
				elif "profile_" in xtelnetprompt and not xtelnetprompt.endswith(".png"):
					telnetprompt.append(xtelnetprompt)
				else:
					print("no profilefile")                                	
		self.list = []
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions", "MenuActions", "EPGSelectActions"],
			{
				"cancel": self.Exit,
				"exit": self.Exit,
				"red": self.Exit,
				"ok": self.ok,
				"green": self.ok,
			}, 1)
			
		self.Mlist = []
		self.Mlist.append(MenuEntryItem((InfoEntryComponent('profile_org'), _("profile_org"), 'profile_org')))
		telnetprompt.sort()
		for profiles in telnetprompt:
			self.Mlist.append(MenuEntryItem((InfoEntryComponent('%s' % profiles), _('%s' % profiles), '%s' % profiles)))

		self.onChangedEntry = []
		if (getDesktop(0).size().width() == 1920):
			self["Mlist"] = PanelList([], font0=36, font1=28, itemHeight=50)
		else:
			self["Mlist"] = PanelList([])
		self["Mlist"].l.setList(self.Mlist)
		self["Mlist"].onSelectionChanged.append(self.selectionChanged) 	


	def setWindowTitle(self):
		self.setTitle('%s' % (_('TelnetPrompt')))

	def getCurrentEntry(self):
		if self['Mlist'].l.getCurrentSelection():
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
		menu2 = menu1[:-4]
		os.system("rm /etc/profile")
		os.system("cp /etc/profile_files/%s /etc/profile" % menu1)
		
		self.close()
