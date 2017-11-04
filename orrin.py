from lxml import html
import requests
import subprocess
from settings import settings

url = 'http://forums.ltheory.com/ucp.php?mode=login'
values = {'username': settings("LT_USERNAME"),
          'password': settings("LT_PASSWORD"),
          'login':'Login',
          'redirect': './index.php'}
def fetch_new_pages(tree):
    global something_new
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
        command = "open \"http://forums.ltheory.com/" + unread_page.get("href")[2:] + "\""
        something_new = True
        subprocess.run(command, shell=True, check=True)
def fetch_forum(new_url):
    global url, values
    values['redirect'] = new_url
    page = requests.post(url, data=values)

    tree = html.fromstring(page.content)
    unreads = tree.cssselect('.forum_unread a, .forum_unread_locked a, .forum_unread_subforum a')
    fetch_new_pages(tree)
    for a in unreads:
        next_page_url = a.get("href")
        values['redirect'] = next_page_url
        if "viewforum" in next_page_url:
            fetch_forum(next_page_url)
            continue
        new_page = requests.post(url, data=values)
        new_tree = html.fromstring(new_page.content)
        fetch_new_pages(new_tree)

something_new = False
fetch_forum("./index.php")
if not something_new:
    print("Sorry, but there is no new content.")



