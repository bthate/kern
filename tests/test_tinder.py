# OKBOT - the ok bot !
#
#

import os, random, sys, time, unittest

from kern.obj import Object, get
from kern.hdl import Event, get_kernel, launch

param = Object()
param.add = ["test@shell", "bart"]
param.dne = ["test4", ""]
param.edt = ["mods.irc.Cfg", "mods.irc.Cfg server=localhost", "mods.irc.Cfg channel=#dunkbots"]
param.rm = ["reddit", ]
param.dpl = ["reddit title,summary,link",]
param.log = ["test1", ""]
param.flt = ["0", "1", ""]
param.fnd = ["log test2", "todo test3", "rss reddit"]
param.rss = ["https://www.reddit.com/r/python/.rss", ""]
param.tdo = ["test4", ""]

events = []
ignore = ["ps", "rm"]
nrtimes = 1

k = get_kernel()
print(repr(k))

class Event(Event):

    def reply(self, txt):
        if "v" in k.cfg.opts:
            print(txt)

class Test_Tinder(unittest.TestCase):

    def test_all(self):
        for x in range(k.cfg.index or 1):
            tests(k)

    def test_thrs(self):
        thrs = []
        for x in range(k.cfg.index or 1):
            launch(tests, k)
        consume(events)
        
def consume(elems):
    fixed = []
    res = []
    for e in elems:
        r = e.wait()
        res.append(r)
        fixed.append(e)
    for f in fixed:
        try:
            elems.remove(f)
        except ValueError:
            continue
    k.stop()
    return res
    
def tests(b):
    keys = list(k.cmds)
    print(keys)
    random.shuffle(keys)
    for cmd in keys:
        if cmd in ignore:
            continue
        events.extend(do_cmd(cmd))

def do_cmd(cmd):
    exs = get(param, cmd, [""])
    e = list(exs)
    random.shuffle(e)
    events = []
    nr = 0
    for ex in e:
        nr += 1
        txt = cmd + " " + ex 
        if "-v" in sys.argv:
            print(txt)
        e = Event()
        e.txt = txt
        k.queue.put(e)
        events.append(e)
    return events
