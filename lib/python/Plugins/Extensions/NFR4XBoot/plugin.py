from boxbranding import getMachineProcModel, getMachineBuild, getBoxType, getMachineName, getImageDistro, getMachineBrand, getImageFolder, getMachineRootFile, getImageArch  
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.Setup import Setup
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
PLUGINVERSION = '1.00'
NFR4XBootInstallation_Skin = '\n\t\t<screen name="NFR4XBootInstallation" position="center,center" size="902,380" title="NFR4XBoot - Installation" >\n\t\t      <widget name="label1" position="10,10" size="840,30" zPosition="1" halign="center" font="Regular;25" backgroundColor="#9f1313" transparent="1"/>\n\t\t      <widget name="label2" position="10,80" size="840,290" zPosition="1" halign="center" font="Regular;20" backgroundColor="#9f1313" transparent="1"/>\n\t\t      <widget name="config" position="10,160" size="840,200" scrollbarMode="showOnDemand" transparent="1"/>\n\t\t      <ePixmap pixmap="skin_default/buttons/red.png" position="10,290" size="140,40" alphatest="on" />\n\t\t      <ePixmap pixmap="skin_default/buttons/green.png" position="150,290" size="140,40" alphatest="on" />\n\t\t      <ePixmap pixmap="skin_default/buttons/blue.png" position="300,290" size="140,40" alphatest="on" />\n\t\t      <widget name="key_red" position="10,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t      <widget name="key_green" position="150,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t      <widget name="key_blue" position="300,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t</screen>'
NFR4XBootImageChoose_Skin = '\n\t\t<screen name="NFR4XBootImageChoose" position="center,center" size="902,380" title="NFR4XBoot - Menu">\n\t\t\t<widget name="label2" position="145,10" size="440,30" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="label3" position="145,35" size="440,30" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="label4" position="145,60" size="440,30" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="label5" position="145,85" size="440,30" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="label6" position="420,10" size="440,30" zPosition="1" halign="right" font="Regular;20" backgroundColor="#9f1313" foregroundColor="#00389416" transparent="1" />\n\t\t\t<widget name="label7" position="420,35" size="440,30" zPosition="1" halign="right" font="Regular;20" backgroundColor="#9f1313" foregroundColor="#00389416" transparent="1" />\n\t\t\t<widget name="label8" position="420,60" size="440,30" zPosition="1" halign="right" font="Regular;20" backgroundColor="#9f1313" foregroundColor="#00389416" transparent="1" />\n\t\t\t<widget name="label9" position="420,85" size="440,30" zPosition="1" halign="right" font="Regular;20" backgroundColor="#9f1313" foregroundColor="#00389416" transparent="1" />\n\t\t\t<widget name="label10" position="145,110" size="440,30" zPosition="1" font="Regular;20" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="label11" position="420,110" size="440,30" zPosition="1" halign="right" font="Regular;20" backgroundColor="#9f1313" foregroundColor="#00389416" transparent="1" />\n\t\t\t<widget name="label1" position="25,145" size="840,22" zPosition="1" halign="center" font="Regular;18" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="device_icon" position="25,20" size="80,80" alphatest="on" />\n\t\t\t<widget name="free_space_progressbar" position="265,42" size="500,13" borderWidth="1" zPosition="3" />\n\t\t\t<widget name="config" position="25,180" size="840,150" scrollbarMode="showOnDemand" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="10,340" size="150,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="185,340" size="150,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/yellow.png" position="360,340" size="150,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/blue.png" position="535,340" size="150,40" alphatest="on" />\n\t\t\t<widget name="key_red" position="5,center" zPosition="1" size="160,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_green" position="180,340" zPosition="1" size="160,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_yellow" position="355,340" zPosition="1" size="160,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t\t<widget name="key_blue" position="530,340" zPosition="1" size="160,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_menu" position="705,340" zPosition="1" size="160,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" /><ePixmap pixmap="skin_default/buttons/menu.png" position="710,340" size="150,40" alphatest="on" /></screen>'
NFR4XBootImageInstall_Skin = '\n\t\t    <screen name="NFR4XBootImageInstall" position="center,center" size="770,340" title="NFR4XBoot - Image Installation" >\n\t\t\t      <widget name="config" position="10,10" size="750,220" scrollbarMode="showOnDemand" transparent="1"/>\n\t\t\t      <ePixmap pixmap="skin_default/buttons/red.png" position="10,290" size="140,40" alphatest="on" />\n\t\t\t      <ePixmap pixmap="skin_default/buttons/green.png" position="150,290" size="140,40" alphatest="on" />\n\t\t\t      <ePixmap pixmap="skin_default/buttons/yellow.png" position="290,290" size="140,40" alphatest="on" />\n\t\t\t      <widget name="HelpWindow" position="330,310" zPosition="5" size="1,1" transparent="1" alphatest="on" />      \n\t\t\t      <widget name="key_red" position="10,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t      <widget name="key_green" position="150,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t      <widget name="key_yellow" position="290,290" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t    </screen>'

