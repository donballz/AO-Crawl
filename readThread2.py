# Reads and outputs contents of specified threads
from urllib2 import urlopen
from datetime import datetime
import json
import threading
import Queue


def get_next_post(page):
    start_link = page.find('post_message_')
    if start_link == -1:
        return None, 0, 0

    start_pnum = page.find('e_', start_link)
    end_pnum = page.find('"', start_link)
    pnum = long(page[start_pnum + 2:end_pnum])

    start_quote = page.find('>', start_link)
    end_quote = page.find('<!-- / message -->', start_quote + 1)
    post = page[start_quote + 1:end_quote]

    try:
        post = post.decode('windows-1252')
    except:
        post = "******post can't decode******"

    return post, end_quote, pnum


def get_title(page):
    start_link = page.find('<title')
    if start_link == -1:
        return None
    start_quote = page.find('>', start_link)
    end_quote = page.find('</title>', start_quote + 1)
    post = page[start_quote + 1:end_quote]
    return post


def get_poster(page):
    start_link = page.find('<a class="bigusername"')
    if start_link == -1:
        return None
    start_quote = page.find('>', start_link)
    end_quote = page.find('</a>', start_quote + 1)
    post = page[start_quote + 1:end_quote]
    return post


def get_timestamp(page):
    start_link = page.find('<!-- status icon and date -->')
    if start_link == -1:
        return None, 0
    start_quote = page.find('</a>', start_link)
    end_quote = page.find('<!-- / status icon and date -->', start_quote + 1)
    post = page[start_quote + 4:end_quote]
    return post


def get_last_page_num(page):
    """
    takes thread page 1 and return long integer number of pages
    """
    start_link = page.find('<div class="pagenav"')
    if start_link == -1:
        return None
    start_quote = page.find('>Page', start_link)
    end_quote = page.find('</td>', start_quote)
    end_num = long(page[start_quote + 11:end_quote])
    return end_num


def get_page(url):
    """
    simple page getter for initial pull
    """
    try:
        return urlopen(url).read()
    except:
        return None
    return None


def get_page_queue(url, queue):
    """
    enqueue page data using python Queue class
    """
    queue.put(urlopen(url).read())
    return None


def build_page_list(tnum):
    """
    takes first page and return list of links
    """
    url_list = []
    url1 = build_url(tnum, 1)
    page = get_page(url1)
    for idx in range(2, get_last_page_num(page)):
        url_list.append(build_url(tnum, idx))
    result = Queue.Queue()
    result.put(page)
    threads = [threading.Thread(target=get_page_queue, args=(url, result)) for url in url_list]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return result


def get_quoted(post):
    posters = []
    while True:
        start_link = post.find('<strong>')
        if start_link == -1:
            return posters
        start_quote = post.find('>', start_link)
        end_quote = post.find('</strong>', start_quote + 1)
        quoted = post[start_quote + 1:end_quote]
        posters.append(quoted)
        post = post[end_quote + 1:]
    return posters


def clean_posts(post):
    words = clean_string(post).split()
    polished = ""
    for word in words:
        polished += word + ' '
    return polished


def clean_string(post):
    start_link = 0
    while True:
        start_link = post.find('<', start_link)
        if start_link == -1:
            return post
        end_quote = post.find('>', start_link + 1)
        if post[start_link:start_link + 25] == '<img src="images/smilies/':
            end_smilie = post.find('" ', start_link)
            smilie = '{' + post[start_link + 25:end_smilie] + '}'
        else:
            smilie = ""
        post = post[:start_link] + smilie + post[end_quote + 1:]
    return post


def union(p, q):
    for e in q:
        if e not in p:
            p.append(e)


def build_thread_dict(tnum, page_num=1):
    posts = []
    post_log = []
    page_list = build_page_list(tnum)
    page = page_list.get()
    thread = {
        "Thread Number": tnum,
        "Thread Title": get_title(page),
        "OP": get_poster(page),
        "Date Pulled": datetime.now().date().strftime('%m/%d/%Y')
    }
    while page:
        while True:
            post, endpos, pnum = get_next_post(page)
            if post:
                if pnum in post_log:
                    thread["Posts"] = posts
                    return thread
                post_log.append(pnum)
                quoted = get_quoted(post)
                posts.append({
                    "Poster": get_poster(page),
                    "Post": clean_posts(post),
                    "PostNum": pnum,
                    "PostTime": get_timestamp(page).strip(),
                    "Quoted": quoted
                })
                #altcode: "PostTime": datetime.strptime(time_str, '%m-%d-%Y, %I:%M %p')
                page = page[endpos:]
            else:
                break
        if page_list.full():
            page = page_list.get()
        else:
            page = None
    thread["Posts"] = posts
    return thread


def build_url(tnum, page_num):
    server = "http://www.actuarialoutpost.com/"
    tbase = "actuarial_discussion_forum/showthread.php?t="
    url = server + tbase + str(tnum)
    url = url + "&pp=40&page=" + str(page_num)
    return url


def get_n_threads(start_thread, num_threads):
    tnum = start_thread
    endnum = start_thread + num_threads
    threads = {}
    while tnum < endnum:
        threads[tnum] = build_thread_dict(tnum)
        tnum += 1
    return threads


def output_thread(tnum, page_num=1):
    out_file = open(str(tnum) + '.json', 'w')
    out_file.write(json.dumps(build_thread_dict(tnum, page_num)))
    out_file.close()
    return None
