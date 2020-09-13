from MenuList import MenuList
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT

def FindServiceControlEntryComponent(service, name):
	res = [
		(service, name),
		(eListboxPythonMultiContent.TYPE_TEXT, 80, 5, 300, 50, 0, RT_HALIGN_LEFT, name)
	]

	return res

class FindServiceControlListe(MenuList):
	def __init__(self, list, enableWrapAround = False):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		self.l.setFont(0, gFont("Regular", 20))
		self.l.setItemHeight(32)

	def etoggleSelectedLock(self):
		
		print ("self.l.getCurrentSelection():", self.l.getCurrentSelection())
		print ("self.l.getCurrentSelectionIndex():", self.l.getCurrentSelectionIndex())
		curSel = self.l.getCurrentSelection()
		#if curSel[0][2]:
		if curSel[0]:
		
			return curSel[0][0]
		else:
		
			return curSel[0][0]