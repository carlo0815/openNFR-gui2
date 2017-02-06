from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.InfoBar import InfoBar
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.EventView import EventViewSimple
from Components.ActionMap import ActionMap
from Components.FileList import FileList
from Components.MenuList import MenuList
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Components.config import config, ConfigSubsection, ConfigText, ConfigSelection, getConfigListEntry, configfile
from Tools.Directories import fileExists, pathExists
from Tools.HardwareInfo import HardwareInfo
from ServiceReference import ServiceReference
from Screens.InputBox import InputBox
from enigma import eConsoleAppContainer, eServiceReference, ePicLoad, getDesktop, eServiceCenter
from os import system as os_system
from os import stat as os_stat
from os import walk as os_walk
from os import popen as os_popen
from os import rename as os_rename
from os import mkdir as os_mkdir
from os import path as os_path
from os import remove as os_remove
from os import listdir as os_listdir
from time import strftime as time_strftime
from time import localtime as time_localtime
import os


explSession = None
HDSkn = False
sz_w = getDesktop(0).size().width()
if sz_w > 800:
	HDSkn = True
else:
	HDSkn = False
	
cEditor = """<screen name="cEditor" position="40,90" size="1180,590" title="File-Explorer">
                          <widget name="filedata" position="5,7" size="1170,527" itemHeight="25" />
                          <ePixmap position="6,559" size="35,27" pixmap="skin_default/buttons/key_red.png" alphatest="blend" />
                          <ePixmap position="332,559" size="35,27" pixmap="skin_default/buttons/key_green.png" alphatest="blend" />
                          <ePixmap position="658,559" size="35,27" pixmap="skin_default/buttons/key_yellow.png" alphatest="blend" />
                          <ePixmap position="984,559" size="35,27" pixmap="skin_default/buttons/key_blue.png" alphatest="blend" />
                          <widget source="key_red" render="Label" position="41,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular; 21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                          <widget source="key_green" render="Label" position="368,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="foreground" />
                          <widget source="key_yellow" render="Label" position="695,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="foreground" />
                          <widget source="key_blue" render="Label" position="1022,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="foreground" />
                          <eLabel name="new eLabel" position="6,553" size="1170,2" backgroundColor="blue" foregroundColor="blue" />
                          </screen>"""
               
class vEditor(Screen):
	global HDSkn
	if HDSkn:
		if (getDesktop(0).size().width()) > 1030:
                        skin = """
			  <screen name="vEditor" position="40,90" size="1180,590" title="File-Explorer">
                          <widget name="filedata" position="5,7" size="1170,527" itemHeight="25" />
                          <ePixmap position="6,559" size="35,27" pixmap="skin_default/buttons/key_red.png" alphatest="blend" />
                          <ePixmap position="332,559" size="35,27" pixmap="skin_default/buttons/key_green.png" alphatest="blend" />
                          <ePixmap position="658,559" size="35,27" pixmap="skin_default/buttons/key_yellow.png" alphatest="blend" />
                          <ePixmap position="984,559" size="35,27" pixmap="skin_default/buttons/key_blue.png" alphatest="blend" />
                          <widget source="key_red" render="Label" position="41,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular; 21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                          <widget source="key_green" render="Label" position="368,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="foreground" />
                          <widget source="key_yellow" render="Label" position="695,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="foreground" />
                          <widget source="key_blue" render="Label" position="1022,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="foreground" />
                          <eLabel name="new eLabel" position="6,553" size="1170,2" backgroundColor="blue" foregroundColor="blue" />
                          </screen>"""
		else:
			skin = """
			<screen position="center,77" size="900,450" title="File-Explorer">
				<widget name="filedata" position="2,0" size="896,450" itemHeight="25"/>
			        <ePixmap pixmap="skin_default/buttons/key_red.png" position="60,250" zPosition="0" size="140,40" alphatest="on" />
			        <ePixmap pixmap="skin_default/buttons/key_green.png" position="250,250" zPosition="0" size="140,40" alphatest="on" />
			        <ePixmap pixmap="skin_default/buttons/key_yellow.png" position="440,250" zPosition="0" size="140,40" alphatest="on" />
			        <ePixmap pixmap="skin_default/buttons/key_blue.png" position="640,250" zPosition="0" size="140,40" alphatest="blend" />
			        <widget name="key_red" position="60,250" size="140,40" zPosition="-1" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="blue" />
			        <widget name="key_green" position="250,250" size="140,40" zPosition="-1" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="blue" />
			        <widget name="key_yellow" position="440,250" size="140,40" zPosition="-1" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="blue" />
			        <widget name="key_blue" position="640,250" size="140,40" zPosition="-1" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="blue" />

			</screen>"""
	else:
		skin = """
		<screen position="center,77" size="620,450" title="File-Explorer">
			<widget name="filedata" position="0,0" size="620,450" itemHeight="25"/>
			        <ePixmap pixmap="skin_default/buttons/key_red.png" position="60,200" zPosition="0" size="140,40" alphatest="on" />
			        <ePixmap pixmap="skin_default/buttons/key_green.png" position="250,250" zPosition="0" size="140,40" alphatest="on" />
			        <ePixmap pixmap="skin_default/buttons/key_yellow.png" position="440,250" zPosition="0" size="140,40" alphatest="on" />
			        <ePixmap pixmap="skin_default/buttons/key_blue.png" position="640,250" zPosition="0" size="140,40" alphatest="blend" />
			        <widget name="key_red" position="60,200" size="140,40" zPosition="-1" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="yellow" />
			        <widget name="key_green" position="200,250" size="140,40" zPosition="-1" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="blue" />
			        <widget name="key_yellow" position="400,250" size="140,40" zPosition="-1" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="blue" />
			        <widget name="key_blue" position="600,250" size="140,40" zPosition="-1" valign="center" halign="center" font="Regular;20" transparent="1" backgroundColor="blue" />

		</screen>"""

