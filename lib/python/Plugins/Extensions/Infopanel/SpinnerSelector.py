from Plugins.Plugin import PluginDescriptor
from Plugins.Extensions.Infopanel.SpinnerSelectionBox import SpinnerSelectionBox
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.config import config
import os
import shutil


class SpinnerSelector:
	def __init__(self,session):
		self.session = session
		path = "/usr/share/enigma2/Spinner/"
		dirs = os.listdir(path)
		if not dirs:
			for i in list(range(64)):
				if (os.path.isfile("/usr/share/enigma2/spinner/wait%d.png"%(i+1))):
					if not os.path.exists("/usr/share/enigma2/Spinner/lastused"):
						os.mkdir("/usr/share/enigma2/Spinner/lastused")
					shutil.copy("/usr/share/enigma2/spinner/wait%d.png"%(i+1), "/usr/share/enigma2/Spinner/lastused/wait%d.png"%(i+1))
					dirs = os.listdir(path)
		dirs.sort()
		menu = []
		for dir in dirs:
			p = path + dir
			if os.path.isdir(p):
				menu.append((dir,dir))
		self.session.openWithCallback(self.menuCallback, SpinnerSelectionBox, title=_("Chose Spinner"), list=menu)

	def menuCallback(self,choice):
		if choice is None:
			return
		for i in list(range(64)):
			if (os.path.isfile("/usr/share/enigma2/spinner/wait%d.png"%(i+1))):
				os.system("rm -f /usr/share/enigma2/spinner/wait%d.png"%(i+1))
			if (os.path.isfile("/usr/share/enigma2/Spinner/%s/wait%d.png"%(choice,i+1))):
				shutil.copy("/usr/share/enigma2/Spinner/%s/wait%d.png"%(choice,i+1),  "/usr/share/enigma2/spinner/wait%d.png"%(i+1)) 
		self.session.openWithCallback(self.restart, MessageBox, _("GUI needs a restart to apply a new spinner.\nDo you want to restart the GUI now ?"), MessageBox.TYPE_YESNO)

	def restart(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3) 