def Freespace(dev):
    statdev = os.statvfs(dev)
    space = statdev.f_bavail * statdev.f_frsize / 1024
    print '[NFR4XBoot] Free space on %s = %i kilobytes' % (dev, space)
    return space


class NFR4XBootInstallation(Screen):

    def __init__(self, session):
        self.skin = NFR4XBootInstallation_Skin
        Screen.__init__(self, session)
        self.list = []
        self['config'] = MenuList(self.list)
        self['key_red'] = Label(_('Install'))
        self['key_green'] = Label(_('Cancel'))
        self['key_blue'] = Label(_('Devices Panel'))
        self['label1'] = Label(_('Welcome to NFR4XBoot %s MultiBoot Plugin installation.') % PLUGINVERSION)
        self['label2'] = Label(_('Here is the list of mounted devices in Your STB\n\nPlease choose a device where You would like to install NFR4XBoot:'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.install,
         'green': self.close,
         'back': self.close,
         'blue': self.devpanel})
        self.updateList()

    def updateList(self):
        myusb, myhdd, mymmc = ('', '', '')
        myoptions = []
        if fileExists('/proc/mounts'):
            fileExists('/proc/mounts')
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/media/usb') != -1:
                    myusb = '/media/usb/'
                    continue
                if line.find('/media/mmc') != -1:
                    mymmc = '/media/mmc/'
                    continue
                if line.find('/hdd') != -1:
                    myhdd = '/media/hdd/'
                    continue

            f.close()
        else:
            self['label2'].setText(_('Sorry it seems that there are not Linux formatted devices mounted on your STB. To install NFR4XBoot you need a Linux formatted part1 device. Click on the blue button to open NFR Devices Panel'))
            fileExists('/proc/mounts')
        if myusb:
            self.list.append(myusb)
        else:
            myusb
        if mymmc:
            self.list.append(mymmc)
        else:
            mymmc
        if myhdd:
            myhdd
            self.list.append(myhdd)
        else:
            myhdd
        self['config'].setList(self.list)

    def devpanel(self):
        try:
			####ersetzen mit unseren Mountmanager####
            from Screens.HddSetup import HddSetup
            self.session.open(HddSetup)
        except:
            self.session.open(MessageBox, _('You are not running NFR Image. You must mount devices Your self.'), MessageBox.TYPE_INFO)

    def myclose(self):
        self.close()

    def myclose2(self, message):
        self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
        os.system('reboot -p')
        self.close()

    def checkReadWriteDir(self, configele):
        import os.path
        import Components.Harddisk
        supported_filesystems = frozenset(('ext4', 'ext3', 'ext2', 'nfs'))
        candidates = []
        mounts = Components.Harddisk.getProcMounts()
        for partition in Components.Harddisk.harddiskmanager.getMountedPartitions(False, mounts):
            if partition.filesystem(mounts) in supported_filesystems:
                candidates.append((partition.description, partition.mountpoint))

        if candidates:
            locations = []
            for validdevice in candidates:
                locations.append(validdevice[1])

            if Components.Harddisk.findMountPoint(os.path.realpath(configele)) + '/' in locations or Components.Harddisk.findMountPoint(os.path.realpath(configele)) in locations:
                if fileExists(configele, 'w'):
                    return True
                else:
                    dir = configele
                    self.session.open(MessageBox, _('The directory %s is not writable.\nMake sure you select a writable directory instead.') % dir, type=MessageBox.TYPE_ERROR)
                    return False
            else:
                dir = configele
                self.session.open(MessageBox, _('The directory %s is not a EXT2, EXT3, EXT4 or NFS partition.\nMake sure you select a valid partition type.') % dir, type=MessageBox.TYPE_ERROR)
                return False
        else:
            dir = configele
            self.session.open(MessageBox, _('The directory %s is not a EXT2, EXT3, EXT4 or NFS partition.\nMake sure you select a valid partition type.') % dir, type=MessageBox.TYPE_ERROR)
            return False

    def install(self):
        check = False
        if fileExists('/proc/mounts'):
            fileExists('/proc/mounts')
            f = open('/proc/mounts', 'r')
            for line in f.readlines():
                if line.find('/media/usb') != -1:
                    check = True
                    continue
                if line.find('/media/mmc') != -1:
                    check = True
                    continue
                if line.find('/hdd') != -1:
                    check = True
                    continue

            f.close()
        else:
            fileExists('/proc/mounts')
        if check == False:
            self.session.open(MessageBox, _('Sorry, there is not any connected devices in your STB.\nPlease connect HDD or USB to install NFR4X Multiboot!'), MessageBox.TYPE_INFO)
        else:
            fileExists('/boot/dummy')
            self.mysel = self['config'].getCurrent()
            if self.checkReadWriteDir(self.mysel):
                message = _('Do You really want to install NFR4XBoot in:\n ') + self.mysel + '?'
                ybox = self.session.openWithCallback(self.install2, MessageBox, message, MessageBox.TYPE_YESNO)
                ybox.setTitle(_('Install Confirmation'))
            else:
                self.close()
                
    def install2(self, yesno):
	config.NFRBootmanager = ConfigSubsection()
	config.NFRBootmanager.bootmanagertimeout = ConfigSelection([('5',_("5 seconds")),('10',_("10 seconds")),('15',_("15 seconds")),('20',_("20 seconds")),('30',_("30 seconds"))], default='5')	
        if getMachineBuild() in ("u5", "u51", "u52", "u53", "u5pvr", "sf8008"):
            self.install3(False)
        elif yesno:
            self.MACHINEBRAND = getMachineBrand()
            if  self.MACHINEBRAND == "Vu+":
                os.system("opkg install packagegroup-base-nfs")	
            message = _('Do you want to use Bootmanager by booting?\nBox will reboot after choice ')
            ybox = self.session.openWithCallback(self.install3, MessageBox, message, MessageBox.TYPE_YESNO)
            ybox.setTitle(_('Install Confirmation'))
        else:
            self.session.open(MessageBox, _('Installation aborted !'), MessageBox.TYPE_INFO)                

    def install3(self, yesno):
        print "yesno:", yesno
        if yesno:
            cmd2 = 'mkdir /media/nfr4xboot;mount ' + self.mysel + ' /media/nfr4xboot'
            os.system(cmd2)
            if fileExists('/proc/mounts'):
                fileExists('/proc/mounts')
                f = open('/proc/mounts', 'r')
                for line in f.readlines():
                    if line.find(self.mysel):
		        mntdev = line.split(' ')[0]
                f.close()
                mntid = os.system('blkid -s UUID -o value ' + mntdev + '>/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/bin/install')
                os.system("mv /etc/fstab /etc/fstab1")
                os.system("grep -v  /media/nfr4xboot /etc/fstab1 > /etc/fstab")
                os.system("rm /etc/fstab1")
                os.system('blkid -s UUID -o value ' + mntdev + '>/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/bin/install')
                fstabuuid = os.popen('blkid -s UUID -o value ' + mntdev).read()
                fstabuuidwrite = 'UUID=' + fstabuuid.strip() + '        /media/nfr4xboot        auto        defaults	       1        1'
                fileHandle = open ('/etc/fstab', 'a')
                fileHandle.write(fstabuuidwrite)
                fileHandle.close()                
            cmd = 'mkdir ' + self.mysel + 'NFR4XBootI;mkdir ' + self.mysel + 'NFR4XBootUpload'
            os.system(cmd)
            os.system('cp /sbin/nfr4x_multiboot /sbin/nfr4xinit')
            os.system('chmod 777 /sbin/nfr4xinit;chmod 777 /sbin/init;ln -sfn /sbin/nfr4xinit /sbin/init')
            os.system('mv /etc/init.d/volatile-media.sh /etc/init.d/volatile-media.sh.back')
            out3 = open('/media/nfr4xboot/NFR4XBootI/.timer', 'w')
            out3.write(config.NFRBootmanager.bootmanagertimeout.value)
            out3.close()	
            out2 = open('/media/nfr4xboot/NFR4XBootI/.nfr4xboot', 'w')
            out2.write('Flash')
            out2.close()
            out = open('/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/.nfr4xboot_location', 'w')
            out.write(self.mysel)
            out.close()
            os.system('cp /usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/.nfr4xboot_location /etc/nfr4x/')
            image = getImageDistro()
            if fileExists('/etc/image-version'):
                if 'build' not in image:
                    f = open('/etc/image-version', 'r')
                    for line in f.readlines():
                        if 'build=' in line:
                            image = image + ' build ' + line[6:-1]
                            open('/media/nfr4xboot/NFR4XBootI/.Flash', 'w').write(image)
                            break

                    f.close()
            self.myclose2(_('NFR4XBoot has been installed succesfully!'))
        else:
            cmd2 = 'mkdir /media/nfr4xboot;mount ' + self.mysel + ' /media/nfr4xboot'
            os.system(cmd2)
            if fileExists('/proc/mounts'):
                fileExists('/proc/mounts')
                f = open('/proc/mounts', 'r')
                for line in f.readlines():
                    if line.find(self.mysel):
		        mntdev = line.split(' ')[0]
                f.close()
                mntid = os.system('blkid -s UUID -o value ' + mntdev + '>/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/bin/install')
                os.system("mv /etc/fstab /etc/fstab1")
                os.system("grep -v  /media/nfr4xboot /etc/fstab1 > /etc/fstab")
                os.system("rm /etc/fstab1")
                os.system('blkid -s UUID -o value ' + mntdev + '>/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/bin/install')
                fstabuuid = os.popen('blkid -s UUID -o value ' + mntdev).read()
                fstabuuidwrite = 'UUID=' + fstabuuid.strip() + '        /media/nfr4xboot        auto        defaults	       1        1'
                fileHandle = open('/etc/fstab', 'a')
                fileHandle.write(fstabuuidwrite)
                fileHandle.close()
            cmd = 'mkdir ' + self.mysel + 'NFR4XBootI;mkdir ' + self.mysel + 'NFR4XBootUpload'
            os.system(cmd)
            os.system('cp /usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/bin/nfr4xinitnoboot /sbin/nfr4xinit')
            os.system('chmod 777 /sbin/nfr4xinit;chmod 777 /sbin/init;ln -sfn /sbin/nfr4xinit /sbin/init')
            os.system('mv /etc/init.d/volatile-media.sh /etc/init.d/volatile-media.sh.back')
            out2 = open('/media/nfr4xboot/NFR4XBootI/.nfr4xboot', 'w')
            out2.write('Flash')
            out2.close()
            out = open('/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/.nfr4xboot_location', 'w')
            out.write(self.mysel)
            out.close()
            os.system('cp /usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/.nfr4xboot_location /etc/nfr4x/')
            image = getImageDistro()
            if fileExists('/etc/image-version'):
                if 'build' not in image:
                    f = open('/etc/image-version', 'r')
                    for line in f.readlines():
                        if 'build=' in line:
                            image = image + ' build ' + line[6:-1]
                            open('/media/nfr4xboot/NFR4XBootI/.Flash', 'w').write(image)
                            break

                    f.close()
            self.myclose2(_('NFR4XBoot has been installed succesfully, and Box rebooting now!'))

