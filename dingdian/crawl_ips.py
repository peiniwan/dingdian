# -*- coding: utf-8 -*-
import MySQLdb
import requests
from bs4 import BeautifulSoup
from scrapy import Selector
import sys;

reload(sys);
sys.setdefaultencoding("utf8")
conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123", db="mysql", charset="utf8")
cursor = conn.cursor()


def crawl_ips():
    """
    爬取西刺网的免费代理IP
     create table proxy_ip(
      id int primary key auto_increment,
      ip varchar(120),
      port varchar(10),
      speed varchar(15),
      proxy_type varchar(10)
  );
    """
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4"
    }
    for i in range(2093):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)
        ip_list = []
        all_trs = BeautifulSoup(re.text, 'lxml').find_all('tr')
        for tr in all_trs[1:]:
            # print tr
            ip = tr.find_all('td')[1].get_text()
            port = tr.find_all('td')[2].get_text()
            proxy_type = tr.find_all('td')[5].get_text()
            speed = tr.find_all('td')[6].find_all('div')[0]['title']
            ip_list.append((ip, port, proxy_type, speed))

        for ip_info in ip_list:
            cursor.execute(
                "insert proxy_ip(ip, port, speed, proxy_type) VALUES('{0}', '{1}', '{2}', '{3}')".format(
                    ip_info[0], ip_info[1], ip_info[3], ip_info[2]
                )
            )
            conn.commit()


class GetIP(object):
    def delete_ip(self, ip):
        """
        从数据库中删除无效的IP
        """
        delete_sql = """
            DELETE FROM proxy_ip WHERE ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        """
        判断IP是否可用
        """
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        """
        从数据库中随机获取一个可用的IP
        """
        random_sql = """
            SELECT ip, port FROM proxy_ip
            ORDER BY RAND()
            LIMIT 1
        """
        result = cursor.execute(random_sql)

        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]

            judge_re = self.judge_ip(ip, port)
            if judge_re:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()


if __name__ == '__main__':
    # crawl_ips()
    #好多不能用
    get_ip = GetIP()
    get_ip.get_random_ip()
