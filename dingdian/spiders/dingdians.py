# -*- coding: utf-8 -*-
import re
import sys

import scrapy  # 导入scrapy包
from bs4 import BeautifulSoup
from scrapy.http import Request  ##一个单独的request的模块，需要跟进URL的时候，需要用它
# 爬虫名字和工程名字不能一样，否则这行会报错
from dingdian.mysqlpipelines.MySql import Sql
from dingdian.items import DingdianItem, DcontentItem

reload(sys)
sys.setdefaultencoding("utf8")


class Myspider(scrapy.Spider):
    # entrypoint.py的第三个参数，此Name的名字！在整个项目中有且只能有一个、名字不可重复
    name = 'dingdians'
    # 这个不是必须的；但是在某写情况下需要用得到，比如使用爬取规则的时候就需要了；
    # 它的作用是只会跟进存在于allowed_domains中的URL。不存在的URL会被忽
    allowed_domains = ['x23us.com']
    bash_url = 'https://www.x23us.com/class/'
    bashurl = '.html'
    x = 0

    def start_requests(self):
        for i in range(1, 2):  # 11
            url = self.bash_url + str(i) + '_1' + self.bashurl
            yield Request(url, self.parse)
            """
            yieid Request，请求新的URL，后面跟的是回调函数，你需要哪一个函数来处理这个返回值，就调用那一个函数，
            返回值会以参数的形式传递给你所调用的函数。
            """

    # 回调函数
    def parse(self, response):
        # print(response.text)
        max_num = BeautifulSoup(response.text, 'lxml').find_all('div', class_='pagelink')[0].find_all('a')[
            -1].get_text()
        bashurl = str(response.url)[:-7]
        for num in range(1, int(max_num) + 1):
            url = bashurl + '_' + str(num) + self.bashurl
            yield Request(url, callback=self.get_name)

    def get_name(self, response):
        # print(response.text)

        tds = BeautifulSoup(response.text, 'lxml').find_all('tr', bgcolor='#FFFFFF')
        category = BeautifulSoup(response.text, 'lxml').find('div', class_='bdsub').find('dt').get_text().split('-')[
            0].strip()
        for td in tds:
            if self.x == 2:
                return
            self.x = self.x + 1
            """
            <tr bgcolor="#FFFFFF">
            <td class="L"><a href="https://www.x23us.com/book/68553" title="剑来简介">[简介]</a><a href="http://www.x23us.com/html/68/68553/" target="_blank">剑来</a></td>
            <td class="L"><a href="http://www.x23us.com/html/68/68553/" target="_blank"> 第三百零六章 老僧不爱说佛法</a></td>
            <td class="C">烽火戏诸侯</td>
            <td class="R">3844K</td>
            <td class="C">18-05-25</td>
            <td class="C">连载</td>
            </tr>
            """
            novelname = td.find_all('a')[1].get_text()
            novelurl = td.find_all('a')[1]['href']
            author = td.find_all('td')[-4].get_text()
            every_category = category
            yield Request(novelurl, callback=self.get_chapterurl,
                          meta={'name': novelname, 'url': novelurl, 'author': author, 'category': every_category})

    def get_chapterurl(self, response):
        # print(response.text)
        item = DingdianItem()
        # # response.meta[key]：这个是提取从上一个函数传递下来的值。
        # item['name'] = str(response.meta['name']).replace('\xa0', '')
        item['name'] = response.meta['name']
        item['novelurl'] = response.meta['url']
        soup = BeautifulSoup(response.text, 'lxml')
        # html里的meta， 获取方式,不能用find，find_all
        """
        <meta name="og:novel:category" content="玄幻魔法"/> 
        <meta name="og:novel:author" content="横扫天涯"/> 
        <meta name="og:novel:book_name" content="天道图书馆"/> 
        <meta name="og:novel:read_url" content="https://www.x23us.com/html/67/67025/"/>  
        """
        category = soup.find(attrs={'name': 'og:novel:category'})['content']
        author = soup.find(attrs={'name': 'og:novel:author'})['content']
        bash_url = soup.find(attrs={'name': 'og:novel:read_url'})['content']
        # bash_url = BeautifulSoup(response.text, 'lxml').find('p', class_='btnlinks').find('a', class_='read')['href']
        name_id = str(response.url)[-6:-1].replace('/', '')
        item['category'] = str(category).encode('UTF-8')
        item['author'] = str(author)
        item['name_id'] = name_id
        # 返回item是不能用return的哦！用了就结束了，程序就不会继续下去了，得用yield
        yield item
        yield Request(url=bash_url, callback=self.get_chapter, meta={'name_id': name_id})

    # 不知道为什么这个 方法不执行了
    def get_chapter(self, response):
        # <td class="L"><a href="27764222.html">第一章 骗子</a></td>
        urls = re.findall(r'<td class="L"><a href="(.*?)">(.*?)</a></td>', response.text)
        # num这个变量的作用是因为Scrapy是异步的方式运作，你采集到的章节顺序都是混乱的，
        # 需要给它有序的序列，我们按照这个排序就能得到正确的章节顺序
        num = 0
        for url in urls:
            num = num + 1
            chapterurl = response.url + url[0]
            chaptername = url[1]
            rets = Sql.sclect_chapter(chapterurl)
            if rets[0] == 1:
                print('章节已经存在了')
                pass
            else:
                yield Request(chapterurl, callback=self.getchaptercontent,
                              meta={'num': num, 'name_id': response.meta['name_id'], 'chaptername': chaptername,
                                    'chapterurl': chapterurl})

    def getchaptercontent(self, response):
        item = DcontentItem()
        item['num'] = response.meta['num']
        item['id_name'] = response.meta['name_id']
        item['chaptername'] = str(response.meta['chaptername']).replace('\xa0', '')
        item['chapterurl'] = response.meta['chapterurl']
        content = BeautifulSoup(response.text, 'lxml').find('dd', id='contents').get_text()
        item['chaptercontent'] = str(content).replace('\xa0', '')
        yield item