class NFR4XBootImageChoose(Screen):

    def __init__(self, session):
        self.skin = NFR4XBootImageChoose_Skin
        Screen.__init__(self, session)
        self.list = []
        self.setTitle('NFR4XBoot %s - Menu' % PLUGINVERSION)
        self['device_icon'] = Pixmap()
        self['free_space_progressbar'] = ProgressBar()
        self['linea'] = ProgressBar()
        self['config'] = MenuList(self.list)
        self['key_red'] = Label(_('Boot Image'))
        self['key_green'] = Label(_('Install Image'))
        self['key_yellow'] = Label(_('Remove Image '))
        self['key_blue'] = Label(_('Uninstall'))
        self['key_menu'] = Label(_('Bootsetup'))        
        self['label2'] = Label(_('NFR4XBoot is running from:'))
        self['label3'] = Label(_('Used:'))
        self['label4'] = Label(_('Available:'))
        self['label5'] = Label(_('NFR4XBoot is running image:'))
        self['label6'] = Label('')
        self['label7'] = Label('')
        self['label8'] = Label('')
        self['label9'] = Label('')
        self['label10'] = Label(_('Number of installed images in NFR4XBoot:'))
        self['label11'] = Label('')
        self['label1'] = Label(_('Here is the list of installed images in Your STB. Please choose an image to boot.'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions', 'MenuActions'], {'red': self.boot,
         'green': self.install,
         'yellow': self.remove,
         'blue': self.advanced,
         'menu': self.bootsetup,         
         'back': self.close})
        self.onShow.append(self.updateList)
        
    def bootsetup(self):
        menulist = []
        if getMachineBuild() not in ("u5", "u51", "u52", "u53", "u5pvr", "sf8008"):
            menulist.append((_('Use Bootmanager by Booting'), 'withnfr4xboot'))
            menulist.append((_('Boot without Bootmanager'), 'withoutnfr4xboot'))
	    menulist.append((_('Setup Bootmanagertimeout'), 'bootmanagertimeout'))
        else:
            menulist.append((_('Boot without Bootmanager'), 'withoutnfr4xboot'))	
        self.session.openWithCallback(self.menuBootsetupCallback, ChoiceBox, title=_('What would You like to do ?'), list=menulist)
    def menuBootsetupCallback(self, choice):
	config.NFRBootmanager = ConfigSubsection()
	config.NFRBootmanager.bootmanagertimeout = ConfigSelection([('5',_("5 seconds")),('10',_("10 seconds")),('15',_("15 seconds")),('20',_("20 seconds")),('30',_("30 seconds"))], default='5')	
        self.show()
        if choice is None:
            return
        else:
            if choice[1] == 'withnfr4xboot':
                cmd0 = 'cp /sbin/nfr4x_multiboot /sbin/nfr4xinit'
                cmd1 = 'chmod 777 /sbin/nfr4xinit;chmod 777 /sbin/init;ln -sfn /sbin/nfr4xinit /sbin/init'
                self.session.openWithCallback(self.close, Console, _('NFR4XBoot work with Bootmanager by Booting!'), [cmd0, cmd1])
            if choice[1] == 'withoutnfr4xboot':
                cmd0 = 'cp /usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/bin/nfr4xinitnoboot /sbin/nfr4xinit'
                cmd1 = 'chmod 777 /sbin/nfr4xinit;chmod 777 /sbin/init;ln -sfn /sbin/nfr4xinit /sbin/init'
                self.session.openWithCallback(self.updateList, Console, _('NFR4XBoot work without Bootmanager by Booting!'), [cmd0, cmd1])
            if choice[1] == 'bootmanagertimeout':
                self.session.openWithCallback(self.setupDone, Setup, 'bootmanagertimeout', 'Extensions/Infopanel')
	    return 

    def setupDone(self, test=None):
	if config.NFRBootmanager.bootmanagertimeout == '':
            config.NFRBootmanager.bootmanagertimeout = defaultprefix
            config.NFRBootmanager.bootmanagertimeout.save()
            out3 = open('/media/nfr4xboot/NFR4XBootI/.timer', 'w')
            out3.write(config.NFRBootmanager.bootmanagertimeout.value)
            out3.close()            
        else:
            config.NFRBootmanager.bootmanagertimeout.save()
            out3 = open('/media/nfr4xboot/NFR4XBootI/.timer', 'w')
            out3.write(config.NFRBootmanager.bootmanagertimeout.value)
            out3.close()   

    def updateList(self):
        self.list = []
        try:
            pluginpath = '/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot'
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
        self['label6'].instance.setForegroundColor(parseColor(color))
        self['label7'].instance.setForegroundColor(parseColor(color))
        self['label8'].instance.setForegroundColor(parseColor(color))
        self['label9'].instance.setForegroundColor(parseColor(color))
        self['label11'].instance.setForegroundColor(parseColor(color))
        self['free_space_progressbar'].instance.setForegroundColor(parseColor(color))
        try:
            f2 = open('/media/nfr4xboot/NFR4XBootI/.nfr4xboot', 'r')
            mypath2 = f2.readline().strip()
            f2.close()
        except:
            mypath2 = 'Flash'

        if mypath2 == 'Flash':
            image = getImageDistro()
            if fileExists('/etc/image-version'):
                if 'build' not in image:
                    f = open('/etc/image-version', 'r')
                    for line in f.readlines():
                        if 'build=' in line:
                            image = image + ' build ' + line[6:-1]
                            open('/media/nfr4xboot/NFR4XBootI/.Flash', 'w').write(image)
                            break

                    f.close()
        elif fileExists('/media/nfr4xboot/NFR4XBootI/.Flash'):
            f = open('/media/nfr4xboot/NFR4XBootI/.Flash', 'r')
            image = f.readline().strip()
            f.close()
        image = ' [' + image + ']'
        self.list.append('Flash' + image)
        self['label6'].setText(mypath)
        self['label7'].setText(def_free_space_percent)
        self['label8'].setText(dev_free_space[0:-3] + ' MB')
        self['label9'].setText(mypath2)
        mypath = '/media/nfr4xboot/NFR4XBootI/'
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
            message = _('Are you sure you want to Boot Image:\n') + self.mysel + ' ?'
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

    def remove(self):
        self.mysel = self['config'].getCurrent()
        if self.mysel:
            f = open('/media/nfr4xboot/NFR4XBootI/.nfr4xboot', 'r')
            mypath = f.readline().strip()
            f.close()
            try:
                if mypath == self.mysel:
                    self.session.open(MessageBox, _('Sorry you cannot delete the image, is currently booted from or select for next booting'), MessageBox.TYPE_INFO, 4)
                if self.mysel.startswith('Flash'):
                    self.session.open(MessageBox, _('Sorry you cannot delete Flash image'), MessageBox.TYPE_INFO, 4)
                else:
                    out = open('/media/nfr4xboot/NFR4XBootI/.nfr4xboot', 'w')
                    out.write('Flash')
                    out.close()
                    message = _('Are you sure you want to delete Image:\n ') + self.mysel + ' ?'
                    ybox = self.session.openWithCallback(self.remove2, MessageBox, message, MessageBox.TYPE_YESNO)
                    ybox.setTitle(_('Delete Confirmation'))
            except:
                print 'no image to remove'

        else:
            self.mysel

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

    def remove2(self, yesno):
        if yesno:
            cmd = "echo -e '\n\nNFR4XBoot deleting image..... '"
            cmd1 = 'rm -r /media/nfr4xboot/NFR4XBootI/' + self.mysel
            self.session.openWithCallback(self.up, Console, _('NFR4XBoot: Deleting Image'), [cmd, cmd1])
        else:
            self.session.open(MessageBox, _('Removing canceled!'), MessageBox.TYPE_INFO)

    def installMedia(self):
        images = False
        myimages = os.listdir('/media/nfr4xboot/NFR4XBootUpload')
        print myimages
        for fil in myimages:
            if fil.endswith('.zip'):
                images = True
                break
            else:
                images = False

        if images == True:
            self.session.openWithCallback(self.up2, NFR4XBootImageInstall)
        else:
            mess = _('The /media/nfr4xboot/NFR4XBootUpload directory is EMPTY!\n\nPlease upload a zip file to install')
            self.session.open(MessageBox, mess, MessageBox.TYPE_INFO)

    def install(self):
        count = 0
        for fn in os.listdir('/media/nfr4xboot/NFR4XBootI'):
            dirfile = '/media/nfr4xboot/NFR4XBootI/' + fn
            if os.path.isdir(dirfile):
                count = count + 1

        if count > 12:
            myerror = _('Sorry you can install a max of 10 images.')
            self.session.open(MessageBox, myerror, MessageBox.TYPE_INFO)
        else:
            menulist = []
            menulist.append((_('Install from /media/nfr4xboot/NFR4XBootUpload'), 'media'))
            menulist.append((_('Install from Internet (OpenPLi,OpenVix,OpenATV,Egami,OpenNFR,OpenHDF)'), 'internet'))
            self.session.openWithCallback(self.menuCallback, ChoiceBox, title='Choose they way for installation', list=menulist)

    def menuCallback(self, choice):
        self.show()
        if choice is None:
            return
        else:
            if choice[1] == 'internet':
                from Plugins.Extensions.NFR4XBoot.download_images import NFR4XChooseOnLineImage
                self.session.open(NFR4XChooseOnLineImage)
            if choice[1] == 'media':
                self.installMedia()
            return

    def advanced(self):
        menulist = []
        menulist.append((_('Remove NFR4XBoot'), 'rmnfr4xboot'))
        menulist.append((_('Remove all installed images'), 'rmallimg'))
        self.session.openWithCallback(self.menuAdvancedCallback, ChoiceBox, title=_('What would You like to do ?'), list=menulist)

    def menuAdvancedCallback(self, choice):
        self.show()
        if choice is None:
            return
        else:
            if choice[1] == 'rmnfr4xboot':
                f = file('/etc/fstab','r')
                lines = f.readlines()
                f.close()
                print "lines:", lines
                for line in lines:
                    if "/media/nfr4xboot" in line:
                        lines.remove(line)
                os.system("/etc/fstab")
                f = file('/etc/fstab','w')  
                for l in lines:
                    f.write(l)
                f.close()
                
                cmd0 = "echo -e '\n\nNFR4XBoot preparing to remove....'"
                cmd1 = 'rm /sbin/nfr4xinit'
                cmd1a = "echo -e '\n\nNFR4XBoot removing boot manager....'"
                cmd2 = 'rm /sbin/init'
                cmd3 = 'ln -sfn /sbin/init.sysvinit /sbin/init'
                cmd4 = 'chmod 777 /sbin/init'
                cmd4a = "echo -e '\n\nNFR4XBoot restoring media mounts....'"
                cmd5 = 'mv /etc/init.d/volatile-media.sh.back /etc/init.d/volatile-media.sh'
                cmd6 = 'rm /media/nfr4xboot/NFR4XBootI/.nfr4xboot'
                cmd7 = 'rm /media/nfr4xboot/NFR4XBootI/.Flash'
                cmd8 = 'rm /usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/.nfr4xboot_location'
                cmd8a = "echo -e '\n\nNFR4XBoot remove complete....'"
                self.session.openWithCallback(self.close, Console, _('NFR4XBoot is removing...'), [cmd0,
                 cmd1,
                 cmd1a,
                 cmd2,
                 cmd3,
                 cmd4,
                 cmd4a,
                 cmd5,
                 cmd6,
                 cmd7,
                 cmd8,
                 cmd8a])
            if choice[1] == 'rmallimg':
                cmd = "echo -e '\n\nNFR4XBoot deleting images..... '"
                cmd1 = 'rm -rf /media/nfr4xboot/NFR4XBootI/*'
                self.session.openWithCallback(self.updateList, Console, _('NFR4XBoot: Deleting All Images'), [cmd, cmd1])
            return


