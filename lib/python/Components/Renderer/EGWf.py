# This converter base on Spaze Team weather converter.

from Renderer import Renderer
from enigma import ePixmap, eEnv
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Components.config import ConfigText, config, ConfigSubsection

class EGWf(Renderer):

    def __init__(self):
        Renderer.__init__(self)
        self.path = 'picon'
        self.nameCache = {}
        self.pngname = ''

    def applySkin(self, desktop, parent):
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == 'path':
                self.path = value
            else:
                attribs.append((attrib, value))

        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap

    def changed(self, what):
        if self.instance:
            pngname = 'xxx'
            if what[0] != self.CHANGED_CLEAR:
                pngname = self.source.text
                self.nameCache[pngname] = pngname
            if self.pngname != pngname:
                if pngname == '':
                    self.instance.hide()
                else:
                    self.instance.show()
                    self.instance.setPixmapFromFile(pngname)
                self.pngname = pngname
