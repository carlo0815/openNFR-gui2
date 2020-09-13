from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.MenuList import MenuList
from Plugins.Plugin import PluginDescriptor
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from os import path, walk
from enigma import eEnv

class LCDClockSelector(Screen):
	clocklist = []
	root = eEnv.resolve("${datadir}/enigma2/display/lcdskins/")

	def __init__(self, session, args = None):

		Screen.__init__(self, session)

		self.clocklist = []
		self.previewPath = ""
		path.walk(self.root, self.find, "")

		self.clocklist.sort()
		self["ClockList"] = MenuList(self.clocklist)
		self.clocklist.insert(0, "no Clock")
		self["Preview"] = Pixmap()
		self["lab1"] = Label(_("Select skin:"))
		self["lab2"] = Label(_("Preview:"))
		self["lab3"] = Label(_("Select your skin and press OK to activate the selected skin."))

		self["actions"] = NumberActionMap(["WizardActions", "InputActions", "EPGSelectActions"],
		{
			"ok": self.ok,
			"back": self.close,
			"up": self.up,
			"down": self.down,
			"left": self.left,
			"right": self.right,
		}, -1)

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		tmp = config.skin.display_skin.value
		if tmp in self.clocklist:
			tmp = config.skin.display_skin.value
			idx = 0
			for skin in self.clocklist:
				if skin == tmp:
					break
				idx += 1
			if idx < len(self.clocklist):
				self["ClockList"].moveToIndex(idx)
		else:
			idx = 0
			self["ClockList"].moveToIndex(idx)
		self.loadPreview()

	def up(self):
		self["ClockList"].up()
		self.loadPreview()

	def down(self):
		self["ClockList"].down()
		self.loadPreview()

	def left(self):
		self["ClockList"].pageUp()
		self.loadPreview()

	def right(self):
		self["ClockList"].pageDown()
		self.loadPreview()

	def find(self, arg, dirname, names):
		for x in names:
			if x.startswith("clock_") and x.endswith(".xml"):
			    if dirname != self.root:
			        subdir = dirname[19:]
			        skinname = x
			        skinname = subdir + "/" + skinname
			        self.clocklist.append(skinname)
			    else:
			        skinname = x
			        self.clocklist.append(skinname)

	def ok(self):
		skinfile = self["ClockList"].getCurrent()
		print ("LCDSkinselector: Selected Skin: ", skinfile)
		if skinfile == "no Clock":
			config.skin.display_skin.value = "skin_display.xml"
		else:
                	config.skin.display_skin.value = skinfile
		config.skin.display_skin.save()
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply a new skin\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI now?"))

	def loadPreview(self):
		pngpath = self["ClockList"].getCurrent()
		try:
			pngpath = pngpath.replace(".xml", "_prev.png")
			pngpath = self.root+pngpath
		except AttributeError:
			pngpath = resolveFilename("${datadir}/enigma2/display/lcdskins/noprev.png")
		
		if not path.exists(pngpath):
			pngpath = eEnv.resolve("${datadir}/enigma2/display/lcdskins/noprev.png")		
		if self.previewPath != pngpath:
			self.previewPath = pngpath

		self["Preview"].instance.setPixmapFromFile(self.previewPath)

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
