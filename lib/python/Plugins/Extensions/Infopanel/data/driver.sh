#!/bin/sh
kernel=`uname -r`
case "$1" in
tcdriver)
	echo -n "enable tc Driver and reboot...\n "
        rm /etc/modules-load.d/_formuler1.conf
        cp /etc/modules-load.d/_formuler1.conf_tc /etc/modules-load.d/_formuler1.conf
        rm -r /lib/modules/$kernel/extra
        cp -r /lib/modules/$kernel/extratc /lib/modules/$kernel/extra        
	echo -e "done.\n"
	;;

cidriver)
	echo -n "enable ci Driver and reboot...\n "
        rm /etc/modules-load.d/_formuler1.conf
        cp /etc/modules-load.d/_formuler1.conf_ci /etc/modules-load.d/_formuler1.conf
        rm -r /lib/modules/$kernel/extra
        cp -r /lib/modules/$kernel/extraci /lib/modules/$kernel/extra               
	echo -e "done.\n"
	;;
esac

exit 0