class NFR4XBootImageInstall(Screen, ConfigListScreen):

    def __init__(self, session):
        self.skin = NFR4XBootImageInstall_Skin
        Screen.__init__(self, session)
        fn = 'NewImage'
        sourcelist = []
        for fn in os.listdir('/media/nfr4xboot/NFR4XBootUpload'):
            if fn.find('.zip') != -1:
                fn = fn.replace('.zip', '')
                sourcelist.append((fn, fn))
                continue

        if len(sourcelist) == 0:
            sourcelist = [('None', 'None')]
        self.source = ConfigSelection(choices=sourcelist)
        self.target = ConfigText(fixed_size=False)
        self.sett = ConfigYesNo(default=False)
        self.zipdelete = ConfigYesNo(default=False)
        self.bootquest = ConfigYesNo(default=True)
        self.target.value = ''
        self.curselimage = ''
        try:
            if self.curselimage != self.source.value:
                self.target.value = self.source.value[:-13]
                self.curselimage = self.source.value
        except:
            pass

        self.createSetup()
        ConfigListScreen.__init__(self, self.list, session=session)
        self.source.addNotifier(self.typeChange)
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'CiSelectionActions',
         'VirtualKeyboardActions'], {'cancel': self.cancel,
         'red': self.cancel,
         'green': self.imageInstall,
         'yellow': self.openKeyboard}, -2)
        self['key_green'] = Label(_('Install'))
        self['key_red'] = Label(_('Cancel'))
        self['key_yellow'] = Label(_('Keyboard'))
        self['HelpWindow'] = Pixmap()
        self['HelpWindow'].hide()

    def createSetup(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Source Image file'), self.source))
        self.list.append(getConfigListEntry(_('Image Name'), self.target))
        self.list.append(getConfigListEntry(_('Copy Settings to the new Image'), self.sett))
        self.list.append(getConfigListEntry(_('Boot new Image directly?'), self.bootquest))
        self.list.append(getConfigListEntry(_('Delete Download Imagezip after Install?'), self.zipdelete))

    def typeChange(self, value):
        self.createSetup()
        self['config'].l.setList(self.list)
        if self.curselimage != self.source.value:
            self.target.value = self.source.value[:-13]
            self.curselimage = self.source.value

    def openKeyboard(self):
        sel = self['config'].getCurrent()
        if sel:
            if sel == self.target:
                if self['config'].getCurrent()[1].help_window.instance is not None:
                    self['config'].getCurrent()[1].help_window.hide()
            self.vkvar = sel[0]
            if self.vkvar == _('Image Name'):
                self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self['config'].getCurrent()[0], text=self['config'].getCurrent()[1].value)
        return

    def VirtualKeyBoardCallback(self, callback = None):
        if callback is not None and len(callback):
            self['config'].getCurrent()[1].setValue(callback)
            self['config'].invalidate(self['config'].getCurrent())
        return

    def imageInstall(self):
        if self.check_free_space():
            pluginpath = '/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot'
            myerror = ''
            source = self.source.value.replace(' ', '')
            target = self.target.value.replace(' ', '')
            for fn in os.listdir('/media/nfr4xboot/NFR4XBootI'):
                if fn == target:
                    myerror = _('Sorry, an Image with the name ') + target + _(' is already installed.\n Please try another name.')
                    continue

            if source == 'None':
                myerror = _('You have to select one Image to install.\nPlease, upload your zip file in the folder: /media/nfr4xboot/NFR4XBootUpload and select the image to install.')
            if target == '':
                myerror = _('You have to provide a name for the new Image.')
            if target == 'Flash':
                myerror = _('Sorry this name is reserved. Choose another name for the new Image.')
            if len(target) > 35:
                myerror = _('Sorry the name of the new Image is too long.')
            if myerror:
                myerror
                self.session.open(MessageBox, myerror, MessageBox.TYPE_INFO)
            else:
                myerror
                message = "echo -e '\n\n"
                message += _('NFR4XBoot will install the new image.\n\n')
                message += _('Please: DO NOT reboot your STB and turn off the power.\n\n')
                message += _('The new image will be installed and auto booted in few minutes.\n\n')
                message += "'"
                if fileExists(pluginpath + '/ex_init.py'):
                    cmd1 = 'python ' + pluginpath + '/ex_init.py'
                else:
                    cmd1 = 'python ' + pluginpath + '/ex_init.pyo'
                cmd = '%s %s %s %s %s %s %s %s %s' % (cmd1,
                 source,
                 target.replace(' ', '.'),
                 str(self.sett.value),
                 str(self.bootquest.value),
                 str(self.zipdelete.value),
                 getImageFolder(),
                 getMachineRootFile(),
                 getImageArch())						   
                print '[NFR4X-BOOT]: ', cmd
                self.session.open(Console, _('NFR4XBoot: Install new image'), [message, cmd])

    def check_free_space(self):
        if Freespace('/media/nfr4xboot/NFR4XBootUpload') < 300000:
            self.session.open(MessageBox, _('Not enough free space on /media/nfr4xboot/ !!\nYou need at least 300Mb free space.\n\nExit plugin.'), type=MessageBox.TYPE_ERROR)
            return False
        return True

    def cancel(self):
        self.close()

