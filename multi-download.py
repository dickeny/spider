#!/usr/bin/python
#-*- coding: UTF-8 -*-

import os
import re
import sys
import logging
import requests
import threading
import Queue
import time
import traceback

done_path = os.path.dirname(__file__) + "/done-sounds.txt"
output_dir = "sounds/"

site = "http://www.ximalaya.com"
headers = {
'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.6',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Referer': 'http://www.ximalaya.com/zhubo/10936615/',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36',
}


open(done_path, "a")
done_urls = set( line.strip() for line in open(done_path).readlines() )

local = threading.local()
def get(path):
    if not hasattr(local, 's'):
        local.s = requests.Session()
    if not path.startswith("http:"):
        if not path.startswith("/"): path = "/" + path
        path = site + path
    return local.s.get(path, headers=headers, timeout=60, allow_redirects=True)

def do_download_file(line):
    done = []
    urls = set()
    for v in line.strip().split(","):
        if not v.isdigit(): continue
        path = "http://www.ximalaya.com/tracks/%s.json" % v
        if path in done_urls: continue
        logging.info(path)
        rsp = get(path)
        done.append( path )

        n = int(v)/1000
        result_dir = output_dir + "%s/" % n
        #if not os.path.exists(result_dir):
        #    os.mkdir(result_dir)

        f = result_dir+ "%s.json" % v
        #open(f, "w").write(rsp.content)

        data = rsp.json()
        for key in ['play_path', 'play_path_32', 'play_path_64']:
            if data.get(key, None): urls.add(data[key])
        f = "urls.txt"
        open(f, "a").write("\n".join(urls) + "\n")
    return done


class multi_thread_worker:
    def __init__(self, thread_num=10):
        self.thread_num = thread_num
        self.lock = threading.Lock()
        self.job_count = 0
        self.job_done = False
        self.jobs = Queue.Queue()
        self.output_q = Queue.Queue()
        threads = []
        for i in range(self.thread_num):
            t = threading.Thread(target=self.thread_download)
            t.daemon = True
            t.start()
            threads.append( t )
        t = threading.Thread(target=self.thread_done)
        t.daemon = True
        t.start()
        threads.append( t )
        self.threads = threads

    def wait_job_done(self):
        self.job_done = True
        for t in self.threads:
            while t.is_alive():
                time.sleep(1)

    def thread_download(self):
        while not self.job_done or self.job_count > 0 or not self.jobs.empty():
            try:
                job = self.jobs.get(timeout=1)
            except Queue.Empty:
                time.sleep(1)
                continue
            try:
                rsp = do_download_file(job)
                self.output_q.put( rsp )
            except Exception,e:
                traceback.print_exc()
                pass
            with self.lock:
                self.job_count -= 1

    def thread_done(self):
        new_urls = set()
        while not self.job_done or self.job_count > 0 or not self.output_q.empty():
            try:
                rsp = self.output_q.get(timeout=1)
            except Queue.Empty:
                time.sleep(1)
                continue
            if not rsp: continue
            done_urls.update(rsp)
            new_urls.update(rsp)
            n = len(new_urls)
            #logging.info("current n = %d, done_urls = %d" % (n, len(done_urls)))
            if len(new_urls) > 100:
                logging.info("dump new(%d) all(%d)" % (n, len(done_urls)) )
                open(done_path, "a").write("\n" + "\n".join(new_urls))
                new_urls = set()
        logging.info("saving new(%d) all(%d)" % (n, len(done_urls)) )
        open(done_path, "w").write("\n".join(done_urls))

    def add_job(self, job):
        self.jobs.put(job)
        with self.lock:
            self.job_count += 1

worker = multi_thread_worker(20)
def download_file(path):
    for line in open(path).readlines():
        worker.add_job(line)

def download_dir(d):
    for root, dirs, files in os.walk(d):
        for f in files:
            download_file(root + f)
        for dd in dirs:
            download_dir(dd)

def main():
    logging.info("starting...")
    for d in sys.argv:
        download_dir(d)
    worker.wait_job_done()



if __name__ == "__main__":
    logging.basicConfig(
            format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level = logging.INFO
            )
    sys.exit(main())


    # curl 'http://bbs.feng.com/read-htm-tid-10510681.html' 
