#from boxbranding import getMachineProcModel, getMachineBuild, getBoxType, getMachineName 
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.Button import Button
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MenuList import MenuList
from Components.Input import Input
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Components.Pixmap import Pixmap, MultiPixmap
from Components.config import *
from Components.ConfigList import ConfigListScreen
import Components.Harddisk
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
import os
from skin import parseColor
#from boxbranding import *
PLUGINVERSION = '1.00'
NFR4XBootImageChoose_Skin = '\n\t\t<screen name="NFR4XBootImageChoose_Client" position="center,center" size="902,380" title="NFR4XBoot - Client_Menu" >\n\t\t\t<widget name="label2" position="145,10" size="440,30" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t<widget name="label3" position="145,35" size="440,30" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t<widget name="label4" position="145,60" size="440,30" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t<widget name="label5" position="145,85" size="440,30" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t<widget name="label6" position="420,10" size="440,30" zPosition="1" halign="right" font="Regular;20" backgroundColor="#9f1313" foregroundColor="#00389416" transparent="1"/>\n\t\t\t<widget name="label7" position="420,35" size="440,30" zPosition="1" halign="right" font="Regular;20" backgroundColor="#9f1313" foregroundColor="#00389416" transparent="1"/>\n\t\t\t<widget name="label8" position="420,60" size="440,30" zPosition="1" halign="right" font="Regular;20" backgroundColor="#9f1313" foregroundColor="#00389416" transparent="1"/>\n\t\t\t<widget name="label9" position="420,85" size="440,30" zPosition="1" halign="right" font="Regular;20" backgroundColor="#9f1313" foregroundColor="#00389416" transparent="1"/>\n\t\t\t<widget name="label10" position="145,110" size="440,30" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t<widget name="label11" position="420,110" size="440,30" zPosition="1" halign="right" font="Regular;20" backgroundColor="#9f1313" foregroundColor="#00389416" transparent="1"/>\n\t\t\t<widget name="label1" position="25,145" size="840,22" zPosition="1" halign="center" font="Regular;18" backgroundColor="#9f1313" transparent="1"/>\n\t\t\t<widget name="device_icon" position="25,20" size="80,80" alphatest="on" />\n\t\t\t<widget name="free_space_progressbar" position="265,42" size="500,13" borderWidth="1" zPosition="3" />\n\t\t\t<widget name="config" position="25,180" size="840,150" scrollbarMode="showOnDemand"/>\n\t\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="10,340" size="150,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="260,340" size="150,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/yellow.png" position="520,340" size="150,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/blue.png" position="750,340" size="150,40" alphatest="on" />\n\t\t\t<widget name="key_red" position="5,340" zPosition="1" size="160,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_green" position="255,340" zPosition="1" size="160,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_yellow" position="515,340" zPosition="1" size="160,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t\t<widget name="key_blue" position="745,340" zPosition="1" size="160,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t</screen>'

