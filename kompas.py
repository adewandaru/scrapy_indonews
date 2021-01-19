# -*- coding: utf-8 -*-
import scrapy
import datetime
import lxml
import re

class KompasSpider(scrapy.Spider):
    name = "kompas"
    allowed_domains = ["kompas.com"]

    start_urls = []
    start = datetime.datetime.strptime("01-01-2013", "%d-%m-%Y")
    end = datetime.datetime.strptime("01-01-2014", "%d-%m-%Y")
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days)]

    for date in date_generated:
        for i in range(1, 40):
            start_urls.append(date.strftime("http://indeks.kompas.com/?tanggal=%d&bulan=%m&tahun=%Y&pos=indeks&p=" + str(i)))

    def parse(self, response):
        for href in response.css("h3 a::attr(href)"):
            full_url = response.urljoin(href.extract())
            yield scrapy.Request(full_url, callback=self.parse_news)

    def parse_news(self,response):
        yield {
            'title': remove_html_markup(response.css('h2').extract()),
            'text': remove_html_markup(response.css("div.kcm-read-text").extract()),
            'url': response.url
        }

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
