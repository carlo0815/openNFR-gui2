import sys
import os
import struct
import shutil

media_nf = '/media/nfr4xboot'
mediahome = media_nf + '/NFR4XBootI/'

extensions_path = '/usr/lib/enigma2/python/Plugins/Extensions/'
extensions_path_extractpy = extensions_path + 'NFR4XBoot/ubi_reader/ubi_extract_files.py'
extensions_path_extractpyo = extensions_path_extractpy + 'o'
dev_null = ' > /dev/null 2>&1'

def NFR4XBootMainEx(source, target, installsettings, bootquest, zipdelete, getimagefolder, getMachineRootFile, getImageArch):
    media_nfr_target = mediahome + target
    list_one = ['rm -r ' + media_nfr_target + dev_null,
                'mkdir ' + media_nfr_target + dev_null, 
                'chmod -R 0777 ' + media_nfr_target]
    
    for command in list_one:
        os.system(command)
    
    rc = NFR4XBootExtract(source, target, zipdelete, getimagefolder, getMachineRootFile, getImageArch)
    
    list_two = ['mkdir -p ' + media_nfr_target + '/media' + dev_null,
                'rm ' + media_nfr_target + media_nf + dev_null, 
                'rmdir ' + media_nfr_target + media_nf + dev_null,
                'mkdir -p ' + media_nfr_target + media_nf + dev_null,
                'cp /etc/network/interfaces ' + media_nfr_target + '/etc/network/interfaces' + dev_null,
                'cp /etc/passwd ' + media_nfr_target + '/etc/passwd' + dev_null,
                'cp /etc/resolv.conf ' + media_nfr_target + '/etc/resolv.conf' + dev_null,
                'cp /etc/wpa_supplicant.conf ' + media_nfr_target + '/etc/wpa_supplicant.conf' + dev_null,
                'rm -rf ' + media_nfr_target + extensions_path + 'HbbTV',
                'cp -r ' + extensions_path + 'NFR4XBoot/NFR4XBoot_client ' + media_nfr_target + extensions_path + dev_null,
                'cp -r ' + extensions_path + 'NFR4XBoot/.nfr4xboot_location ' + media_nfr_target + extensions_path + 'NFR4XBoot_client/.nfr4xboot_location' + dev_null]
                
    for command in list_two:
        os.system(command)
    
    if installsettings == "True":
        
        list_three = ['mkdir -p ' + media_nfr_target + '/etc/enigma2' + dev_null,
                      'cp -f /etc/enigma2/* ' + media_nfr_target + '/etc/enigma2/',
                      'cp -f /etc/tuxbox/* ' + media_nfr_target + '/etc/tuxbox/']
        for command in list_three:
            os.system(command)
        
    os.system('mkdir -p ' + media_nfr_target + '/media/usb' + dev_null)
    
    list_four = ['/etc/fstab', '/usr/lib/enigma2/python/Components/config.py', '/usr/lib/enigma2/python/Tools/HardwareInfoVu.py']
    for entrie in list_four:
        filename = media_nfr_target + entrie
        tempfile = filename + '.tmp'
        if os.path.exists(filename):
                out = open(tempfile, 'w')
                f = open(filename, 'r')
                for line in f.readlines():
                  if '/etc/fstab' in entrie:  
                     if '/dev/mtdblock2' in line:
                        line = '#' + line
                     elif '/dev/root' in line:
                        line = '#' + line
                  if 'config.py' in entrie:  
                     if 'if file("/proc/stb/info/vumodel")' in line:
                        line = '#' + line
                     elif 'rckeyboard_enable = True' in line:
                        line = '#' + line
                  if 'HardwareInfoVu.py' in entrie:  
                     if 'print "hardware detection failed"' in line:
                        line = '\t\t    HardwareInfoVu.device_name ="duo"'
          
                  out.write(line)

                f.close()
                out.close()
                os.rename(tempfile, filename)
    
    tpmd = media_nfr_target + '/etc/init.d/tpmd'
    if os.path.exists(tpmd):
       os.remove(tpmd)
    
    
    filename = media_nfr_target + '/etc/bhversion'
    if os.path.exists(filename):
       os.system('echo "BlackHole 2.0.9" > ' + filename)
    
    mypath = media_nfr_target + '/usr/lib/opkg/info/'
    if not os.path.exists(mypath):
       mypath = media_nfr_target + '/var/lib/opkg/info/'
        
    for file_name in os.listdir(mypath):
        
        list_five = ['-bootlogo.postinst', '-bootlogo.postrm', '-bootlogo.preinst', '-bootlogo.prerm']
        
        for entrie in list_five:
            if entrie in file_name or (('kernel-image' in file_name) and ('postinst' in file_name)):
               filename = mypath + file_name
               tempfile = filename + '.tmp'
               out = open(tempfile, 'w')
               f = open(filename, 'r')
               for line in f.readlines():
                   if '/boot' in line:
                      line = line.replace('/boot', '/boot > /dev/null 2>\\&1; exit 0')
                   out.write(line)

               f.close()
               out.close()
               os.rename(tempfile, filename)
               os.chmod(filename, 0755)

    rc = NFR4XBootRemoveUnpackDirs(getimagefolder)
    if bootquest == "True":
        out = open(mediahome + '.nfr4xboot', 'w')
        out.write(target)
        out.close()
        os.system('touch /tmp/.opennfrreboot; sync; reboot -p')        
    else: 
        out = open(mediahome + '.nfr4xboot', 'w')
        out.write(target)
        out.close()    
        os.system('echo "[NFR4XBoot] Image-Install ready, Image starts by next booting, please push exit!"')
    

