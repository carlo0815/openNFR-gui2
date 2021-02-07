from __future__ import print_function
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Tools import Notifications
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap, HelpableActionMap
from Plugins.Plugin import PluginDescriptor
from Plugins.Extensions.TVHeadEnd.TVHSatconfig import *
from Screens.WizardLanguage import WizardLanguage
from Screens.Rc import Rc
from Screens.Standby import TryQuitMainloop
import os
from shutil import copyfile
###########################################################################
if os.path.isfile('/etc/init.d/tvheadend.sh'):
	os.system("/etc/init.d/tvheadend.sh start")
class TVHeadendSetup(Screen):
	skin = """
		<screen name="OpenNFR TVHeadend Setup" position="center,center" size="950,470" title="OpenNFR TVHeadend Setup">
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVHeadEnd/redlogo.png" position="0,380" size="950,84" alphatest="on" zPosition="1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVHeadEnd/alliance.png" position="670,255" size="100,67" alphatest="on" zPosition="1" />
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVHeadEnd/opennfr_info.png" position="510,11" size="550,354" alphatest="on" zPosition="1" />
		<!--widget source="global.CurrentTime" render="Label" position="450, 340" size="500,24" font="Regular;20" foregroundColor="white" halign="right" transparent="1" zPosition="5">
		<convert type="ClockToText">&gt;Format%H:%M:%S</convert>
		</widget!-->
		<eLabel backgroundColor="un56c856" position="0,330" size="950,1" zPosition="0" />
		<widget name="myMenu" position="10,10" size="480,300" zPosition="1" scrollbarMode="showOnDemand" backgroundColor="un251e1f20" transparent="1" />
		</screen>
"""

	def __init__(self, session, args = 0):
		self.session = session
		list = []
		list.append(("TVHeadend Setup and Autostart every Boot", "TVHeadend_Setup"))
		list.append(("Stop 'Autostart TVHeadend every Boot'", "TVHeadend_Stop"))
		list.append(("Start TVHeadend", "TVHeadend_Setup1"))                
		list.append(("Stop TVHeadend", "TVHeadend_Stop1"))
		list.append(("Start TVHeadend standalone without E2", "TVHeadend_Start1"))                                  		
		list.append((_("Exit"), "exit"))
		
		Screen.__init__(self, session)
		self["myMenu"] = MenuList(list)
		self["myActionMap"] = ActionMap(["SetupActions"],
		{
			"ok": self.go,
			"cancel": self.cancel
		}, -1)

	def go(self):
		returnValue = self["myMenu"].l.getCurrentSelection()[1]
		print("[TVHeadend_Setup] returnValue: ", returnValue)
		
		if returnValue is not None:
			if returnValue is "TVHeadend_Setup":
				self.prombt()
			elif returnValue is "TVHeadend_Stop":
				self.prombt_stop()
			elif returnValue is "TVHeadend_Setup1":
				os.system("/usr/lib/enigma2/python/Plugins/Extensions/TVHeadEnd/tvheadend.sh start")
				self.close(None)                                  
			elif returnValue is "TVHeadend_Stop1":
				os.system("/usr/lib/enigma2/python/Plugins/Extensions/TVHeadEnd/tvheadend.sh stop")
				self.close(None)
			elif returnValue is "TVHeadend_Start1":
				os.system("/usr/lib/enigma2/python/Plugins/Extensions/TVHeadEnd/tvheadend1.sh &")
				os.system("killall enigma2")
				self.close(None)                                                                                         		
			else:
				print("\n[TVHeadend_Setup] cancel\n")
				self.close(None)

	def prombt_stop(self):
		os.system("/etc/init.d/tvheadend.sh stop")	
		os.system("rm /etc/init.d/tvheadend.sh")
		self.close(None)

	def prombt(self):
		self.session.openWithCallback(self.boot_quest, NimSelection)
		
	def boot_quest(self):
		self.session.openWithCallback(self.boot_ing,MessageBox,_("To start TVHeadend we need a reboot!\nDo you want to reboot now ?"), MessageBox.TYPE_YESNO)      		
		
	def boot_ing(self, answer):
		src1 = "/usr/lib/enigma2/python/Plugins/Extensions/TVHeadEnd/tvheadend.sh"
		dst1 = "/etc/init.d/tvheadend.sh"
		if answer is True:
			if os.path.isfile('/etc/init.d/tvheadend.sh'):
				print("TVheadendscript already installed")
			else:                                        
				copyfile(src1, dst1)
				os.chmod(dst1, 0o755)
			self.session.open(TryQuitMainloop, 2)
		else:                         			
			self.close(None)
        		
	def cancel(self):
		print("\n[TVHeadend_Setup] cancel\n")
		self.close(None)

###########################################################################
		
class Installcheck(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.prombt()
		
	def prombt(self):
		self.session.openWithCallback(self.install,MessageBox,_("This Setup-plugin need Install tvheadendplugin too. Do you want to Install it?"),  MessageBox.TYPE_YESNO, timeout = 20)

	def install(self, answer):
		if answer is True:
			print("INSTALL")
			cmd = "opkg update;"
			cmd += "opkg install --force-overwrite tvheadend;"
			self.session.open(Console, title = _("Please wait install TVHeadend-BinaryPlugin"), cmdlist = [cmd], closeOnSuccess = True)	
		else:
			print("NO INSTALL")		
			self.close()
###########################################################################

def main(session, **kwargs):
	if os.path.isfile('/usr/bin/tvheadend'):
		print("\n[TVHeadend_Setup] start\n")	
		session.open(TVHeadendSetup)
	else:	
		Installcheck(session)

###########################################################################

def Plugins(**kwargs):
	return PluginDescriptor(
			name="TVHeadend_Setup",
			description="Setup your Tuner for TVHeadend",
			where = PluginDescriptor.WHERE_PLUGINMENU,
			icon="logo.png",
			fnc=main)