class cEditor(Screen):
	skin = """
	<screen name="cEditor" position="40,90" size="1180,590" title="File-Explorer">
                          <widget name="filedata" position="5,7" size="1170,527" itemHeight="25" />
                          <ePixmap position="6,559" size="35,27" pixmap="skin_default/buttons/key_red.png" alphatest="blend" />
                          <ePixmap position="332,559" size="35,27" pixmap="skin_default/buttons/key_green.png" alphatest="blend" />
                          <ePixmap position="658,559" size="35,27" pixmap="skin_default/buttons/key_yellow.png" alphatest="blend" />
                          <ePixmap position="984,559" size="35,27" pixmap="skin_default/buttons/key_blue.png" alphatest="blend" />
                          <widget source="key_red" render="Label" position="41,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular; 20" transparent="1" shadowColor="black" shadowOffset="-1,-1" />
                          <widget source="key_green" render="Label" position="368,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="foreground" />
                          <widget source="key_yellow" render="Label" position="695,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="foreground" />
                          <widget source="key_blue" render="Label" position="1022,562" zPosition="2" size="214,22" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" backgroundColor="foreground" />
                          <eLabel name="new eLabel" position="6,553" size="1170,2" backgroundColor="blue" foregroundColor="blue" />
                          </screen>"""
	def __init__(self, session, file):
		from Components.Sources.StaticText import StaticText
		
		Screen.__init__(self, session)
		self.skin = cEditor.skin
		self.session = session
		self.file_name = file
		self.list = []
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText(_("NewLine"))	
		self["key_blue"] = StaticText(_("DeleteLine"))                	
		self["filedata"] = MenuList(self.list)
		self["actions"] = ActionMap(["WizardActions", "ColorActions"],

		{
		    "ok": self.editLine,
                    "back": self.exitEditor,
		    "yellow": self.yellow,  
		    "blue": self.blue,                                       
		    "green": self.green,
		    "red": self.close,

		}, -1)
		self.selLine = None
		self.oldLine = None
		self.isChanged = False
		self.GetFileData(file)
		
	def green(self):
        	self.SaveFile(True)		
		
	def exitEditor(self):
		if self.isChanged:
			warningtext = "\nhave been CHANGED! Do you want to save it?\n\nWARNING!"
			warningtext = warningtext + "\n\nThe Editor-Funktions are beta (not full tested) !!!"
			warningtext = warningtext + "\nThe author are NOT RESPONSIBLE\nfor DATA LOST OR DISORDERS !!!"
			dei = self.session.openWithCallback(self.SaveFile, MessageBox,_(self.file_name+warningtext), MessageBox.TYPE_YESNO)
			dei.setTitle(_("SoftcamEdit..."))
		else:
			self.close()

	def GetFileData(self, fx):
		try:
			flines = open(fx, "r")
			for line in flines:
				self.list.append(line)
			flines.close()
			self.setTitle(fx)
		except:
			pass


	def yellow(self):
		self.selLine = self["filedata"].getSelectionIndex()
		self.list.insert(self.selLine, ""'\n')
		self.selLine = None
		#self.SaveFile(True)
		self.session.open(MessageBox, _("New line is inserted!"), MessageBox.TYPE_INFO, timeout=3)
		
	def blue(self):
		self.selLine = self["filedata"].getSelectionIndex()
                i = int(self.selLine) 
                li = i - 1
                lr = i + 2		
                #for x in self.list[li:lr]:
                #         self.isChanged = True
                del self.list[i]
		self.selLine = None
		self.session.open(MessageBox, _("Select Line is deleted!"), MessageBox.TYPE_INFO, timeout=3)
		#self.SaveFile(True)		

	def editLine(self):
		try:
			self.selLine = self["filedata"].getSelectionIndex()
			self.oldLine = self.list[self.selLine]
			editableText = self.list[self.selLine][:-1]
			self.session.openWithCallback(self.callbackEditLine, vInputBox, title=_("old:  "+self.list[self.selLine]), windowTitle=_("Edit line "+str(self.selLine+1)), text=editableText)
		except:
			dei = self.session.open(MessageBox, _("This line is not editable!"), MessageBox.TYPE_ERROR)
			dei.setTitle(_("Error..."))


	def callbackEditLine(self, newline):
                i = int(self.selLine) 
                li = i - 1
                lr = i + 2
		if newline is not None:
			for x in self.list[li:lr]:
				if x == self.oldLine:
					self.isChanged = True
					#self.list.remove(x)
					del self.list[i]
					self.list.insert(self.selLine, newline+'\n')
		self.selLine = None
		self.oldLine = None

	def SaveFile(self, answer):
		if answer is True:
			try:
				eFile = open(self.file_name, "w")
				for x in self.list:
					eFile.writelines(x)
				eFile.close()
			except:
				pass
			self.close()
		else:
			self.close()

class vInputBox(InputBox):
	vibnewx = str(getDesktop(0).size().width()-80)
	sknew = '<screen name="vInputBox" position="center,center" size="'+vibnewx+',70" title="Input...">\n'
	sknew = sknew + '<widget name="text" position="5,5" size="1270,25" font="Regular;15"/>\n<widget name="input" position="0,40" size="'
	sknew = sknew + vibnewx + ',30" font="Regular;20"/>\n</screen>'
	skin = sknew
	def __init__(self, session, title = "", windowTitle = _("Input"), useableChars = None, **kwargs):
		InputBox.__init__(self, session, title, windowTitle, useableChars, **kwargs)
                		
