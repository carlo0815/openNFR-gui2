from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Harddisk import harddiskmanager
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Task import job_manager
from Screens.MessageBox import MessageBox
from Tools.BoundFunction import boundFunction
from enigma import eConsoleAppContainer, eServiceReference, ePicLoad, getDesktop, eServiceCenter
import Screens.InfoBar  
import os
import shutil
class MovePlugins_ext(Screen):
	skin = """
		<screen name="MovePlugins_ext" position="0,0" size="1280,720" title="Move Plugins to HDD/USB" flags="wfNoBorder">
			<ePixmap position="center,center" zPosition="-10" size="1280,720" pixmap="menu/back2b.png" />
			<eLabel position="837,95" zPosition="3" size="375,214" backgroundColor="unff000000" />
			<widget source="session.VideoPicture" render="Pig" position="837,95" zPosition="-8" size="375,214" />
			<ePixmap position="848,596" size="350,44" pixmap="menu/db.png" transparent="1" alphatest="blend" />
			<widget source="global.CurrentTime" render="Label" position="1125,12" size="100,28" font="Regular;26" halign="right" backgroundColor="backtop" transparent="1" foregroundColor="cyan1">
			<convert type="ClockToText">Default</convert>
			</widget>
			<widget source="global.CurrentTime" render="Label" position="905,37" size="320,25" font="Regular;20" halign="right" backgroundColor="backtop" transparent="1" foregroundColor="cyan1">
			<convert type="ClockToText">Format:%A, %d.%m.%Y</convert>
			</widget>
			<eLabel text="Move Plugins to HDD/USB" position="65,17" size="720,43" font="Regular;26" backgroundColor="backtop" transparent="1" foregroundColor="cyan1" />
			<widget source="Title" render="Label" position="65,98" size="670,28" font="Regular;26" backgroundColor="background" transparent="1" />
			<eLabel position="65,130" size="710,2" backgroundColor="grey" />
			<widget name="config" position="65,140" size="710,480" font="Regular;35" itemHeight="30" scrollbarMode="showOnDemand" enableWrapAround="1" backgroundColor="background" transparent="1" />
			<ePixmap pixmap="buttons/red.png" position=" 70,670" size="30,30" alphatest="blend" />
			<ePixmap pixmap="buttons/green.png" position="360,670" size="30,30" alphatest="blend" />
			<widget source="key_red" render="Label" position="105,672" size="240,24" zPosition="1" font="Regular;20" backgroundColor="black" transparent="1" />
			<widget source="key_green" render="Label" position="395,672" size="240,24" zPosition="1" font="Regular;20" backgroundColor="black" transparent="1" />
			<ePixmap position="962,431" size="128,128" zPosition="2" pixmap="icons/setup.png" transparent="1" alphatest="blend" />
			<widget name="introduction" position="123,398" size="600,200" font="Regular;26" transparent="1" foregroundColor="cyan1" alphatest="blend" zPosition="2" />
		</screen>"""	
	def __init__(self, session, hdd, text, question):
	        from Components.Sources.StaticText import StaticText
	        self.skin = MovePlugins_ext.skin	
		Screen.__init__(self, session)
		global pluginpoint
		pluginpoint = hdd.findMount()
		self.question = question
		self.curentservice = None
		self["config"] = Label(_("Extensions outsource to: ") + hdd.findMount())
		self["introduction"] = Label(text)
		self["key_red"] = StaticText(_("Cancel"))
                self["key_green"] = StaticText(_("Ok"))
		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"ok": self.hddQuestion,
			"cancel": self.close
		})
		self["shortcuts"] = ActionMap(["ShortcutActions"],
		{
			"red": self.close,
			"green": self.hddQuestion			
		})

	def hddQuestion(self, answer=False):
		if Screens.InfoBar.InfoBar.instance.timeshiftEnabled():
			message = self.question + "\n\n" + _("You seem to be in timeshift, the service will briefly stop as timeshift stops.")
			message += '\n' + _("Do you want to continue?")
			self.session.openWithCallback(self.stopTimeshift, MessageBox, message)
		else:
			self.hddConfirmed(True)

	def stopTimeshift(self, confirmed):
		if confirmed:
			self.curentservice = self.session.nav.getCurrentlyPlayingServiceReference()
			self.session.nav.stopService()
			Screens.InfoBar.InfoBar.instance.stopTimeshiftcheckTimeshiftRunningCallback(True)
			self.hddConfirmed(True)

	def hddConfirmed(self, confirmed):
		if not confirmed:
			return  
		try:
			self.pluginConfirmed()
			

		except Exception, ex:
			self.session.open(MessageBox, str(ex), type=MessageBox.TYPE_ERROR, timeout=10)

		if self.curentservice:
			self.session.nav.playService(self.curentservice)
		self.close()

	def pluginConfirmed(self):
	        PLUGINDIR = "/usr/lib/enigma2/python/Plugins/Extensions"
	        oldplug = "/usr/lib/enigma2/python/Extensionsold"
	        mountpath = pluginpoint + "/Extensions"	
		try:
			mounts = open("/proc/mounts", 'r')
			result = []
			tmp = [line.strip().split(' ') for line in mounts]
			mounts.close()
			for item in tmp:
				# Spaces are encoded as \040 in mounts
				if pluginpoint in item:
					if "ext2" in item or "ext3" in item or "ext4" in item:
						extplugs = True
				        else:
                                        	extplugs = False

		except IOError, ex:
			print "[Harddisk] Failed to open /proc/mounts", ex

			
		if extplugs == True:	
	        	if os.path.exists("%s" % PLUGINDIR) == True:
	        		if os.path.exists("%s" % mountpath) == True:
	                		message = _("On Device is a folder Extensions, do you want to use this?")
	                		self.session.openWithCallback(self.pluginConfirmed_Ext, MessageBox, message)
                        	else: 
	                		shutil.copytree(PLUGINDIR, mountpath)
                        	        if os.path.islink(PLUGINDIR) and  os.path.exists("%s" % mountpath) == True:
                                                message = _("Plugins already moved to %s!" % mountpath)
                                                self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                                        elif os.path.islink(PLUGINDIR) and  os.path.exists("%s" % mountpath) == False: 
                                                message = _("Something wrong in Image! Please check all again.")
                                                self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                                        else:                                                             
                               			os.rename(PLUGINDIR, oldplug)        
                                		os.symlink(mountpath, PLUGINDIR)
                                		message = _("Plugins moved to %s ready!" % mountpath)
                                		self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                	else:
                        	message = _("Something wrong in Image! Please check all again.")
	                	self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5) 
                else:
                       	message = _("Selected Device not in EXT2(3/4)-Format, needed for working!")
	               	self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)                 


	def pluginConfirmed_Ext(self, confirmed):
	        PLUGINDIR = "/usr/lib/enigma2/python/Plugins/Extensions"
	        oldplug = "/usr/lib/enigma2/python/Extensionsold"
	        mountpath = pluginpoint + "/Extensions"	
	        if confirmed:
	                if os.path.islink(PLUGINDIR):
	                        self.close()
	                else:
                                os.rename(PLUGINDIR, oldplug)   	                	
                                os.symlink(mountpath, PLUGINDIR)
	        else:
                        if os.path.islink(PLUGINDIR):
                                self.close()
                        else:
                                shutil.rmtree(mountpath)
                                shutil.copytree(PLUGINDIR, mountpath)
                                os.rename(PLUGINDIR, oldplug)   	                	
                                os.symlink(mountpath, PLUGINDIR)       	
  
	        self.close()
                
