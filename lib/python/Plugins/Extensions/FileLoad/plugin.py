from Plugins.Plugin import PluginDescriptor
import subprocess
cmd = ['python','-O','/usr/lib/enigma2/python/Plugins/Extensions/FileLoad/upload.pyo']
cmd1 = ['python','-O','/usr/lib/enigma2/python/Plugins/Extensions/FileLoad/delete.pyo']
extScript = subprocess.Popen(cmd,shell=False,stdout=subprocess.PIPE)
extScript = subprocess.Popen(cmd1,shell=False,stdout=subprocess.PIPE)
        
def Plugins(**kwargs):
    return PluginDescriptor()
