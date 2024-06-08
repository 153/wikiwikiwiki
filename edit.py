import os, re, time
from flask import Blueprint, request, redirect
import markdown
import view
from utils import *

edit = Blueprint("edit", __name__)

@edit.route("/e/")
def new_page():
    return "Hi"

@edit.route("/e/", methods = ["POST"])
@edit.route("/e/<page>")
def page_editor(page=None):
    content = ""
    data = request.form
    if request.method == "GET":
        if page_exist(page):
            with open(f"pages/{page}.txt", "r") as content:
                content = content.read()
    else:
        if "title" in data:
            page = data["title"]
        if "content" in data:
            content = data["content"]

    with open("html/edit.html") as temp:
        temp = temp.read()
    preview = view.format_page(page, content, True)
    preview = temp.format(preview, content, page)
    head = "\n".join(page_head(f"Edit: {page}"))
    preview = head + preview
    return preview

def edit_page():
    return f"<pre> {data} </pre>"
