from Screens.Screen import Screen
from Components.ActionMap import NumberActionMap
from Components.Label import Label
#from Components.ChoiceList import ChoiceEntryComponent, ChoiceList
from Components.MenuList import MenuList
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Plugins.Extensions.Infopanel.Spinner import Spinner
from Plugins.Extensions.Infopanel.outofflash import MoveSpinner_int, MoveSpinner
import os

class SpinnerSelectionBox(Screen):
	skin = """ <screen name="SpinnerSelectionBox" position="center,center" size="1280,720" title="SpinnerSelection" flags="wfNoBorder">
		<widget source="global.CurrentTime" render="Label" position="1125,12" size="100,28" font="Regular; 26" halign="right" backgroundColor="background" transparent="1" foregroundColor="cyan1">
		<convert type="ClockToText">Default</convert>
		</widget>
		<widget source="global.CurrentTime" render="Label" position="905,37" size="320,25" font="Regular;20" halign="right" backgroundColor="background" transparent="1" foregroundColor="cyan1">
		<convert type="ClockToText">Format:%A, %d.%m.%Y</convert>
		</widget>
		<ePixmap position="center,center" zPosition="-10" size="1280,720" pixmap="skin_default/menu/back2b.png" />
		<ePixmap pixmap="skin_default/menu/db.png" position="848,596" size="350,44" alphatest="blend" zPosition="1" />
		<ePixmap pixmap="skin_default/menu/nfr.png" position="950,430" size="150,150" alphatest="on" zPosition="1" />
		<ePixmap pixmap="skin_default/menu/opennfr_info.png" position="837,95" size="379,216" alphatest="on" zPosition="1" />
		<eLabel backgroundColor="grey" position="66,602" size="715,1" zPosition="0" />
		<widget name="bild" position="65,96" zPosition="1" size="715,200" alphatest="blend" />
		<widget name="list" position="65,298" size="715,300" zPosition="1" scrollbarMode="showOnDemand" transparent="1" />
		<widget name="text" position="64,608" size="715,25" font="Regular;20" transparent="1" foregroundColor="cyan1" halign="left" backgroundColor="backtop" />
		<widget source="Title" render="Label" position="65,17" size="720,43" font="Regular;35" backgroundColor="backtop" transparent="1" foregroundColor="cyan1" />
		<eLabel position="837,95" zPosition="3" size="375,214" backgroundColor="unff000000" />
		<widget source="session.VideoPicture" render="Pig" position="837,95" size="375,214" backgroundColor="transparent" zPosition="1" />
 		<ePixmap pixmap="skin_default/buttons/red.png" position="70,670" size="30,30" alphatest="blend" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="360,670" size="30,30" alphatest="blend" />
		<widget source="key_red" render="Label" position="105,672" size="240,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />
		<widget source="key_green" render="Label" position="395,672" size="240,24" zPosition="1" font="Regular;20" halign="left" backgroundColor="black" transparent="1" />
		</screen>"""
	def __init__(self, session, title = "", list1 = []):
		Screen.__init__(self, session)

		self["text"] = Label(title)
		self.list = list1
		self.summarylist = [] 
		cursel = self.list[0]
		self.Bilder = []
		if cursel:
			for i in list(range(64)):
				if (os.path.isfile("/usr/share/enigma2/Spinner/%s/wait%d.png"%(cursel[0],i+1))):
					self.Bilder.append("/usr/share/enigma2/Spinner/%s/wait%d.png"%(cursel[0],i+1))
		self["bild"] = Spinner(self.Bilder);
		self["list"] = MenuList(list = self.list) #, selection = selection)
		self["list"].onSelectionChanged.append(self.Changed)
		self["summary_list"] = StaticText()
		self.updateSummary()
		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Save"))
		self["actions"] = NumberActionMap(["WizardActions", "DirectionActions", "ColorActions"], 
		{
			"ok": self.go,
			"back": self.cancel,
			"up": self.up,
			"down": self.down,
			"red": self.cancel,
			"green": self.go,
		}, -1)
		

	def KeyYellow(self):
		self.session.openWithCallback(self.Key_ex, MoveSpinner)
		
	def KeyBlue(self):
		self.session.openWithCallback(self.Key_ex, MoveSpinner_int)
		
	def Key_ex(self, arg):
		self.cancel()


	def Changed(self):
		cursel = self["list"].l.getCurrentSelection()
		if cursel:
			self.Bilder = []
			for i in list(range(64)):
				if (os.path.isfile("/usr/share/enigma2/Spinner/%s/wait%d.png"%(cursel[0],i+1))):
					self.Bilder.append("/usr/share/enigma2/Spinner/%s/wait%d.png"%(cursel[0],i+1))
			self["bild"].SetBilder(self.Bilder)
			
		
	def keyLeft(self):
		pass
	
	def keyRight(self):
		pass
	
	def up(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.moveUp)
				self.updateSummary(self["list"].l.getCurrentSelectionIndex())
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == 0:
					break

	def down(self):
		if len(self["list"].list) > 0:
			while 1:
				self["list"].instance.moveSelection(self["list"].instance.moveDown)
				self.updateSummary(self["list"].l.getCurrentSelectionIndex())
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == len(self["list"].list) - 1:
					break

	# runs the current selected entry
	def go(self):
		cursel = self["list"].l.getCurrentSelection()
		if cursel:
			self.goEntry(cursel[0])
		else:
			self.cancel()

	# runs a specific entry
	def goEntry(self, entry):
		if len(entry) > 2 and isinstance(entry[1], str) and entry[1] == "CALLFUNC":
			# CALLFUNC wants to have the current selection as argument
			arg = self["list"].l.getCurrentSelection()[0]
			entry[2](arg)
		else:
			self.close(entry)

	def updateSummary(self, curpos=0):
		pos = 0
		summarytext = ""
		for entry in self.summarylist:
			if pos > curpos-2 and pos < curpos+5:
				if pos == curpos:
					summarytext += ">"
				else:
					summarytext += entry[0]
				summarytext += ' ' + entry[1] + '\n'
			pos += 1
		self["summary_list"].setText(summarytext)

	def cancel(self):
		self.close(None) 
