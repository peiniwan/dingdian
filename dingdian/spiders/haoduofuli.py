# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule, Request  ##CrawlSpider与Rule配合使用可以骑到历遍全站的作用
from scrapy.linkextractors import LinkExtractor  ##配合Rule进行URL规则匹配
from dingdian.items import HaoduofuliItem
from scrapy import FormRequest  ##Scrapy中用作登录使用的一个包


# xpath练习，scrapy登录练习
class myspider(CrawlSpider):
    name = 'haoduofuli'
    allowed_domains = ['haoduofuli.wang']
    start_urls = ['http://www.haoduofuli.wang/wp-login.php']

    def parse_start_url(self, response):
        # 如果你登录的有验证码之类的，你就可以在此处加入各种处理方法；
        # 比如提交给打码平台，或者自己手动输入、再或者pil处理之类的

        formdate = {
            'log': 'account',
            'pwd': 'password',
            'rememberme': "forever",
            'wp-submit': "登录",
            'redirect_to': "http://www.haoduofuli.wang/wp-admin/",
            'testcookie': "1"
        }
        return [FormRequest.from_response(response, formdata=formdate, callback=self.after_login)]

    name = 'haoduofuli'
    allowed_domains = ['haoduofuli.wang']
    start_urls = ['http://www.haoduofuli.wang/moviepc']

    # 可以在此处加上判断来确认是否登录成功、进行其他动作。
    def after_login(self, response):
        lnk = 'http://www.haoduofuli.wang'
        # 这一个请求也算作 初始URL 只不过 不是start_urls的返回response 所以不会调用parse_start_url函数
        return Request(lnk)

    # 表示所有response都会通过这个规则进行过滤匹配后缀为.html的URL了、callback =’parse_item’表示将获取到的response
    # 交给parse_item函数处理（这儿要注意了、不要使用parse函数、因为CrawlSpider使用的parse来实现逻辑、如果你使用了
    # parse函数、CrawlSpider会运行失败。）、follow = True表示跟进匹配到的URL（顺便说一句allow的参数支持正则表达式）
    # 至于我这儿的allow的参数为啥是’.\html’；自己观察一下我们需要获取想要信息的页面的URL是不是都是以.html结束的？明白了吧！
    rules = (
        Rule(LinkExtractor(allow=('\.html',)), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = HaoduofuliItem()
        item['url'] = response.url
        # 在根节点下面的有一个id为post_content的标签里面的第一个p标签（p[1]）
        # 后面加上text()标签就是提取文本
        item['category'] = response.xpath('//*[@id="content"]/div[1]/div[1]/span[2]/a/text()').extract()[0]
        item['title'] = response.xpath('//*[@id="content"]/div[1]/h1/text()').extract()[0]
        # response.xpath(‘你Copy的XPath’).extract()[‘要取第几个值’],不加[0]是因为我们要所有的地址、加了只能获取一个了
        item['imgurl'] = response.xpath('//*[@id="post_content"]/p/img/@src').extract()
        return item
