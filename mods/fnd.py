"find objects."

import os, time
import kern.obj

from kern.csl import elapsed, parse
from kern.hdl import find_shorts
from kern.obj import cdir, find, format, fntime, get, keys

def __dir__():
    return ("fnd",)

def fnd(event):
    "find object by provding key==value getters."
    if not event.args:
        wd = os.path.join(kern.obj.workdir, "store", "")
        cdir(wd)
        fns = os.listdir(wd)
        fns = sorted({x.split(os.sep)[0] for x in fns})
        if fns:
            event.reply("|".join(fns))
        return
    parse(event, event.txt)
    otype = event.args[0]
    shorts = find_shorts("mods")
    otypes = get(shorts, otype, [otype,])
    args = list(keys(event.gets))
    try:
        arg = event.args[1:]
    except ValueError:
        arg = []
    args.extend(arg)
    nr = -1
    for otype in otypes:
        for o in find(otype, event.gets, event.index, event.timed):
            nr += 1
            if "f" in event.opts:
                pure = False
            else:
                pure = True
            txt = "%s %s" % (str(nr), format(o, args, pure))
            if "t" in event.opts:
                txt += " %s" % (elapsed(time.time() - fntime(o.__stamp__)))
            event.reply(txt)
    if nr == -1:
        event.reply("no matching objects found.")
