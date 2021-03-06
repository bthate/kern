"display rss feed in your IRC channel."

import datetime, html.parser, os, random, re, time, urllib

from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

from kern.obj import Default, Object, all, edit, find, get, last, save, update
from kern.obj import Cfg as BaseCfg
from kern.hdl import Repeater, get_kernel, launch

from .irc import bus

def __dir__():
    return ("Cfg", "Feed", "Rss", "Seen", "Fetcher", "rm", "dpl", "fed", "ftc", "rss")

debug = False

try:
    import feedparser
    gotparser = True
except ModuleNotFoundError:
    gotparser = False

debug = False

timestrings = [
    "%a, %d %b %Y %H:%M:%S %z",
    "%d %b %Y %H:%M:%S %z",
    "%d %b %Y %H:%M:%S",
    "%a, %d %b %Y %H:%M:%S",
    "%d %b %a %H:%M:%S %Y %Z",
    "%d %b %a %H:%M:%S %Y %z",
    "%a %d %b %H:%M:%S %Y %z",
    "%a %b %d %H:%M:%S %Y",
    "%d %b %Y %H:%M:%S",
    "%a %b %d %H:%M:%S %Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dt%H:%M:%S+00:00",
    "%a, %d %b %Y %H:%M:%S +0000",
    "%d %b %Y %H:%M:%S +0000",
    "%d, %b %Y %H:%M:%S +0000"
]


def init(krn):
    "krn is kernel the init takes place on. return the fetcher started."
    f = Fetcher()
    f.start()
    return f

class Cfg(BaseCfg):

    "rss configuration."

    def __init__(self):
        super().__init__()
        self.dosave = True

class Feed(Default):

    "data received."

class Rss(Object):

    "rss url."

    def __init__(self):
        super().__init__()
        self.rss = ""

class Seen(Object):
    "all the urls seen."
    def __init__(self):
        super().__init__()
        self.urls = []

class Fetcher(Object):

    "fetch the rss feeds."

    cfg = Cfg()
    seen = Seen()

    def __init__(self):
        super().__init__()
        self._thrs = []

    def display(self, o):
        "o is the object to display"
        result = ""
        dl = []
        try:
            dl = o.display_list.split(",")
        except AttributeError:
            pass
        if not dl:
            dl = self.cfg.display_list.split(",")
        if not dl or not dl[0]:
            dl = ["title", "link"]
        for key in dl:
            if not key:
                continue
            data = get(o, key, None)
            if key == "link" and self.cfg.tinyurl:
                datatmp = get_tinyurl(data)
                if datatmp:
                    data = datatmp[0]
            if data:
                data = data.replace("\n", " ")
                data = strip_html(data.rstrip())
                data = unescape(data)
                result += data.rstrip()
                result += " - "
        return result[:-2].rstrip()

    def fetch(self, rssobj):
        "obj is the rss object to fetch"
        counter = 0
        objs = []
        if not rssobj.rss:
            return 0
        for o in reversed(list(get_feed(rssobj.rss))):
            if not o:
                continue
            f = Feed()
            update(f, rssobj)
            update(f, o)
            u = urllib.parse.urlparse(f.link)
            if u.path and not u.path == "/":
                url = "%s://%s/%s" % (u.scheme, u.netloc, u.path)
            else:
                url = f.link
            if url in Fetcher.seen.urls:
                continue
            Fetcher.seen.urls.append(url)
            counter += 1
            objs.append(f)
            if self.cfg.dosave:
                save(f)
        if objs:
            save(Fetcher.seen)
        for o in objs:
            txt = self.display(o)
            for bot in bus:
                bot.announce(txt)
        return counter

    def run(self):
        "does one run of fetching."
        thrs = []
        for o in all("mods.rss.Rss"):
            thrs.append(launch(self.fetch, o))
        return thrs

    def start(self, repeat=True):
        "repeat is boolean whether to start or not start the Repeater."
        last(Fetcher.cfg)
        last(Fetcher.seen)
        if repeat:
            repeater = Repeater(300.0, self.run)
            repeater.start()

    def stop(self):
        "save seen."
        save(self.seen)


def get_feed(url):
    "fetch a feed."
    if debug:
        return [Object(), Object()]
    try:
        result = get_url(url)
    except (HTTPError, URLError):
        return [Object(), Object()]
    if gotparser:
        result = feedparser.parse(result.data)
        if "entries" in result:
            for entry in result["entries"]:
                yield entry
    else:
        print("feedparser is missing")
        return [Object(), Object()]