def checkkernel():
    mycheck = 0
    if not fileExists('/media/usb'):
        os.system('mkdir /media/usb')
    if getBoxType() in ('iqonios300hd', 'starsatlx'): 
        mycheck = 2
    else:
        mycheck = 1
    return mycheck

def main(session, **kwargs):
    m = checkkernel()
    if m == 1:
        try:
            f = open('/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/.nfr4xboot_location', 'r')
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
        except:
            pass

        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/.nfr4xboot_location'):
            if fileExists('/media/nfr4xboot/NFR4XBootI/.nfr4xboot'):
                session.open(NFR4XBootImageChoose)
            else:
                session.open(NFR4XBootInstallation)
        else:
            session.open(NFR4XBootInstallation)
    elif m == 2:
        session.open(MessageBox, _('Sorry: NFR4XBoot no work by this Box!'), MessageBox.TYPE_INFO, 3)
    else:
        session.open(MessageBox, _('Sorry: Wrong image in flash found. You have to install in flash NFR Image'), MessageBox.TYPE_INFO, 3)


def menu(menuid, **kwargs):
    filename = '/etc/videomode2'
    if os.path.exists(filename):
        pass
    else: 
        f = open(filename, 'w')
        f.write("576i")
        f.close()
    m = checkkernel()
    if m == 1:
        if menuid == 'mainmenu':
            return [(_('NFR4X MultiBoot'),
              main,
              'nfr4x_boot',
              1)]
        return []
    else:
        return []


from Plugins.Plugin import PluginDescriptor

def Plugins(**kwargs):
    return [PluginDescriptor(name='NFR4XBoot', description='NFR4X MultiBoot', where=PluginDescriptor.WHERE_MENU, fnc=menu), PluginDescriptor(name='NFR4XBoot', description=_('E2 Light Multiboot'), icon='NFR4XBootFHD.png', where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)] 