def NFR4XBootRemoveUnpackDirs(getimagefolder):
    os.chdir(media_nf + '/NFR4XBootUpload')
    if os.path.exists(media_nf + '/NFR4XBootUpload/%s'% getimagefolder):
       shutil.rmtree('%s'% getimagefolder)
 

def NFR4XBootExtract(source, target, zipdelete, getimagefolder, getMachineRootFile, getImageArch):
    NFR4XBootRemoveUnpackDirs(getimagefolder)
    os.system('rm -rf ' + media_nf + '/ubi')
    if not os.path.exists(media_nf + '/ubi'):
       os.system('mkdir ' + media_nf + '/ubi')
    sourcefile = media_nf + '/NFR4XBootUpload/%s.zip' % source
    if os.path.exists(sourcefile):
        os.chdir(media_nf + '/NFR4XBootUpload')
        if os.path.exists(media_nf + '/NFR4XBootUpload/usb_update.bin'):
           os.system('rm -rf ' + media_nf + '/NFR4XBootUpload/usb_update.bin')
        os.system('echo "[NFR4XBoot] Extracking ZIP image file"')
        os.system('unzip ' + sourcefile)

        if zipdelete == "True":
           os.system('rm -rf ' + sourcefile)
        else:
           os.system('echo "[NFR4XBoot] keep  %s for next time"'% sourcefile) 
	if "cortexa15hf" in getImageArch:
           if os.path.exists(media_nf + '/NFR4XBootUpload/%s'% getimagefolder):
              os.chdir('%s'% getimagefolder)
			
           print '[NFR4XBoot] Extracting tar.bz2 image and moving extracted image to our target'
           if os.path.exists('/usr/bin/bzip2'):
               sfolder = media_nf + '/NFR4XBootUpload/%s'% getimagefolder
               cmd = 'tar -jxf ' + sfolder + '/rootfs.tar.bz2 -C ' + media_nf + '/NFR4XBootI/' + target + ' > /dev/null 2>&1'
           os.system(cmd)
           os.chdir('/home/root')
	else:		
           if os.path.exists(media_nf + '/NFR4XBootUpload/%s'% getimagefolder):
              os.chdir('%s'% getimagefolder)
              os.system('mv %s rootfs.bin'% getMachineRootFile)
				
           print '[NFR4XBoot] Extracting UBIFS image and moving extracted image to our target'
           if os.path.exists(extensions_path_extractpyo):
               os.chmod(extensions_path_extractpyo, 0777)
               cmd = 'python ' + extensions_path_extractpyo + ' rootfs.bin -o ' + media_nf + '/ubi'
           else:
               os.chmod(extensions_path_extractpy, 0777)
               cmd = 'python ' + extensions_path_extractpy + ' rootfs.bin -o ' + media_nf + '/ubi'        
           print cmd
           os.system(cmd)
           os.chdir('/home/root')
           os.system('cp -r -p ' + media_nf + '/ubi/rootfs/* ' + media_nf + '/NFR4XBootI/' + target)
           os.system('chmod -R +x ' + media_nf + '/NFR4XBootI/' + target)
           os.system('rm -rf ' + media_nf + '/ubi')
    return 1 
