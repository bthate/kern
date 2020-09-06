"data entry."

import time

from kern.obj import Object, find, fntime, save
from kern.csl import elapsed

def __init__():
    return ("Log", "Todo", "dne", "log", "tdo")

class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""

class Todo(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""

def dne(event):
    if not event.args:
        return
    selector = {"txt": event.args[0]}
    db = Db()
    for o in db.find("mods.ent.Todo", selector):
        o._deleted = True
        save(o)
        event.reply("ok")
        break

def log(event):
    if not event.rest:
        return
    l = Log()
    l.txt = event.rest
    save(l)
    event.reply("ok")

def tdo(event):
    if not event.rest:
        return
    o = Todo()
    o.txt = event.rest
    save(o)
    event.reply("ok")
