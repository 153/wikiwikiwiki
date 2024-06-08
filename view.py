from flask import Blueprint, request, redirect
import markdown
import os, re, time

view = Blueprint("view", __name__)

def page_index():
    pagedir = os.listdir("pages")
    page = "<link rel='stylesheet' href='/style.css'>"
    page += "<h2>AllPages</h2><ul>"
    page += "<style>a {color: green}</style>"
    
    for p in pagedir:
        if p[-4:] == ".txt":
            p = p[:-4]
            page += f"<li> <a href='/w/{p}'>{p}</a>"
    return page

def page_exist(page):
    pagedir = os.listdir("pages") 
    if page + ".txt" in pagedir:
        return True
    return False

def load_page(page):
    if not page_exist(page):
        return "404"
    with open(f"./pages/{page}.txt", "r") as pagef:
        pagef = pagef.read()
    page = format_page(page, pagef)
    return page

def link_processor(content):
    w_link = "<a style='color:green' href='/w/{0}'>{0}</a>"
    n_link = "<a style='color:red' href='/c/{0}'>{0}</a>"
    links = []
    pascal = r"\b([A-Z][a-z]+){2,}\b"
    def check_pascal(result):
        links.append(result)
        if page_exist(result):
            return w_link.format(result)
        return n_link.format(result)
    content = re.sub(pascal, lambda x: check_pascal(x.group()), content)

    brackets = r"\[\[([a-zA-Z0-9_]+)\]\]"
    def check_bracket(result):
        result = result[2:-2]
        links.append(result)
        if page_exist(result):
            return w_link.format(result)
        return n_link.format(result)
    content = re.sub(brackets, lambda x: check_bracket(x.group()), content)
    return content

def page_head(title):
    page = [f"<title>WWW: {title}</title>"]
    page.append("<link rel='stylesheet' href='/style.css'>")
    page.append(f"<h2>{title}</h2>")
    return page

def format_page(title, content):
    modified = time.gmtime(os.path.getmtime(f"pages/{title}.txt"))
    modified = time.strftime('%Y.%m.%d [%a] %H:%M', modified)
    
    template = page_head(title)
    
    content = markdown.markdown(content)
    content = link_processor(content)
    content = content.replace("</a>'", "</a>")
    content = content.replace("</a>\\", "</a>")
    
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
