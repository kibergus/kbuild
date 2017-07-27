import sys

from core import Task, Builder
from android import android

def kbuild_main(builder):
    if len(sys.argv) < 2:
        print "Usage: {0} <task_name>".format(sys.argv[0])
        print "Known tasks: " + ", ".join(builder.task_names())
        sys.exit(0)

    builder.build(sys.argv[1])