class MovePlugins(Screen):
	def __init__(self, session):
	        Screen.__init__(self, session)
		Screen.setTitle(self, _("Plugins out of flash"))
		self.skinName = "HarddiskSelection" # For derived classes
		if harddiskmanager.HDDCount() == 0:
			tlist = [(_("no storage devices found"), 0)]
			self["hddlist"] = MenuList(tlist)
		else:
			self["hddlist"] = MenuList(harddiskmanager.HDDList())

		self["actions"] = ActionMap(["OkCancelActions"],
		{
			"ok": self.okbuttonClick,
			"cancel": self.close
		})

	def doIt(self, selection):
		self.session.openWithCallback(self.close, MovePlugins_ext, selection,
			 text=_("Do you really want to use selected Device for Plugins?\n"),
			 question=_(""))

	def okbuttonClick(self):
		selection = self["hddlist"].getCurrent()
		if selection[1] != 0:
			self.doIt(selection[1])
			self.close(True)
			
class MovePlugins_int(Screen):
	skin = """
		<screen name="MovePlugins_int" position="0,0" size="1280,720" title="Move Plugins back to Flash" flags="wfNoBorder">
			<ePixmap position="center,center" zPosition="-10" size="1280,720" pixmap="menu/back2b.png" />
			<eLabel position="837,95" zPosition="3" size="375,214" backgroundColor="unff000000" />
			<widget source="session.VideoPicture" render="Pig" position="837,95" zPosition="-8" size="375,214" />
			<ePixmap position="848,596" size="350,44" pixmap="menu/db.png" transparent="1" alphatest="blend" />
			<widget source="global.CurrentTime" render="Label" position="1125,12" size="100,28" font="Regular;26" halign="right" backgroundColor="backtop" transparent="1" foregroundColor="cyan1">
			<convert type="ClockToText">Default</convert>
			</widget>
			<widget source="global.CurrentTime" render="Label" position="905,37" size="320,25" font="Regular;20" halign="right" backgroundColor="backtop" transparent="1" foregroundColor="cyan1">
			<convert type="ClockToText">Format:%A, %d.%m.%Y</convert>
			</widget>
			<eLabel text="Move Plugins back to Flash" position="65,17" size="720,43" font="Regular;26" backgroundColor="backtop" transparent="1" foregroundColor="cyan1" />
			<widget source="Title" render="Label" position="65,98" size="670,28" font="Regular;26" backgroundColor="background" transparent="1" />
			<eLabel position="65,130" size="710,2" backgroundColor="grey" />
			<widget name="config" position="65,140" size="710,480" font="Regular;35" itemHeight="30" scrollbarMode="showOnDemand" enableWrapAround="1" backgroundColor="background" transparent="1" />
			<ePixmap pixmap="buttons/red.png" position=" 70,670" size="30,30" alphatest="blend" />
			<ePixmap pixmap="buttons/green.png" position="360,670" size="30,30" alphatest="blend" />
			<widget source="key_red" render="Label" position="105,672" size="240,24" zPosition="1" font="Regular;20" backgroundColor="black" transparent="1" />
			<widget source="key_green" render="Label" position="395,672" size="240,24" zPosition="1" font="Regular;20" backgroundColor="black" transparent="1" />
			<ePixmap position="962,431" size="128,128" zPosition="2" pixmap="icons/setup.png" transparent="1" alphatest="blend" />
			<widget name="introduction" position="123,398" size="600,200" font="Regular;26" transparent="1" foregroundColor="cyan1" alphatest="blend" zPosition="2" />
		</screen>"""	
	def __init__(self, session):
	        from Components.Sources.StaticText import StaticText
	        self.skin = MovePlugins_int.skin
		Screen.__init__(self, session)
		self["config"] = Label(_("Move Plugins back to flash?"))
		self["introduction"] = Label(_("Do you really want move Plugins back to flash?"))
                self["key_red"] = StaticText(_("Cancel"))
                self["key_green"] = StaticText(_("Ok"))
                self["actions"] = ActionMap(["WizardActions", "ColorActions", "EPGSelectActions"],

                {
                "ok": self.doIt,
                "back": self.close,
                "green": self.doIt,
                "red": self.close,

                }, -1)

	def doIt(self):
	        oldplug = "/usr/lib/enigma2/python/Extensionsold"        
                PLUGINDIR = "/usr/lib/enigma2/python/Plugins/Extensions"
                if os.path.islink(PLUGINDIR):
                        message = _("Plugins moved back to flash ready!")
                        os.unlink(PLUGINDIR)
                        os.rename(oldplug, PLUGINDIR)
                        self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                else:
                        message = _("Plugins already back in flash!")
                        self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                         
                         			
