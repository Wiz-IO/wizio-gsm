##########################################################################
# Autor: WizIO 2021 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/wizio-gsm
# 
# Support: Comet Electronics 
#   https://www.comet.bg/en
##########################################################################

import os
from shutil import copyfile
from os.path import join
from SCons.Script import DefaultEnvironment, Builder
from colorama import Fore

def do_copy(src, dst, name):
    if False == os.path.isfile( join(dst, name) ):
        copyfile( join( src, name ), join( dst, name ) )                 

def do_mkdir(dir):
    if False == os.path.isdir( dir ):
        try:
            os.mkdir( dir )
        except OSError:
            print ("[ERROR] Creation of the directory %s failed" % dir)
            exit(1)
    return dir

def dev_set_linker(env, default): # set default or custom linker script
    #[INI] board_build.linker = $PROJECT_DIR/custom.ld
    linker = env.BoardConfig().get("build.linker", "default")
    if "default" != linker and "$PROJECT_DIR" in linker:
        linker = linker.replace('$PROJECT_DIR', env["PROJECT_DIR"]).replace("\\", "/")
        env.Append( LDSCRIPT_PATH = linker )    
        print('  * LINKER       : Custom')
    else:
        env.Append( LDSCRIPT_PATH = default )
        print('  * LINKER       : Default')

def dev_set_memory(env): # set memory values to linker
    #[INI] board_build.stack = ?
    value = env.BoardConfig().get("build.stack", "0x0400")
    print('  * STACK SIZE   :', value)     
    env.Append( LINKFLAGS = ['-Xlinker', '--defsym=STACKSIZE=' + value] ) 
    #[INI] board_build.heap = ?
    value = env.BoardConfig().get("build.heap", "0x8000")
    print('  * HEAP SIZE    :', value)  
    env.Append( 
        CPPDEFINES = [ "HEAP_SIZE=" + value ],
        LINKFLAGS  = ['-Xlinker', '--defsym=HEAPSIZE=' + value] 
    )  

def dev_set_nano(env): 
    #[INI] board_build.nano = disable
    env.nano = []     
    if env.BoardConfig().get("build.nano", "enable") == "enable":
        env.nano = ["-specs=nano.specs", "-u", "_printf_float", "-u", "_printf_double"] # "_scanf_float"
    if len(env.nano) > 0: print('  * SPECS        :', env.nano[0][7:])
    else:                 print('  * SPECS        : default')
    return env.nano

def dev_set_compiler(env):
    env.Replace(
        BUILD_DIR = env.subst("$BUILD_DIR").replace("\\", "/"),
        AR="arm-none-eabi-ar",
        AS="arm-none-eabi-as",
        CC="arm-none-eabi-gcc",
        GDB="arm-none-eabi-gdb",
        CXX="arm-none-eabi-g++",
        OBJCOPY="arm-none-eabi-objcopy",
        RANLIB="arm-none-eabi-ranlib",
        SIZETOOL="arm-none-eabi-size",
        ARFLAGS=["rc"],
        SIZEPROGREGEXP=r"^(?:\.text|\.data|\.bootloader)\s+(\d+).*",
        SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit)\s+(\d+).*",
        SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
        SIZEPRINTCMD='$SIZETOOL --mcu=$BOARD_MCU -C -d $SOURCES',
        PROGSUFFIX=".elf",  
    )
    env.libs = [] 
    env.nano = [] 
    env.mcu           = env.BoardConfig().get("build.mcu", "default")      # chip info
    env.core          = env.BoardConfig().get("build.core", "default")     # arduino core
    env.variant       = env.BoardConfig().get("build.variant", "default")  # arduino variant
    env.cortex        = env.BoardConfig().get("build.cortex", "default")
    env.optimization  = env.BoardConfig().get("build.optimization", "-Os")
    env.framework_dir = env.PioPlatform().get_package_dir('framework-wizio-gsm')

    env.Append(
        ASFLAGS    = [ env.cortex, "-x", "assembler-with-cpp" ],
        CPPDEFINES = [],
        CPPPATH    = [
            join("$PROJECT_DIR", "src"),
            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include"), 
            join("$PROJECT_DIR", "config")              
        ],
        CCFLAGS    = [
            env.cortex,
            env.optimization,
            "-Wall",
            "-Wextra",
            "-Wfatal-errors",
            "-Wno-sign-compare",
            "-Wno-type-limits",
            "-Wno-unused-parameter",
            "-Wno-unused-function",
            "-Wno-unused-but-set-variable",
            "-Wno-unused-variable",
            "-Wno-unused-value",
            "-Wno-unused-label",
            "-Wno-strict-aliasing",
            "-Wno-maybe-uninitialized",
            "-Wno-implicit-fallthrough",
            "-Wno-missing-field-initializers",            
        ],
        CFLAGS = [
            env.cortex,
            "-Wno-discarded-qualifiers",
            "-Wno-ignored-qualifiers",
            '-Wno-pointer-sign',            
        ],
        CXXFLAGS = [
            "-fno-rtti",
            "-fno-exceptions",
            "-fno-threadsafe-statics",
            "-fno-non-call-exceptions",
            "-fno-use-cxa-atexit",
        ],
        LINKFLAGS = [
            env.cortex,
            env.optimization,
            env.nano
        ],  
    )  
