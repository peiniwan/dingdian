# -*- coding: utf-8 -*-

import MySQLdb

from dingdian import settings

MYSQL_HOSTS = settings.MYSQL_HOSTS
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_PORT = settings.MYSQL_PORT
MYSQL_DB = settings.MYSQL_DB

cnx = MySQLdb.connect(host=MYSQL_HOSTS, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DB, charset='utf8')
cur = cnx.cursor()


class Sql:
    """
    DROP TABLE IF EXISTS `dd_name`;
    CREATE TABLE `dd_name` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `xs_name` varchar(255) DEFAULT NULL,
      `xs_author` varchar(255) DEFAULT NULL,
      `category` varchar(255) DEFAULT NULL,
      `name_id` varchar(255) DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4;
    """

    # classmethod作用是我们不需要初始化类就可以直接调用类中的函数使用
    @classmethod
    def insert_dd_name(cls, xs_name, xs_author, category, name_id):
        sql = 'INSERT INTO dd_name (`xs_name`, `xs_author`, `category`, `name_id`) VALUES (%(xs_name)s, %(xs_author)s, %(category)s, %(name_id)s)'
        value = {
            'xs_name': xs_name,
            'xs_author': xs_author,
            'category': category,
            'name_id': name_id
        }
        cur.execute(sql, value)
        cnx.commit()

    """
    DROP TABLE IF EXISTS `dd_chaptername`;
    CREATE TABLE `dd_chaptername` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `xs_chaptername` varchar(255) DEFAULT NULL,
      `xs_content` text,
      `id_name` int(11) DEFAULT NULL,
      `num_id` int(11) DEFAULT NULL,
      `url` varchar(255) DEFAULT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=2726 DEFAULT CHARSET=utf8mb4;
    SET FOREIGN_KEY_CHECKS=1;
    """

    @classmethod
    def insert_dd_chaptername(cls, xs_chaptername, xs_content, id_name, num_id, url):
        sql = 'INSERT INTO dd_chaptername (`xs_chaptername`, `xs_content`, `id_name`, `num_id`, `url`) VALUES (%(xs_chaptername)s, %(xs_content)s, %(id_name)s, %(num_id)s, %(url)s)'
        value = {
            'xs_chaptername': xs_chaptername,
            'xs_content': xs_content,
            'id_name': id_name,
            'num_id': num_id,
            'url': url
        }
        cur.execute(sql, value)
        cnx.commit()

    @classmethod
    def id_name(cls, xs_name):
        sql = 'SELECT id FROM dd_name WHERE xs_name=%(xs_name)s'
        value = {
            'xs_name': xs_name
        }
        cur.execute(sql, value)
        for name_id in cur:
            return name_id[0]

    @classmethod
    def select_name(cls, name_id):
        sql = "SELECT EXISTS(SELECT 1 FROM dd_name WHERE name_id=%(name_id)s)"
        value = {
            'name_id': name_id
        }
        cur.execute(sql, value)
        # 查找name_id这个字段，如果存在则会返回1,不存在则会返回0,去重
        return cur.fetchall()[0]

    @classmethod
    def sclect_chapter(cls, url):
        sql = "SELECT EXISTS(SELECT 1 FROM dd_chaptername WHERE url=%(url)s)"
        value = {
            'url': url
        }
        cur.execute(sql, value)
        return cur.fetchall()[0]
