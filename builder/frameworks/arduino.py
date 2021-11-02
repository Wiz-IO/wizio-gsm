##########################################################################
# Autor: WizIO 2021 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/wizio-gsm
# 
# Support: Comet Electronics 
#   https://www.comet.bg/en
##########################################################################

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
env.platform = "arduino"
module = env.platform + "-" + env.BoardConfig().get("build.core")
m = __import__(module)       
globals()[module] = m
m.dev_init(env)
#print( env.Dump() )
