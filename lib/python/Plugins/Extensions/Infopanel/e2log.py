from enigma import *
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.Label import Label
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
               <ePixmap position="252,559" size="35,27" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/green.png" alphatest="blend" zPosition="2" />
               <ePixmap position="724,559" size="35,27" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/pics/blue.png" alphatest="blend" zPosition="4" />
               <widget name="key_red" render="Label" position="48,562" zPosition="2" size="190,22" valign="center" halign="center" font="Regular; 20" transparent="1" />
               <widget name="key_green" render="Label" position="291,562" zPosition="2" size="190,22" valign="center" halign="center" font="Regular;21" transparent="1" backgroundColor="foreground" />
               <widget name="key_blue" render="Label" position="762,562" zPosition="2" size="190,22" valign="center" halign="center" font="Regular;21" transparent="1" backgroundColor="foreground" />
               <widget name="config" position="5,7" size="1170,527" scrollbarMode="showOnDemand" />
    </screen> """



    def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		
		self.place = "/media/hdd"
		self.filename = "e2log"
		
		self.list = []
		self.list.append(getConfigListEntry(_("Place:"), ConfigSelection(choices=["/media/hdd", "/media/usb", "/tmp"], default=self.place)))
		self.list.append(getConfigListEntry(_("File name:"), ConfigText(default=self.filename, fixed_size=False)))
		ConfigListScreen.__init__(self, self.list)
		
		self["key_red"] = Button(_("Stop_E2_Loggen"))
		self["key_green"] = Button("Start_E2_Loggen")
		self["key_blue"] = Button(_("Exit"))
		self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'CiSelectionActions'],
		{
			'red': self.red,
			'ok': self.ok,
			'green': self.ok,
			'blue': self.cancel,
			'cancel': self.cancel
		}, -2)
		self['status'] = Label()

    def ok(self):
		self.place = self.list[0][1].getValue()
		self.filename = self.list[1][1].getValue()
		if os.path.ismount(self.place):
			target = "init 5; killall enigma2; /usr/bin/enigma2 > "+self.place+"/"+self.filename+" 2>&1" 
			self.session.open(Console, title=_("E2_Log..."), cmdlist = [target], closeOnSuccess = False)		
                else:
                        self.session.open(MessageBox, _("Folder not exist please try other!"), MessageBox.TYPE_INFO, timeout=10)
		
    def cancel(self):
		self.close(False)
		
    def red(self):
		target = "init 6" 
		self.session.open(Console, title=_("E2_Log..."), cmdlist = [target], closeOnSuccess = False)
