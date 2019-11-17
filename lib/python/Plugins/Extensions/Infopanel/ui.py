##################################
# Configuration GUI

import plugin
import os
import enigma
from enigma import *
from Components.config import config, configfile, getConfigListEntry, ConfigSelection, ConfigSubsection, ConfigEnableDisable, ConfigText, ConfigClock, ConfigLocations, ConfigInteger
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Tools.FuzzyDate import FuzzyTime

FRIENDLY = {
	"/media/hdd": _("Harddisk"),
	"/media/usb": _("USB"),
	"/media/cf": _("CF"),
	"/media/mmc1": _("SD"),
	}
def getLocationChoices():
	result = []
	for line in open('/proc/mounts', 'r'):
		items = line.split()
		if items[1].startswith('/media'):
			desc = FRIENDLY.get(items[1], items[1])
			if items[0].startswith('//'):
				desc += ' (*)'
			result.append((items[1], desc))
	return result


class Config(ConfigListScreen,Screen):
	skin = """
<screen position="center,center" size="560,400" title="AutoBackup Configuration" >
	<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
	<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
	<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 

	<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
	<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
	<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

	<widget name="config" position="10,40" size="540,200" scrollbarMode="showOnDemand" />
	<widget name="status" position="10,250" size="540,130" font="Regular;16" />

	<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,383" size="14,14" zPosition="3"/>
	<widget font="Regular;18" halign="left" position="505,380" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
		<convert type="ClockToText">Default</convert>
	</widget>
	<widget name="statusbar" position="10,380" size="470,20" font="Regular;18" />
</screen>"""
		
	def __init__(self, session, args = 0):
		self.session = session
		self.setup_title = _("AutoBackup Configuration")
		config.plugins.configurationbackup = ConfigSubsection()
		config.plugins.configurationbackup.enabled = ConfigEnableDisable(default = False)
		config.plugins.configurationbackup.maxbackup = ConfigInteger(default=99, limits=(0, 99))
		config.plugins.configurationbackup.backuplocation = ConfigText(default = '/media/hdd/', visible_width = 50, fixed_size = False)
		config.plugins.configurationbackup.wakeup = ConfigClock(default = ((3*60) + 0) * 60) # 3:00
		config.plugins.configurationbackup.backupdirs = ConfigLocations(default=[eEnv.resolve('${sysconfdir}/enigma2/'), '/etc/network/interfaces', '/etc/wpa_supplicant.conf', '/etc/wpa_supplicant.ath0.conf', '/etc/wpa_supplicant.wlan0.conf', '/etc/resolv.conf', '/etc/default_gw', '/etc/hostname'])

		Screen.__init__(self, session)
		cfg = config.plugins.configurationbackup
		choices=getLocationChoices()
		if choices:
			currentwhere = cfg.backuplocation.value
			defaultchoice = choices[0][0] 
			for k,v in choices:
				if k == currentwhere:
					defaultchoice = k
					break
		else:
			defaultchoice = ""
			choices = [("", _("Nowhere"))]
		self.cfgwhere = ConfigSelection(default=defaultchoice, choices=choices)
		configList = [
			getConfigListEntry(_("Backup location"), self.cfgwhere),
			getConfigListEntry(_("Daily automatic backup"), config.plugins.configurationbackup.enabled),
			getConfigListEntry(_("Automatic start time"), config.plugins.configurationbackup.wakeup),
			getConfigListEntry(_("Max. saved backup"), config.plugins.configurationbackup.maxbackup),			
			]
		ConfigListScreen.__init__(self, configList, session=session, on_change = self.changedEntry)
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Ok"))
		self["key_blue"] = Button("")
		self["statusbar"] = Label()
		self["status"] = Label()
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "MenuActions"],
		{
			"red": self.cancel,
			"green": self.save,
			"blue": self.disable,
			"save": self.save,
			"cancel": self.cancel,
			"ok": self.save,
		}, -2)
		self.onChangedEntry = []
		self.data = ''
		self.container = enigma.eConsoleAppContainer()
		self.container.appClosed.append(self.appClosed)
		self.container.dataAvail.append(self.dataAvail)
		self.cfgwhere.addNotifier(self.changedWhere)
		self.onClose.append(self.__onClose)

	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]
	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())
	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

	def changedWhere(self, cfg):
		self.isActive = False
		if not cfg.value:
			self["status"].setText(_("No suitable media found, insert USB stick, flash card or harddisk."))
			self.isActive = False
		else:
			config.plugins.configurationbackup.backuplocation.value = cfg.value
			path = os.path.join(cfg.value, 'backup')
			if not os.path.exists(path):
				self["status"].setText(_("No backup present"))
			else:
				self.isActive = True
		if self.isActive:
			self["key_blue"].setText(_("Disable"))
		else:
			self["key_blue"].setText("")

	def disable(self):
		cfg = self.cfgwhere
		if not cfg.value:
			return
		self.changedWhere(cfg)

	def __onClose(self):
		self.cfgwhere.notifiers.remove(self.changedWhere)

	def save(self):
		config.plugins.configurationbackup.backuplocation.value = self.cfgwhere.value
		config.plugins.configurationbackup.backuplocation.save()
		self.saveAll()
		self.close(True,self.session)

	def cancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close(False,self.session)

	def showOutput(self):
		self["status"].setText(self.data)


	def appClosed(self, retval):
		print "[AutoBackup] done:", retval
		if retval:
			txt = _("Failed")
		else:
			txt = _("Done")
		self.showOutput()
		self.data = ''
		self["statusbar"].setText(txt)
		self.changedWhere(self.cfgwhere)

	def dataAvail(self, s):
		self.data += s
		print "[AutoBackup]", s.strip()
		self.showOutput()

