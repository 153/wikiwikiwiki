import os, re, time
from flask import Blueprint, request, redirect
import markdown
import view
import whitelist as wl
from utils import *

edit = Blueprint("edit", __name__)

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
    print(data)
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
            print(title)
        if "content" in data:
            content = data["content"].strip()
        if "author" in data:
            if len(author):
                author = data["author"]
        if not "preview" in data:
            if len(title):
                return publish(title, content, author)

    if not wl.approve():
        return wl.show_captcha(0, f"/e/{title}")
    with open("html/edit.html") as temp:
        temp = temp.read()
    preview = view.format_page(title, content, True)
    preview = temp.format(preview, content, title, author)
    head = "\n".join(page_head(f"Edit: {title}"))
    preview = head + preview
    return preview

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

    # Cleanup input
    data = request.form
    title = title[:20]
    content = content.strip()[:10000]
    if "\r" in content:
        content = content.replace("\r", "")
    author = author.strip()[:25]

    # Debug 
    page = [f"<meta http-equiv='refresh' content='3; url=/w/{title}'>"]
    page.append("You will be redirected in 3 seconds...")
    page.append("<pre>")
    page.append(f"title: {title}")
    page.append(f"content:\n{content}")
    page.append(f"author: {author}")

    fn = title + ".txt"

    # Get revision number
    revisions = []
    pages = os.listdir("pages")
    for f in pages:
        if f.startswith(fn + "."):
            revisions.append(f)

    fnr = fn + "." + str(len(revisions))
    page.append(str(revisions))
    page.append(f"Revision: {fnr}")

    # Write the page 
    with open(f"pages/{fnr}", "w") as rev:
        rev.write(content)
    if len(content) > 0:
        with open(f"pages/{fn}", "w") as rev:
            rev.write(content)
    else:
        os.remove(f"pages/{fn}")

    return "\n".join(page)
