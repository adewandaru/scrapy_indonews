# -*- coding: utf-8 -*-
import scrapy
import datetime
import lxml
import re
import logging

import psycopg2
import psycopg2.extras
try:
    conn = psycopg2.connect("dbname='gatotkaca' user='postgres' host='localhost' password='Raisonne'")
except:
    print "I am unable to connect to the database"
cur = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
cur.execute("""SELECT url, id FROM article WHERE url NOT LIKE '%20.detik.com%'""")
rows = cur.fetchall()


class DetikKeywordsSpider(scrapy.Spider):
    name = "detik-keywords"

    def start_requests(self):
        for r in rows:
            yield scrapy.Request(url=r["url"], callback=self.parse, meta={"id": r["id"]})


    def parse(self, response):
        keywords = response.xpath('/html/head/meta[@name="keywords"]/@content')
        print keywords.extract()
        print response.meta.get("id")
        cur.execute("UPDATE article SET keywords = (%s) WHERE id=%s ",(keywords.extract()[0], (response.meta.get("id"))))
        conn.commit()


#start_urls = ['http://indeks.kompas.com/?tanggal=%d&bulan=%d&tahun=%d&pos=indeks' %(n,n+1,n+2) for n in range(0, 26)]
#print start_urls
