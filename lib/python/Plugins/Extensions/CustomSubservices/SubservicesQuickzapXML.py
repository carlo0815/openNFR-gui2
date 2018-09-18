# -*- coding: utf-8 -*- 

from Screens.Screen import Screen
from Components.ActionMap import NumberActionMap
from Components.Label import Label

from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.ServiceEventTracker import InfoBarBase

from Screens.SubservicesQuickzap import SubservicesQuickzap

from enigma import eTimer, eServiceReference

class SubservicesQuickzapXML(SubservicesQuickzap):

	def __init__(self, session, subservices):
		SubservicesQuickzap.__init__(self, session, subservices)

		self.subservices = subservices
		if self.subservices is not None:
			self.n = len(subservices)
		self.service = self.session.nav.getCurrentlyPlayingServiceReference()
		self.__lastservice = self.currentlyPlayingSubservice = self.getSubserviceIndex(self.service)

		self.skinName = "SubservicesQuickzap"

	def onLayoutFinished(self):
		self.setTitle(_("Subservices") + " XML")

	def updateSubservices(self):
		pass

	def nextSubservice(self):
		if self.n:
			if self.currentlyPlayingSubservice >= self.n - 1:
				self.playSubservice(0)
			else:
				self.playSubservice(self.currentlyPlayingSubservice + 1)

	def previousSubservice(self):
		if self.n:
			if self.currentlyPlayingSubservice > self.n:
				self.currentlyPlayingSubservice = self.n
			if self.currentlyPlayingSubservice == 0:
				self.playSubservice(self.n - 1)
			else:
				self.playSubservice(self.currentlyPlayingSubservice - 1)

	def getSubserviceIndex(self, service):
		if self.n is None or service is None:
			return -1
		try:
			for x in range(self.n):
				if service == eServiceReference(self.subservices[x].getRef()):
					return x
		except:
			return -1

	def keyNumberGlobal(self, number):
		if number == 0:
			self.playSubservice(self.__lastservice)
		elif self.n is not None and number <= self.n:
			self.playSubservice(number-1)

	def showSelection(self):
		tlist = []
		n = self.n or 0
		if n:
			idx = 0
			while idx < n:
				i = self.subservices[idx]
				tlist.append((i.getName(), idx))
				idx += 1
		keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "green", "yellow"] + [""] * n
		self.session.openWithCallback(self.subserviceSelected, ChoiceBox, title=_("Please select a subservice..."), list = tlist, selection = self.currentlyPlayingSubservice, keys = keys, windowTitle=_("Subservices") + " XML")

	def subserviceSelected(self, service):
		if service is not None:
			self.playSubservice(service[1])

	def playSubservice(self, number = 0):
		#try:
		newservice = eServiceReference(self.subservices[number].getRef())
		#except:
		#	newservice = None
		if newservice and newservice.valid():
			self.__lastservice = self.currentlyPlayingSubservice
			self.session.nav.stopService()
			self.session.nav.playService(newservice, checkParentalControl=False, adjust=False)
			self.currentlyPlayingSubservice = number
			self.currentSubserviceNumberLabel.setText(str(number+1))
			self.doShow()
