#!/bin/sh
################################
#####  EOS TEAM  #####
####### http://www.nachtfalke.biz/  #######
################################

PLUGINDIR=/usr/lib/enigma2/python/Plugins/Extensions
if [ -f /.*info ]; then
   echo "Makes Only Sense With Images In Flash"
   exit 1
fi
if [ ! -d /media/usb ]; then
   echo "/media/usb Not Found" 
   exit 1
fi
if [ `mount | grep /media/usb | wc -l` -eq 0 ]; then
   echo "USB Stick Not Mounted" 
   exit 1
fi
if [ ! -d $PLUGINDIR ]; then
   if [ -d /media/usb/Extensions ]; then
      echo "$PLUGINDIR Already Moved" 
      ln -sfn /media/usb/Extensions $PLUGINDIR
      exit 0
   fi
fi
if [ ! -d $PLUGINDIR ]; then
   if [ ! -d /media/usb/Extensions ]; then
      echo "$PLUGINDIR Already Moved , But Nothing On USB" 
      echo "Now We Are In Trouble" 
      echo "Try Reinstalling Other Plugins" 
      mkdir $PLUGINDIR > /dev/null 2>&1
      exit 0
   fi
fi
if [ -d /media/usb/Extensions ]; then
   echo "$PLUGINDIR Already Moved" 
   ln -sfn /media/usb/Extensions $PLUGINDIR
   exit 0
fi
echo "Stopping enigma2 To Move $PLUGINDIR To USB Stick"
init 4
sleep 5
killall -9 enigma2 > /dev/null 2>&1
mv $PLUGINDIR /media/usb
ln -sfn /media/usb/Extensions $PLUGINDIR
rmdir /media/usb/Extensions/Extensions > /dev/null 2>&1
echo "Starting enigma2"
init 3
exit 0
