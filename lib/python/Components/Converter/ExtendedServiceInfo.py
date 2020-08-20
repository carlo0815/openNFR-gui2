# -*- coding: utf-8 -*-
from Components.config import config, ConfigText
from Components.Converter.Converter import Converter
from Components.Element import cached
from ServiceReference import ServiceReference
from enigma import eServiceCenter, eServiceReference, iServiceInformation, iPlayableService
from string import upper
import gettext
from xml.etree.cElementTree import parse

class ExtendedServiceInfo(Converter, object):
	TUNERINFO = 0
	SERVICENAME = 1
	SERVICENUMBER = 2
	ORBITALPOSITION = 3
	FROMCONFIG = 4
	SATNAME = 5
	PROVIDER = 6	
	ALL = 7

	def __init__(self, type):
		Converter.__init__(self, type)
		self.list = []
        	self.satNames = {}
        	self.readSatXml()
        	self.getLists()
        	self.getList()
		if type == "TunerInfo":
			self.type = self.TUNERINFO
		elif type == "ServiceName":
			self.type = self.SERVICENAME
		elif type == "ServiceNumber":
			self.type = self.SERVICENUMBER
		elif type == "OrbitalPosition":
			self.type = self.ORBITALPOSITION
		elif type == "Config":
			self.type = self.FROMCONFIG
		elif type == 'SatName':
			self.type = self.SATNAME
		elif type == 'Provider':
			self.type = self.PROVIDER		
		else:
			self.type = self.ALL

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""
		
		text = ""
		
		tunerinfo = self.getTunerInfo(service)
		orbital = self.getOrbitalPosition(service)
		name = info.getName().replace('\xc2\x86', '').replace('\xc2\x87', '')
		number = self.getServiceNumber(name)
		satName = self.satNames.get(orbital, orbital)

		if self.type == self.TUNERINFO:
			if config.usage.setup_level.value == "expert":
				text = tunerinfo
			else:
				text = ""
				
		elif self.type == self.SERVICENAME:
			text = name
		elif self.type == self.SERVICENUMBER:
			if config.usage.setup_level.value == "expert":
				text = number
			else:
				text = ""
			
		elif self.type == self.ORBITALPOSITION:
			if config.usage.setup_level.value == "expert":
				text = orbital
			else:
				text = ""
		elif self.type == self.SATNAME:
			text = satName
		elif self.type == self.PROVIDER:
			text = info.getInfoString(iServiceInformation.sProvider)				
		elif self.type == self.FROMCONFIG:
			if config.plugins.ExtendedServiceInfo.showServiceNumber.value == True:
				text = "%s. %s" % (number, name)
			else:
				text = name
			if config.plugins.ExtendedServiceInfo.showOrbitalPosition.value == True and orbital != "":
				text = "%s (%s)" % (text, orbital)
		else:
			text = "%s. %s" % (number, name)
			if orbital != "":
				text = "%s (%s) " % (text, orbital)
		
		return text

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)

	def getServiceNumber(self, name):
		if name in self.list:
			for idx in list(range(1, len(self.list))):
				if name == self.list[idx-1]:
					return str(idx)
		else:
			return ""

	def getList(self):
		serviceHandler = eServiceCenter.getInstance()
		services = serviceHandler.list(eServiceReference('1:134:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
		bouquets = services and services.getContent("SN", True)
		
		for bouquet in bouquets:
			services = serviceHandler.list(eServiceReference(bouquet[0]))
			channels = services and services.getContent("SN", True)
			
			for channel in channels:
				if not channel[0].startswith("1:64:"): # Ignore marker
					self.list.append(channel[1].replace('\xc2\x86', '').replace('\xc2\x87', ''))
					
	def getLists(self):
		self.tv_list = self.getListFromRef(eServiceReference('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
		self.radio_list = self.getListFromRef(eServiceReference('1:7:2:0:0:0:0:0:0:0:(type == 2) FROM BOUQUET "bouquets.radio" ORDER BY bouquet'))
					

	def getOrbitalPosition(self, service):
		feinfo = service.frontendInfo()
		orbital = 0
		if feinfo is not None:
			frontendData = feinfo and feinfo.getAll(True)
			if frontendData is not None:
				if "tuner_type" in frontendData:
					if frontendData["tuner_type"] == "DVB-S":
						orbital = int(frontendData["orbital_position"])
		
		if orbital > 1800:
			return str((float(3600 - orbital))/10.0) + "Â°W"
		elif orbital > 0:
			return str((float(orbital))/10.0) + "Â°E"
		return ""

	def getTunerInfo(self, service):
		tunerinfo = ""
		feinfo = (service and service.frontendInfo())
		ar_fec = ["Auto", "1/2", "2/3", "3/4", "5/6", "7/8", "3/5", "4/5", "8/9", "9/10", "None"]
		ar_pol = ["H", "V", "CL", "CR"]
		if (feinfo is not None):
			frontendData = (feinfo and feinfo.getAll(True))
			if (frontendData is not None):
				if (frontendData.get("tuner_type") == "DVB-C"):
					frequency = (str((frontendData.get("frequency") / 1000)) + " MHz")
					symbolrate = str(int(frontendData.get("symbol_rate", 0) / 1000))
					polarisation_i = 0
					tunerinfo = (frequency + " " + symbolrate)
				if (frontendData.get("tuner_type") == "DVB-T"):
					frequency = (str((frontendData.get("frequency") / 1000)) + " MHz")
					symbolrate = str(int(frontendData.get("symbol_rate", 0) / 1000))
					polarisation_i = 0
					tunerinfo = (frequency + " " + symbolrate)
				if (frontendData.get("tuner_type") == "DVB-S"):
					frequency = (str((frontendData.get("frequency") / 1000)) + " MHz")
					symbolrate = str(int(frontendData.get("symbol_rate", 0) / 1000))
					polarisation_i = frontendData.get("polarization")
					fec_i = frontendData.get("fec_inner")
					tunerinfo = (frequency + " " + ar_pol[polarisation_i] + " " + ar_fec[fec_i] + " " + symbolrate)
				return tunerinfo
		else:
			return ""
			
	def getListFromRef(self, ref):
		list = []
		serviceHandler = eServiceCenter.getInstance()
		services = serviceHandler.list(ref)
		bouquets = services and services.getContent('SN', True)
		for bouquet in bouquets:
			services = serviceHandler.list(eServiceReference(bouquet[0]))
			channels = services and services.getContent('SN', True)
			for channel in channels:
                		if not channel[0].startswith('1:64:'):
                    			list.append(channel[1].replace('\xc2\x86', '').replace('\xc2\x87', ''))

        	return list

	def readSatXml(self):
        	satXml = parse('/etc/tuxbox/satellites.xml').getroot()
        	if satXml is not None:
            		for sat in satXml.findall('sat'):
                		name = sat.get('name') or None
                		position = sat.get('position') or None
                		if name is not None and position is not None:
                    			position = '%s.%s' % (position[:-1], position[-1:])
                    			if position.startswith('-'):
                        			position = '%sW' % position[1:]
                    			else:
                        			position = '%sE' % position
                    			if position.startswith('.'):
                        			position = '0%s' % position
                    			self.satNames[position] = name

        	return	
