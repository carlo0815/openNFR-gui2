# -*- coding: utf-8 -*- 
from Components.PluginComponent import plugins
from Components.config import config
from Components.Converter.ServiceInfo import ServiceInfo
from Components.Element import cached
from Plugins.Plugin import PluginDescriptor

from Screens.Screen import Screen
from Screens.ChannelSelection import BouquetSelector
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBarGenerics import InfoBarSubserviceSelection
from Screens.MessageBox import MessageBox

from enigma import iServiceInformation, eEPGCache, eServiceCenter, eServiceReference, iSubserviceListPtr

import xml.dom.minidom
import datetime
from Plugins.Extensions.CustomSubservices.Subservice import Subservice
from Plugins.Extensions.CustomSubservices.SubserviceGroup import SubserviceGroup
from Plugins.Extensions.CustomSubservices.SubservicesQuickzapXML import SubservicesQuickzapXML


XML_PATH = "/etc/enigma2/subservices.xml"

#change/add methods of InfoBarSubserviceSelection

def checkSubservicesAvail(self):
	#check traditional subservices first
	service = self.session.nav.getCurrentService()
	subservices = service and service.subServices()
	if not subservices or subservices.getNumberOfSubservices() == 0:
		serviceRef = self.session.nav.getCurrentlyPlayingServiceReference()
		subservices = serviceRef and self.getAvailableSubservices(serviceRef) or None
		if not subservices or len(subservices) == 0:
			self["SubserviceQuickzapAction"].setEnabled(False)

InfoBarSubserviceSelection.checkSubservicesAvail = checkSubservicesAvail

def changeSubservice(self, direction):
	serviceRef = self.session.nav.getCurrentlyPlayingServiceReference()
	subservices = serviceRef and self.getAvailableSubservices(serviceRef) or None
	if subservices and len(subservices) > 0:
		#custom subservices
		n = len(subservices)
		selection = -1
		idx = 0
		while idx < n:
			if subservices[idx].getRef() == serviceRef.toString():
				selection = idx
				break
			idx += 1
		if selection != -1:
			selection += direction
			if selection >= n:
				selection=0
			elif selection < 0:
				selection= n - 1
			try:
				newservice = eServiceReference(subservices[selection].getRef())
			except:
				newservice = None
			if newservice and newservice.valid():
				del subservices
				del serviceRef
				self.playSubservice(newservice)
	else:
		#traditional subservices
		service = self.session.nav.getCurrentService()
		subservices = service and service.subServices()
		n = subservices and subservices.getNumberOfSubservices()
		if n and n > 0:
			selection = -1
			ref = self.session.nav.getCurrentlyPlayingServiceReference()
			idx = 0
			while idx < n:
				if subservices.getSubservice(idx).toString() == ref.toString():
					selection = idx
					break
				idx += 1
			if selection != -1:
				selection += direction
				if selection >= n:
					selection = 0
				elif selection < 0:
					selection = n - 1
				newservice = subservices.getSubservice(selection)
				if newservice.valid():
					del subservices
					del service
					self.playSubservice(newservice)

InfoBarSubserviceSelection.changeSubservice = changeSubservice

def subserviceSelection(self):
	serviceRef = self.session.nav.getCurrentlyPlayingServiceReference()
	subservices = serviceRef and self.getAvailableSubservices(serviceRef) or None
	if subservices and len(subservices) > 0:
		#custom subservices
		self.bouquets = self.servicelist and self.servicelist.getBouquetList()
		n = len(subservices)
		selection = 0
		if n and n > 0:
			tlist = []
			idx = 0
			while idx < n:
				i = subservices[idx]
				if i.getRef() == serviceRef.toString():
					selection = idx
				tlist.append((i.getDisplayString(), i))
				idx += 1

			if self.bouquets and len(self.bouquets):
				keys = ["red", "blue", "", "1", "2", "3", "4", "5", "6", "7", "8", "9", "green", "yellow"] + [""] * n
				if config.usage.multibouquet.value:
					tlist = [(_("Quick zap"), "quickzap", subservices), (_("Add to bouquet"), "CALLFUNC", self.addSubserviceToBouquetCallback), ("--", "")] + tlist
				else:
					tlist = [(_("Quick zap"), "quickzap", subservices), (_("Add to favourites"), "CALLFUNC", self.addSubserviceToBouquetCallback), ("--", "")] + tlist
				selection += 3
			else:
				tlist = [(_("Quick zap"), "quickzap", subservices), ("--", "")] + tlist
				keys = ["red", "", "1", "2", "3", "4", "5", "6", "7", "8", "9", "green", "yellow"] + [""] * n
				selection += 2
			self.session.openWithCallback(self.subserviceSelected, ChoiceBox, title=_("Please select a subservice..."), list = tlist, selection = selection, keys = keys, skin_name = "SubserviceSelection")
	else:
		#traditional subservices
		service = self.session.nav.getCurrentService()
		subservices = service and service.subServices()
		self.bouquets = self.servicelist.getBouquetList()
		n = subservices and subservices.getNumberOfSubservices()
		selection = 0
		if n and n > 0:
			ref = self.session.nav.getCurrentlyPlayingServiceReference()
			tlist = []
			idx = 0
			cnt_parent = 0
			while idx < n:
				i = subservices.getSubservice(idx)
				if i.toString() == ref.toString():
					selection = idx
				tlist.append((i.getName(), i))
				if i.getUnsignedData(6):
					cnt_parent += 1
				idx += 1

			if cnt_parent and self.bouquets and len(self.bouquets):
				keys = ["red", "blue", "", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ] + [""] * n
				if config.usage.multibouquet.value:
					tlist = [(_("Quick zap"), "quickzap", service.subServices()), (_("Add to bouquet"), "CALLFUNC", self.addSubserviceToBouquetCallback), ("--", "")] + tlist
				else:
					tlist = [(_("Quick zap"), "quickzap", service.subServices()), (_("Add to favourites"), "CALLFUNC", self.addSubserviceToBouquetCallback), ("--", "")] + tlist
				selection += 3
			else:
				tlist = [(_("Quick zap"), "quickzap", service.subServices()), ("--", "")] + tlist
				keys = ["red", "", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ] + [""] * n
				selection += 2

			self.session.openWithCallback(self.subserviceSelected, ChoiceBox, title=_("Please select a sub service..."), list = tlist, selection = selection, keys = keys, skin_name = "SubserviceSelection")

