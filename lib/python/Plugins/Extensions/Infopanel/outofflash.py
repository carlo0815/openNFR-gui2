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
	        try:
		        if Screens.InfoBar.InfoBar.instance.timeshiftEnabled():
			        message = self.question + "\n\n" + _("You seem to be in timeshift, the service will briefly stop as timeshift stops.")
			        message += '\n' + _("Do you want to continue?")
			        self.session.openWithCallback(self.stopTimeshift, MessageBox, message)
		        else:
			        self.hddConfirmed(True)
		except:
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

class MoveVideos_ext(Screen):
	skin = """
		<screen name="MoveVideos_ext" position="0,0" size="800,600" title="Move Bootvideos to HDD/USB">
				<eLabel text="Move Bootvideos to HDD/USB" position="66,98" size="720,28" font="Regular;26" backgroundColor="backtop" transparent="1" />
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
	        self.skin = MoveVideos_ext.skin	
		Screen.__init__(self, session)
		global videopoint
		videopoint = hdd.findMount()
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
		self.setTitle('%s - %s: %s (%d%%)' % (_('Move Bootvideos to HDD/USB'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)		
		
	def hddQuestion(self, answer=False):
	        try:
		        if Screens.InfoBar.InfoBar.instance.timeshiftEnabled():
			        message = self.question + "\n\n" + _("You seem to be in timeshift, the service will briefly stop as timeshift stops.")
			        message += '\n' + _("Do you want to continue?")
			        self.session.openWithCallback(self.stopTimeshift, MessageBox, message)
		        else:
			        self.hddConfirmed(True)
		except:
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
			self.videoConfirmed()
			

		except Exception, ex:
			self.session.open(MessageBox, str(ex), type=MessageBox.TYPE_ERROR, timeout=10)

		if self.curentservice:
			self.session.nav.playService(self.curentservice)
		self.close()

	def videoConfirmed(self):
	        VIDEODIR = "/usr/share/enigma2/bootvideos"
	        mountpath = videopoint + "/bootvideos"	
		try:
			mounts = open("/proc/mounts", 'r')
			result = []
			tmp = [line.strip().split(' ') for line in mounts]
			mounts.close()
			for item in tmp:
				# Spaces are encoded as \040 in mounts
				if videopoint in item:
					if "ext2" in item or "ext3" in item or "ext4" in item:
						extvideo = True
				        else:
                                        	extvideo = False

		except IOError, ex:
			print "[Harddisk] Failed to open /proc/mounts", ex

			
		if extvideo == True:	
	        	if os.path.exists("%s" % VIDEODIR) == True:
	        		if os.path.exists("%s" % mountpath) == True:
	                		message = _("On Device is a folder bootvideos, do you want to use this? Attention if you answer with yes Bootvideos from flash will be deleted!")
	                		self.session.openWithCallback(self.videoConfirmed_Ext, MessageBox, message)
                        	else: 
	                		shutil.copytree(VIDEODIR, mountpath)
                        	        if os.path.islink(VIDEODIR) and  os.path.exists("%s" % mountpath) == True:
                                                message = _("Bootvideos already moved to %s!" % mountpath)
                                                self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                                        elif os.path.islink(VIDEODIR) and  os.path.exists("%s" % mountpath) == False: 
                                                message = _("Something wrong in Image! Please check all again.")
                                                self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                                        else:                                                             
                               			shutil.rmtree(VIDEODIR)        
                                		os.symlink(mountpath, VIDEODIR)
                                		message = _("Bootvideos moved to %s ready!" % mountpath)
                                		self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                	else:
                        	message = _("Something wrong in Image! Please check all again.")
	                	self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5) 
                else:
                       	message = _("Selected Device not in EXT2(3/4)-Format, needed for working!")
	               	self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)                 


	def videoConfirmed_Ext(self, confirmed):
	        VIDEODIR = "/usr/share/enigma2/bootvideos"
	        mountpath = videopoint + "/bootvideos"	
	        if confirmed:
	                if os.path.islink(VIDEODIR):
	                        print "1"
	                        self.close()
	                else:
	                        print "2"
                                shutil.rmtree(VIDEODIR)   	                	
                                os.symlink(mountpath, VIDEODIR)
	        else:
                        if os.path.islink(VIDEODIR):
                                print "3"
                                self.close()
                        else:
                                print "4"
                                shutil.rmtree(mountpath)
                                shutil.copytree(VIDEODIR, mountpath)
                                shutil.rmtree(VIDEODIR)   	                	
                                os.symlink(mountpath, VIDEODIR)       	
  
	        self.close()
                
class MoveVideos(Screen):
	def __init__(self, session):
	        Screen.__init__(self, session)
		Screen.setTitle(self, _("Bootvideos out of flash"))
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
		self.session.openWithCallback(self.close, MoveVideos_ext, selection,
			 text=_("Do you really want to use selected Device for Bootvideos?\n"),
			 question=_(""))

	def okbuttonClick(self):
		selection = self["hddlist"].getCurrent()
		if selection[1] != 0:
			self.doIt(selection[1])
			self.close(True)
			
class MoveVideos_int(Screen):
	skin = """
		<screen name="MoveVideos_int" position="0,0" size="800,600" title="Move Bootvideos back to Flash">
				<eLabel text="Move Bootvideos back to Flash" position="66,98" size="720,28" font="Regular;26" backgroundColor="backtop" transparent="1" />
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
	        self.skin = MoveVideos_int.skin
		Screen.__init__(self, session)
		self["config"] = Label(_("Move Bootvideos back to flash?"))
		self["introduction"] = Label(_("Do you really want move Bootvideos back to flash?"))
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
                VIDEODIR = "/usr/share/enigma2/bootvideos"
                if os.path.islink(VIDEODIR):
                        message = _("Bootvideos moved back to flash ready!")
                        os.unlink(VIDEODIR)
                        os.mkdir(VIDEODIR)
                        self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                else:
                        message = _("Bootvideos already back in flash!")
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
		self.setTitle('%s - %s: %s (%d%%)' % (_('Move Bootvideos back to Flash'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)			

		
class MoveBootlogos_ext(Screen):
	skin = """
		<screen name="MoveBootlogos_ext" position="0,0" size="800,600" title="Move Bootlogos to HDD/USB">
				<eLabel text="Move Bootlogos to HDD/USB" position="66,98" size="720,28" font="Regular;26" backgroundColor="backtop" transparent="1" />
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
		self.skin = MoveBootlogos_ext.skin	
		Screen.__init__(self, session)
		global bootlogopoint
		bootlogopoint = hdd.findMount()
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
		self.setTitle('%s - %s: %s (%d%%)' % (_('Move Bootlogos to HDD/USB'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)		
		
	def hddQuestion(self, answer=False):
	        try:
		        if Screens.InfoBar.InfoBar.instance.timeshiftEnabled():
			        message = self.question + "\n\n" + _("You seem to be in timeshift, the service will briefly stop as timeshift stops.")
			        message += '\n' + _("Do you want to continue?")
			        self.session.openWithCallback(self.stopTimeshift, MessageBox, message)
		        else:
			        self.hddConfirmed(True)
		except:
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
			self.bootlogoConfirmed()
			

		except Exception, ex:
			self.session.open(MessageBox, str(ex), type=MessageBox.TYPE_ERROR, timeout=10)

		if self.curentservice:
			self.session.nav.playService(self.curentservice)
		self.close()

	def bootlogoConfirmed(self):
	        BOOTLOGODIR = "/usr/share/enigma2/bootlogos"
	        mountpath = bootlogopoint + "/bootlogos"	
		try:
			mounts = open("/proc/mounts", 'r')
			result = []
			tmp = [line.strip().split(' ') for line in mounts]
			mounts.close()
			for item in tmp:
				# Spaces are encoded as \040 in mounts
				if bootlogopoint in item:
					if "ext2" in item or "ext3" in item or "ext4" in item:
						extbootlogo = True
					else:
						extbootlogo = False

		except IOError, ex:
			print "[Harddisk] Failed to open /proc/mounts", ex

			
		if extbootlogo == True:	
	        	if os.path.exists("%s" % BOOTLOGODIR) == True:
	        		if os.path.exists("%s" % mountpath) == True:
	                		message = _("On Device is a folder bootLOGOS, do you want to use this? Attention if you answer with yes Bootlogos from flash will be deleted!")
	                		self.session.openWithCallback(self.bootlogoConfirmed_Ext, MessageBox, message)
                        	else: 
	                		shutil.copytree(BOOTLOGODIR, mountpath)
                        	        if os.path.islink(BOOTLOGODIR) and  os.path.exists("%s" % mountpath) == True:
                                                message = _("Bootlogos already moved to %s!" % mountpath)
                                                self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                                        elif os.path.islink(BOOTLOGODIR) and  os.path.exists("%s" % mountpath) == False: 
                                                message = _("Something wrong in Image! Please check all again.")
                                                self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                                        else:                                                             
                               			shutil.rmtree(BOOTLOGODIR)        
                                		os.symlink(mountpath, BOOTLOGODIR)
                                		message = _("Bootlogos moved to %s ready!" % mountpath)
                                		self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                	else:
                        	message = _("Something wrong in Image! Please check all again.")
	                	self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5) 
                else:
                       	message = _("Selected Device not in EXT2(3/4)-Format, needed for working!")
	               	self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)                 


	def bootlogoConfirmed_Ext(self, confirmed):
	        BOOTLOGODIR = "/usr/share/enigma2/bootlogos"
	        mountpath = bootlogopoint + "/bootlogos"
	        if confirmed:
	                if os.path.islink(BOOTLOGODIR):
	                        self.close()
	                else:
                                shutil.rmtree(BOOTLOGODIR)   	                	
                                os.symlink(mountpath, BOOTLOGODIR)
	        else:
                        if os.path.islink(BOOTLOGODIR):
                                self.close()
                        else:
                                shutil.rmtree(mountpath)
                                shutil.copytree(BOOTLOGODIR, mountpath)
                                shutil.rmtree(BOOTLOGODIR)   	                	
                                os.symlink(mountpath, BOOTLOGODIR)       	
  
	        self.close()
                
class MoveBootlogos(Screen):
	def __init__(self, session):
	        Screen.__init__(self, session)
		Screen.setTitle(self, _("Bootlogos out of flash"))
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
		self.session.openWithCallback(self.close, MoveBootlogos_ext, selection,
			 text=_("Do you really want to use selected Device for Bootlogos?\n"),
			 question=_(""))

	def okbuttonClick(self):
		selection = self["hddlist"].getCurrent()
		if selection[1] != 0:
			self.doIt(selection[1])
			self.close(True)
			
class MoveBootlogos_int(Screen):
	skin = """
		<screen name="MoveBootlogos_int" position="0,0" size="800,600" title="Move Bootlogos back to Flash">
				<eLabel text="Move Bootlogos back to Flash" position="66,98" size="720,28" font="Regular;26" backgroundColor="backtop" transparent="1" />
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
		self.skin = MoveBootlogos_int.skin
		Screen.__init__(self, session)
		self["config"] = Label(_("Move Bootlogos back to flash?"))
		self["introduction"] = Label(_("Do you really want move Bootlogos back to flash?"))
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
                BOOTLOGODIR = "/usr/share/enigma2/bootlogos"
                if os.path.islink(BOOTLOGODIR):
                        message = _("Bootlogos moved back to flash ready!")
                        os.unlink(BOOTLOGODIR)
                        os.mkdir(BOOTLOGODIR)
                        self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                else:
                        message = _("Bootlogos already back in flash!")
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
		self.setTitle('%s - %s: %s (%d%%)' % (_('Move Bootlogos back to Flash'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)

class MoveRadiologos_ext(Screen):
	skin = """
		<screen name="MoveRadiologos_ext" position="0,0" size="800,600" title="Move Radiologos to HDD/USB">
				<eLabel text="Move Radiologos to HDD/USB" position="66,98" size="720,28" font="Regular;26" backgroundColor="backtop" transparent="1" />
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
		self.skin = MoveRadiologos_ext.skin	
		Screen.__init__(self, session)
		global radiologopoint
		radiologopoint = hdd.findMount()
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
		self.setTitle('%s - %s: %s (%d%%)' % (_('Move Radiologos to HDD/USB'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)		
		
	def hddQuestion(self, answer=False):
	        try:
		        if Screens.InfoBar.InfoBar.instance.timeshiftEnabled():
			        message = self.question + "\n\n" + _("You seem to be in timeshift, the service will briefly stop as timeshift stops.")
			        message += '\n' + _("Do you want to continue?")
			        self.session.openWithCallback(self.stopTimeshift, MessageBox, message)
		        else:
			        self.hddConfirmed(True)
		except:
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
			self.radiologoConfirmed()
			

		except Exception, ex:
			self.session.open(MessageBox, str(ex), type=MessageBox.TYPE_ERROR, timeout=10)

		if self.curentservice:
			self.session.nav.playService(self.curentservice)
		self.close()

	def radiologoConfirmed(self):
	        RADIOLOGODIR = "/usr/share/enigma2/radiologos"
	        mountpath = radiologopoint + "/radiologos"	
		try:
			mounts = open("/proc/mounts", 'r')
			result = []
			tmp = [line.strip().split(' ') for line in mounts]
			mounts.close()
			for item in tmp:
				# Spaces are encoded as \040 in mounts
				if radiologopoint in item:
					if "ext2" in item or "ext3" in item or "ext4" in item:
						extradiologo = True
					else:
						extradiologo = False

		except IOError, ex:
			print "[Harddisk] Failed to open /proc/mounts", ex

			
		if extradiologo == True:	
	        	if os.path.exists("%s" % RADIOLOGODIR) == True:
	        		if os.path.exists("%s" % mountpath) == True:
	                		message = _("On Device is a folder radiologos, do you want to use this? Attention if you answer with yes Radiologos from flash will be deleted!")
	                		self.session.openWithCallback(self.radiologoConfirmed_Ext, MessageBox, message)
                        	else: 
	                		shutil.copytree(RADIOLOGODIR, mountpath)
                        	        if os.path.islink(RADIOLOGODIR) and  os.path.exists("%s" % mountpath) == True:
                                                message = _("Radiologos already moved to %s!" % mountpath)
                                                self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                                        elif os.path.islink(RADIOLOGODIR) and  os.path.exists("%s" % mountpath) == False: 
                                                message = _("Something wrong in Image! Please check all again.")
                                                self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                                        else:                                                             
                               			shutil.rmtree(RADIOLOGODIR)        
                                		os.symlink(mountpath, RADIOLOGODIR)
                                		message = _("Radiologos moved to %s ready!" % mountpath)
                                		self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                	else:
                        	message = _("Something wrong in Image! Please check all again.")
	                	self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5) 
                else:
                       	message = _("Selected Device not in EXT2(3/4)-Format, needed for working!")
	               	self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)                 


	def radiologoConfirmed_Ext(self, confirmed):
	        RADIOLOGODIR = "/usr/share/enigma2/radiologos"
	        mountpath = radiologopoint + "/radiologos"
	        if confirmed:
	                if os.path.islink(RADIOLOGODIR):
	                        self.close()
	                else:
                                shutil.rmtree(RADIOLOGODIR)   	                	
                                os.symlink(mountpath, RADIOLOGODIR)
	        else:
                        if os.path.islink(RADIOLOGODIR):
                                self.close()
                        else:
                                shutil.rmtree(mountpath)
                                shutil.copytree(RADIOLOGODIR, mountpath)
                                shutil.rmtree(RADIOLOGODIR)   	                	
                                os.symlink(mountpath, RADIOLOGODIR)       	
  
	        self.close()
                
class MoveRadiologos(Screen):
	def __init__(self, session):
	        Screen.__init__(self, session)
		Screen.setTitle(self, _("Radiologos out of flash"))
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
		self.session.openWithCallback(self.close, MoveRadiologos_ext, selection,
			 text=_("Do you really want to use selected Device for Radiologos?\n"),
			 question=_(""))

	def okbuttonClick(self):
		selection = self["hddlist"].getCurrent()
		if selection[1] != 0:
			self.doIt(selection[1])
			self.close(True)
			
class MoveRadiologos_int(Screen):
	skin = """
		<screen name="MoveRadiologos_int" position="0,0" size="800,600" title="Move Radiologos back to Flash">
				<eLabel text="Move Radiologos back to Flash" position="66,98" size="720,28" font="Regular;26" backgroundColor="backtop" transparent="1" />
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
		self.skin = MoveRadiologos_int.skin
		Screen.__init__(self, session)
		self["config"] = Label(_("Move Radiologos back to flash?"))
		self["introduction"] = Label(_("Do you really want move Radiologos back to flash?"))
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
                RADIOLOGODIR = "/usr/share/enigma2/radiologos"
                if os.path.islink(RADIOLOGODIR):
                        message = _("Radiologos moved back to flash ready!")
                        os.unlink(RADIOLOGODIR)
                        os.mkdir(RADIOLOGODIR)
                        self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                else:
                        message = _("Radiologos already back in flash!")
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
		self.setTitle('%s - %s: %s (%d%%)' % (_('Move Radiologos back to Flash'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)	

class MoveSpinner_ext(Screen):
	skin = """
		<screen name="MoveSpinner_ext" position="0,0" size="800,600" title="Move Spinner to HDD/USB">
				<eLabel text="Move Spinner to HDD/USB" position="66,98" size="720,28" font="Regular;26" backgroundColor="backtop" transparent="1" />
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
		self.skin = MoveSpinner_ext.skin	
		Screen.__init__(self, session)
		global spinnerpoint
		spinnerpoint = hdd.findMount()
		self.question = question
		self.curentservice = None
		self["config"] = Label(_("Spinner outsource to: ") + hdd.findMount())
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
		self.setTitle('%s - %s: %s (%d%%)' % (_('Move Spinner to HDD/USB'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)		
		
	def hddQuestion(self, answer=False):
	        try:
		        if Screens.InfoBar.InfoBar.instance.timeshiftEnabled():
			        message = self.question + "\n\n" + _("You seem to be in timeshift, the service will briefly stop as timeshift stops.")
			        message += '\n' + _("Do you want to continue?")
			        self.session.openWithCallback(self.stopTimeshift, MessageBox, message)
		        else:
			        self.hddConfirmed(True)
		except:
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
			self.spinnerConfirmed()
			

		except Exception, ex:
			self.session.open(MessageBox, str(ex), type=MessageBox.TYPE_ERROR, timeout=10)

		if self.curentservice:
			self.session.nav.playService(self.curentservice)
		self.close()

	def spinnerConfirmed(self):
	        SPINNERDIR = "/usr/share/enigma2/Spinner"
	        mountpath = spinnerpoint + "/Spinner"	
		try:
			mounts = open("/proc/mounts", 'r')
			result = []
			tmp = [line.strip().split(' ') for line in mounts]
			mounts.close()
			for item in tmp:
				# Spaces are encoded as \040 in mounts
				if spinnerpoint in item:
					if "ext2" in item or "ext3" in item or "ext4" in item:
						extspinner = True
					else:
						extspinner = False

		except IOError, ex:
			print "[Harddisk] Failed to open /proc/mounts", ex

			
		if extspinner == True:	
	        	if os.path.exists("%s" % SPINNERDIR) == True:
	        		if os.path.exists("%s" % mountpath) == True:
	                		message = _("On Device is a folder Spinner, do you want to use this? Attention if you answer with yes Spinner from flash will be deleted!")
	                		self.session.openWithCallback(self.spinnerConfirmed_Ext, MessageBox, message)
                        	else: 
	                		shutil.copytree(SPINNERDIR, mountpath)
                        	        if os.path.islink(SPINNERDIR) and  os.path.exists("%s" % mountpath) == True:
                                                message = _("Spinner already moved to %s!" % mountpath)
                                                self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                                        elif os.path.islink(SPINNERDIR) and  os.path.exists("%s" % mountpath) == False: 
                                                message = _("Something wrong in Image! Please check all again.")
                                                self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                                        else:                                                             
                               			shutil.rmtree(SPINNERDIR)        
                                		os.symlink(mountpath, SPINNERDIR)
                                		message = _("Spinner moved to %s ready!" % mountpath)
                                		self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                	else:
                        	message = _("Something wrong in Image! Please check all again.")
	                	self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5) 
                else:
                       	message = _("Selected Device not in EXT2(3/4)-Format, needed for working!")
	               	self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)                 


	def spinnerConfirmed_Ext(self, confirmed):
	        SPINNERDIR = "/usr/share/enigma2/Spinner"
	        mountpath = spinnerpoint + "/Spinner"
	        if confirmed:
	                if os.path.islink(SPINNERDIR):
	                        self.close()
	                else:
                                shutil.rmtree(SPINNERDIR)   	                	
                                os.symlink(mountpath, SPINNERDIR)
	        else:
                        if os.path.islink(SPINNERDIR):
                                self.close()
                        else:
                                shutil.rmtree(mountpath)
                                shutil.copytree(SPINNERDIR, mountpath)
                                shutil.rmtree(SPINNERDIR)   	                	
                                os.symlink(mountpath, SPINNERDIR)       	
  
	        self.close()
                
class MoveSpinner(Screen):
	def __init__(self, session):
	        Screen.__init__(self, session)
		Screen.setTitle(self, _("Spinner out of flash"))
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
		self.session.openWithCallback(self.close, MoveSpinner_ext, selection,
			 text=_("Do you really want to use selected Device for Spinner?\n"),
			 question=_(""))

	def okbuttonClick(self):
		selection = self["hddlist"].getCurrent()
		if selection[1] != 0:
			self.doIt(selection[1])
			self.close(True)
			
class MoveSpinner_int(Screen):
	skin = """
		<screen name="MoveSpinner_int" position="0,0" size="800,600" title="Move Spinner back to Flash">
				<eLabel text="Move Spinner back to Flash" position="66,98" size="720,28" font="Regular;26" backgroundColor="backtop" transparent="1" />
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
		self.skin = MoveSpinner_int.skin
		Screen.__init__(self, session)
		self["config"] = Label(_("Move Spinner back to flash?"))
		self["introduction"] = Label(_("Do you really want move Spinner back to flash?"))
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
                SPINNERDIR = "/usr/share/enigma2/Spinner"
                if os.path.islink(SPINNERDIR):
                        message = _("Spinner moved back to flash ready!")
                        os.unlink(SPINNERDIR)
                        os.mkdir(SPINNERDIR)
                        self.session.openWithCallback(self.close, MessageBox, message, MessageBox.TYPE_INFO, timeout = 5)
                else:
                        message = _("Spinner already back in flash!")
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
		self.setTitle('%s - %s: %s (%d%%)' % (_('Move Spinner back to Flash'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)				
