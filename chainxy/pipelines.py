# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import time
import datetime
from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter
import MySQLdb
import pdb

class ChainxyPipeline(object):

    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        file = open('%s_%s.csv' % (spider.name, datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d')), 'w+b')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.fields_to_export = ["name","number","item_type","location","building","bedroom","bathroom","size","title_deep_number","description","date","link","photo"]
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class DatabasePipeline(object):

    def __init__(self, db, user, passwd, host):
        self.conn = MySQLdb.connect(db=db,
                                    user=user,
                                    passwd=passwd,
                                    host=host,
                                    charset='utf8',
                                    use_unicode=True)
        self.cursor = self.conn.cursor()

    
    def process_item(self, item, spider):
        try:
            query = ('INSERT INTO listing_%s (id, name, number, item_type, location, building, bedroom, bathroom, size, price, title_deep_number, description, date, link, photo ) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")')

            self.cursor.execute(query % (str(item["item_type"]), str(item["item_id"]), str(item["name"]),str(item["number"]),str(item["item_type"]),str(item["location"]),str(item["building"]),str(item["bedroom"]),str(item["bathroom"]),str(item["size"]), str(item["price"]),str(item["title_deep_number"]),str(item["description"]),str(item["date"]),str(item["link"]),str(item["photo"])))
        except:
            try:
                query = ('UPDATE listing_%s SET name="%s", number="%s", item_type="%s", location="%s", building="%s", bedroom="%s", bathroom="%s", size="%s", price="%s", title_deep_number="%s", description="%s", date="%s", link="%s", photo="%s" WHERE id =%s;')

                self.cursor.execute(query % (str(item["item_type"]), str(item["name"] or item['name']) ,str(item["number"]) ,str(item["item_type"]) ,str(item["location"]),str(item["building"]) ,str(item["bedroom"]) ,str(item["bathroom"]) ,str(item["size"]), str(item["price"]),str(item["title_deep_number"]) ,str(item["description"]),str(item["date"]),str(item["link"]),str(item["photo"]), str(item["item_id"])))
            except Exception as e:
                # pdb.set_trace()
                print e
                pass

        try:
            self.conn.commit()
        except Exception as e:
            pass
            pdb.set_trace()


        return item

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise NotConfigured
        db = db_settings['db']
        user = db_settings['user']
        passwd = db_settings['passwd']
        host = db_settings['host']
        return cls(db, user, passwd, host)