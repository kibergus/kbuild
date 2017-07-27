#!/usr/bin/env python2
# NOTE: This magic hack is only to make it work from the same git repository.
# In normal life build system is installed appropriately and this line shuold not be there
__path__=["KBUILD_ROOT_PATH"]

from kbuild import kbuild_main, android, Task, Builder
import sh

builder = Builder()
android(builder, api_version="25", build_tools_version="25.0.0")

builder["compile"].before(sh.echo, "Look, I'm compiling the sources!")
builder["compile"].after(sh.echo, "The sources are compiled!")

kbuild_main(builder)
