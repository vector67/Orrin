from lxml import html
import requests
import subprocess
from settings import settings
import sys
import pickle
import os.path

session = requests.Session()
session_file = "_session.dat"
user_agent = settings("USER_AGENT") or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38"
head = {'User-Agent': user_agent}
def save_session(session):
    with open(settings("SESSION_FILE"), "wb") as f:
        pickle.dump(session, f)

def login(forced_login):
    global session, head, session_file
    has_logged_in = False
    if not forced_login and os.path.isfile(settings("SESSION_FILE")):
        with open(settings("SESSION_FILE"), "rb") as f:
            session = pickle.load(f)
        content = str(session_get_url_content(settings("FORUM_URL") + "ucp.php"))
        if content.lower().find("welcome to the user control panel.") >= 0:
            has_logged_in = True
        else:
            print("Couldn't use previously saved session to login again")
    
    if not has_logged_in:
        forum_username = settings("LT_USERNAME")
        forum_pw = settings("LT_PASSWORD")
        if forum_username != "" and forum_pw != "":
            lurl = settings("FORUM_URL") + "ucp.php?mode=login"
            payload = {"username": forum_username, \
                           "password": forum_pw, \
                           'redirect': 'index.php', \
                           'sid': '', \
                           'login': 'Login'}
            try:
                p = session.post(lurl, headers=head, data=payload, timeout=5)
                save_session(session)
                has_logged_in = True
            except Exception as e:
                has_logged_in = False

            htmlstr = ""
    return has_logged_in

def session_get_url_content(url):
    global session, head
    page = session.get(url, headers=head, timeout=15)
    save_session(session)
    return page.content

urls_to_open = []
def fetch_new_pages(tree):
    global something_new, urls_to_open
    classes = """.topic_unread a,
                 .topic_unread_mine a,
                 .topic_unread_locked a,
                 .topic_unread_locked_mine a,
                 .topic_unread_hot a,
                 .topic_unread_hot_mine a,
                 .sticky_unread a,
                 .sticky_unread_locked_mine a,
                 .sticky_unread_mine a,
                 .announce_unread a,
                 .announce_unread_locked a,
                 .announce_unread_locked_mine a,
                 .announce_unread_mine a,
                 .global_unread a,
                 .global_unread_locked a,
                 .global_unread_locked_mine a,
                 .global_unread_mine a"""
    unread_pages = tree.cssselect(classes)
    for unread_page in unread_pages:
        new_url = settings("FORUM_URL") + unread_page.get("href")[2:]
        urls_to_open.append(new_url)
        print(new_url)
        sys.stdout.flush()
        something_new = True

def fetch_forum(new_url):
    global url, values
    tree = html.fromstring(session_get_url_content(new_url))
    unreads = tree.cssselect('.forum_unread a, .forum_unread_locked a, .forum_unread_subforum a')
    fetch_new_pages(tree)
    for a in unreads:
        next_page_url = a.get("href")
        if "viewforum" in next_page_url:
            fetch_forum(settings("FORUM_URL") + next_page_url)
            continue
        new_tree = html.fromstring(session_get_url_content(next_page_url))
        fetch_new_pages(new_tree)

if login(False):
    something_new = False
    fetch_forum(settings("FORUM_URL") + "search.php?search_id=unreadposts")
    for url in urls_to_open:
        command = "open \"" + url + "\""
        subprocess.run(command, shell=True, check=True)
    if not something_new:
        print("Sorry, but there is no new content.")
else:
    print("Failed to login to the Limit Theory forums")



