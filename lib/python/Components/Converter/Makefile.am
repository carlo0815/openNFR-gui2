installdir = $(pkglibdir)/python/Components/Converter

if SPARK
mv installdir/bitratecalc.so_sh4 installdir/bitratecalc.so
rm -r installdir/bitratecalc.so_mips
else
mv installdir/bitratecalc.so_mips installdir/bitratecalc.so
rm -r installdir/bitratecalc.so_sh4
endif

dist_install_DATA = *.so
install_PYTHON = *.py
