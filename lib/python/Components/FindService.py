from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.FindServiceControlListe import FindServiceControlEntryComponent, FindServiceControlListe 
from Screens.ChoiceBox import ChoiceBox
from Screens.ChannelSelection import service_types_tv
from enigma import eServiceCenter, eTimer, eServiceReference
from operator import itemgetter
from os import system
import os       

SPECIAL_CHAR = 96
class FindService(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
                self.list = []
		self.servicelist = FindServiceControlListe(self.list)
		self["servicelist"] = self.servicelist;
		#self.onShown.append(self.chooseLetter)
		self.currentLetter = chr(SPECIAL_CHAR)
		self.readServiceList()
		self.chooseLetterTimer = eTimer()
		self.chooseLetterTimer.callback.append(self.chooseLetter)
		self.onLayoutFinish.append(self.LayoutFinished)

		self["actions"] = ActionMap(["WizardActions"],
		{
			"ok": self.select,
			"back": self.cancel,
		}, -1)

	def LayoutFinished(self):
		self.chooseLetterTimer.start(0, True)

	def cancel(self):
		self.chooseLetter()

	def select(self):
                new_ref = self.servicelist.etoggleSelectedLock()
                ref = str(new_ref)
                
                #Testabfrage
                #f = open('/tmp/new_ref','w')
                #f.write('%s' % (ref))
                #f.close()
                
                cmd = str('#!/bin/sh\n#created by TBX (EOS-Developer)\nwget "http://127.0.0.1/web/zap?sRef=%s">/dev/null 2>&1 -O /tmp' % ref)
                
                f = open('/tmp/cmd','w')
                f.write(cmd)
                f.close()
                
                os.system("chmod 755 /tmp/cmd")
                os.system('/tmp/cmd &')
                os.system('sleep 1')
                os.system('rm /tmp/cmd')
                self.close()

	def readServiceList(self):
		serviceHandler = eServiceCenter.getInstance()
		refstr = '%s ORDER BY name' % (service_types_tv)
		self.root = eServiceReference(refstr)
		self.servicesList = {}
		list = serviceHandler.list(self.root)
		if list is not None:
			services = list.getContent("CN", True) #(servicecomparestring, name)
			for s in services:
				key = s[1].lower()[0]
				if key < 'a' or key > 'z':
					key = chr(SPECIAL_CHAR)
				#key = str(key)
				if not self.servicesList.has_key(key):
					self.servicesList[key] = []
				self.servicesList[key].append(s)
			
	def chooseLetter(self):
		print "choose letter"
		mylist = []
		for x in self.servicesList.keys():
			if x == chr(SPECIAL_CHAR):
				x = (_("special characters"), x)
			else:
				x = (x, x)
			mylist.append(x)
		mylist.sort(key=itemgetter(1))
		sel = ord(self.currentLetter) - SPECIAL_CHAR
		self.session.openWithCallback(self.letterChosen, ChoiceBox, title=_("Show services beginning with"), list=mylist, keys = [], selection = sel)

	def letterChosen(self, result):
		if result is not None:
			print "result:", result
			self.currentLetter = result[1]
			self.list = [FindServiceControlEntryComponent(x[0], x[1]) for x in self.servicesList[result[1]]]
			
                        self.servicelist.setList(self.list)
		else:
		
			self.close()