#!/bin/sh
###########################################
# Screenshotscript e2 #
###########################################
#
# (C) by karlchen1963
# 26.05.2012: Version 1.00
input=$1

if [ $input == "o" ]; then
wget 'http://127.0.0.1/web/message?text=15%20Sekunden%20Zeit,%20um%20ins%20Menue%20zu%20wechseln...\n&type=2&timeout=5'>/dev/null 2>&1 -O /tmp
sleep 13
wget 'http://127.0.0.1/web/message?text=Screenshot_OSD%20wird%20gestartet\n&type=2&timeout=2'>/dev/null 2>&1 -O /tmp
sleep 2
rm -f /tmp/dump.png
/usr/bin/grab -o -p /tmp/dump.png
wget 'http://127.0.0.1/web/message?text=ScreenShot%20fertig%20->%20/tmp/dump.png\n&type=2&timeout=10'>/dev/null 2>&1 -O /tmp

elif [ $input == "v" ]; then
wget 'http://127.0.0.1/web/message?text=15%20Sekunden%20Zeit,%20um%20ins%20Programm%20zu%20wechseln...\n&type=2&timeout=5'>/dev/null 2>&1 -O /tmp
sleep 13
wget 'http://127.0.0.1/web/message?text=Screenshot_Video%20wird%20gestartet\n&type=2&timeout=2'>/dev/null 2>&1 -O /tmp
sleep 2
rm -f /tmp/dump.png
e2service=`wget -q -O - http://127.0.0.1/web/getcurrent | grep "<e2servicereference>" | sed s/".*<e2servicereference>"/""/ | sed s/"<\/e2servicereference>"/""/`
/usr/bin/grab -v -p   /tmp/dump.png  $e2service 
wget 'http://127.0.0.1/web/message?text=ScreenShot%20fertig%20->%20/tmp/dump.png\n&type=2&timeout=10'>/dev/null 2>&1 -O /tmp

else
wget 'http://127.0.0.1/web/message?text=15%20Sekunden%20Zeit,%20um%20ins%20Menue+Programm%20zu%20wechseln...\n&type=2&timeout=5'>/dev/null 2>&1 -O /tmp
sleep 13
wget 'http://127.0.0.1/web/message?text=Screenshot_All%20wird%20gestartet\n&type=2&timeout=2'>/dev/null 2>&1 -O /tmp
sleep 2
rm -f /tmp/dump.png
e2service=`wget -q -O - http://127.0.0.1/web/getcurrent | grep "<e2servicereference>" | sed s/".*<e2servicereference>"/""/ | sed s/"<\/e2servicereference>"/""/`
/usr/bin/grab -p  /tmp/dump.png  $e2service
wget 'http://127.0.0.1/web/message?text=ScreenShot%20fertig%20->%20/tmp/dump.png\n&type=2&timeout=10'>/dev/null 2>&1 -O /tmp
fi