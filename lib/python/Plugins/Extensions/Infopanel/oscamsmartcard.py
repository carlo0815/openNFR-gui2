from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Plugins.Extensions.Infopanel.Manager import NFRCamManager

#############################################################

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("OscamSmartcard", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/Infopanel/data/locale/"))

def _(txt):
	t = gettext.dgettext("OscamSmartcard", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])
	return block

#############################################################
emuactive = 0

config.plugins.OscamSmartcard = ConfigSubsection()

				#Oscam webifPort
config.plugins.OscamSmartcard.WebifPort = ConfigSelection(default="83", choices = [
				("83", _("83")), #default
				("8000", _("8000"))
				])
				# Smartcard oscam.server
config.plugins.OscamSmartcard.internalReader0 = ConfigSelection(default="none", choices = [
				("V13", _("Sky V13")),
				("V13_fast", _("Sky V13 Fastmode")),
				("V14", _("Sky V14")),
				("V14_fast", _("Sky V14 Fastmode")),
				("S02", _("Sky S02")),
				("HD01", _("HD+ HD01 white")),
				("HD02", _("HD+ HD02 black")),
				("I02-Beta", _("I02 Beta")),
				("I12-Beta", _("I12 Beta")),
				("I12-Nagra", _("I12 Nagra")),
				("V23", _("KabelBW V23")),
				("ORF", _("ORF 0D05")),
				("ORF_ICE_crypto", _("ORF ICE Cryptoworks 0D95")),
				("ORF_ICE_irdeto", _("ORF ICE Irdeto 0648")),
				("SRG-V2", _("SRG V2")),
				("SRG-V4", _("SRG V4")),
				("SRG-V5", _("SRG V5")),
				("UM01", _("UnityMedia UM01")),
				("UM02", _("UnityMedia UM02")),
				("UM03", _("UnityMedia UM03")),
				("D01", _("Kabel Deutschl. D01")),
				("D02", _("Kabel Deutschl. D02")),
				("D09", _("Kabel Deutschl. D09")),
				("MTV", _("MTV")),
				("tivu", _("Tivusat")),
				("JSC", _("JSC-sports - Viaccess")),
				("hallotv", _("HalloTV")),
				("RedlightHD", _("Redlight Elite HD - Viaccess")),
				("FreeXTV", _("FreeX TV - Viaccess")),
				("none", _("None"))
				])
config.plugins.OscamSmartcard.internalReader1 = ConfigSelection(default="none", choices = [
				("V13", _("Sky V13")),
				("V13_fast", _("Sky V13 Fastmode")),
				("V14", _("Sky V14")),
				("V14_fast", _("Sky V14 Fastmode")),
				("S02", _("Sky S02")),
				("HD01", _("HD+ HD01 white")),
				("HD02", _("HD+ HD02 black")),
				("I02-Beta", _("I02 Beta")),
				("I12-Beta", _("I12 Beta")),
				("I12-Nagra", _("I12 Nagra")),
				("V23", _("KabelBW V23")),
				("ORF", _("ORF 0D05")),
				("ORF_ICE_crypto", _("ORF ICE Cryptoworks 0D95")),
				("ORF_ICE_irdeto", _("ORF ICE Irdeto 0648")),
				("SRG-V2", _("SRG V2")),
				("SRG-V4", _("SRG V4")),
				("SRG-V5", _("SRG V5")),
				("UM01", _("UnityMedia UM01")),
				("UM02", _("UnityMedia UM02")),
				("UM03", _("UnityMedia UM03")),
				("D01", _("Kabel Deutschl. D01")),
				("D02", _("Kabel Deutschl. D02")),
				("D09", _("Kabel Deutschl. D09")),
				("MTV", _("MTV")),
				("tivu", _("Tivusat")),
				("JSC", _("JSC-sports - Viaccess")),
				("hallotv", _("HalloTV")),
				("RedlightHD", _("Redlight Elite HD - Viaccess")),
				("FreeXTV", _("FreeX TV - Viaccess")),
				("none", _("None"))
				])
