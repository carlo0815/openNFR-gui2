#!/bin/sh
################################
#####  EOS TEAM  #####
####### http://www.nachtfalke.biz/  #######
################################

PLUGINDIR=/usr/lib/enigma2/python/Plugins/Extensions
if [ `mount | grep /media/hdd | wc -l` -eq 0 ]; then
   echo "HDD Not Mounted" 
   exit 1
fi
if [ -d $PLUGINDIR ]; then
   if [ `ls -F $PLUGINDIR | grep @ | wc -l` -eq 0 ]; then
      echo "$PLUGINDIR Already Moved" 
      if [ -d /media/hdd/Extensions ]; then
         echo "But /media/hdd/Extensions Still Exists , Maybe You Should Remove It Manually"
      fi 
      exit 0
   fi
else
   mkdir $PLUGINDIR > /dev/null 2>&1
fi
if [ ! -d /media/hdd/Extensions ]; then
   echo "/media/hdd/Extensions Not Found" 
   echo "Now We Are In Trouble" 
   echo "Try Reinstalling Other Plugins" 
   rm $PLUGINDIR > /dev/null 2>&1
   mkdir $PLUGINDIR > /dev/null 2>&1
   exit 0
fi
rm $PLUGINDIR > /dev/null 2>&1
echo "Stopping enigma2 To Move From HDD Back To $PLUGINDIR"
init 4
sleep 5
killall -9 enigma2 > /dev/null 2>&1
rm $PLUGINDIR > /dev/null 2>&1
mv /media/hdd/Extensions $PLUGINDIR 
rmdir $PLUGINDIR/Extensions > /dev/null 2>&1
echo "Starting enigma2"
init 3
exit 0
