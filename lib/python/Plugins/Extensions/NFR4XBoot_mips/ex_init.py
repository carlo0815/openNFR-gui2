import sys, nfr4xboot
if len(sys.argv) < 4:
    pass
else:
    nfr4xboot.NFR4XBootMainEx(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
