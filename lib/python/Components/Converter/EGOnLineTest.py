from Components.config import config
from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import eServiceCenter, eServiceReference, iServiceInformation
from Poll import Poll
from os import system
from Components.Network import iNetwork
from Components.config import ConfigYesNo

import threading

def hayinet():
    ret = True
    #try:
    #	ret = config.misc.spazeinfobarinet.value
    #except:
    #   pass

    return ret

class EGOnLineTest(Poll, Converter, object):
    ALL = 1
    INETCONECTION = 2
    NETCONECTION = 3

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.poll_interval = 10000
        self.poll_enabled = True

        if type == 'InetConection':
            self.poll_interval = 5000
            self.type = self.INETCONECTION
        elif type == 'NetConection':
            self.poll_interval = 5000
            self.type = self.NETCONECTION
        else:
            self.type = self.ALL

    @cached
    def getBoolean(self):
        ret = False
        service = self.source.service
        info = service and service.info()
        if not info:
            return False
        if self.type == self.INETCONECTION:
            if not hayinet():
                ret = False
            else:
                try:
                    f = open('/tmp/testinet.txt', 'r')
                    texto = f.read().replace('\n', '')
                    f.close()
                    if '1 packets transmitted, 1 packets received' in texto:
                        ret = True
                except:
                    pass

                try:
                    system('ping -q -c 1 -s 6 -w 2 www.google.com >/tmp/testinet.txt &')
                except:
                    pass

        elif self.type == self.NETCONECTION:
            try:
                adapters = [ (iNetwork.getFriendlyAdapterName(x), x) for x in iNetwork.getAdapterList() ]
            except:
                adapters = False

            if not adapters:
                ret = False
            else:
                puerta = '0.0.0.0'
                for x in adapters:
                    if iNetwork.getAdapterAttribute(x[1], 'up') is True:
                        puerta = str(iNetwork.getAdapterAttribute(x[1], 'gateway')).replace(',', '.').replace('[', '').replace(' ', '').replace(']', '')
                        break

                if puerta == '0.0.0.0':
                    ret = False
                else:
                    try:
                        f = open('/tmp/testnet.txt', 'r')
                        texto = f.read().replace('\n', '')
                        f.close()
                        if '1 packets transmitted, 1 packets received' in texto:
                            ret = True
                    except:
                        pass

                    try:
                        system('ping -q -c 1 -s 6 -w 2 ' + puerta + ' >/tmp/testnet.txt &')
                    except:
                        pass

        return ret

    boolean = property(getBoolean)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] == self.type:
            Converter.changed(self, what)