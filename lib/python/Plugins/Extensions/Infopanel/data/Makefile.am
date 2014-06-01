installdir = $(pkglibdir)/python/Plugins/Extensions/Infopanel/data


dist_install_DATA = \
	iperf \
	iperf.7z \
	ofgwrite \
	screenshot.sh  \
	unrar-free  \
	unzip  


install-data-hook:
	@chmod +x $(DESTDIR)$(installdir)/iperf 
	@chmod +x $(DESTDIR)$(installdir)/ofgwrite
	@chmod +x $(DESTDIR)$(installdir)/unrar-free
	@chmod +x $(DESTDIR)$(installdir)/unzip
	@chmod +x $(DESTDIR)$(installdir)/screenshot.sh

