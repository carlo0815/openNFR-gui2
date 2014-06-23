installdir = $(pkglibdir)/python/Plugins/Extensions/Infopanel/data


dist_install_DATA = \
	iperf \
	iperf.7z \
	ofgwrite \
	screenshot.sh  \
	unrar-free  \
	unzip  
	PluginHDDi.sh \
	PluginHDDu.sh  \
	PluginUSBi.sh  \
	PluginUSBu.sh
	
install-data-hook:
	@chmod +x $(DESTDIR)$(installdir)/iperf 
	@chmod +x $(DESTDIR)$(installdir)/ofgwrite
	@chmod +x $(DESTDIR)$(installdir)/unrar-free
	@chmod +x $(DESTDIR)$(installdir)/unzip
	@chmod +x $(DESTDIR)$(installdir)/screenshot.sh
	@chmod +x $(DESTDIR)$(installdir)/PluginHDDi.sh
	@chmod +x $(DESTDIR)$(installdir)/PluginHDDu.sh
	@chmod +x $(DESTDIR)$(installdir)/PluginUSBi.sh
	@chmod +x $(DESTDIR)$(installdir)/PluginUSBu.sh
