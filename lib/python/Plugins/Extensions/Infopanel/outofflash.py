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
from os import popen, system, remove, listdir, chdir, getcwd, statvfs, mkdir, path, walk
from Components.ProgressBar import ProgressBar

def getVarSpaceKb():
    try:
        s = statvfs('/')
    except OSError:
        return (0, 0)

    return (float(s.f_bfree * (s.f_bsize / 1024)), float(s.f_blocks * (s.f_bsize / 1024)))


class MovePlugins_ext(Screen):
	skin = """
		<screen name="MovePlugins_ext" position="0,0" size="800,600" title="Move Plugins to HDD/USB">
				<eLabel text="Move Plugins to HDD/USB" position="66,98" size="720,28" font="Regular;26" backgroundColor="backtop" transparent="1" />
				<widget source="Title" render="Label" position="65,17" size="721,43" font="Regular; 28" backgroundColor="background" transparent="1" foregroundColor="cyan1" />
				<eLabel position="65,130" size="710,2" backgroundColor="grey" />
				<widget name="config" position="65,140" size="710,211" font="Regular;35" itemHeight="30" scrollbarMode="showOnDemand" enableWrapAround="1" backgroundColor="background" transparent="1" />
				<ePixmap pixmap="skin_default/buttons/red.png" position="64,493" size="30,30" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/green.png" position="515,493" size="30,30" alphatest="blend" />
				<widget source="key_red" render="Label" position="101,494" size="240,24" zPosition="1" font="Regular;20" backgroundColor="black" transparent="1" />
				<widget source="key_green" render="Label" position="549,496" size="240,24" zPosition="1" font="Regular;20" backgroundColor="black" transparent="1" />
				<ePixmap position="962,431" size="128,128" zPosition="2" pixmap="icons/setup.png" transparent="1" alphatest="blend" />
				<widget name="introduction" position="116,350" size="600,118" font="Regular;26" transparent="1" foregroundColor="cyan1" alphatest="blend" zPosition="2" />
				<eLabel name="spaceused" text="% Flash Used..." position="164,549" size="150,20" font="Regular;19" halign="left" foregroundColor="white" backgroundColor="black" transparent="1" zPosition="5" />
				<widget name="spaceused" position="329,548" size="380,20" foregroundColor="white" backgroundColor="blue" zPosition="3" />
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
		self.onShown.append(self.setWindowTitle)		
		self['spaceused'] = ProgressBar()		
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
		self.setTitle('%s - %s: %s (%d%%)' % (_('Move Plugins to HDD/USB'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)		
		
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
		<screen name="MovePlugins_int" position="0,0" size="800,600" title="Move Plugins back to Flash">
				<eLabel text="Move Plugins back to Flash" position="66,98" size="720,28" font="Regular;26" backgroundColor="backtop" transparent="1" />
				<widget source="Title" render="Label" position="65,17" size="721,43" font="Regular; 28" backgroundColor="background" transparent="1" foregroundColor="cyan1" />
				<eLabel position="65,130" size="710,2" backgroundColor="grey" />
				<widget name="config" position="65,140" size="710,211" font="Regular;35" itemHeight="30" scrollbarMode="showOnDemand" enableWrapAround="1" backgroundColor="background" transparent="1" />
				<ePixmap pixmap="skin_default/buttons/red.png" position="64,493" size="30,30" alphatest="blend" />
				<ePixmap pixmap="skin_default/buttons/green.png" position="515,493" size="30,30" alphatest="blend" />
				<widget source="key_red" render="Label" position="101,494" size="240,24" zPosition="1" font="Regular;20" backgroundColor="black" transparent="1" />
				<widget source="key_green" render="Label" position="549,496" size="240,24" zPosition="1" font="Regular;20" backgroundColor="black" transparent="1" />
				<ePixmap position="962,431" size="128,128" zPosition="2" pixmap="icons/setup.png" transparent="1" alphatest="blend" />
				<widget name="introduction" position="116,350" size="600,118" font="Regular;26" transparent="1" foregroundColor="cyan1" alphatest="blend" zPosition="2" />
				<eLabel name="spaceused" text="% Flash Used..." position="164,549" size="150,20" font="Regular;19" halign="left" foregroundColor="white" backgroundColor="black" transparent="1" zPosition="5" />
				<widget name="spaceused" position="329,548" size="380,20" foregroundColor="white" backgroundColor="blue" zPosition="3" />
			</screen>"""	
  
	def __init__(self, session):
	        from Components.Sources.StaticText import StaticText
	        self.skin = MovePlugins_int.skin
		Screen.__init__(self, session)
		self["config"] = Label(_("Move Plugins back to flash?"))
		self["introduction"] = Label(_("Do you really want move Plugins back to flash?"))
		self.onShown.append(self.setWindowTitle)		
		self['spaceused'] = ProgressBar()				
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
		self.setTitle('%s - %s: %s (%d%%)' % (_('Move Plugins back to Flash'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)		                        			
