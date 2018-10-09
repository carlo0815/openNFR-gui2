from Screens.InfoBar import InfoBar
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components import Harddisk
from os import path, listdir, system
class MultiBootStartup(ConfigListScreen, Screen):
	skin = """
	<screen name="MultiBootStartupDS" position="center,center" size="700,350" title="MultiBoot STARTUP Selector">
    		<eLabel name="b" position="0,0" size="700,350" backgroundColor="background" zPosition="-2" />
    		<eLabel name="a" position="1,1" size="698,348" backgroundColor="background" zPosition="-1" />
    		<eLabel text="Press left/right to select Image" backgroundColor="white" font="Regular; 24" foregroundColor="black" halign="center" position="10,125" size="580,40" transparent="0" zPosition="3" />
    		<widget source="config" render="Label" position=" 10,15" size="680,90" itemHeight="30" halign="center" font="Regular; 30" enableWrapAround="1" transparent="1" scrollbarMode="showOnDemand" />
    		<widget source="options" render="Label" position="10,168" size="680,40" halign="left" valign="center" font="Regular; 24" backgroundColor="background" foregroundColor="white" transparent="1" />
    		<eLabel position="-15,267" size="711,1" backgroundColor="grey" />
    		<widget name="description" position="11,270" size="680,30" halign="center" valign="center" font="Regular;19" backgroundColor="background" foregroundColor="cyan" transparent="1" />
    		<ePixmap pixmap="skin_default/buttons/red.png" position="20,315" size="30,30" zPosition="2" alphatest="blend" />
    		<ePixmap pixmap="skin_default/buttons/green.png" position="210,315" size="30,30" zPosition="2" alphatest="blend" />
    		<ePixmap pixmap="skin_default/buttons/key_yellow.png" position="366,315" size="30,30" zPosition="2" alphatest="blend" />
    		<widget source="key_red" render="Label" position="55,315" size="160,24" zPosition="2" font="Regular;20" backgroundColor="black" transparent="1" />
    		<widget source="key_green" render="Label" position="245,315" size="160,24" zPosition="2" font="Regular;20" backgroundColor="black" transparent="1" />
    		<widget source="key_yellow" render="Label" position="401,315" size="160,24" zPosition="2" font="Regular;20" backgroundColor="black" transparent="1" />
    		<ePixmap position="612,125" size="81,40" zPosition="10" pixmap="skin_default/buttons/key_leftright.png" transparent="1" alphatest="blend" />
    		<widget name="cancel" position="0,0" size="0,0" />
    		<widget name="ok" position="0,0" size="0,0" />
	</screen>
	"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.title = _("MultiBoot Selector")
		self.skinName = ["MultiBootStartupDS"]
		self.emmc = False
		self.checkEMMC()
		if self.emmc:
			self["key_yellow"] = StaticText(_("Init"))
		else:
			self["key_yellow"] = StaticText()
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["config"] = StaticText(_("Select Image: STARTUP_1"))
		self.selection = 0
		self.list = self.list_files("/boot")
		self.startup()
		self["actions"] = ActionMap(["WizardActions", "SetupActions", "ColorActions"],
		{
			"left": self.left,
			"right": self.right,
			"green": self.save,
			"red": self.cancel,
			"yellow": self.init,
			"cancel": self.cancel,
			"ok": self.save,
		}, -2)
		self.onLayoutFinish.append(self.layoutFinished)
	def layoutFinished(self):
		self.setTitle(self.title)
	def createSummary(self):
		from Screens.SimpleSummary import SimpleSummary
		return SimpleSummary
	def startup(self):
		self["config"].setText(_("Select Image: %s") %self.list[self.selection])
	def save(self):
		print "[MultiBootStartup] select new startup: ", self.list[self.selection]
		system("cp -f /boot/%s /boot/STARTUP"%self.list[self.selection])
		restartbox = self.session.openWithCallback(self.restartBOX,MessageBox,_("Do you want to reboot now with selected image?"), MessageBox.TYPE_YESNO)
	def init(self):
		if self.emmc:
			self.TITLE = _("Init SDCARD")
			cmdlist = []
			cmdlist.append("dd if=/dev/zero of=/dev/sda bs=512 count=1 conv=notrunc")
			cmdlist.append("rm -f /tmp/init.sh")
			cmdlist.append("echo -e 'sfdisk /dev/sda <<EOF' >> /tmp/init.sh")
			cmdlist.append("echo -e ',8M' >> /tmp/init.sh")
			cmdlist.append("echo -e ',2048M' >> /tmp/init.sh")
			cmdlist.append("echo -e ',8M' >> /tmp/init.sh")
			cmdlist.append("echo -e ',2048M' >> /tmp/init.sh")
			cmdlist.append("echo -e 'EOF' >> /tmp/init.sh")
			cmdlist.append("chmod +x /tmp/init.sh")
			cmdlist.append("/tmp/init.sh")
			self.session.open(Console, title = self.TITLE, cmdlist = cmdlist, closeOnSuccess = True)
	def checkEMMC(self):
		if path.exists('/boot/STARTUP'):
			f = open('/boot/STARTUP', 'r')
			f.seek(5)
			image = f.read(4)
			if image == "emmc":
				self.emmc = True
	def cancel(self):
		self.close()
	def left(self):
		self.selection = self.selection - 1
		if self.selection == -1:
			self.selection = len(self.list) - 1
		self.startup()
	def right(self):
		self.selection = self.selection + 1
		if self.selection == len(self.list):
			self.selection = 0
		self.startup()
	def read_startup(self, FILE):
		self.file = FILE
		with open(self.file, 'r') as myfile:
			data=myfile.read().replace('\n', '')
		myfile.close()
		return data
	def list_files(self, PATH):
		files = []
		self.path = PATH
		for name in listdir(self.path):
			if path.isfile(path.join(self.path, name)):
				cmdline = self.read_startup("/boot/" + name).split("=",1)[1].split(" ",1)[0]
				if cmdline in Harddisk.getextdevices("ext4") and not name == "STARTUP":
					files.append(name)
		return files
	def restartBOX(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 2)
		else:
			self.close()
