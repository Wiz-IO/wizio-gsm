##########################################################################
# Autor: WizIO 2021 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/wizio-gsm
# 
# Support: Comet Electronics 
#   https://www.comet.bg/en
##########################################################################

from os.path import join
from SCons.Script import (AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default, DefaultEnvironment)
from colorama import Fore
import click

env = DefaultEnvironment()

click.echo(
    "%s<<<<<<<<<<<< %s 2021 Georgi Angelov >>>>>>>>>>>>"
    % ( click.style("", fg="green", bold=True), env.BoardConfig().get("name").upper() )
)

elf = env.BuildProgram()
src = env.MakeHeader( join("$BUILD_DIR", "${PROGNAME}"), env.ElfToBin(join("$BUILD_DIR", "${PROGNAME}"), elf) )
AlwaysBuild( src )

upload = env.Alias("upload", src, [ 
    env.VerboseAction(env.AutodetectUploadPort, "Looking for upload port..."),
    env.VerboseAction("$UPLOADCMD", "Uploading: $PROGNAME"),
    env.VerboseAction("", "Ready"),
])
AlwaysBuild( upload )    

Default( src )
