"edit an object."

import kern.obj

from kern.obj import ENOCLASS, edit, get_cls, lasttype, save
from kern.hdl import list_files, find_shorts

def __dir__():
    return ("edt",)

def edt(event):
    "!edt loweredclassname) - edit the last object of a class."
    if not event.args:
        event.reply(list_files(kern.obj.workdir) or "no files yet")
        return
    cn = event.args[0]
    shorts = find_shorts(__name__)
    if shorts:
        cn = shorts[0]
    try:
        l = lasttype(cn)
    except IndexError:
        return
    if not l:
        try:
            c = get_cls(cn)
            l = c()
            event.reply("created %s" % cn)
        except ENOCLASS:
            event.reply(list_files(kern.obj.workdir) or "no files yet")
            return
    if len(event.args) == 1:
        event.reply(l)
        return
    if len(event.args) == 2:
        setter = {event.args[1]: ""}
    else:
        setter = {event.args[1]: event.args[2]}
    edit(l, setter)
    save(l)
    event.reply("ok")