config.plugins.OscamSmartcard.externalReader0 = ConfigSelection(default="none", choices = [
				("V13", _("Sky V13")),
				("V13_fast", _("Sky V13 Fastmode")),
				("V14", _("Sky V14")),
				("V14_fast", _("Sky V14 Fastmode")),
				("S02", _("Sky S02")),
				("HD01", _("HD+ HD01 white")),
				("HD02", _("HD+ HD02 black")),
				("I02-Beta", _("I02 Beta")),
				("I12-Beta", _("I12 Beta")),
				("I12-Nagra", _("I12 Nagra")),
				("V23", _("KabelBW V23")),
				("ORF", _("ORF 0D05")),
				("ORF_ICE_crypto", _("ORF ICE Cryptoworks 0D95")),
				("ORF_ICE_irdeto", _("ORF ICE Irdeto 0648")),
				("SRG-V2", _("SRG V2")),
				("SRG-V4", _("SRG V4")),
				("SRG-V5", _("SRG V5")),
				("UM01", _("UnityMedia UM01")),
				("UM02", _("UnityMedia UM02")),
				("UM03", _("UnityMedia UM03")),
				("D01", _("Kabel Deutschl. D01")),
				("D02", _("Kabel Deutschl. D02")),
				("D09", _("Kabel Deutschl. D09")),
				("MTV", _("MTV")),
				("tivu", _("Tivusat")),
				("JSC", _("JSC-sports - Viaccess")),
				("hallotv", _("HalloTV")),
				("RedlightHD", _("Redlight Elite HD - Viaccess")),
				("FreeXTV", _("FreeX TV - Viaccess")),
				("none", _("None"))
				])
config.plugins.OscamSmartcard.externalReader1 = ConfigSelection(default="none", choices = [
				("V13", _("Sky V13")),
				("V13_fast", _("Sky V13 Fastmode")),
				("V14", _("Sky V14")),
				("V14_fast", _("Sky V14 Fastmode")),
				("S02", _("Sky S02")),
				("HD01", _("HD+ HD01 white")),
				("HD02", _("HD+ HD02 black")),
				("I02-Beta", _("I02 Beta")),
				("I12-Beta", _("I12 Beta")),
				("I12-Nagra", _("I12 Nagra")),
				("V23", _("KabelBW V23")),
				("ORF", _("ORF 0D05")),
				("ORF_ICE_crypto", _("ORF ICE Cryptoworks 0D95")),
				("ORF_ICE_irdeto", _("ORF ICE Irdeto 0648")),
				("SRG-V2", _("SRG V2")),
				("SRG-V4", _("SRG V4")),
				("SRG-V5", _("SRG V5")),
				("UM01", _("UnityMedia UM01")),
				("UM02", _("UnityMedia UM02")),
				("UM03", _("UnityMedia UM03")),
				("D01", _("Kabel Deutschl. D01")),
				("D02", _("Kabel Deutschl. D02")),
				("D09", _("Kabel Deutschl. D09")),
				("MTV", _("MTV")),
				("tivu", _("Tivusat")),
				("JSC", _("JSC-sports - Viaccess")),
				("hallotv", _("HalloTV")),
				("RedlightHD", _("Redlight Elite HD - Viaccess")),
				("FreeXTV", _("FreeX TV - Viaccess")),
				("none", _("None"))
				])
				# Smartcard oscam.server.emu
if emuactive == 1:
	config.plugins.OscamSmartcard.EMU = ConfigSelection(default="emu_none", choices = [
					("emu", _("Yes")),
					("emu_none", _("No"))
					])

#######################################################################

