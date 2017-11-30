#!/bin/sh
kernel=`uname -r`
if ! [ -d "/etc/extraci" ] ; then
	cp -r /lib/modules/$kernel/extra /etc
	mv /etc/extra /etc/extraci
	echo copy extraci
	# ...
fi
if ! [  -f "/etc/modules-load.d/_formuler1.conf_ci" ] ; then
	cp -r /etc/modules-load.d/_formuler1.conf /etc/modules-load.d/_formuler1.conf_ci
	echo copy modload
fi
if ! [  -f "/etc/modules-load.d/_formuler3.conf_ci" ] ; then
	cp -r /etc/modules-load.d/_formuler3.conf /etc/modules-load.d/_formuler3.conf_ci
	echo copy modload
fi
if ! [  -f "/etc/modules-load.d/_formuler4.conf_ci" ] ; then
	cp -r /etc/modules-load.d/_formuler4.conf /etc/modules-load.d/_formuler4.conf_ci
	echo copy modload
fi
case "$1" in
tcdriver)
	echo -n "enable tc Driver and reboot...\n "
        rm /etc/modules-load.d/_formuler1.conf
        cp /etc/modules-load.d/_formuler1.conf_tc /etc/modules-load.d/_formuler1.conf
        rm -r /lib/modules/$kernel/extra
        cp -r /etc/extratc /lib/modules/$kernel/extra        
	echo -e "done.\n"
	;;

cidriver)
	echo -n "enable ci Driver and reboot...\n "
        rm /etc/modules-load.d/_formuler1.conf
        cp /etc/modules-load.d/_formuler1.conf_ci /etc/modules-load.d/_formuler1.conf
        rm -r /lib/modules/$kernel/extra
        cp -r /etc/extraci /lib/modules/$kernel/extra               
	echo -e "done.\n"
	;;
ip3driver)
	echo -n "enable ip Driver and reboot...\n "
        rm /etc/modules-load.d/_formuler3.conf
        cp /etc/modules-load.d/_formuler3.conf_ip /etc/modules-load.d/_formuler3.conf
        rm -r /lib/modules/$kernel/extra
        cp -r /etc/extraip /lib/modules/$kernel/extra        
	echo -e "done.\n"
	;;

ci3driver)
	echo -n "enable ci Driver and reboot...\n "
        rm /etc/modules-load.d/_formuler3.conf
        cp /etc/modules-load.d/_formuler3.conf_ci /etc/modules-load.d/_formuler3.conf
        rm -r /lib/modules/$kernel/extra
        cp -r /etc/extraci /lib/modules/$kernel/extra               
	echo -e "done.\n"
	;;
ip4driver)
	echo -n "enable ip Driver and reboot...\n "
        rm /etc/modules-load.d/_formuler4.conf
        cp /etc/modules-load.d/_formuler4.conf_ip /etc/modules-load.d/_formuler4.conf
        rm -r /lib/modules/$kernel/extra
        cp -r /etc/extraip /lib/modules/$kernel/extra        
	echo -e "done.\n"
	;;

ci4driver)
	echo -n "enable ci Driver and reboot...\n "
        rm /etc/modules-load.d/_formuler4.conf
        cp /etc/modules-load.d/_formuler4.conf_ci /etc/modules-load.d/_formuler4.conf
        rm -r /lib/modules/$kernel/extra
        cp -r /etc/extraci /lib/modules/$kernel/extra               
	echo -e "done.\n"
	;;	
esac

exit 0

