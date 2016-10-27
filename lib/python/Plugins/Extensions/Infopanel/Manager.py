from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry
from Components.Console import Console
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.List import List
from Components.ScrollLabel import ScrollLabel
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from glob import glob
from enigma import eTimer
from time import sleep
from os import path
import os
import Softcam
import shutil
from Screens.VirtualKeyBoard import VirtualKeyBoard
class NFRCamManager(Screen):
	skin = """
  <screen name="NFRCamManager" position="center,center" size="820,410" title="NFR SoftCam Manager">
    <eLabel position="4,-1" size="800,2" backgroundColor="black" />
    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/big-red-on.png" position="2,368" size="200,40" alphatest="blend" zPosition="-1" />
    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/big-green-on.png" position="208,368" size="200,40" alphatest="blend" zPosition="-1" />
    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/big-yellow-on.png" position="412,368" size="200,40" alphatest="blend" zPosition="-1" />
    <ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/big-blue-on.png" position="615,368" size="200,40" alphatest="blend" zPosition="-1" />
    <widget source="list" render="Listbox" position="5,10" size="442,300" scrollbarMode="showOnDemand" transparent="1">
      <convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryPixmapAlphaTest(pos = (0, 0), size = (100, 50), png = 1), 
			MultiContentEntryText(pos = (120, 10), size = (275, 40), font=0, \
				flags = RT_HALIGN_LEFT, text = 0), 
			MultiContentEntryText(pos = (20, 35), size = (70, 20), font=1, \
				flags = RT_HALIGN_CENTER, text = 2), 
				],
	"fonts": [gFont("Regular", 26),gFont("Regular", 12)],
	"itemHeight": 50
	}
	</convert>
    </widget>
    <eLabel halign="center" position="512,10" size="210,35" font="Regular;20" text="Ecm info" transparent="1" />
    <widget name="status" position="460,47" size="320,260" font="Regular;16" halign="center" noWrap="1" transparent="1" />
    <widget name="key_red" position="2,368" zPosition="2" size="200,40" valign="center" halign="center" font="Regular;22" transparent="1" />
    <widget name="key_green" position="208,368" zPosition="2" size="200,40" valign="center" halign="center" font="Regular;22" transparent="1" />
    <widget name="key_yellow" position="412,368" zPosition="2" size="200,40" valign="center" halign="center" font="Regular;22" transparent="1" />
    <widget name="key_blue" position="615,368" zPosition="2" size="200,40" valign="center" halign="center" font="Regular;22" transparent="1" />
  </screen>
  """

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("NFR-SoftCam manager"))
		self.Console = Console()
		self["key_red"] = Label(_("Stop"))
		self["key_green"] = Label(_("Start"))
		self["key_yellow"] = Label(_("Restart"))
		self["key_blue"] = Label(_("Setup"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.ok,
				"green": self.start,
				"red": self.stop,
				"yellow": self.restart,
				"blue": self.setup
			}, -1)
		self["status"] = ScrollLabel()
		self["list"] = List([])
		Softcam.checkconfigdir()
		self.actcam = config.NFRSoftcam.actcam.value
		self.camstartcmd = ""
		self.createinfo()
		self.Timer = eTimer()
		self.Timer.callback.append(self.listecminfo)
		self.Timer.start(1000*4, False)

	def createinfo(self):
	        for fdelete in glob ('/usr/emu/*.x'):
			os.remove (fdelete)
			
	        for fdelete in glob ('/usr/emu/*.usb'):
			os.remove (fdelete)
			
                for fdelete in glob ('/usr/keys/*'):
                	if os.path.islink(fdelete):
				os.unlink(fdelete)
	        if os.path.isfile("/tmp/usbsoftcam"):
	                fobj = open("/tmp/usbsoftcam")
	                for line in fobj:
	                    spath = line.rstrip()
	                fobj.close()
	                testfile = spath + "use_softcam"
	        	if os.path.exists(spath) and os.path.isfile(testfile):         
		        	epath = spath + "emu/"	
		        	uemus=[]
		        	uemus = os.listdir(epath)
		        	for emu in uemus:  
		                	emu1 = emu.strip()
		                	src = epath + emu1
		                	dst = "/usr/emu/" + emu1 + ".usb"
			        	os.symlink(src, dst)
		        	kpath = spath + "keys/"	
		        	kemus=[]
		        	kemus = os.listdir(kpath)
		        	for kemu in kemus:
		                	kemu1 = kemu.strip()
		                	src = kpath + kemu1
		                	dst = "/usr/keys/" + kemu1
		                	dst1 = dst
		                	if os.path.isfile(dst):
		                		self.Console.ePopen("mv %s %s.org" % (dst,dst1))
		                		sleep(0.50)
			        	os.symlink(src, dst)                                                                                 			
	
		emus=[]
		for fAdd in glob ('/etc/*.emu'):
			searchfile = open(fAdd, "r")
			for line in searchfile:
				if "binname" in line:
					emus.append(line[10:])
			searchfile.close()
			
		for fAdd1 in glob ('/etc/init.d/softcam.*'):
			searchfile1 = open(fAdd1, "r")
			for line1 in searchfile1:
				if 'echo "/usr/bin/' in line1:
					line2 = line1[15:]
					line3 = line2.split(" ")
					line4 = line3[0]
					emus.append(line4)
			searchfile1.close()			
	
		for emu in emus:
		        emu1 = emu.strip()
		        src = "/usr/bin/" + emu1
		        dst = "/usr/emu/" + emu1 + ".x"
			os.symlink(src, dst)
	
	        self.iscam = False
		self.startcreatecamlist()
		self.listecminfo()

	def listecminfo(self):
		listecm = ""
		try:
			ecmfiles = open("/tmp/ecm.info", "r")
			for line in ecmfiles:
				if line[32:]:
					linebreak = line[23:].find(' ') + 23
					listecm += line[0:linebreak]
					listecm += "\n" + line[linebreak + 1:]
				else:
					listecm += line
			self["status"].setText(listecm)
			ecmfiles.close()
		except:
			self["status"].setText("")

	def startcreatecamlist(self):
		self.Console.ePopen("ls %s" % config.NFRSoftcam.camdir.value,
			self.camliststart)
	

	def camliststart(self, result, retval, extra_args):
		if result.strip() and not result.startswith('ls: '):
			self.iscam = True
			self.softcamlist = result.splitlines()
			self.Console.ePopen("chmod 755 %s/*" %
				config.NFRSoftcam.camdir.value)
			if self.actcam != "none" and Softcam.getcamscript(self.actcam):
				self.createcamlist()
			else:
				self.Console.ePopen("pidof %s" % self.actcam, self.camactive)
		else:
			if path.exists("/usr/bin/cam") and not self.iscam and \
				config.NFRSoftcam.camdir.value != "/usr/bin/cam":
				self.iscam = True
				config.NFRSoftcam.camdir.value = "/usr/bin/cam"
				self.startcreatecamlist()
			elif config.NFRSoftcam.camdir.value != "/usr/emu":
				self.iscam = False
				config.NFRSoftcam.camdir.value = "/usr/emu"
				self.startcreatecamlist()
			else:
				self.iscam = False

	def camactive(self, result, retval, extra_args):
		if result.strip():
			self.createcamlist()
		else:
			for line in self.softcamlist:
				if line != self.actcam:
					self.Console.ePopen("pidof %s" % line, self.camactivefromlist, line)
			self.Console.ePopen("echo 1", self.camactivefromlist, "none")

	def camactivefromlist(self, result, retval, extra_args):
		if result.strip():
			self.actcam = extra_args
			self.createcamlist()

	def createcamlist(self):
	        f = open("/etc/emulist", "w")
		name = self.softcamlist	
                f.write("\n".join(map(lambda x: str(x), name)))		
		f.close()                	
		self.list = []
		try:
			test = self.actcam
		except:
			self.actcam = "none"
		if self.actcam != "none":
			softpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS,
				"/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/actcam.png"))
			self.list.append((self.actcam, softpng, self.checkcam(self.actcam)))
		softpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS,
			"/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/defcam.png"))
		for line in self.softcamlist:
			if line != self.actcam:
				self.list.append((line, softpng, self.checkcam(line)))
      		self["list"].setList(self.list)

	def checkcam (self, cam):
		cam = cam.lower()
		if Softcam.getcamscript(cam):
			return "Script"
		elif "oscam" in cam:
			return "Oscam"
		elif "mgcamd" in cam:
			return "Mgcamd"
		elif "wicard" in cam:
			return "Wicard"
		elif "camd3" in cam:
			return "Camd3"
		elif "mcas" in cam:
			return "Mcas"
		elif "cccam" in cam:
			return "CCcam"
		elif "gbox" in cam:
			return "Gbox"
		elif "ufs910camd" in cam:
			return "Ufs910"
		elif "incubuscamd" in cam:
			return "Incubus"
		elif "mpcs" in cam:
			return "Mpcs"
		elif "mbox" in cam:
			return "Mbox"
		elif "newcs" in cam:
			return "Newcs"
		elif "vizcam" in cam:
			return "Vizcam"
		elif "sh4cam" in cam:
			return "Sh4CAM"
		elif "rucam" in cam:
			return "Rucam"
		else:
			return cam[0:6]

	def start(self):
		if self.iscam:
			self.camstart = self["list"].getCurrent()[0]
			if self.camstart != self.actcam:
				print "[NFR-SoftCam Manager] Start SoftCam"
				self.camstartcmd = Softcam.getcamcmd(self.camstart)
				msg = _("Starting %s") % self.camstart
				self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
				self.activityTimer = eTimer()
				self.activityTimer.timeout.get().append(self.stopping)
				self.activityTimer.start(100, False)

	def stop(self):
		if self.iscam and self.actcam != "none":
			Softcam.stopcam(self.actcam)
			msg  = _("Stopping %s") % self.actcam
			self.actcam = "none"
			self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
			self.activityTimer = eTimer()
			self.activityTimer.timeout.get().append(self.closestop)
			self.activityTimer.start(1000, False)

	def closestop(self):
		self.activityTimer.stop()
		if self.mbox:
			self.mbox.close()
		self.createinfo()

	def restart(self):
		if self.iscam:
			print "[NFR-SoftCam Manager] restart SoftCam"
			self.camstart = self.actcam
			if self.camstartcmd == "":
				self.camstartcmd = Softcam.getcamcmd(self.camstart)
			msg = _("Restarting %s") % self.actcam
			self.mbox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
			self.activityTimer = eTimer()
			self.activityTimer.timeout.get().append(self.stopping)
			self.activityTimer.start(100, False)

	def stopping(self):
		self.activityTimer.stop()
		Softcam.stopcam(self.actcam)
		self.actcam = self.camstart
		service = self.session.nav.getCurrentlyPlayingServiceReference()
		if service:
			self.session.nav.stopService()
		self.Console.ePopen(self.camstartcmd)
		print "[NFR-SoftCam Manager] ", self.camstartcmd
		if self.mbox:
			self.mbox.close()
		if service:
			self.session.nav.playService(service)
		self.createinfo()

	def ok(self):
		if self.iscam:
			if self["list"].getCurrent()[0] != self.actcam:
				self.start()
			else:
				self.restart()

	def cancel(self):
		if config.NFRSoftcam.actcam.value != self.actcam:
			config.NFRSoftcam.actcam.value = self.actcam
		config.NFRSoftcam.save()
		self.close()

	def setup(self):
		self.session.openWithCallback(self.createinfo, ConfigEdit)

