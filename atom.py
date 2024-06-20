import time
from flask import Blueprint

atom = Blueprint("atom", __name__)

tstring = "%Y-%m-%dT%H:%M:%S+00:00"
url = "https://wiki.gikopoi.com" # changeme!

feed_temp = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

<title>{title}</title>
<author><name>Anonymous</name></author>
<id>{url}</id>
<link rel="self" href="{link}" />
<updated>{published}</updated>"""

entry_temp = """\n<entry>
<title>{title}</title>
<link rel="alternate" href="{url}" />
<id>{url}</id>
<published>{published}</published>
<updated>{updated}</updated>
<content type="html">
{content}
</content>
</entry>"""

def unix2atom(unix):
    atom = time.strftime(tstring, time.localtime(int(unix)))
    return atom

@atom.route("/feed.atom")
def feed():
    link = url + "/feed.atom"
    entries = []
    with open("data/log.txt", "r") as log:
        log = log.read().strip().splitlines()
    log = log[::-1][:50]
    for entry in log:
        entry = entry.split()
        entry[0] = unix2atom(int(entry[0]))
        entry[1] = entry[1].split(".")
        e_url = url + "/o/" + entry[1][0] + "." + entry[1][2]
        entry = entry_temp.format(title=f"{entry[1][0]} #{entry[1][2]}",
                                  published=entry[0], updated=entry[0],
                                  url=e_url,
                                  content=f"{entry[1][0]} revision #{entry[1][2]}")
        entries.append(entry)
    publish = unix2atom(int(log[-1].split()[0]))
    entries.append("\n</feed>")
    entries = "".join(entries)
    output = feed_temp.format(title="Page edits on wikiwikiwiki",
                              url=link, link=link,
                              published=publish)
    output += entries
    return output

if __name__ == "__main__":
    feed()
