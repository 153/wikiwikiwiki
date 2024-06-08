import os, re, time
from flask import Blueprint, request, redirect
import markdown
from utils import *

view = Blueprint("view", __name__)

def load_page(page):
    if not page_exist(page):
        return "404"
    with open(f"./pages/{page}.txt", "r") as pagef:
        pagef = pagef.read()
    page = format_page(page, pagef)
    return page

def format_page(title, content, preview=0):
    content = markdown.markdown(content)
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
    template.append(f"// <a style='color:darkred' href='/e/{title}'>edit</a>")
    template.append("// modified: " + modified)

    return "\n".join(template)

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
    if page == "AllPages":
        return page_index()
    elif page_exist(page):
        return load_page(page)
        
    return page + " -- Page does not exist"