InfoBarSubserviceSelection.subserviceSelection = subserviceSelection

def subserviceSelected(self, service):
	#check traditional subservices first and call old method
	del self.bouquets
	if not service is None:
		if isinstance(service[1], str):
			if service[1] == "quickzap":
				if not isinstance(service[2], iSubserviceListPtr):
					self.session.open(SubservicesQuickzapXML, service[2])
				else:
					from Screens.SubservicesQuickzap import SubservicesQuickzap
					self.session.open(SubservicesQuickzap, service[2])
		else:
			self["SubserviceQuickzapAction"].setEnabled(True)
			if isinstance(service[1], Subservice):
				try:
					ref = eServiceReference(service[1].getRef())
				except:
					ref = None
				if ref:
					self.playSubservice(ref)
			else:
				self.playSubservice(service[1])

InfoBarSubserviceSelection.subserviceSelected = subserviceSelected

def addSubserviceToBouquetCallback(self, service):
	if service and len(service) > 1:
		if (isinstance(service[1], Subservice) and eServiceReference(service[1].getRef()).valid()) or (isinstance(service[1], eServiceReference)):
			self.selectedSubservice = service
			if self.bouquets is None:
				cnt = 0
			else:
				cnt = len(self.bouquets)
			if cnt > 1: # show bouquet list
				self.bsel = self.session.openWithCallback(self.bouquetSelClosed, BouquetSelector, self.bouquets, self.addSubserviceToBouquet)
			elif cnt == 1: # add to only one existing bouquet
				self.addSubserviceToBouquet(self.bouquets[0][1])
				self.session.open(MessageBox, _("Service has been added to the favourites."), MessageBox.TYPE_INFO, timeout=5)

InfoBarSubserviceSelection.addSubserviceToBouquetCallback = addSubserviceToBouquetCallback

def addSubserviceToBouquet(self, dest):
	if isinstance(self.selectedSubservice[1], Subservice):
		#custom subservices
		self.servicelist.addServiceToBouquet(dest, eServiceReference(self.selectedSubservice[1].getRef()))
	else:
		self.servicelist.addServiceToBouquet(dest, self.selectedSubservice[1])
	if self.bsel:
		self.bsel.close(True)
	else:
		del self.selectedSubservice

InfoBarSubserviceSelection.addSubserviceToBouquet = addSubserviceToBouquet

def getAvailableSubservices(self, currentRef):
	#Read channels and groups from xml config file
	if not hasattr(self.session, "subserviceGroups"):
		self.session.subserviceGroups = readChannelsFromXml()
	subserviceGroups = self.session.subserviceGroups
	#Determine whether channel has subservices
	possibleSubservices = self.getPossibleSubservicesForCurrentChannel(currentRef, subserviceGroups)
	#Determine whether subservices are active
	activeSubservices = self.getActiveSubservicesForCurrentChannel(possibleSubservices)
	del subserviceGroups
	del possibleSubservices
	return activeSubservices

InfoBarSubserviceSelection.getAvailableSubservices = getAvailableSubservices

