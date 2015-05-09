# -*- coding: utf-8 -*-

class Subservice(object):
	__name = ""
	__ref = ""
	__currentShowName = "?"
	__currentShowTime = "?"
	__notActiveShowName = "?"
	__displayPattern = "title:time"
	
	def __init__(self, name, ref, notActiveShowName, displayPattern):
		self.setName(name)
		self.setRef(ref)
		self.setNotActiveShowName(notActiveShowName)
		self.setDisplayPattern(displayPattern)
			
	def getName(self):
		return self.__name
		
	def getRef(self):
		return self.__ref
		
	def getCurrentShowName(self):
		if self.__currentShowName == "":
			return "?"
		else:
			return self.__currentShowName
	
	def getCurrentShowTime(self):
		if self.__currentShowName == "":
			return "?"
		else:
			return self.__currentShowTime
	
	def getNotActiveShowName(self):
		if self.__notActiveShowName == "":
			return "?"
		else:
			return self.__notActiveShowName
	
	def getDisplayPattern(self):
		if self.__displayPattern == "":
			return "title:time"
		else:
			return self.__displayPattern
	
	def getDisplayString(self):
		displayString = ""
		displayLength = 65
		
		#default for epg not available
		if self.__currentShowName == "EPG nicht verfügbar":
			displayString += self.__name
			displayString += " ("
			displayString += self.__currentShowName
			displayString += ")"
			return displayString

		parts = self.__displayPattern.split('=')
		if len(parts) > 1:
			try:
				displayLength = int(parts[1])
			except:
				displayLength = 65

		parts = parts[0].split(':')
		
		if parts and len(parts) > 0:
			
			for part in parts:
				if part == "chn":
					displayString += self.__name
					displayString += " "
				elif part == "title":
					if "chn" in parts:
						displayLength = displayLength - len(self.__name) - 1
					if "time" in parts:
						displayLength = displayLength - 16
					if len(self.__currentShowName) > displayLength:
						displayString += self.__currentShowName[:displayLength-4]
						displayString += "... "
					else:
						displayString += self.__currentShowName
						displayString += " "
				elif part == "time":
					displayString += "("
					displayString += self.__currentShowTime
					displayString += ") "
					
			if len(displayString) < 1 or displayString == "":
				displayString = self.__currentShowName[:displayLength-19] + "... " + self.__currentShowTime
				
		else:
			displayString = self.__currentShowName[:displayLength-19] + "... " + self.__currentShowTime
			
		return displayString
	
	def setName(self, name):
		self.__name = str(name)
	
	def setRef(self, ref):
		self.__ref = str(ref)
		#DEBUG: print "Set ref to: " + str(self.__ref) + "\n"
		
	def setCurrentShowName(self, currentShowName):
		if currentShowName is None or currentShowName == "":
			self.__currentShowName = "?"
		else:
			self.__currentShowName = currentShowName
			
	def setCurrentShowTime(self, currentShowTime):
		if currentShowTime is None or currentShowTime == "":
			self.__currentShowTime = "title:time"
		else:
			self.__currentShowTime = currentShowTime
			
	
	def setNotActiveShowName(self, notActiveShowName):
		if notActiveShowName is None or notActiveShowName == "":
			self.__notActiveShowName = "?"
		else:
			self.__notActiveShowName = notActiveShowName
	
	def setDisplayPattern(self, displayPattern):
		if displayPattern is None or displayPattern == "":
			self.__displayPattern = "title:time"
		else:
			self.__displayPattern = displayPattern
	
	def isActive(self):
		if self.__currentShowName != "?" and self._currentShowName != self.__notActiveShowName:
			return True
		else:
			return False
	
	
