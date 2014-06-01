from enigma import *
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Tools.Directories import fileExists, crawlDirectory, resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Button import Button
from Components.Label import Label
from Components.Sources.List import List
from Screens.MessageBox import MessageBox
from Components.MountPoints import MountPoints
from Components.Disks import Disks
from Components.ExtraMessageBox import ExtraMessageBox

import os
import sys
import re

class HddMount(Screen):

	skin = """
                    <screen name="HddMount" position="center,115" size="900,530" title="HddMount" flags="wfBorder">
                      <ePixmap position="10,497" size="35,27" pixmap="skin_default/buttons/red.png" alphatest="blend" />
                      <ePixmap position="230,497" size="35,27" pixmap="skin_default/buttons/green.png" alphatest="blend" />
                      <ePixmap position="464,497" size="35,27" pixmap="skin_default/buttons/yellow.png" alphatest="blend" />
                      <ePixmap position="695,497" size="35,27" pixmap="skin_default/buttons/blue.png" alphatest="blend" />
                      <widget name="key_red" position="48,498" zPosition="2" size="150,22" valign="center" halign="center" font="Regular; 20" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                      <widget name="key_green" position="273,499" zPosition="2" size="150,22" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="foreground" />
                      <widget name="key_yellow" position="508,499" zPosition="3" size="150,22" valign="center" halign="center" font="Regular; 21" transparent="1" backgroundColor="foreground" />
                      <widget name="key_blue" position="736,499" zPosition="3" size="150,22" valign="center" halign="center" font="Regular; 21" transparent="1" backgroundColor="foreground" />
                     <eLabel text="Hard Drive Mount" zPosition="2" position="10,11" size="880,40" halign="left" font="Regular;28" foregroundColor="un538eff" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="black" />
                      <widget name="menu" position="10,59" size="880,410" scrollbarMode="showOnDemand" transparent="1" />
                    </screen> """
                    
	def __init__(self, session, device, partition):
		Screen.__init__(self, session)
		
		self.device = device
		self.partition = partition
		self.mountpoints = MountPoints()
		self.mountpoints.read()
		self.fast = False
		
		self.list = []
		self.list.append("Mount as main hdd")
		self.list.append("Mount as /media/usb")
		self.list.append("Mount as /media/usb1")
		self.list.append("Mount as /media/usb2")
		self.list.append("Mount as /media/usb3")
		self.list.append("Mount as /media/cf")
		self.list.append("Mount as /media/mmc1")
		self.list.append("Mount on custom path")
		
		self["menu"] = MenuList(self.list)
		
		self["key_red"] = Button(_("Fixed mount"))
		self["key_green"] = Button("Fast mount")
		self["key_blue"] = Button(_("Exit"))
		self["key_yellow"] = Button("")
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"green": self.green,
			"ok": self.ok,
			"red": self.ok,
			"cancel": self.quit,
		}, -2)
		
	def ok(self):
		self.fast = False
		selected = self["menu"].getSelectedIndex()
		if selected == 0:
			self.setMountPoint("/media/hdd")
		elif selected == 1:
			self.setMountPoint("/media/usb")
		elif selected == 2:
			self.setMountPoint("/media/usb1")
		elif selected == 3:
			self.setMountPoint("/media/usb2")
		elif selected == 4:
			self.setMountPoint("/media/usb3")
		elif selected == 5:
			self.setMountPoint("/media/cf")
		elif selected == 6:
			self.setMountPoint("/media/mmc1")
		elif selected == 7:
			self.session.openWithCallback(self.customPath, VirtualKeyBoard, title = (_("Insert mount point:")), text = "/media/custom")
			
	def green(self):
		self.fast = True
		selected = self["menu"].getSelectedIndex()
		if selected == 0:
			self.setMountPoint("/media/hdd")
		elif selected == 1:
			self.setMountPoint("/media/usb")
		elif selected == 2:
			self.setMountPoint("/media/usb1")
		elif selected == 3:
			self.setMountPoint("/media/usb2")
		elif selected == 4:
			self.setMountPoint("/media/usb3")
		elif selected == 5:
			self.setMountPoint("/media/cf")
		elif selected == 6:
			self.setMountPoint("/media/mmc1")
		elif selected == 7:
			self.session.openWithCallback(self.customPath, VirtualKeyBoard, title = (_("Insert mount point:")), text = "/media/custom")
		
	def customPath(self, result):
		if result and len(result) > 0:
			result = result.rstrip("/")
			os.system("mkdir -p %s" % result)
			self.setMountPoint(result)
		
	def setMountPoint(self, path):
		self.cpath = path
		if self.mountpoints.exist(path):
			self.session.openWithCallback(self.setMountPointCb, ExtraMessageBox, "Selected mount point is already used by another drive.", "Mount point exist!",
																[ [ "Change old drive with this new drive", "ok.png" ],
																[ "Mantain old drive", "cancel.png" ],
																])
		else:
			self.setMountPointCb(0)
			
	def setMountPointCb(self, result):
		if result == 0:
			if self.mountpoints.isMounted(self.cpath):
				if not self.mountpoints.umount(self.cpath):
					self.session.open(MessageBox, _("Cannot umount current drive.\nA record in progress, timeshit or some external tools (like samba and nfsd) may cause this problem.\nPlease stop this actions/applications and try again"), MessageBox.TYPE_ERROR)
					self.close()
					return
			self.mountpoints.delete(self.cpath)
			if not self.fast:
				self.mountpoints.add(self.device, self.partition, self.cpath)
			self.mountpoints.write()
			if not self.mountpoints.mount(self.device, self.partition, self.cpath):
				self.session.open(MessageBox, _("Cannot mount new drive.\nPlease check filesystem or format it and try again"), MessageBox.TYPE_ERROR)
			elif self.cpath == "/media/hdd":
				os.system("/bin/mkdir /hdd/movie")
				os.system("/bin/mkdir /hdd/music")
				os.system("/bin/mkdir /hdd/picture")

			self.close()
	
	def quit(self):
		self.close()
		
