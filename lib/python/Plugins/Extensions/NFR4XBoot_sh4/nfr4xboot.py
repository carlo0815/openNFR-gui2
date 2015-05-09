import sys
import os
import struct
import shutil
from glob import glob

def NFR4XBootMainEx(source, target, installsettings, filesys, zipdelete):
    nfr4xhome = '/media/nfr4xboot'
    nfr4xroot = 'media/nfr4xboot'

    to = '/media/nfr4xboot/NFR4XBootI/' + target
    cmd = 'rm -r %s > /dev/null 2<&1' % to
    rc = os.system(cmd)
    to = '/media/nfr4xboot/NFR4XBootI/' + target
    cmd = 'mkdir %s > /dev/null 2<&1' % to
    rc = os.system(cmd)
    to = '/media/nfr4xboot/NFR4XBootI/' + target
    cmd = 'chmod -R 0777 %s' % to
    rc = os.system(cmd)
    print "filesys:", filesys
    if filesys == "jffs2":
        rc = NFR4XBootExtractJFFS(source, target, zipdelete)
    cmd = 'mkdir -p %s/NFR4XBootI/%s/media > /dev/null 2>&1' % (nfr4xhome, target)
    rc = os.system(cmd)
    cmd = 'rm %s/NFR4XBootI/%s/%s > /dev/null 2>&1' % (nfr4xhome, target, nfr4xroot)
    rc = os.system(cmd)
    cmd = 'rmdir %s/NFR4XBootI/%s/%s > /dev/null 2>&1' % (nfr4xhome, target, nfr4xroot)
    rc = os.system(cmd)
    cmd = 'mkdir -p %s/NFR4XBootI/%s/%s > /dev/null 2>&1' % (nfr4xhome, target, nfr4xroot)
    rc = os.system(cmd)
    cmd = 'cp /etc/network/interfaces %s/NFR4XBootI/%s/etc/network/interfaces > /dev/null 2>&1' % (nfr4xhome, target)
    rc = os.system(cmd)
    #cmd = 'cp /etc/passwd %s/NFR4XBootI/%s/etc/passwd > /dev/null 2>&1' % (nfr4xhome, target)
    #rc = os.system(cmd)
    cmd = 'cp /etc/resolv.conf %s/NFR4XBootI/%s/etc/resolv.conf > /dev/null 2>&1' % (nfr4xhome, target)
    rc = os.system(cmd)
    cmd = 'cp /etc/wpa_supplicant.conf %s/NFR4XBootI/%s/etc/wpa_supplicant.conf > /dev/null 2>&1' % (nfr4xhome, target)
    rc = os.system(cmd)
    cmd = 'rm -rf %s/NFR4XBootI/%s/usr/lib/enigma2/python/Plugins/Extensions/HbbTV' % (nfr4xhome, target)
    rc = os.system(cmd)
    cmd = 'cp -r /usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/NFR4XBoot_client %s/NFR4XBootI/%s/usr/lib/enigma2/python/Plugins/Extensions/ > /dev/null 2>&1' % (nfr4xhome, target)
    rc = os.system(cmd)
    cmd = 'cp -r /usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/.nfr4xboot_location %s/NFR4XBootI/%s/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot_client/.nfr4xboot_location > /dev/null 2>&1' % (nfr4xhome, target)
    rc = os.system(cmd)
    if installsettings == 'True':
        cmd = 'mkdir -p %s/NFR4XBootI/%s/etc/enigma2 > /dev/null 2>&1' % (nfr4xhome, target)
        rc = os.system(cmd)
        cmd = 'cp -f /etc/enigma2/* %s/NFR4XBootI/%s/etc/enigma2/' % (nfr4xhome, target)
        rc = os.system(cmd)
        cmd = 'cp -f /etc/tuxbox/* %s/NFR4XBootI/%s/etc/tuxbox/' % (nfr4xhome, target)
        rc = os.system(cmd)
    cmd = 'mkdir -p %s/NFR4XBootI/%s/media > /dev/null 2>&1' % (nfr4xhome, target)
    rc = os.system(cmd)
    cmd = 'mkdir -p %s/NFR4XBootI/%s/media/usb > /dev/null 2>&1' % (nfr4xhome, target)
    rc = os.system(cmd)
    filename = nfr4xhome + '/NFR4XBootI/' + target + '/etc/fstab'
    filename2 = filename + '.tmp'
    out = open(filename2, 'w')
    f = open(filename, 'r')
    for line in f.readlines():
        if line.find('/dev/mtdblock2') != -1:
            line = '#' + line
        elif line.find('/dev/root') != -1:
            line = '#' + line
        out.write(line)

    f.close()
    out.close()
    os.rename(filename2, filename)
    kernelcheckflash = os.listdir('/lib/modules')
    kernelcheckmulti = os.listdir('%s/NFR4XBootI/%s/lib/modules' %(nfr4xhome, target))
    oedir = nfr4xhome + '/NFR4XBootI/' + target
    oecheck = nfr4xhome + '/NFR4XBootI/' + target + '/etc/oe-git.log'
    if kernelcheckflash == kernelcheckmulti:
        if os.path.exists(oecheck):
            print "Use Driver from Image"
        else:
            print "Copy Driver from Flash"
	    for fdelete in glob (oedir + '/*.opk'):
		    os.remove (fdelete)
            cmd = 'mv %s/NFR4XBootI/%s/lib/modules %s/NFR4XBootI/%s/lib/modules1' % (nfr4xhome, target, nfr4xhome, target) 
            rc = os.system(cmd)
            cmd = 'cp -r /lib/modules %s/NFR4XBootI/%s/lib' % (nfr4xhome, target)
            rc = os.system(cmd)         
    else:
        print "Copy Driver"
	for fdelete in glob (oedir + '/*.opk'):
		os.remove (fdelete)
        cmd = 'mv %s/NFR4XBootI/%s/lib/modules %s/NFR4XBootI/%s/lib/modules1' % (nfr4xhome, target, nfr4xhome, target) 
        rc = os.system(cmd)
        cmd = 'cp -r /lib/modules %s/NFR4XBootI/%s/lib' % (nfr4xhome, target)
        rc = os.system(cmd)
    if os.path.exists('%s/NFR4XBootI/%s/lib/modules1' %(nfr4xhome, target)):
        print "Search TDT Driver"
        koLIST = []
        for fdelete in glob ('%s/NFR4XBootI/%s/lib/modules1/*.ko' %(nfr4xhome, target)):
            koLIST.append(fdelete)
        for line in koLIST:
            treiberdir = "%s/NFR4XBootI/%s/lib/modules1" %(nfr4xhome, target)
            treiber = line.replace(treiberdir, '') + '\n'
            for dirpath, dirnames, filenames in os.walk("%s/NFR4XBootI/%s/lib/modules" %(nfr4xhome, target)):
                for filename in [f for f in filenames if f.endswith('.ko')]:
                    src = os.path.join(dirpath, filename)
                    if filename in treiber:
                        shutil.copy2(src, '%s/NFR4XBootI/%s/lib/modules' %(nfr4xhome, target))
    else:
        print "OE-Image Driver"    
    tpmd = nfr4xhome + '/NFR4XBootI/' + target + '/etc/init.d/tpmd'
    if os.path.exists(tpmd):
        os.system('rm ' + tpmd)
    filename = nfr4xhome + '/NFR4XBootI/' + target + '/usr/lib/enigma2/python/Components/config.py'
    if os.path.exists(filename):
        filename2 = filename + '.tmp'
        out = open(filename2, 'w')
        f = open(filename, 'r')
        for line in f.readlines():
            if line.find('if file("/proc/stb/info/vumodel")') != -1:
                line = '#' + line
            elif line.find('rckeyboard_enable = True') != -1:
                line = '#' + line
            out.write(line)

        f.close()
        out.close()
        os.rename(filename2, filename)
    filename = nfr4xhome + '/NFR4XBootI/' + target + '/usr/lib/enigma2/python/Tools/HardwareInfoVu.py'
    if os.path.exists(filename):
        filename2 = filename + '.tmp'
        out = open(filename2, 'w')
        f = open(filename, 'r')
        for line in f.readlines():
            if line.find('print "hardware detection failed"') != -1:
                line = '\t\t    HardwareInfoVu.device_name ="duo"'
            out.write(line)

        f.close()
        out.close()
        os.rename(filename2, filename)
    filename = nfr4xhome + '/NFR4XBootI/' + target + '/etc/bhversion'
    if os.path.exists(filename):
        os.system('echo "BlackHole 2.0.9" > ' + filename)
    mypath = nfr4xhome + '/NFR4XBootI/' + target + '/usr/lib/opkg/info/'
    if not os.path.exists(mypath):
        mypath = nfr4xhome + '/NFR4XBootI/' + target + '/var/lib/opkg/info/'
    if not os.path.exists(mypath):
        mypath = nfr4xhome + '/NFR4XBootI/' + target + '/var/opkg/info/'        
    for fn in os.listdir(mypath):
        if fn.find('kernel-image') != -1 and fn.find('postinst') != -1:
            filename = mypath + fn
            filename2 = filename + '.tmp'
            out = open(filename2, 'w')
            f = open(filename, 'r')
            for line in f.readlines():
                if line.find('/boot') != -1:
                    line = line.replace('/boot', '/boot > /dev/null 2>\\&1; exit 0')
                out.write(line)

            if f.close():
                out.close()
                os.rename(filename2, filename)
                cmd = 'chmod -R 0755 %s' % filename
                rc = os.system(cmd)
        if fn.find('-bootlogo.postinst') != -1:
            filename = mypath + fn
            filename2 = filename + '.tmp'
            out = open(filename2, 'w')
            f = open(filename, 'r')
            for line in f.readlines():
                if line.find('/boot') != -1:
                    line = line.replace('/boot', '/boot > /dev/null 2>\\&1; exit 0')
                out.write(line)

            f.close()
            out.close()
            os.rename(filename2, filename)
            cmd = 'chmod -R 0755 %s' % filename
            rc = os.system(cmd)
        if fn.find('-bootlogo.postrm') != -1:
            filename = mypath + fn
            filename2 = filename + '.tmp'
            out = open(filename2, 'w')
            f = open(filename, 'r')
            for line in f.readlines():
                if line.find('/boot') != -1:
                    line = line.replace('/boot', '/boot > /dev/null 2>\\&1; exit 0')
                out.write(line)

            f.close()
            out.close()
            os.rename(filename2, filename)
            cmd = 'chmod -R 0755 %s' % filename
            rc = os.system(cmd)
        if fn.find('-bootlogo.preinst') != -1:
            filename = mypath + fn
            filename2 = filename + '.tmp'
            out = open(filename2, 'w')
            f = open(filename, 'r')
            for line in f.readlines():
                if line.find('/boot') != -1:
                    line = line.replace('/boot', '/boot > /dev/null 2>\\&1; exit 0')
                out.write(line)

            f.close()
            out.close()
            os.rename(filename2, filename)
            cmd = 'chmod -R 0755 %s' % filename
            rc = os.system(cmd)
        if fn.find('-bootlogo.prerm') != -1:
            filename = mypath + fn
            filename2 = filename + '.tmp'
            out = open(filename2, 'w')
            f = open(filename, 'r')
            for line in f.readlines():
                if line.find('/boot') != -1:
                    line = line.replace('/boot', '/boot > /dev/null 2>\\&1; exit 0')
                out.write(line)

            f.close()
            out.close()
            os.rename(filename2, filename)
            cmd = 'chmod -R 0755 %s' % filename
            rc = os.system(cmd)

    rc = NFR4XBootRemoveUnpackDirs()
    filename = nfr4xhome + '/NFR4XBootI/.nfr4xboot'
    out = open('/media/nfr4xboot/NFR4XBootI/.nfr4xboot', 'w')
    out.write(target)
    out.close()
    os.system('touch /tmp/.opennfrreboot')
    rc = os.system('sync')
    os.system('reboot -p')


