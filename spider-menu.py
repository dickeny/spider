#!/usr/bin/python
#-*- coding: UTF-8 -*-

import os
import re
import sys
import logging
import requests


done_path = os.path.dirname(__file__) + "/done-menu.txt"
entry = "/dq/"
output_dir = "output-menu/"
output_file = "output_menu.txt"

site = "http://www.ximalaya.com"
headers = {
'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.6',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Referer': 'http://www.ximalaya.com/1687033/album/2758446/',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
}

#re_thread    = r'''<a href="forum.php\?mod=viewthread&tid=([0-9]*).* onclick=.* class="s xst">(.*)</a>'''
re_thread    = r'''<a href="read-htm-tid-([0-9]*).html" onclick=.* class="s xst">(.*)</a>'''
re_attchment = r'''get=jQuery.get\('(plugin.php.*)',{},function.*html....>(.*)</a>'''
re_download  = r'''href="(/plugin.php[^"]*attach)"'''
formats = ['epub', 'mobi', 'azw3', 'azw']

open(done_path, "a")
done_urls = set( line.decode("UTF-8").strip() for line in open(done_path).readlines() )

s = requests.Session()
def get(path):
    if not path.startswith("http:"):
        if not path.startswith("/"): path = "/" + path
        path = site + path
    return s.get(path, headers=headers, timeout=60)


def visit_album(name, href):
    rsp = get(href)
    tag = re.compile(r'''<div class="personal_body" sound_ids="([^"]*)"''')
    result = tag.findall(rsp.text)
    if not result: return
    logging.info("%s %s" % (href, name))
    open(output_file, "w").write(result[0] + "\n")

    #f = output_dir + href.replace(site + "/", "").replace("/", "_")
    #open(f, "w").write(result[0])


def visit_page(menu, href):
    base_path = href
    idx = 0
    tag = re.compile(r'''a href="([^"]*)" hashlink title="([^"]*)" class="discoverAlbum_title"''')
    while True:
        idx += 1
        if idx > 200: break
        path = "%s%d/" % (base_path, idx)
        logging.info("%s %s" % (path, menu))
        if path in done_urls: continue
        rsp = get(path)
        results = tag.findall(rsp.text)
        if not results: break;
        for href, name in results:
            if href in done_urls: continue
            visit_album(name, href)
            done_urls.add(href)

        done_urls.add(path)
        open(done_path, "w").write( ("\n".join(done_urls)).encode("UTF-8") )

def visit_entry():
    path = "/dq/"
    tag = re.compile(r'''<a class="tagBtn " href="(/dq/[^"]*)" tid="([^"]*)" hashlink''')
    rsp = get(path)
    for href, name in tag.findall(rsp.text):
        logging.debug("%s: %s" % (href, name))
        visit_page(name, href)

def main():
    visit_entry()


if __name__ == "__main__":
    logging.basicConfig(
            format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level = logging.INFO
            )
    sys.exit(main())