def MountEntry(description, details):
	picture = LoadPixmap(cached = True, path = resolveFilename(SCOPE_CURRENT_SKIN, "/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/icons/diskusb.png"));

	return (picture, description, details)
			
class HddFastRemove(Screen):

	skin = """
                <screen name="HddFastRemove" position="center,115" size="900,530" title="HddFastRemove" flags="wfBorder">
                      <ePixmap position="10,497" size="35,27" pixmap="skin_default/buttons/red.png" alphatest="blend" />
                      <ePixmap position="230,497" size="35,27" pixmap="skin_default/buttons/green.png" alphatest="blend" />
                      <ePixmap position="464,497" size="35,27" pixmap="skin_default/buttons/yellow.png" alphatest="blend" />
                      <ePixmap position="695,497" size="35,27" pixmap="skin_default/buttons/blue.png" alphatest="blend" />
                      <widget name="key_red" position="48,498" zPosition="2" size="150,22" valign="center" halign="center" font="Regular; 20" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                      <widget name="key_green" position="273,499" zPosition="2" size="150,22" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="foreground" />
                      <widget name="key_yellow" position="508,499" zPosition="3" size="150,22" valign="center" halign="center" font="Regular; 21" transparent="1" backgroundColor="foreground" />
                      <widget name="key_blue" position="736,499" zPosition="3" size="150,22" valign="center" halign="center" font="Regular; 21" transparent="1" backgroundColor="foreground" />
                      <eLabel text="Hard Drive Remove" zPosition="2" position="10,11" size="880,40" halign="left" font="Regular;28" foregroundColor="un538eff" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="black" />
                      <widget source="menu" render="Listbox" position="11,58" size="880,410" scrollbarMode="showOnDemand" transparent="1">
                      <convert type="TemplatedMultiContent">
				{"template": [
					MultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (48, 48), png = 0),
					MultiContentEntryText(pos = (65, 3), size = (190, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),
					MultiContentEntryText(pos = (65, 27), size = (190, 38), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 2),
					],
					"fonts": [gFont("Regular", 22), gFont("Regular", 18)],
					"itemHeight": 50
				}
			</convert>
                     </widget>
                    </screen>"""


	def __init__(self, session):
		Screen.__init__(self, session)
		self.mdisks = Disks()
		self.mountpoints = MountPoints()
		self.mountpoints.read()
		self.disks = list ()
		self.mounts = list ()
		for disk in self.mdisks.disks:
			if disk[2] == True:
				diskname = disk[3]
				for partition in disk[5]:
					mp = ""
					rmp = ""
					try:
						mp = self.mountpoints.get(partition[0][:3], int(partition[0][3:]))
						rmp = self.mountpoints.getRealMount(partition[0][:3], int(partition[0][3:]))
					except Exception, e:
						pass
					if len(mp) > 0:
						self.disks.append(MountEntry(disk[3], "P.%s (Fixed: %s)" % (partition[0][3:], mp)))
						self.mounts.append(mp)
					elif len(rmp) > 0:
						self.disks.append(MountEntry(disk[3], "P.%s (Fast: %s)" % (partition[0][3:], rmp)))
						self.mounts.append(rmp)
						
		self["menu"] = List(self.disks)
		self["key_red"] = Button(_("Umount"))
		self["key_blue"] = Button(_("Exit"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"blue": self.quit,
			"red": self.red,
			"cancel": self.quit,
		}, -2)
		
	def red(self):
		if len(self.mounts) > 0:
			self.sindex = self['menu'].getIndex()
			self.mountpoints.umount(self.mounts[self.sindex])
			self.session.open(MessageBox, _("Media unmounted"), MessageBox.TYPE_INFO)
			self.close()
		
	def quit(self):
		self.close()
