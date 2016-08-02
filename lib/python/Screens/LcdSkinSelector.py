from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from Components.MenuList import MenuList
from Plugins.Plugin import PluginDescriptor
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LCDSKIN
from os import path, walk
from enigma import eEnv
import os

class LCDSkinSelector(Screen):
	skinlist = []
	root = eEnv.resolve("${datadir}/enigma2/display/lcdskins/")
	root1 = eEnv.resolve("${datadir}/enigma2/display/")

	def __init__(self, session, args = None):

		Screen.__init__(self, session)

		self.skinlist = []
		self.previewPath = ""
		path.walk(self.root, self.find, "")

		self.skinlist.sort()
		print "self.skinlist1:", self.skinlist
		self["SkinList"] = MenuList(self.skinlist)
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
		if tmp in self.skinlist:
			tmp = config.skin.display_skin.value
			idx = 0
			for skin in self.skinlist:
				if skin == tmp:
					break
				idx += 1
			if idx < len(self.skinlist):
				self["SkinList"].moveToIndex(idx)
		else:
			idx = 0
			self["SkinList"].moveToIndex(idx)
		self.loadPreview()

	def up(self):
		self["SkinList"].up()
		self.loadPreview()

	def down(self):
		self["SkinList"].down()
		self.loadPreview()

	def left(self):
		self["SkinList"].pageUp()
		self.loadPreview()

	def right(self):
		self["SkinList"].pageDown()
		self.loadPreview()

	def find(self, arg, dirname, names):
		for root, dirs, files in os.walk(self.root1, followlinks=True):
			for subdir in dirs:
				if ("lcdskins") not in subdir:
                                        if subdir.startswith("OE-A_") or subdir.startswith("OpenNFR_"):
                                                src = self.root1 + subdir
					        dst = self.root + subdir
					        if not os.path.islink(dst):
						        os.symlink(src, dst)
                for x in names:
                        if x.startswith("skin_") and x.endswith(".xml"):
				if dirname <> self.root:
					subdir = dirname[19:]
					skinname = x
					skinname = subdir + "/" + skinname
					self.skinlist.append(skinname)
				else:
					skinname = x
					self.skinlist.append(skinname)
					
			else:
                        	if x.startswith("OE-A_") or x.startswith("OpenNFR_"):
                                        skinname = x
					self.skinlist.append(skinname)
                                		
	def ok(self):
		skinstest = self["SkinList"].getCurrent()
		if skinstest.startswith("OE-A_") or skinstest.startswith("OpenNFR_"):
			skinfile = self["SkinList"].getCurrent() + "/skin_display.xml"
		else:
			skinfile = self["SkinList"].getCurrent()
		print "LCDSkinselector: Selected Skin: ", skinfile
		config.skin.display_skin.value = skinfile
		config.skin.display_skin.save()
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply a new skin\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI now?"))

	def loadPreview(self):
		pngpath = self["SkinList"].getCurrent()
                try:
                	if pngpath.startswith("OE-A_") or pngpath.startswith("OpenNFR_"):
                		try:
					pngpath = pngpath + ("/prev.png")
					pngpath = self.root+pngpath
				except AttributeError:
					pngpath = resolveFilename(SCOPE_LCDSKIN, "lcdskins/noprev.png")                
                	else:
                
                		try:
					pngpath = pngpath.replace(".xml", "_prev.png")
					pngpath = self.root+pngpath
				except AttributeError:
					pngpath = resolveFilename(SCOPE_LCDSKIN, "lcdskins/noprev.png")
		except AttributeError:
		        pngpath = resolveFilename(SCOPE_LCDSKIN, "lcdskins/noprev.png")
		if not path.exists(pngpath):
			pngpath = eEnv.resolve("/usr/share/enigma2/display/lcdskins/noprev.png")		
		if self.previewPath != pngpath:
			self.previewPath = pngpath

		self["Preview"].instance.setPixmapFromFile(self.previewPath)

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
