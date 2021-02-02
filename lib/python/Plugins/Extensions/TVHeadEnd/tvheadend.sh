#!/bin/bash
### BEGIN INIT INFO
# Provides:          tvheadend
# Required-Start:    $local_fs $remote_fs $network
# Required-Stop:     $local_fs $remote_fs $network
# Should-Start:      $syslog
# Should-Stop:       $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1
# Short-Description: start/stop tvheadend Server
### END INIT INFO


TVHNAME="tvheadend"
TVHBIN="/usr/bin/tvheadend"
TVHUSER="root"
TVHGROUP="su"
PIDFILE=/var/run/$TVHNAME.pid


start() {
	echo -n "Starting tvheadend: "
	start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user ${TVHUSER} --exec ${TVHBIN} -- \
		-u ${TVHUSER} -g ${TVHGROUP} -f -C
	echo "Done."
}


stop() {
			echo -n "Stopping $TVHNAME: "
			start-stop-daemon --stop --quiet --pidfile $PIDFILE --name ${TVHNAME}
			killall tvheadend
			echo "Done."
}



case "$1" in
	start) start ;;
	stop) stop ;;
	*) echo "Usage: $0 [start|stop]" && exit 1 ;;
esac


exit 0