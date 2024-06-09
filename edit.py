import os, re, time
from flask import Blueprint, request, redirect
import view
import whitelist as wl
from utils import *

edit = Blueprint("edit", __name__)

def fn_check(fn):
    print(fn)
    if " " in fn:
        fn = fn.replace(" ", "_")
    fn = re.sub(r"[^a-zA-Z0-9_]", "", fn)
    print(fn)
    return fn

def publish(title, content, author=None):
    if not wl.approve():
        return wl.show_captcha(0, f"/e/{title}")
    if title in ["HomePage", "all", "MarkUp"]:
        return "Sorry, you can't edit these pages."

    ip = wl.get_ip()
    
    # Cleanup input
    data = request.form
    author = author[:25].strip()
    if "<" in author:
        author.replace("<", "")
    title = title[:20]
    if "\r" in content:
        content = content.replace("\r", "")
    content = content.strip()[:10000]

    # Debug 
    page = [f"<meta http-equiv='refresh' content='3; url=/w/{title}'>"]
    page.append("You will be redirected in 3 seconds...")
    page.append("<pre>")
    
    # Get revision number
    fn = title + ".txt"
    revisions = []
    pages = os.listdir("pages")
    for f in pages:
        if f.startswith(fn + "."):
            revisions.append(f)

    fnr = fn + "." + str(len(revisions))
    page.append(f"Revision: {fnr}")

    # Write the page 
    with open(f"pages/{fnr}", "w") as rev:
        rev.write(content)
    if len(content) > 0:
        with open(f"pages/{fn}", "w") as rev:
            rev.write(content)
    else:
        os.remove(f"pages/{fn}")

    lcon = str(len(content))
    update_log(fnr, lcon, author, ip)
    backlinks(title, content)

    return "\n".join(page)

def update_log(fn, lcon, author, ip):
    udt = str(int(time.time()))
    lf = "data/log.txt"
    with open(lf, "r") as logfile:
        logfile = logfile.read().strip().splitlines()
    line = " ".join([udt, fn, ip, lcon, author])
    logfile.append(line)
    logfile = "\n".join(logfile)
    with open(lf, "w") as log:
        log.write(logfile)

def backlinks(fn, content):
    links = {}
    with open("data/links.txt", "r") as linkdb:
        linkdb = linkdb.read().strip().splitlines()
    for line in linkdb:
        line = line.split(" ")
        links[line[0]] = line[1:]
    print(links)
    print("!!!!!")
    linksout = link_processor(content, 1)
    linksout = [x[:20] for x in linksout]
    print(linksout)
    
    if fn in linksout:
        linksout.remove(fn)
        
    for entry in linksout:
        if entry not in links:
            links[entry] = [fn]
        else:
            links[entry].append(fn)
            links[entry] = list(set(links[entry]))
    if fn not in links:
        links[fn] = []
        
    print("!!!")
    print(links)

    links = [" ".join([x, *links[x]]) for x in links]
    links = "\n".join(links)
    with open("data/links.txt", "w") as linkdb:
        linkdb.write(links)
    print(links)

@edit.route("/e/", methods=["GET"])
def new_page():
    head = "\n".join(page_head("Edit"))
    return head + "To create a new page, please follow a RedLink"

@edit.route("/e/", methods = ["POST"])
@edit.route("/e/<page>", methods=["POST", "GET"])
def page_editor(page=None):
    author = "Anonymous"
    title = ""
    content = ""
    data = request.form
    if request.method == "GET":
        if page_exist(page):
            with open(f"pages/{page}.txt", "r") as content:
                content = content.read()
            title = page
        else:
            title = fn_check(page)
    else:
        if "title" in data:
            title = fn_check(data["title"])
        if "content" in data:
            content = data["content"].strip()
        if "author" in data:
            if len(data["author"]):
                author = data["author"]
        if not "preview" in data:
            if len(title):
                return publish(title, content, author)

    if len(content):
        if "\r" in content:
            content = content.replace("\r", "")
    if not wl.approve():
        return wl.show_captcha(0, f"/e/{title}")
    with open("html/edit.html") as temp:
        temp = temp.read()
    preview = view.format_page(title, content, True)
    preview = temp.format(preview, content, title, author)
    head = "\n".join(page_head(f"Edit: {title}"))
    preview = head + preview
    preview += "\n<hr><a style='color:darkred' href='/w/'>home</a> "
    preview += f"// <a style='color:darkred' href='/r/{title}'>reverse</a>"
    preview += f"// <a style='color:darkred' href='/w/{title}'>back</a>"
    return preview
