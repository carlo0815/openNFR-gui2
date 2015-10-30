from Components.ActionMap import ActionMap
from Components.config import config
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.SystemInfo import SystemInfo
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_SKIN, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
import xml.etree.cElementTree
from __init__ import _
import inspect

class UserMainMenuConfig(Screen):

    def __init__(self, session, plugin_path, args = 0):
        Screen.__init__(self, session)
        self.skin_path = plugin_path
        self.session = session
        self.title = _('openNFR user main menu')
        try:
            self['title'] = StaticText(self.title)
        except:
            print 'self["title"] was not found in skin'

        self.entrylist = []
        self.addlist = []
        templist = config.plugins.infopanel_usermenus.value
        for tempitem in templist.split(','):
            self.addlist.append(tempitem)

        self['menu'] = List(self.entrylist)
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Save'))
        self['key_yellow'] = StaticText(_('Defaults'))
        self['shortcuts'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keyOk,
         'cancel': self.keyCancel,
         'green': self.keySave,
         'yellow': self.keyYellow}, -2)
        self.statusok = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'Extensions/Infopanel/images/installed.png'))
        self.statusremove = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'Extensions/Infopanel/images/remove.png'))
        nodetype = 'plugin'
        id_list = []
        for l in plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO]):
            l.id = l.name.lower().replace(' ', '_')
            if len(inspect.getargspec(l.__call__).args) == 1:
                if l.id not in id_list:
                    nodeweight = 10
                    id_list.append(l.id)
                    if l.id in self.addlist:
                        statuspng = self.statusok
                    else:
                        statuspng = self.statusremove
                    self.entrylist.append((_(l.name),
                     l.id,
                     statuspng,
                     nodeweight,
                     nodetype))

        self['menu'].setList(self.entrylist)

    def keyOk(self):
        menuentryselection = self['menu'].getCurrent()[1]
        current_index = self['menu'].getIndex()
        current_text = self['menu'].getCurrent()[0]
        weight = self['menu'].getCurrent()[3]
        nodetype = self['menu'].getCurrent()[4]
        if nodetype == 'plugin':
            if menuentryselection in self.addlist:
                self.addlist.remove(menuentryselection)
                self.entrylist[current_index] = (current_text,
                 menuentryselection,
                 self.statusremove,
                 weight,
                 nodetype)
            else:
                self.addlist.append(menuentryselection)
                self.entrylist[current_index] = (current_text,
                 menuentryselection,
                 self.statusok,
                 weight,
                 nodetype)
        self['menu'].updateList(self.entrylist)

    def keySave(self):
        newconfigvalue = ''
        for tempitem in self.addlist:
            newconfigvalue = newconfigvalue + tempitem + ','

        newconfigvalue = newconfigvalue.strip(',')
        config.plugins.infopanel_usermenus.value = newconfigvalue
        config.plugins.infopanel_usermenus.save()
        self.close()

    def keyYellow(self):
        config.plugins.infopanel_usermenus.value = ''
        config.plugins.infopanel_usermenus.save()
        self.close()

    def keyCancel(self):
        self.close()