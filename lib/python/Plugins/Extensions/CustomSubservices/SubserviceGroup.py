# -*- coding: utf-8 -*-

from Subservice import Subservice

class SubserviceGroup(object):
	__name = ""
	__subservices = []
	
	def __init__(self):
		self.__channels = []
		
	def getName(self):
		return self.__name
	
	def getSubservices(self):
		return self.__channels
		
	def setName(self, name):
		self.__name = name
		
	def addSubservice(self, subservice):
		self.__channels.append(subservice)
	
	def removeSubservice(self, ref):
		index = i = -1
		for subservice in self.__subservice:
			i = i + 1
			if subservice.getRef() == ref:
				index = i
		
		if index != -1:
			self.__subservices.remove(self.__subservices[index])
					
	def clearSubservices(self):
		del self.__subservices[:]

		
	