def file_time(timestamp):
    "timestamp is the unix timestamp to derive a filename from."
    s = str(datetime.datetime.fromtimestamp(timestamp))
    return s.replace(" ", os.sep) + "." + str(random.randint(111111, 999999))

def get_tinyurl(url):
    "query tinyurl"
    postarray = [
        ('submit', 'submit'),
        ('url', url),
        ]
    postdata = urlencode(postarray, quote_via=quote_plus)
    req = Request('http://tinyurl.com/create.php', data=bytes(postdata, "UTF-8"))
    req.add_header('User-agent', useragent())
    for txt in urlopen(req).readlines():
        line = txt.decode("UTF-8").strip()
        i = re.search('data-clipboard-text="(.*?)"', line, re.M)
        if i:
            return i.groups()
    return []

def get_url(url):
    "url is used to fetch a webpage."
    print(url)
    url = urllib.parse.urlunparse(urllib.parse.urlparse(url))
    req = urllib.request.Request(url)
    req.add_header('User-agent', useragent())
    response = urllib.request.urlopen(req)
    response.data = response.read()
    return response

def strip_html(text):
    "text is string to strip."
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def to_time(daystr):
    "convert a string into a timestamp."
    daystr = daystr.strip()
    if "," in daystr:
        daystr = " ".join(daystr.split(None)[1:7])
    elif "(" in daystr:
        daystr = " ".join(daystr.split(None)[:-1])
    else:
        try:
            d, h = daystr.split("T")
            h = h[:7]
            daystr = " ".join([d, h])
        except (ValueError, IndexError):
            pass
    res = 0
    for tstring in timestrings:
        try:
            res = time.mktime(time.strptime(daystr, tstring))
            break
        except ValueError:
            try:
                res = time.mktime(time.strptime(" ".join(daystr.split()[:-1]), tstring))
            except ValueError:
                pass
        if res:
            break
    return res

def unescape(text):
    "text is a tring to unescape."
    txt = re.sub(r"\s+", " ", text)
    return html.parser.HTMLParser().unescape(txt)

def useragent():
    "return useragent string."
    return 'Mozilla/5.0 (X11; Linux x86_64) OQ +http://github.com/bthate/oq)'

def rm(event):
    "!rm <matchinurl> - remove feed url."
    if not event.args:
        return
    selector = {"rss": event.args[0]}
    nr = 0
    got = []
    for o in find("ob.rss.Rss", selector):
        nr += 1
        o._deleted = True
        got.append(o)
    for o in got:
        save(o)
    event.reply("ok")

def dpl(event):
    "!dpl <matchinurl> [key1,key2,key3] - set keys to display."
    if len(event.args) < 2:
        return
    setter = {"display_list": event.args[1]}
    for o in find("ob.rss.Rss", {"rss": event.args[0]}):
        edit(o, setter)
        save(o)
    event.reply("ok")

def fed(event):
    "!fed <matchindata> - search saved feeds."
    if not event.args:
        return
    match = event.args[0]
    nr = 0
    res = list(find("ob.rss.Feed", {"link": match}))
    for o in res:
        if match:
            event.reply("%s %s - %s - %s - %s" % (nr,
                                                  o.title,
                                                  o.summary,
                                                  o.updated or o.published or "nodate",
                                                  o.link))
        nr += 1
    if nr:
        return
    res = list(db.find("ob.rss.Feed", {"title": match}))
    for o in res:
        if match:
            event.reply("%s %s - %s - %s" % (nr, o.title, o.summary, o.link))
        nr += 1
    res = list(db.find("ob.rss.Feed", {"summary": match}))
    for o in res:
        if match:
            event.reply("%s %s - %s - %s" % (nr, o.title, o.summary, o.link))
        nr += 1
    if not nr:
        event.reply("no results found")

def ftc(event):
    "!ftc - runs one fetch of rss feeds."
    res = []
    thrs = []
    fetchr = Fetcher()
    fetchr.start(False)
    thrs = fetchr.run()
    for thr in thrs:
        res.append(thr.join() or 0)
    if res:
        event.reply("fetched %s" % ",".join([str(x) for x in res]))
        return
    event.reply("no feeds registered.")

def rss(event):
    "!rss <feedurl>"
    if not event.args:
        return
    url = event.args[0]
    res = list(find("ob.rss.Rss", {"rss": url}))
    if res:
        event.reply("feed is already known.")
        return
    o = Rss()
    o.rss = event.args[0]
    save(o)
    event.reply("ok")

fetcher = Fetcher()
