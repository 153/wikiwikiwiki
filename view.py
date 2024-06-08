import os, re, time
from flask import Blueprint, request, redirect
import mistune
from utils import *

view = Blueprint("view", __name__)

markdown = mistune.create_markdown(escape=False,
    plugins=['strikethrough', 'footnotes', 'table', 'url',
             'task_lists', 'abbr', 'mark', 'superscript',
             'subscript', 'spoiler'])

def load_page(page):
    if not page_exist(page):
        return "404"
    with open(f"./pages/{page}.txt", "r") as pagef:
        pagef = pagef.read()
    page = format_page(page, pagef)
    return page

def format_page(title, content, preview=0):
    content = markdown(content)
    content = link_processor(content)
    if preview is True:
        return content
    template = []
    template = page_head(title)
    modified = time.gmtime(os.path.getmtime(f"pages/{title}.txt"))
    modified = time.strftime('%Y.%m.%d [%a] %H:%M', modified)
    template.append(content)
    template.append("<hr>")
    template.append(f"<a style='color:darkred' href='/w/'>home</a> ")
    template.append(f"// <a style='color:darkred' href='/r/{title}'>reverse</a>")
    template.append(f"// <a style='color:darkred' href='/e/{title}'>edit</a>")
    template.append("// modified: " + modified)

    return "\n".join(template)

def page_index():
    pagedir = os.listdir("pages")
    page = "\n".join(page_head("All pages"))
    page += "\n<style>a {color: green}</style>"
    page += "\n<ol style='columns: 3'>"
    
    for p in sorted(pagedir):
        if p[-4:] == ".txt":
            p = p[:-4]
            page += f"\n<li> <a href='/w/{p}'>{p}</a>"
    page += "\n</ol>\n<a style='color:darkred' href='/w/'>home</a>"
    return page

def recent_changes():
    with open("data/log.txt", "r") as logfile:
        logfile = logfile.read().strip().splitlines()
    logfile = logfile[-20:]
    log = []
    for i in logfile:
        i = i.split()
        if len(i) > 5:
            i[4] = " ".join(i[4])
        pn = i[1].split(".")[0]
        pn = f"<a style='color:green' href='/w/{pn}'>{pn}</a>"
        mod = time.gmtime(int(i[0]))
        mod = time.strftime('%Y-%m-%d %H:%M', mod)
        i = [pn, i[4], mod, i[3]]
        log.append("<tr><td>" + "<td>".join(i))
    page = "\n".join(page_head("Recent changes"))
    page += "\n<table>"
    page += "\n<th>Page<th>Author<th>Time<th>Char\n"
    page += "\n".join(log[::-1])
    page += "\n</table>\n<p><a style='color:darkred' href='/w/'>home</a>"
    return page

def popular():
    with open("data/links.txt", "r") as linkdb:
        linkdb = linkdb.read().strip().splitlines()
    linkdb = [x.split() for x in linkdb]
    linkdb.sort(key=len, reverse=True)
    
    exist = []
    nexist = []
    for x in linkdb:
        if page_exist(x[0]):
            exist.append([x[0], str(len(x) - 1)])
        else:
            nexist.append([x[0], str(len(x) - 1)])
            
    popular = []
    wanted = []
    orphans = []
    for e in exist:
        if int(e[1]) > 0:
            popular.append(f"<a style='color:green' href='/w/{e[0]}'>{e[0]}</a>")
            if int(e[1]) > 1:
                popular[-1] += f" ({e[1]})"
        else:
            orphans.append(f"<a style='color:green' href='/w/{e[0]}'>{e[0]}</a>")
    for n in nexist[:30]:
        wanted.append(f"<a style='color:red' href='/e/{n[0]}'>{n[0]}</a>")
        if int(n[1]) > 1:
            wanted[-1] += f" ({n[1]})"

    popular = "<b>Popular:</b> <ol><li>" + "<li>".join(popular[:30]) + "</ol>"
    orphans = "<b>Orphans:</b> <ol><li>" + "<li>".join(orphans[:30]) + "</ol>"
    wanted = "<b>Wanted:</b><ol><li>" + "<li>".join(wanted) + "</ol>"

    page = page_head("Popularity")
    page.append("Top 30 for each category. <p>")
    page.append("<div class='row'>")
    for i in [popular, orphans, wanted]:
        page.append(f"<div class='column'>{i}</div>")
    page.append("</div>")
    page = "\n".join(page)
    page += "<a style='color:darkred' href='/w/'>home</a>"
    return page
        
    
@view.route("/")
def home():
    return redirect("/w/")

@view.route("/w/")
def home_page():
    return load_page("HomePage")

@view.route("/w/<page>")
def page_v(page):
    if page == "HomePage":
        return home_page()
    elif page == "all":
        return page_index()
    elif page == "recent":
        return recent_changes()
    elif page == "popular":
        return popular()

    elif page_exist(page):
        return load_page(page)
        
    return redirect(f"/e/{page}")

@view.route("/r/<title>")
def backlinks(title):
    page = page_head(f"Reverse: {title}")
    page.append("<ul>")
    page.append(f"<li><a style='color:darkred' href='/w/{title}'>{title}</a><p>")
    with open("data/links.txt", "r") as linkdb:
        linkdb = linkdb.read().strip().splitlines()
    linkdb = [x.split() for x in linkdb]
    print(linkdb)
    links = []
    for x in linkdb:
        if x[0] == title:
            links += x[1:]
    print(links)
    linklist = []
    for x in links:
        if page_exist(x):
            linklist.append(f"<li><a style='color:green' href='/w/{x}'>{x}</a>")
        else:
            linklist.append(f"<li><a style='color:red' href='/e/{x}'>{x}</a>")
    page += sorted(linklist)
    page.append("</ul>")
    print(links)
    return "\n".join(page)
