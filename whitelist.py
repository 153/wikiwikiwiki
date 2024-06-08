import os
import random
import string
import time

from captcha.image import ImageCaptcha
from flask import Blueprint, request

whitelist = Blueprint("whitelist", __name__)
klen = 5
image = ImageCaptcha(fonts=['droid.ttf'])
limit = 60

def get_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)

def randstr(length):
    letters = "234578"
    key = "".join(list(random.choice(letters) for i in range(length)))
    return key

def ldlog():
    with open("data/ips.txt", "r") as log:
        log = log.read().splitlines()
    log = [i.split(" ") for i in log]
    log = {i[1]: i for i in log}
    return log

def genkey(ip):
    entry = [str(int(time.time())), ip, str(randstr(klen))]
    image.write(entry[2], f'./static/cap/{ip}.png')
    return entry

def addlog(ip, ig=0):
    log = ldlog()
    if ip not in log or ig:
        entry = genkey(ip)
        log[ip] = entry
        fi = "\n".join([" ".join(log[x]) for x in log])
        with open("data/ips.txt", "w") as iplog:
            iplog.write(fi)
    return log

def approve(ip=0, key=""):
    if not ip:
        ip = get_ip()
    now = str(int(time.time()))
    log = ldlog()
    with open("data/bans.txt") as bans:
        bans = bans.read().splitlines()
    bans = [b.split(" ")[0] if " " else b for b in bans]
    for b in bans:
        if len(b.strip()) < 3:
            continue
        if ip.startswith(b):
            print("!", b, ip)
            return False
    if ip in log:
        if len(log[ip]) == 3:
            if log[ip][2] != key:
                return False
            log[ip].append(now)
            newl = [" ".join(log[k]) for k in log]
            newl = "\n".join(newl)
            with open("data/ips.txt", "w") as log:
                log.write(newl)
            return True
        else:
            return True
    return False

@whitelist.route('/captcha/')
def show_captcha(hide=0, redir='.'):
    ip = get_ip()
    mylog = addlog(ip)
    out = ""
    if not approve():
        with open("static/captcha.html", "r") as capt:
            capt = capt.read()
        out += capt.format(mylog[ip][1], redir)
    else:
        out += "Your IP is approved for posting"
    if hide:
        return out
    from view import page_head
    ph = "\n".join(page_head("Captcha"))
    return ph + out

@whitelist.route('/captcha/refresh')
def refresh():
    ip = get_ip()
    mylog = addlog(ip, 1)
    return "<meta http-equiv='refresh' content='0;URL=/captcha'>"

@whitelist.route('/captcha/check', methods=['POST', 'GET'])
def check(redir=""):
    key = request.args.get('key').lower()
    redir = request.args.get('redir')
    ip = get_ip()
    log = ldlog()
    out = approve(ip, key)
    if out == False:
        out = "You have filled the captcha incorrectly."
        out += "<p>Please <a href='/captcha'>solve the captcha.</a>"
    elif out == True:
        out = "You filled out the captcha correctly!"
        out += "<p>Please <a href='/rules'>review the rules</a> before posting."
        out += "<p>Redirecting in 3 seconds..."
        out += f"<hr><a href='{redir}'>back</a>"
        out += f"<meta http-equiv='refresh' content='3;URL={redir}'>"
        if os.path.isfile(f"./static/cap/{ip}.png"):
            os.remove(f"./static/cap/{ip}.png")
    from view import page_head
    ph = "\n".join(page_head("Captcha"))
    return ph + out

def flood():
    # Completely rewrite this
    ip = get_ip()
    tnow = str(int(time.time()))

    with open("data/log.txt", "r") as log:                
        log = log.read().splitlines()
    log = [x.split("<>") for x in log]
    log = [x for x in log if x[0] == ip]
    if not log: return False
    
    pause = int(tnow) - int(last[2])
    diff = limit - pause
    msg = diff
    if diff > 60:
        msg = f"{diff//60} minutes, {diff %60}"
    if diff > 0:
        print("flood")
        print(msg)
        return "<b>Error: flood detected.</b>" \
            + f"<p>Please wait {msg} seconds before trying to post again."
    return False


# host thread replynumber ip datetime name message
# add "ip's post log" -- (group 3) > (group 4)

def flood_control(mode="comment"):
    user = {"comment" : 60, "thread" : 60*60}
    site = {"comment" : 20, "thread" : 40*60}
    
    user_rate(user[mode], mode)

def get_comment_log():
    tnow = str(int(time.time()))
    logpath = "data/log.txt"
    with open(logpath, "r") as log:                
        log = log.read().splitlines()[-14:-10] # changeme
    try: log = [x.split() for x in log]
    except: return False
    log = [[*L[:4], *L[4].split("<>")] for L in log]
    
    return log
