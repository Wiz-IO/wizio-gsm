##########################################################################
# Autor: WizIO 2021 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/wizio-gsm
# 
# Support: Comet Electronics 
#   https://www.comet.bg/en
##########################################################################

import os, struct, math
from os.path import join
from SCons.Script import Builder
from common import *
from MT6261 import upload_app

def dev_uploader(target, source, env):
    return upload_app( env.BoardConfig().get('build.core'), 
                       join(env.get('BUILD_DIR'), 'program.bin'), 
                       env.get('UPLOAD_PORT'), 
                       env.BoardConfig().get("build.device_format_fat", "no") == 'yes',
                       env.BoardConfig().get("build.device_reset",      "no") == 'yes'  )

def dev_header(target, source, env):  
    dat = source[0].path
    bin = dat.replace('.dat', '.bin')
    dat_size = os.stat( dat ).st_size
    rem_size = 16 - dat_size % 16
    dat_size += rem_size
    dst = open(bin, 'wb')
    arr = [0x4D, 0x4D, 0x4D, 0x01, 0x40, 0x00, 0x00, 0x00, 0x46, 0x49, 0x4C, 0x45, 0x5F, 0x49, 0x4E, 0x46]
    data = bytearray(arr)
    dst.write(data) 
    arr = [0x4F, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x70, 0x07, 0x00, 0x00, 0x70, 0x2C, 0x10] # M66
    data = bytearray(arr)
    dst.write(data)     
    dst.write( struct.pack('<i', dat_size + 64) ) # write size 
    arr = [ 0xFF, 0xFF, 0xFF, 0xFF, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    data = bytearray(arr)
    dst.write(data)     
    arr = [0x40, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    data = bytearray(arr)
    dst.write(data)   
    src = open(dat, 'rb')
    dst.write( src.read() )
    for i in range(rem_size):
        dst.write(b'\0')
    print( 'BIN FILE SIZE:', math.trunc(dst.tell()/1024), 'kB' )
    src.close()
    dst.close() 

    f = open(dat.replace('.dat', '.cfg'), 'w')
    f.write('program.bin\n')
    f.close    

def dev_create_template(env):
    config = join(env.subst('$PROJECT_DIR'), 'config')
    do_mkdir(config)
    template = join(env.framework_dir, 'templates', env.core)
    files = [
        'custom_task_cfg.h',
        'custom_feature_def.h',
        'custom_gpio_cfg.h',
        'custom_heap_cfg.h',                        
        'custom_config.c',
        'custom_sys_cfg.c',
    ]    
    for file_name in files:
        do_copy(template, config, file_name)

    src = join( env.subst('$PROJECT_DIR'), 'src' )
    if False == os.path.isfile( join( src, 'main.cpp' ) ):
        do_copy(template, src, 'main.c' )         
   
def dev_init(env):
    dev_set_compiler(env)
    SDK_DIR = join( env.framework_dir, env.platform, env.core )
    dev_set_linker(env, "c_m66.ld")
    dev_set_nano(env)
    dev_create_template(env)
    env.Append(
        ASFLAGS    = [],
        CPPDEFINES = [],
        CPPPATH    = [
            join('$PROJECT_DIR', 'config'),
            join(SDK_DIR, 'SDK', 'include'),
            join(SDK_DIR, 'SDK', 'ril', 'inc'),
        ],
        CCFLAGS    = [],
        CFLAGS     = [
            '-fno-builtin',
            '-fno-strict-aliasing',            
            '-fsingle-precision-constant',  
            '-Wno-old-style-declaration',        
        ],
        CXXFLAGS   = [],
        LINKFLAGS  = [ 
            "-nostartfiles",
            "-mno-unaligned-access",            
            '-Wl,--gc-sections,--relax', 
        ],
        LIBPATH    = [ join(SDK_DIR, 'LIB') ], 
        LIBS       = [ 'm', 'c', 'gcc', '_app_start_{}'.format(env.core) ], 
        BUILDERS = dict(
            ElfToBin = Builder(
                action = env.VerboseAction(' '.join([ '$OBJCOPY', '-O', 'binary', '$SOURCES', '$TARGET', ]), 'Building $TARGET'),
                suffix = '.dat'
            ),    
            MakeHeader = Builder( 
                action = env.VerboseAction(dev_header, ''),
                suffix = '.bin'
            )       
        ), 
        UPLOADCMD = dev_uploader        
    )

    env.BuildSources( join('$BUILD_DIR', 'config'), join('$PROJECT_DIR', 'config') )
    env.BuildSources( join('$BUILD_DIR', 'ril'), join(SDK_DIR, 'SDK', 'ril', 'src') )