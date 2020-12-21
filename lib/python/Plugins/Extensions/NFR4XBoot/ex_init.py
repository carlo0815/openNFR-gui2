import sys, nfr4xboot
import os
import shutil
for delusb in os.listdir('/media/nfr4xboot/NFR4XBootUpload'):
	if delusb.split('.')[-1] != 'zip':
		if os.path.isfile('/media/nfr4xboot/NFR4XBootUpload/' + delusb) is True:
			os.remove('/media/nfr4xboot/NFR4XBootUpload/' + delusb)
		else:    
			shutil.rmtree('/media/nfr4xboot/NFR4XBootUpload/' + delusb)
if len(sys.argv) < 8:
	pass
else:
	nfr4xboot.NFR4XBootMainEx(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])

