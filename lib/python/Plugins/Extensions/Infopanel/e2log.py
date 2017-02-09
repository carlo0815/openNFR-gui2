from enigma import *
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Button import Button
from Components.ActionMap import ActionMap, NumberActionMap
from Components.config import *
from Components.ConfigList import *
from Tools.Directories import fileExists
from Screens.Console import Console


import os

import re
import string

class E2log(ConfigListScreen, Screen):

    skin = """
               <screen name="E2log" position="40,90" size="1180,590" title="E2log erstellen">
               <ePixmap position="6,559" size="35,27" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/red.png" alphatest="blend" />
               <ePixmap position="247,559" size="35,27" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/green.png" alphatest="blend" zPosition="2" />
               <ePixmap position="493,559" size="35,27" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/yellow.png" alphatest="blend" zPosition="2" />
               <ePixmap position="739,559" size="35,27" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/blue.png" alphatest="blend" zPosition="4" />
               <widget name="key_red" render="Label" position="48,562" zPosition="2" size="190,22" valign="center" halign="center" font="Regular; 20" transparent="1" />
               <widget name="key_green" render="Label" position="291,562" zPosition="2" size="190,22" valign="center" halign="center" font="Regular;21" transparent="1" backgroundColor="foreground" />
               <widget name="key_yellow" render="Label" position="540,562" zPosition="2" size="190,22" valign="center" halign="center" font="Regular;21" transparent="1" backgroundColor="foreground" />
               <widget name="key_blue" render="Label" position="777,562" zPosition="2" size="190,22" valign="center" halign="center" font="Regular;21" transparent="1" backgroundColor="foreground" />
               <widget name="config" position="5,7" size="1170,527" scrollbarMode="showOnDemand" />
    </screen> """

    def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		
		self.place = "/home/root/logs"
		self.filename = "e2log.log"
		
		self.list = []
		self.list.append(getConfigListEntry(_("Place:"), ConfigSelection(choices=["/home/root/logs", "/media/hdd", "/media/usb", "/tmp"], default=self.place)))
		self.list.append(getConfigListEntry(_("File name:"), ConfigText(default=self.filename, fixed_size=False)))
		ConfigListScreen.__init__(self, self.list)
		
		
		self["key_red"] = Button(_("Stop_E2_Loggen"))
		self["key_green"] = Button("Start_E2_Loggen")
		self["key_yellow"] = Button("View E2Log")		
		self["key_blue"] = Button(_("Exit"))
		self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'CiSelectionActions'],
		{
			'red': self.red,
			'ok': self.ok,
			'green': self.ok,
			'yellow': self.showLog,
			'blue': self.cancel,
			'cancel': self.cancel
		}, -2)
		self['status'] = Label()

    def ok(self):
		self.place = self.list[0][1].value
		self.filename = self.list[1][1].value
		if os.path.ismount(self.place) or os.path.exists(self.place):
			target = "init 5; sleep 2 ; /usr/bin/enigma2 > "+self.place+"/"+self.filename+" 2>&1"  
			self.session.open(Console, title=_("E2_Log..."), cmdlist = [target], closeOnSuccess = False)		
                else:
                        self.session.open(MessageBox, _("Folder not exist please try other!"), MessageBox.TYPE_INFO, timeout=10)
		
    def cancel(self):
		self.close(False)

    def showLog(self):
                self.sel = self.place + "/" + self.filename
		if self.sel:
			self.session.open(E2LogManagerViewLog, self.sel)		
		
    def red(self):
		target = "init 6" 
		self.session.open(Console, title=_("E2_Log..."), cmdlist = [target], closeOnSuccess = False)


class E2LogManagerViewLog(Screen):

	skin = """
		<screen name="E2LogManagerViewLog" position="center,center" size="700,400" title="E2Log Manager" >
			<widget name="list" position="0,0" size="700,400" font="Console;14" />
		</screen>"""

	def __init__(self, session, files):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(E2log)
		if os.path.exists(files):
			log = file(files).read()
		else:
			log = ""
		self["list"] = ScrollLabel(str(log))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
		{
			"cancel": self.cancel,
			"ok": self.cancel,
			"up": self["list"].pageUp,
			"down": self["list"].pageDown,
			"right": self["list"].lastPage
		}, -2)

	def cancel(self):
		self.close()
