# -*- coding: utf-8 -*-
import re
import scrapy  # 导入scrapy包
from bs4 import BeautifulSoup
from scrapy.http import Request  ##一个单独的request的模块，需要跟进URL的时候，需要用它
# 爬虫名字和工程名字不能一样，否则这行会报错
from dingdian.items import DingdianItem


# from dingdian.mysqlpipelines.sql import sql


class Myspider(scrapy.Spider):
    # entrypoint.py的第三个参数，此Name的名字！在整个项目中有且只能有一个、名字不可重复
    name = 'dingdians'
    # 这个不是必须的；但是在某写情况下需要用得到，比如使用爬取规则的时候就需要了；
    # 它的作用是只会跟进存在于allowed_domains中的URL。不存在的URL会被忽
    allowed_domains = ['23us.com']
    bash_url = 'http://www.23us.com/class/'
    bashurl = '.html'

    def start_requests(self):
        for i in range(1, 11):
            url = self.bash_url + str(i) + '_1' + self.bashurl
            yield Request(url, self.parse)

    # 回调函数
    def parse(self, response):
        # print(response.text)
        if __name__ == '__main__':
            max_num = BeautifulSoup(response.text, 'lxml').find('div', class_="pagelink").findall('a')[-1].get_text()
            basurl = str(response.url)[:-7]
            for num in range(1, int(max_num) + 1):
                url = basurl + '_' + str(num) + self.bashurl
                yield Request(url, callback=self.get_name)

    def get_name(self, response):
        tds = BeautifulSoup(response.text, 'lxml').find_all('tr', bgcolor="#FFFFFF")
        for td in tds:
            novelname = td.find_all('a')[1].get_text()
            novelurl = td.find_all('a')[1]['href']
            # 多了个一个meta这么一个字典，这是crapy中传递额外数据的方法。因还有一些其他内容需要在下一个页面中才能获取到。
            yield Request(novelurl, callback=self.get_chapterurl, meta={'name': novelname, 'url': novelurl},
                          dont_filter=True)

    def get_chapterurl(self, response):
        item = DingdianItem()
        # response.meta[key]：这个是提取从上一个函数传递下来的值。
        item['name'] = str(response.meta['name']).replace('\xa0', '')
        item['novelurl'] = response.meta['url']
        soup = BeautifulSoup(response.text, 'lxml')
        # meta 获取方式,不能用find，find_all
        category = soup.find(attrs={'name': 'og:novel:category'})['content']
        author = soup.find(attrs={'name': 'og:novel:author'})['content']
        name_id = str(response.url)[-6:-1].replace('/', '')
        item['category'] = str(category)
        item['author'] = str(author)
        item['name_id'] = name_id
        print item
        yield item
        yield Request(response.url, callback=self.get_chapter, meta={'name': name_id})