def NFR4XBootRemoveUnpackDirs():
    os.chdir('/media/nfr4xboot/NFR4XBootUpload')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/enigma2'):
        shutil.rmtree('enigma2')    
    

def NFR4XBootExtractJFFS(source, target, zipdelete):
    NFR4XBootRemoveUnpackDirs()	
    if os.path.exists('/media/nfr4xboot/jffs2') is False:
        rc = os.system('mkdir /media/nfr4xboot/jffs2')
    sourcefile = '/media/nfr4xboot/NFR4XBootUpload/%s.zip' % source
    if os.path.exists(sourcefile) is True:
        os.chdir('/media/nfr4xboot/NFR4XBootUpload')
        os.system('echo "[NFR4XBoot] Extracking ZIP image file"')
        rc = os.system('unzip ' + sourcefile)
        if zipdelete == "True":
                rc = os.system('rm -rf ' + sourcefile)
        else:
                os.system('echo "[NFR4XBoot] keep %s for next time"'% sourcefile)
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/enigma2'):
            os.chdir('enigma2')    
            os.system('mv e2jffs2.img rootfs.bin')
            GETIMAGEFOLDER = '/media/nfr4xboot/NFR4XBootUpload/enigma2'
        print '[NFR4XBoot] Extracting JFFS2 image and moving extracted image to our target'
		
        rootfs_path = GETIMAGEFOLDER + '/rootfs.bin'  
        cmd = 'mknod /media/nfr4xboot/mtdblock7 b 31 7'
        rc = os.system(cmd)
        cmd = '/sbin/modprobe loop '
        rc = os.system(cmd)
        cmd = '/sbin/losetup /dev/loop0 ' + rootfs_path
        rc = os.system(cmd)               
        cmd = '/sbin/modprobe mtdblock'
        rc = os.system(cmd)        
        cmd = '/sbin/modprobe block2mtd'
        rc = os.system(cmd)
        cmd = '/bin/echo "/dev/loop0,128KiB" > /sys/module/block2mtd/parameters/block2mtd'
        rc = os.system(cmd)
        cmd = 'modprobe jffs2'
        rc = os.system(cmd)
        cmd = '/bin/mount -t jffs2 /media/nfr4xboot/mtdblock7 /media/nfr4xboot/jffs2'
        rc = os.system(cmd)
        cmd = 'cp -r -p /media/nfr4xboot/jffs2/* /media/nfr4xboot/NFR4XBootI/' + target
        rc = os.system(cmd)
        cmd = '/bin/umount /media/nfr4xboot/jffs2'
        rc = os.system(cmd)
        cmd = 'chmod -R +x /media/nfr4xboot/NFR4XBootI/' + target
        rc = os.system(cmd)
        cmd = 'rm -rf /media/nfr4xboot/jffs2'
        rc = os.system(cmd)
        cmd = 'rm /media/nfr4xboot/mtdblock7'
        rc = os.system(cmd)
    return 1
