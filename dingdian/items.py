# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DingdianItem(scrapy.Item):
    name = scrapy.Field()
    author = scrapy.Field()
    novelurl = scrapy.Field()
    serialstatus = scrapy.Field()
    serialnumber = scrapy.Field()
    category = scrapy.Field()
    name_id = scrapy.Field()


class DcontentItem(scrapy.Item):
    id_name = scrapy.Field()
    chaptercontent = scrapy.Field()
    # 用于绑定章节顺序
    num = scrapy.Field()
    chapterurl = scrapy.Field()
    # 章节名字
    chaptername = scrapy.Field()


class HaoduofuliItem(scrapy.Item):
    category = scrapy.Field()  # 类型
    title = scrapy.Field()  # 标题
    imgurl = scrapy.Field()  # 图片的地址
    yunlink = scrapy.Field()  # 百度云盘的连接
    password = scrapy.Field()  # 百度云盘的密码
    url = scrapy.Field()  # 页面的地址