class NFR4XBootImageChoose(Screen):

    def __init__(self, session):
        self.skin = NFR4XBootImageChoose_Skin
        Screen.__init__(self, session)
        self.list = []
        self.setTitle('NFR4XBoot %s - Client_Menu' % PLUGINVERSION)
        self['device_icon'] = Pixmap()
        self['free_space_progressbar'] = ProgressBar()
        self['linea'] = ProgressBar()
        self['config'] = MenuList(self.list)
        self['key_red'] = Label(_('Boot Image'))
        self['label2'] = Label(_('NFR4XBoot is running from:'))
        self['label3'] = Label(_('Used:'))
        self['label4'] = Label(_('Available:'))
        self['label7'] = Label('')
        self['label8'] = Label('')
        self['label10'] = Label(_('Number of installed images in NFR4XBoot:'))
        self['label11'] = Label('')
        self['label1'] = Label(_('Here is the list of installed images in Your STB. Please choose an image to boot.'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.boot,'back': self.close,})
        self.onShow.append(self.updateList)

    def updateList(self):
        self.list = []
        try:
            pluginpath = '/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot_client'
            f = open(pluginpath + '/.nfr4xboot_location', 'r')
            mypath = f.readline().strip()
            f.close()
        except:
            mypath = '/media/hdd'

        icon = 'dev_usb.png'
        if 'hdd' in mypath:
            icon = 'dev_hdd.png'
        icon = pluginpath + '/images/' + icon
        png = LoadPixmap(icon)
        self['device_icon'].instance.setPixmap(png)
        device = '/media/nfr4xboot'
        dev_free = dev_free_space = def_free_space_percent = ''
        rc = os.system('df > /tmp/ninfo.tmp')
        if fileExists('/tmp/ninfo.tmp'):
            f = open('/tmp/ninfo.tmp', 'r')
            for line in f.readlines():
                line = line.replace('part1', ' ')
                parts = line.strip().split()
                totsp = len(parts) - 1
                if parts[totsp] == device:
                    if totsp == 5:
                        dev_free = parts[1]
                        dev_free_space = parts[3]
                        def_free_space_percent = parts[4]
                    else:
                        dev_free = 'N/A   '
                        dev_free_space = parts[2]
                        def_free_space_percent = parts[3]
                    break

            f.close()
            os.remove('/tmp/ninfo.tmp')
        self.availablespace = dev_free_space[0:-3]
        perc = int(def_free_space_percent[:-1])
        self['free_space_progressbar'].setValue(perc)
        green = '#00389416'
        red = '#00ff2525'
        yellow = '#00ffe875'
        orange = '#00ff7f50'
        if perc < 30:
            color = green
        elif perc < 60:
            color = yellow
        elif perc < 80:
            color = orange
        else:
            color = red
        self['label7'].instance.setForegroundColor(parseColor(color))
        self['label8'].instance.setForegroundColor(parseColor(color))
        self['label11'].instance.setForegroundColor(parseColor(color))
        self['free_space_progressbar'].instance.setForegroundColor(parseColor(color))
        self.list.append('Flash')
        self['label7'].setText(def_free_space_percent)
        self['label8'].setText(dev_free_space[0:-3] + ' MB')
        mypath = '/media/nfr4xboot/NFR4XBootI/'
        try:
            myimages = os.listdir(mypath)
            for fil in myimages:
                if os.path.isdir(os.path.join(mypath, fil)):
                    self.list.append(fil)

        self['label11'].setText(str(len(self.list) - 1))
        self['config'].setList(self.list)

    def myclose(self):
        self.close()

    def myclose2(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        self.close()

    def boot(self):
        self.mysel = self['config'].getCurrent()
        if self.mysel:
            out = open('/media/nfr4xboot/NFR4XBootI/.nfr4xboot', 'w')
            out.write(self.mysel)
            out.close()
            os.system('rm /tmp/.nfr4xreboot')
            message = _('Are you sure you want to Boot Image:\n') + self.mysel + ' now ?'
            ybox = self.session.openWithCallback(self.boot2, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle(_('Boot Confirmation'))
        else:
            self.mysel

    def boot2(self, yesno):
        if yesno:
            os.system('touch /tmp/.nfr4xreboot')
            os.system('reboot -p')
        else:
            os.system('touch /tmp/.nfr4xreboot')
            self.session.open(MessageBox, _('Image will be booted on the next STB boot!'), MessageBox.TYPE_INFO)


    def up(self):
        self.list = []
        self['config'].setList(self.list)
        self.updateList()

    def up2(self):
        try:
            self.list = []
            self['config'].setList(self.list)
            self.updateList()
        except:
            print ' '

def main(session, **kwargs):
    f = open('/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot_client/.nfr4xboot_location', 'r')
    mypath = f.readline().strip()
    f.close()
    if not fileExists('/media/nfr4xboot'):
        os.mkdir('/media/nfr4xboot')
    cmd = 'mount ' + mypath + ' /media/nfr4xboot'
    os.system(cmd)
    f = open('/proc/mounts', 'r')
    for line in f.readlines():
        if line.find('/media/nfr4xboot') != -1:
            line = line[0:9]
            break

    cmd = 'mount ' + line + ' ' + mypath
    os.system(cmd)
    cmd = 'mount ' + mypath + ' /media/nfr4xboot'
    os.system(cmd)
    session.open(NFR4XBootImageChoose)

def menu(menuid, **kwargs):
    filename = '/etc/videomode2'
    if os.path.exists(filename):
        pass
    else: 
        f = open(filename, 'w')
        f.write("576i")
        f.close()

    if menuid == 'mainmenu':
        return [(_('NFR4X MultiBoot_Client'),
          main,
          'nfr4x_boot',
          1)]
    return []



from Plugins.Plugin import PluginDescriptor

def Plugins(**kwargs):
    return [PluginDescriptor(name='NFR4XBoot', description='NFR4X MultiBoot_Client', where=PluginDescriptor.WHERE_MENU, fnc=menu), PluginDescriptor(name='NFR4XBoot', description=_('E2 Light Multiboot'), icon='plugin_icon.png', where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)]
