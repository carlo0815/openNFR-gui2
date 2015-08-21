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
config.bootvideo = ConfigSubsection()
config.bootvideo.booting = ConfigText(default = "no Bootvideo")

class PanelList(MenuList):
        if (getDesktop(0).size().width() == 1920):
	        def __init__(self, list, font0 = 32, font1 = 24, itemHeight = 50, enableWrapAround = True):
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
	   res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 5), size=(100, 40), png=entry[0]))  # png vorn
	   res.append(MultiContentEntryText(pos=(110, 5), size=(690, 40), font=0, text=entry[1]))  # menupunkt
	   return res
	else:
	   res = [entry]
	   res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 5), size=(100, 40), png=entry[0]))  # png vorn
       	   res.append(MultiContentEntryText(pos=(110, 10), size=(440, 40), font=0, text=entry[1]))  # menupunkt
	   return res
	   

def InfoEntryComponent(file):
	png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/" + file + ".png")
	if png == None:
		png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/default.png")

	res = (png)
	return res
                        	   
           
class BootvideoSetupScreen(Screen):
	skin = """<screen name="BootvideoSetupScreen" position="center,center" size="950,470" title="BootvideoSetupScreen">
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/redlogo.png" position="0,380" size="950,84" alphatest="on" zPosition="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/alliance.png" position="670,255" size="100,67" alphatest="on" zPosition="1" />
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/opennfr_info.png" position="510,11" size="550,354" alphatest="on" zPosition="1" />
				<widget source="global.CurrentTime" render="Label" position="450, 340" size="500,24" font="Regular;20" foregroundColor="white" halign="right" transparent="1" zPosition="5">
				<convert type="ClockToText">&gt;Format%H:%M:%S</convert>
				</widget>
				<eLabel backgroundColor="un56c856" position="0,330" size="950,1" zPosition="0" />
				<widget name="Mlist" position="10,10" size="480,300" zPosition="1" scrollbarMode="showOnDemand" backgroundColor="un251e1f20" transparent="1" />
				<widget name="label1" position="10,340" size="490,25" font="Regular;20" transparent="1" foregroundColor="#f2e000" halign="left" />
                </screen>"""	
	def __init__(self, session):
		Screen.__init__(self, session)
                self.session = session
		Screen.setTitle(self, _("BootvideoSetupScreen"))
                self.Console = Console()
		self.onShown.append(self.setWindowTitle)
		aktbootvideo = config.bootvideo.booting.value
		self["label1"] = Label(_("now Using Bootvideo: %s") % aktbootvideo)
		self["key_red"] = StaticText(_("Exit"))
                self["key_green"] = StaticText(_("Save"))
		self["key_blue"] = StaticText(_("MoveVideos_int"))
                self["key_yellow"] = StaticText(_("MoveVideos_ext"))

	        vpath = "/usr/share/enigma2/bootvideos/"	
		uvideo=[]
		uvideo = os.listdir(vpath)
		bootvideo = []
                for xvideo in uvideo:
                       	if xvideo.endswith(".mp4"):
                       	       	bootvideo.append(xvideo)
                       	elif xvideo.endswith(".mkv"):
                       	       	bootvideo.append(xvideo)
                       	elif xvideo.endswith(".mpeg"):
                       	       	bootvideo.append(xvideo)  
		self.list = []
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions", "MenuActions", "EPGSelectActions"],
			{
				"cancel": self.Exit,
				"exit": self.Exit,
				"red": self.Exit,                                				
				"ok": self.ok,
				"green": self.ok,
				"blue": self.KeyBlue,
				"yellow": self.KeyYellow,
				"info": self.KeyInfo,
                                				
			}, 1)
			
                self.Mlist = []
		self.Mlist.append(MenuEntryItem((InfoEntryComponent('no Bootvideo'), _("no Bootvideo"), 'nobootvideo')))
                for video in bootvideo:
			self.Mlist.append(MenuEntryItem((InfoEntryComponent('%s' % video), _('%s' % video), '%s' % video)))

		self.onChangedEntry = []
		if (getDesktop(0).size().width() == 1920):
			self["Mlist"] = PanelList([], font0=36, font1=28, itemHeight=50)
		else:
		        self["Mlist"] = PanelList([])
		self["Mlist"].l.setList(self.Mlist)
		self["Mlist"].onSelectionChanged.append(self.selectionChanged) 	
		
	def KeyInfo(self):
	        self.session.nav.stopService()
	        menu = self['Mlist'].getCurrent()[2]
		menu1 = list(menu)[7]
		os.system('gst-launch-1.0 playbin uri=file:///usr/share/enigma2/bootvideos/%s' % menu1)
                self.session.nav.playService(self.oldbmcService)

	def KeyYellow(self):
		self.session.open(MoveVideos)
		
	def KeyBlue(self):
		self.session.open(MoveVideos_int)		

	def setWindowTitle(self):
		self.setTitle('%s' % (_('Bootvideo Setup')))
		
	
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
		config.bootvideo.booting.value = menu1
		config.bootvideo.booting.save()	
		configfile.save()
		self.close()
