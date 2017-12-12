import sys, nfr4xboot
if len(sys.argv) < 8:
    pass
else:
    nfr4xboot.NFR4XBootMainEx(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])

