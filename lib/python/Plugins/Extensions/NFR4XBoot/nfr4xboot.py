import sys
import os
import struct
import shutil

def NFR4XBootMainEx(source, target, installsettings, zipdelete):
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
    rc = NFR4XBootExtract(source, target, zipdelete)
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
    cmd = 'cp /etc/passwd %s/NFR4XBootI/%s/etc/passwd > /dev/null 2>&1' % (nfr4xhome, target)
    rc = os.system(cmd)
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
    #os.system('reboot -p')


def NFR4XBootRemoveUnpackDirs():
    os.chdir('/media/nfr4xboot/NFR4XBootUpload')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/venton-hdx'):
        shutil.rmtree('venton-hdx')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/atemio'):
        shutil.rmtree('atemio')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/xpeedlx'):
        shutil.rmtree('xpeedlx')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/xpeedlx3'):
        shutil.rmtree('xpeedlx3')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/vuplus'):
        shutil.rmtree('vuplus')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/update'):
        shutil.rmtree('update')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/unibox'):
        shutil.rmtree('unibox')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/xp1000'):
        shutil.rmtree('xp1000')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/e3hd'):
        shutil.rmtree('e3hd')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/odinm9'):
        shutil.rmtree('odinm9')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/odinm7'):
        shutil.rmtree('odinm7')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/odinm6'):
        shutil.rmtree('odinm6')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/hd2400'):
    	shutil.rmtree('hd2400')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/en2'):
        shutil.rmtree('en2')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/gigablue'):
        shutil.rmtree('gigablue')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/formuler1'):
        shutil.rmtree('formuler1')
    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/formuler3'):
        shutil.rmtree('formuler3')     


def NFR4XBootExtract(source, target, zipdelete):
    NFR4XBootRemoveUnpackDirs()
    if os.path.exists('/media/nfr4xboot/ubi') is False:
        rc = os.system('mkdir /media/nfr4xboot/ubi')
    sourcefile = '/media/nfr4xboot/NFR4XBootUpload/%s.zip' % source
    if os.path.exists(sourcefile) is True:
        os.chdir('/media/nfr4xboot/NFR4XBootUpload')
        print '[NFR4XBoot] Extracknig ZIP image file'
        rc = os.system('unzip ' + sourcefile)
        if zipdelete == "True":
                rc = os.system('rm -rf ' + sourcefile)
        else:
                print '[NFR4XBoot] keep  %s for next time' % sourcefile)
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/update'):
            os.chdir('update')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/unibox'):
            os.chdir('unibox')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/unibox/hde'):
                os.chdir('hde')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/xp1000'):
            os.chdir('xp1000')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/e3hd'):
            os.chdir('e3hd')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/odinm9'):
            os.chdir('odinm9')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/hd2400'):
            os.chdir('hd2400')	
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/en2'):
            os.chdir('en2')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/odinm6'):
            os.chdir('odinm6')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/venton-hdx'):
            os.chdir('venton-hdx')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/atemio'):
            os.chdir('atemio')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/atemio/5x00'):
                os.chdir('5x00')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/atemio/6x00'):
                os.chdir('6x00')
	    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/atemio/6200'):
                os.chdir('6200')
	    if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/atemio/6000'):
                os.chdir('6000')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/atemio/8x00'):
                os.chdir('8x00')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/xpeedlx'):
            os.chdir('xpeedlx')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/xpeedlx3'):
            os.chdir('xpeedlx3')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/vuplus'):
            os.chdir('vuplus')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/vuplus/duo'):
                os.chdir('duo')
                os.system('mv root_cfe_auto.jffs2 rootfs.bin')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/vuplus/solo'):
                os.chdir('solo')
                os.system('mv -f root_cfe_auto.jffs2 rootfs.bin')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/vuplus/ultimo'):
                os.chdir('ultimo')
                os.system('mv -f root_cfe_auto.jffs2 rootfs.bin')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/vuplus/uno'):
                os.chdir('uno')
                os.system('mv -f root_cfe_auto.jffs2 rootfs.bin')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/vuplus/solo2'):
                os.chdir('solo2')
                os.system('mv -f root_cfe_auto.bin rootfs.bin')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/vuplus/duo2'):
                os.chdir('duo2')
                os.system('mv -f root_cfe_auto.bin rootfs.bin')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/gigablue'):
            os.chdir('gigablue')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/gigablue/quad'):
                os.chdir('quad')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/gigablue/quadplus'):
                os.chdir('quadplus')
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/gigablue/se'):
                os.chdir('se')                
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/gigablue/seplus'):
                os.chdir('seplus')                
            if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/gigablue/ueplus'):
                os.chdir('ueplus')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/formuler1'):
                os.chdir('formuler1')
        if os.path.exists('/media/nfr4xboot/NFR4XBootUpload/formuler3'):
                os.chdir('formuler3')     
                
                                
				
        print '[NFR4XBoot] Extracting UBIFS image and moving extracted image to our target'
        if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/ubi_reader/ubi_extract_files.pyo'):
            cmd = 'chmod 777 /usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/ubi_reader/ubi_extract_files.pyo'
            rc = os.system(cmd)
            cmd = 'python /usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/ubi_reader/ubi_extract_files.pyo rootfs.bin -o /media/nfr4xboot/ubi'
        else:
            cmd = 'chmod 777 /usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/ubi_reader/ubi_extract_files.py'
            rc = os.system(cmd)
            cmd = 'python /usr/lib/enigma2/python/Plugins/Extensions/NFR4XBoot/ubi_reader/ubi_extract_files.py rootfs.bin -o /media/nfr4xboot/ubi'        
        print cmd
        rc = os.system(cmd)
        os.chdir('/home/root')
        cmd = 'cp -r -p /media/nfr4xboot/ubi/rootfs/* /media/nfr4xboot/NFR4XBootI/' + target
        rc = os.system(cmd)
        cmd = 'chmod -R +x /media/nfr4xboot/NFR4XBootI/' + target
        rc = os.system(cmd)
        cmd = 'rm -rf /media/nfr4xboot/ubi'
        rc = os.system(cmd)
    return 1