def readChannelsFromXml():
	subserviceGroups = []
	try:
		xmldataRaw = xml.dom.minidom.parse(XML_PATH).getElementsByTagName("options")
		xmldata = xmldataRaw[0].getElementsByTagName("channelgroup")
		for node in xmldata:
			subserviceGroup = SubserviceGroup()
			subserviceGroup.setName(node.getAttributeNode("name").nodeValue)
			notActiveShowName = node.getAttributeNode("notActiveShowName").nodeValue
			displayPattern = node.getAttributeNode("displayPattern").nodeValue
			channels = node.getElementsByTagName("channel")
			for channel in channels:
				name = channel.getElementsByTagName("name")[0].firstChild.nodeValue
				ref = channel.getElementsByTagName("ref")[0].firstChild.nodeValue
				if ref != "none":
					subserviceGroup.addSubservice(Subservice(name, ref, notActiveShowName, displayPattern))
			subserviceGroups.append(subserviceGroup)
	except:
		print ("[CustomSubservicesPlugin] XML config file not available or misconfigured!\n")
		del subserviceGroups[:]
	return subserviceGroups

def getPossibleSubservicesForCurrentChannel(self, currentRef, subserviceGroups):
	possibleSubservices =[]
	actualSubserviceGroup = None
	currentRefStr = currentRef.toString()
	for subserviceGroup in subserviceGroups:
		for channel in subserviceGroup.getSubservices():
			if channel.getRef() == currentRefStr:
				actualSubserviceGroup = subserviceGroup
				break
	if actualSubserviceGroup is not None:
		possibleSubservices = actualSubserviceGroup.getSubservices()
	return possibleSubservices

InfoBarSubserviceSelection.getPossibleSubservicesForCurrentChannel = getPossibleSubservicesForCurrentChannel

def getActiveSubservicesForCurrentChannel(self, possibleSubservices):
	activeSubservices = []
	epgCache = eEPGCache.getInstance()
	for subservice in possibleSubservices:
		#Query epgcache for current event on subservice
		#I...EventID
		#B...Beginn Time
		#D...Duration
		#C...Current Time
		#T...Title
		#S...Subtitle?
		#E...Description
		#R...Service Reference
		#N...Service Name
		#Default: 'IBDCTSERN'
		events = epgCache.lookupEvent(['BDTS', (subservice.getRef(), 0, -1)])
		#check whether events available
		if events is not None and len(events) == 1:
			#check whether channel is inactive
			event = events[0]
			title = event[2]
			subtitle = event[3]
			starttime = datetime.datetime.fromtimestamp(event[0]).strftime('%H:%M')
			endtime = datetime.datetime.fromtimestamp(event[0] + event[1]).strftime('%H:%M')
			if subservice.getNotActiveShowName() != str(subtitle):
				#option seems to be active --> prepare and add it
				subservice.setCurrentShowName(str(title))
				subservice.setCurrentShowTime(str(starttime) + " - " + str(endtime))
				activeSubservices.append(subservice)
		else:
			#add channel as option in unknown state
			subservice.setCurrentShowName("EPG nicht verfügbar")
			activeSubservices.append(subservice)
	return activeSubservices

InfoBarSubserviceSelection.getActiveSubservicesForCurrentChannel = getActiveSubservicesForCurrentChannel

### modified Service.getBoolean to activate/deactivate infobar subservices icon ######
@cached
def getBoolean(self):
	service = self.source.service
	info = service and service.info()
	if not info:
		return False
	if self.type == self.SUBSERVICES_AVAILABLE:
		#Determine whether channel has subservices
		ref = eServiceReference(str(info.getInfoString(iServiceInformation.sServiceref)))
		possibleSubservices = self.getPossibleSubservicesForCurrentChannel(ref, self.subserviceGroups)
		#Determine whether subservices are active
		activeSubservices = self.getActiveSubservicesForCurrentChannel(possibleSubservices)
		if activeSubservices is not None and len(activeSubservices) > 0:
			return True
		else:
			subservices = service.subServices()
			return subservices and subservices.getNumberOfSubservices() > 0
	else:
		return baseServiceInfo_getBoolean(self)

baseServiceInfo_getBoolean = None

def sessionstart(session, **kwargs):
	global baseServiceInfo_getBoolean
	if baseServiceInfo_getBoolean is None:
		print ("\n[CustomSubservicesPlugin] start\n")
		session.subserviceGroups = readChannelsFromXml()
		ServiceInfo.subserviceGroups = session.subserviceGroups
		baseServiceInfo_getBoolean = ServiceInfo.getBoolean
		ServiceInfo.getBoolean = getBoolean
		ServiceInfo.boolean = property(getBoolean)
		ServiceInfo.getPossibleSubservicesForCurrentChannel = getPossibleSubservicesForCurrentChannel
		ServiceInfo.getActiveSubservicesForCurrentChannel = getActiveSubservicesForCurrentChannel


def Plugins(**kwargs):
	return PluginDescriptor(
		name="Custom Subservice Selection Plugin",
		description="Switching subservices based on XML config",
		where=PluginDescriptor.WHERE_SESSIONSTART,
		fnc=sessionstart)