class OscamSmartcard(ConfigListScreen, Screen):
	skin = """
  <screen name="OscamSmartcard-Setup" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="#90000000">
    <eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#20000000" transparent="0" />
    <eLabel font="Regular; 20" foregroundColor="unffffff" backgroundColor="#20000000" halign="left" position="77,645" size="250,33" text="Cancel" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="unffffff" backgroundColor="#20000000" halign="left" position="375,645" size="250,33" text="Save" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="unffffff" backgroundColor="#20000000" halign="left" position="682,645" size="250,33" text="Softcam Restart" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="unffffff" backgroundColor="#20000000" halign="left" position="989,645" size="250,33" text="Info" transparent="1" />
    <widget name="config" position="61,114" size="590,500" scrollbarMode="showOnDemand" transparent="1" />
    <eLabel position="60,55" size="348,50" text="OscamSmartcard" font="Regular; 40" valign="center" transparent="1" backgroundColor="#20000000" />
    <eLabel position="400,58" size="349,50" text="Setup" foregroundColor="unffffff" font="Regular; 30" valign="center" backgroundColor="#20000000" transparent="1" halign="left" />
    <eLabel position="970,640" size="5,40" backgroundColor="#2600E6" />
    <eLabel position="665,640" size="5,40" backgroundColor="#e5dd00" />
    <eLabel position="360,640" size="5,40" backgroundColor="#61e500" />
    <eLabel position="60,640" size="5,40" backgroundColor="#e61700" />
    <widget name="oscamsmartcardhelperimage" position="669,112" size="550,500" zPosition="1" />
    <widget name="HELPTEXT" position="61,400" size="590,250" zPosition="1" font="Regular; 20" halign="left" valign="top" backgroundColor="#20000000" transparent="1" />
    <eLabel text="OscamSmartcard mod by EOS-Team" position="692,70" size="540,25" zPosition="1" font="Regular; 15" halign="right" valign="top" backgroundColor="#20000000" transparent="1" />
  </screen>
"""

	def __init__(self, session, args = None, picPath = None):
		self.config_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.oscamconfigpath = "/usr/keys/"
		self.oscamuser = (self.oscamconfigpath + "oscam.user")
		self.oscamuserTMP = (self.oscamuser + ".tmp")
		self.oscamconf = (self.oscamconfigpath + "oscam.conf")
		self.oscamconfTMP = (self.oscamconf + ".tmp")
		self.oscamserver = (self.oscamconfigpath + "oscam.server")
		self.oscamserverTMP = (self.oscamserver + ".tmp")
		self.oscamdvbapi = (self.oscamconfigpath + "oscam.dvbapi")
		self.oscamdvbapiTMP = (self.oscamdvbapi + ".tmp")
		self.oscamsmartcarddata = "/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/data/"
		self.picPath = picPath
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["oscamsmartcardhelperimage"] = Pixmap()
		self["HELPTEXT"] = Label()
		list = []
		list.append(getConfigListEntry(_("Select OScam WebifPort:"), config.plugins.OscamSmartcard.WebifPort, _("INFORMATION: Select OScam WebifPort\n\nOscam Webif will be accessible on the selected port.\ne.g. http:\\IPOFYOURBOX:83")))
		list.append(getConfigListEntry(_("Internal Reader /dev/sci0:"), config.plugins.OscamSmartcard.internalReader0, _("INFORMATION: Internal Reader /dev/sci0\n\nAll STB's having only one cardslot.\nOn STB's having two cardslots it is mostly the lower cardslot.")))
		list.append(getConfigListEntry(_("Internal Reader /dev/sci1:"), config.plugins.OscamSmartcard.internalReader1, _("INFORMATION: Internal Reader /dev/sci1\n\nOn STB's having two cardslots it is mostly the upper cardslot.")))
		list.append(getConfigListEntry(_("External Reader /dev/ttyUSB0:"), config.plugins.OscamSmartcard.externalReader0, _("INFORMATION: External Reader /dev/ttyUSB0\n\nThis Reader can be used to configure for example a connected easymouse.")))
		list.append(getConfigListEntry(_("External Reader /dev/ttyUSB1:"), config.plugins.OscamSmartcard.externalReader1, _("INFORMATION: External Reader /dev/ttyUSB1\n\nThis Reader can be used to configure for example a second connected easymouse.")))
		if emuactive == 1:
			list.append(getConfigListEntry(_("Enable EMU Reader:"), config.plugins.OscamSmartcard.EMU, _("INFORMATION: Enable EMU Reader\n\nEnabling this Reader, OscamSmartcard will use Oscam Dmod as running Oscam (instead of regular OScam SVN XXXX).\nOscamSmartcard does NOT provide the required file SoftCam.Key!")))

		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {"left": self.keyLeft, "down": self.keyDown, "up": self.keyUp, "right": self.keyRight, "red": self.exit, "yellow": self.reboot, "blue": self.showInfo, "green": self.save, "cancel": self.exit}, -1)
		self.onLayoutFinish.append(self.UpdatePicture)
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()


	def selectionChanged(self):
		self["HELPTEXT"].setText(self["config"].getCurrent()[2])

	def GetPicturePath(self):
		try:
			returnValue = self["config"].getCurrent()[1].value
			path = "/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/images/" + returnValue + ".png"
			return path
		except:
			return "/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/images/no.png"

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)

	def ShowPicture(self):
		self.PicLoad.setPara([self["oscamsmartcardhelperimage"].instance.size().width(),self["oscamsmartcardhelperimage"].instance.size().height(),self.Scale[0], self.Scale[1], 0, 1, "#20000000"])
		self.PicLoad.startDecode(self.GetPicturePath())

	def DecodePicture(self, PicInfo = ""):
		ptr = self.PicLoad.getData()
		self["oscamsmartcardhelperimage"].instance.setPixmap(ptr)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.ShowPicture()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.ShowPicture()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.ShowPicture()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.ShowPicture()

	def reboot(self):
                self.restartSTB()
                
	def showInfo(self):
		self.session.open(MessageBox, _("OscamSmartcard mod by NFR Team for NFR Images"), MessageBox.TYPE_INFO)

	def save(self):
		self.oscamconfigpath = "/usr/keys/"
		self.oscamuser = (self.oscamconfigpath + "oscam.user")
		self.oscamuserTMP = (self.oscamuser + ".tmp")
		self.oscamconf = (self.oscamconfigpath + "oscam.conf")
		self.oscamconfTMP = (self.oscamconf + ".tmp")
		self.oscamserver = (self.oscamconfigpath + "oscam.server")
		self.oscamserverTMP = (self.oscamserver + ".tmp")
		self.oscamdvbapi = (self.oscamconfigpath + "oscam.dvbapi")
		self.oscamdvbapiTMP = (self.oscamdvbapi + ".tmp")
		self.oscamservices = (self.oscamconfigpath + "oscam.services")
		self.oscamservicesTMP = (self.oscamservices + ".tmp")
		for x in self["config"].list:
			if len(x) > 1:
					x[1].save()
			else:
					pass
		try:
			system('mkdir /usr/keys/ > /dev/null 2>&1')
		except:
			pass
		configfile.save()
		self.saveoscamserver()
		self.saveoscamdvbapi()
		self.saveoscamuser()
		self.saveoscamconf()
		self.saveoscamservices()
		self.savecamstart()
		configfile.save()
		self.restartSTB()
			
	def saveoscamserver(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.internalReader0.value + "_internalReader0.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.internalReader1.value + "_internalReader1.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.externalReader0.value + "_externalReader0.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.externalReader1.value + "_externalReader1.txt")
			if emuactive == 1:
				self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.EMU.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamserverTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamserver, "w")
			for line in open(self.oscamserverTMP):
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamserverTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.server!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamdvbapi(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			if emuactive == 1:
				self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.EMU.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.internalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.internalReader1.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.externalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.externalReader1.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamdvbapiTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamdvbapi, "w")
			for line in open(self.oscamdvbapiTMP):
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamdvbapiTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.dvbapi!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamuser(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.user.txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamuserTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamuser, "w")
			for line in open(self.oscamuserTMP):
				if config.plugins.OscamSmartcard.internalReader0.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader1.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader0.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader1.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader0.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader1.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader0.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader1.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader0.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader1.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader0.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader1.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader0.value == 'D09':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader1.value == 'D09':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader0.value == 'D09':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader1.value == 'D09':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamuserTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.user!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamconf(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.conf.txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamconfTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamconf, "w")
			for line in open(self.oscamconfTMP):
				line = line.replace("83", config.plugins.OscamSmartcard.WebifPort.value )
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamconfTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.conf!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamservices(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.internalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.internalReader1.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.externalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.externalReader1.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamservicesTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamservices, "w")
			for line in open(self.oscamservicesTMP):
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamservicesTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.services!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def savecamstart(self):
		self.session.open(EosCamManager)
		self.close()


	def appendconfFile(self,appendFileName):
		skFile = open(appendFileName, "r")
		file_lines = skFile.readlines()
		skFile.close()
		for x in file_lines:
			self.config_lines.append(x)

	def restartSTB(self):
		configfile.save()
		self.session.open(EosCamManager)
		self.close()

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
			else:
					pass
		self.close()