class ConfigEdit(Screen, ConfigListScreen):
	skin = """
		<screen name="ConfigEdit" position="center,center" size="620,250" title="SoftCam path configuration">
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/big-red-on.png" position="7,121" size="295,40" alphatest="blend" zPosition="-1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/buttons/big-green-on.png" position="313,122" size="295,40" alphatest="blend" zPosition="-1" />
		<widget name="key_red" position="7,121" zPosition="2" size="295,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="key_green" position="313,122" zPosition="2" size="295,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<widget name="config" position="6,10" size="600,100" zPosition="1" scrollbarMode="showOnDemand" transparent="1" />
		<widget name="key_blue" position="168,170" zPosition="4" size="295,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/buttons/big-green-on.png" position="168,170" size="295,40" alphatest="blend" zPosition="-1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("SoftCam path configuration"))
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Ok"))
		self["key_blue"] = Label(_("Use VirtualKeyboard"))
		self.VirtualKeyBoard = VirtualKeyBoard		
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
		self.list.append(getConfigListEntry(_("SoftCam config directory"),
			config.NFRSoftcam.camconfig))
		self.list.append(getConfigListEntry(_("SoftCam directory"),
			config.NFRSoftcam.camdir))
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		self.config = config
	def ok(self):
		msg = [ ]
		if not path.exists(config.NFRSoftcam.camconfig.value):
			msg.append("%s " % config.NFRSoftcam.camconfig.value)
		if not path.exists(config.NFRSoftcam.camdir.value):
			msg.append("%s " % config.NFRSoftcam.camdir.value)
		if msg == [ ]:
			if config.NFRSoftcam.camconfig.value.endswith("/"):
				config.NFRSoftcam.camconfig.value = \
					config.NFRSoftcam.camconfig.value[:-1]
			if config.NFRSoftcam.camdir.value.endswith("/"):
				config.NFRSoftcam.camdir.value = \
					config.NFRSoftcam.camdir.value[:-1]
			config.NFRSoftcam.save()
			self.close()
		else:
			self.mbox = self.session.open(MessageBox,
				_("Directory %s does not exist!\nPlease set the correct directory path!")
				% msg, MessageBox.TYPE_INFO, timeout = 5 )

	def cancel(self, answer = None):
		if answer is None:
			if self["config"].isChanged():
				self.session.openWithCallback(self.cancel, MessageBox,
					_("Really close without saving settings?"))
			else:
				self.close()
		elif answer:
			for x in self["config"].list:
				x[1].cancel()
			self.close()

	def blue(self):
        	if self["config"].getCurrent() == getConfigListEntry(_("SoftCam config directory"),config.NFRSoftcam.camconfig):
            		self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=_('Edit your KEY Path'), text=self.config.NFRSoftcam.camconfig.value)
        	elif self["config"].getCurrent() == getConfigListEntry(_("SoftCam directory"),config.NFRSoftcam.camdir):
            		self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=_('Edit your EMU Path'), text=self.config.NFRSoftcam.camdir.value)
				
	def VirtualKeyBoardCallback(self, callback = None):
		if callback is not None and len(callback):
			self["config"].getCurrent()[1].setValue(callback)
			self["config"].invalidate(self["config"].getCurrent())	
