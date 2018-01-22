#!/usr/bin/python
#-*- coding: UTF-8 -*-

import os
import re
import sys
import logging
import requests


done_path = os.path.dirname(__file__) + "/done-zhubo.txt"
output_file = "otuput-zhubo.txt"
output_dir = "output-zhubo/"

site = "http://www.ximalaya.com"
headers = {
'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.6',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Referer': 'http://www.ximalaya.com/1687033/album/2758446/',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
}

open(done_path, "a")
done_urls = set( line.decode("UTF-8").strip() for line in open(done_path).readlines() )

s = requests.Session()
def get(path):
    if not path.startswith("http:"):
        if not path.startswith("/"): path = "/" + path
        path = site + path
    return s.get(path, headers=headers, timeout=60, allow_redirects=True)


def visit_zhubo(uid):
    idx = 0
    tag = re.compile(r'''sound_ids="([^"]*)"''')
    while True:
        idx += 1
        if idx > 500: break
        path = "http://www.ximalaya.com/%s/index_tracks?page=%d" % (uid, idx)
        logging.info(path)
        if path in done_urls: continue
        rsp = get(path)
        results = tag.findall(rsp.json()['html'])
        if not results or not results[0]: break;
        open(output_file, "a").write(results[0] + "\n")
        #f = output_dir + "zhubo_%s_%d" % (uid, idx)
        #open(f, "w").write(results[0])
        done_urls.add(path)

    open(done_path, "w").write( ("\n".join(done_urls)).encode("UTF-8") )

def main():
    zhubo = [
        "/zhubo/",
        "/zhubo/list-musician/",
        "/zhubo/list-emotion/",
        "/zhubo/list-finance/",
        "/zhubo/list-culture/",
        "/zhubo/list-news/",
        "/zhubo/list-book/",
        "/zhubo/list-comic/",
        "/zhubo/list-entertainment/",
        "/zhubo/list-xmlydx/",
        "/zhubo/list-train/",
        "/zhubo/list-music/",
        "/zhubo/list-trip/",
        "/zhubo/list-chair/",
        "/zhubo/list-kid/",
        "/zhubo/list-radio/",
        "/zhubo/list-car/",
        "/zhubo/list-njdj/",
        "/zhubo/list-opera/",
        "/zhubo/list-it/",
        "/zhubo/list-health/",
        "/zhubo/list-cover/",
        "/zhubo/list-storytelling/",
        "/zhubo/list-character/",
        "/zhubo/list-corporation/",
        "/zhubo/list-campus/",
        "/zhubo/list-mm/",
        "/zhubo/list-other/",
        "/zhubo/list-baishitong/",
        "/zhubo/list-fashion/",
        "/zhubo/list-erciyuan/",
        ]
    tag = re.compile(r'''a class="userface110" href="http://www.ximalaya.com/zhubo/(.*)/" hashlink''')
    for href in zhubo:
        idx = 0
        while True:
            idx += 1
            path = "%sp%d/" % (href, idx)
            logging.info(path)
            rsp = get(path)
            results = tag.findall(rsp.text)
            if not results: break
            for uid in results:
                visit_zhubo(uid)


if __name__ == "__main__":
    logging.basicConfig(
            format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level = logging.INFO
            )
    sys.exit(main())


