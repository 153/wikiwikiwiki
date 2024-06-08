import os, re, time

def page_exist(page):
    pagedir = os.listdir("pages") 
    if page + ".txt" in pagedir:
        return True
    return False

def link_processor(content, getlinks=0):
    w_link = "<a style='color:green' href='/w/{0}'>{0}</a>"
    n_link = "<a style='color:red' href='/e/{0}'>{0}</a>"
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

    content = content.replace("</a>'", "</a>")
    content = content.replace("</a>\\", "</a>")

    if getlinks == 1:
        return list(set(links))
    return content

def page_head(title):
    page = [f"<title>WWW: {title}</title>"]
    page.append("<link rel='stylesheet' href='/style.css'>")
    page.append(f"<h1>{title}</h1>")
    return page
