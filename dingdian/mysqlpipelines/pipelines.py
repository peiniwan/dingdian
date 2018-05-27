# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from dingdian.mysqlpipelines.MySql import Sql
from dingdian.items import DingdianItem, DcontentItem


class DingdianPipeline(object):
    def process_item(self, item, spider):
        # deferToThread(self._process_item, item, spider)
        if isinstance(item, DingdianItem):
            name_id = item['name_id']
            ret = Sql.select_name(name_id)
            if ret[0] == 1:
                print('已经存在了')
                pass
            else:
                xs_name = item['name']
                xs_author = item['author']
                category = item['category']
                Sql.insert_dd_name(xs_name, xs_author, category, name_id)
                print('开始存小说标题')

        # 这儿比上面一个Pipeline少一个判断，因为我把判断移动到Spider中去了，
        # 这样就可以减少一次Request，减轻服务器压力
        if isinstance(item, DcontentItem):
            url = item['chapterurl']
            name_id = item['id_name']
            num_id = item['num']
            xs_chaptername = item['chaptername']
            xs_content = item['chaptercontent']
            Sql.insert_dd_chaptername(xs_chaptername, xs_content, name_id, num_id, url)
            print('小说存储完毕')
            return item
