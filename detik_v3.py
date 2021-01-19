# -*- usage : scrapy runspider detik_v3.py -s JOB_DIR=. -o 2018b.json
# 21 maret 2018
import scrapy
import datetime
import lxml
from scrapy.http import FormRequest
from scrapy import Request
import logging
from inspect import getmembers
from pprint import pprint
from bs4 import BeautifulSoup, Tag

class DetikSpider(scrapy.Spider):
    name = "detik"
    allowed_domains = ["news.detik.com"]
    logging.log(logging.INFO, "test--")

    def start_requests(self):
        form_requests = []
        start_urls = []
        start = datetime.datetime.strptime("31-12-2018", "%d-%m-%Y")
        end = datetime.datetime.strptime("27-12-2018", "%d-%m-%Y")
        date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days)]
        for date in date_generated:
            #format of datepick 03 / 31 / 2016
            logging.log(logging.INFO, "tanggal=")
            logging.log(logging.INFO, date.strftime("%m/%d/%Y"))
            #https://news.detik.com/indeks/all?date=03%2F05%2F2018jn
            datestr = date.strftime("%m/%d/%Y")
            req = Request("https://news.detik.com/indeks/all/1?date="+datestr, callback = self.check_maxpage)
            req.meta['date'] = datestr
            req.meta['url'] = "https://news.detik.com/indeks/all/{}?date="+datestr
            form_requests.append(req)
        return form_requests

    def check_maxpage(self, response):
        logging.log(logging.INFO, "pages=")
        max = int(response.css("div.paging.paging2 a:nth-last-of-type(2)::text").extract()[0])
        logging.log(logging.INFO, max)
        urls = [response.meta['url'].format(n) for n in range(1,max + 1)]
        for url in urls:
            req = Request(url, callback = self.parse)
            req.meta['date'] = response.meta['date']
            yield req

    def parse(self, response):
        for href in response.css("#indeks-container a::attr(href)"):
            full_url = response.urljoin(href.extract())
            req = scrapy.Request(full_url, callback=self.parse_news)
            req.meta['date'] = response.meta['date']
            yield req

    def parse_news(self,response):
        yield {
            'title': remove_markup_title(response.css('h1').extract()[0]),
            'text': remove_markup(response.css("div.detail_text").extract()[0]),
            'url': response.url,
            'date': response.meta['date']
        }

def remove_cdata(txt):
    beg = txt.find('<!--')
    txt = txt[:beg]
    return txt

def remove_markup(txt):
    soup = BeautifulSoup(txt, "html.parser")
    txt = soup.get_text()
    txt = txt.replace("\t","").replace("\n","").replace("\\\\\\","").replace("\\","").replace('\"','"')
    txt = remove_cdata(txt)
    return txt

def remove_markup_title(txt):
    soup = BeautifulSoup(txt, "html.parser")
    txt = soup.get_text()
    txt = txt.replace("\t","").replace("\n","").replace("\\\\\\","").replace("\\","").replace('\"','"')
    return txt

def remove_html_markup(arr):
    result = []
    for s in arr:
        s2 = lxml.html.fromstring(s).text_content()
        s3 = s2.encode('ascii', 'ignore')
        s3 = s3.translate(None, '\t\n')
        result.append(s3)
    return result

#start_urls = ['http://indeks.kompas.com/?tanggal=%d&bulan=%d&tahun=%d&pos=indeks' %(n,n+1,n+2) for n in range(0, 26)]
#print start_urls
