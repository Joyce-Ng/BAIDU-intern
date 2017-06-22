#!/usr/bin/env python
# -*- coding: utf-8 -*-
# json2xml
"""
convert json to xml
schema_id: 4811
project:tianningdao travel Q&A data
Author : wuyingjiao01(wuyingjiao01@baidu.com)
Date : 2017/02/27
"""
import json
import xml.dom.minidom as Dom
import sys
import datetime
import time
import urlparse
import urllib
from urlparse import urlsplit, urlunsplit, parse_qsl,urljoin
from urllib import urlencode
reload(sys)
sys.setdefaultencoding( "utf-8" )

class Json2xml(object):
    def __init__(self, filename):
        """
        Inits Json2xmlClass
        """
        self.filename = filename
        #self.doc = Dom.Document()
        self.doc = None
        self.result_city = { }
        self.result_prov = { }
        self.city_count = 0
        self.prov_count = 0
        self.xml_name = ""
        self.provlist = [
            "河北","山西","内蒙古","辽宁","吉林","黑龙江","江苏","浙江","安徽",
            "福建","江西","山东","河南","湖北","湖南","广东","广西","海南",
            "四川","贵州","云南","陕西","甘肃","青海","西藏","宁夏","新疆","台湾"
        ]
    # 清洗完全不相关数据
        self.black = []
    # 通过title对URL升／降权
        self.degrade = [
            '烧烤','旅行社','消费','娱乐','休闲','摄影','游泳','泳衣','电话'
            '坐车','怎样','怎么','交通','大巴','火车','动车','高铁','飞机','骑车',
            '打车','包车','机场','天气','气温','证','票','酒店','旅馆','宾馆','带宠物'
        ]
        self.upgrade = [
            '攻略','好玩','值得'
        ]
        self.de_score = -0.1
        self.up_score = 0.1
        self.source_weight = {'蚂蜂窝':3,'携程':3,'穷游':2,'百度知道':1}
        self.score1 = 1
        self.score2 = 2
        self.score3 = 3
        self.score4 = 4
        self.pv_level1 = 100
        self.pv_level2 = 1000
        self.pv_level3 = 10000
        self.url_score_dict = {}
        self.url_pv_dict = {}
        self.test_count = 0
    #过滤掉时间格式不对的数据
    def is_valid_date(self,strdate):
        try:
            time.strptime(strdate, "%Y-%m-%d")
            return True
        except:
            return False
    #过滤掉2014年之前的数据
    def filter(self,datestr1,datestr2):
        if self.is_valid_date(datestr1):
            date1 = datetime.datetime.strptime(datestr1, "%Y-%m-%d")
            date2 = datetime.datetime.strptime(datestr2, "%Y-%m-%d")
            return date1.date()>=date2.date()
        else:
            return False
    def normurl(self,url):
        split = urlsplit(url)
        return urlunsplit((split.scheme, split.netloc, split.path,'',''))
    #是否命中黑名单
    def is_hit(self,title):
        for word in self.black:
            if title.find(word)>0:
                return 1
        return 0
    #是否命中降级名单
    def is_degrade(self,title):
        score = 0
        for word in self.degrade:
            if title.find(word)>0:
                score += self.de_score
                break
        for word in self.upgrade:
            if title.find(word)>0:
                score += self.up_score
                break
        return score
    #根据PV打分
    def get_pv_score(self,pv):
        if pv == 0:
            return 0
        elif 0 < pv and pv <= self.pv_level1:
            return self.score1
        elif self.pv_level1 < pv and pv <= self.pv_level2:
            return self.score2
        elif self.pv_level2 < pv and pv <= self.pv_level3:
            return self.score3
        else:
            return self.score4
    #根据评论数打分
    def get_answer_score(self,ans):
        if ans == 0:
            return 0
        elif 0 < ans and ans <= 10:
            return self.score1
        elif 10 < ans and ans <= 30:
            return self.score2
        else:
            return self.score3
    #读取url相关数据,生成url_pv_dict,{url1:pv1,url2:pv2}
    def load_url_data(self):
        with open("merge_url_data") as f:
            for line in f:
                data = line.strip().split('\t')
                url = data[0]
                pv = data[4]
                cv = data[5]
                self.url_pv_dict[url] = int(pv)
    #按策略给url打分
    def get_url_score(self,comment):
        url = comment['url']
        source = comment['source'].encode('utf-8')
        title = comment['title'].encode('utf-8')
        pv = self.url_pv_dict.get(url, 0)
        pv_score = self.get_pv_score(pv)
        source_weight = self.source_weight.get(source,1)
        answer_score = self.get_answer_score(comment['answer_count'])
        score = 0.5*source_weight + 0.3*pv_score + 0.1*answer_score + self.is_degrade(title)
        self.url_score_dict[url] = score
        return score
    #评论排序策略，依次根据评论URL分数、PV、日期排序
    def sortby(self,x,y):
        score1 = self.get_url_score(x)
        score2 = self.get_url_score(y)
        pv1 = self.url_pv_dict.get(x['url'], 0)
        pv2 = self.url_pv_dict.get(y['url'], 0)
        date1 = self.get_time_year(x)
        date2 = self.get_time_year(y)
        if score1 != score2:
            if score1 < score2:
                return 1
            else:
                return -1
        else:
            if pv1 != pv2:
                if pv1 < pv2:
                    return 1
                else:
                    return -1
            else:
                if date1 < date2:
                    return 1
                else:
                    return -1
    #评论排序
    def sort_comment2(self,comment_list):
        comment_list2 = comment_list
        for comment in comment_list:
            title = comment['title'].encode('utf-8')
            if self.is_hit(title) == 1:
                print "removed title:",title
                comment_list2.remove(comment)
        comment_list_ret = sorted(comment_list2, cmp = self.sortby)
        return comment_list_ret
    #评论排序策略，根据日期排序
    def sort_data_by_date(self, data):
        data.sort(key = lambda x:self.get_time_year(x), reverse = True)
        return data
    def get_time_year(self, data):
        time = data["time"]
        time = time.split("-")
        time = time[0][-2:] + time[1] + time[2] 
        time = int(time) 
        return time
    #源数据中间变量，对评论列表进行排序
    def json2res(self):
        """
        convert json to intermediate variable
        Args: 
        Returns:
        self.result = {
        "北京":[{"title":aaa,"url":aaa,"time":aaa},...],
        "上海":[{},{},...],
        ...
        }
        """
        with open(self.filename) as f:
            file_lines = f.readlines()
            url_set = set()
            comment_set = set()
            for line in file_lines:
                json_obj = json.loads(line)
                date = json_obj['time']
                #如果时间在2104年之后
                if self.filter(date,"2014-01-01"):
                    key = json_obj['city']
                    url = self.normurl(json_obj['url'])
                    comment = json_obj['abstract']
                    if url in url_set:
                        continue
                    url_set.add(url)
                    if comment in comment_set:
                        continue
                    comment_set.add(comment)
                    json_obj['url'] = url
                    if key in self.provlist:
                        if key not in self.result_prov.keys():
                            self.result_prov[key] = [json_obj]
                        else:
                            self.result_prov[key].append(json_obj)
                    else:
                        if key not in self.result_city.keys():
                            self.result_city[key] = [json_obj]
                        else:
                            self.result_city[key].append(json_obj)
        for prov in self.result_prov.keys():
            if (len(self.result_prov[prov])<3):
                self.result_prov.pop(prov)
        for city in self.result_city.keys():
            if (len(self.result_city[city])<3):
                self.result_city.pop(city)
        for prov in self.result_prov:
            data = self.result_prov[prov]
            self.result_prov[prov] = self.sort_comment2(data)
        for city in self.result_city:
            data = self.result_city[city]
            self.result_city[city] = self.sort_comment2(data)
        f.close()
    #产生随机query提供给pm评估数据
    def gen_random_query(self):
        city_count = 0
        input = ""
        with open("checkres.txt", "w") as f:
            for city in self.result_city:
                if city_count>100:
                    break
                data = self.result_city[city]
                comtlen = len(data)
                if comtlen < 5:
                    city_count = city_count - 1
                    continue
                comment_count = 0
                while comment_count < 5:
                    title = data[comment_count]['title']
                    url = data[comment_count]['url']
                    f.write(city+'\t'+title+'\t'+url+'\n')
                    comment_count += 1
                city_count += 1
        f.close()
        
    def createNode(self, node_name):
        """ createNode """
        return self.doc.createElement(node_name)

    def addNode(self, node, prev_node = None):
        cur_node = node
        if prev_node is not None:
            prev_node.appendChild(cur_node)
        else:
            self.doc.appendChild(cur_node)
        return cur_node

    def setNodeAttr(self, node, att_name, value):
        cur_node = node
        cur_node.setAttribute(att_name, value)

    def setNodeValue(self, cur_node, value):
        node_data = self.doc.createTextNode(value)
        cur_node.appendChild(node_data)

    def genXml(self):
        """ generate XML """
        f = open(self.xml_name, "w")
        f.write(self.doc.toprettyxml(indent = "\t", newl = "\n", encoding = "utf-8"))
        f.close()
    #生成情景页xml,source_id: 26694
    def res2xml_qingjing(self,result,docname):
        """
        convert intermediate variable to xmlfile
        Args: self.result
        Returns: xml file number
        }
        """
        #DOCUMENT
        self.doc = Dom.Document()
        root_node = self.createNode("DOCUMENT")
        self.setNodeAttr(root_node,"content_method","full")
        self.addNode(node = root_node)
        #将存入部分数据的中间变量result转成xml文件
        doc_count = 0
        count = 0
        line_count = 0
        file_count_max = 40
        for city in result:
            data = result[city]
            if count == file_count_max:
                self.xml_name = docname + str(doc_count) + ".xml"
                self.genXml()
                doc_count += 1
                self.doc = Dom.Document()
                root_node = self.createNode("DOCUMENT")
                self.setNodeAttr(root_node,"content_method","full")
                self.addNode(node = root_node)
                count = 0
            item = self.createNode("item")
            key = self.createNode("key")
            self.setNodeValue(key,city)
            self.addNode(key,item)
            #display
            display = self.createNode("display")

            dis_url = self.createNode("url")
            self.setNodeValue(dis_url,"https://baidu.com/")
            self.addNode(dis_url,display)

            dis_title = self.createNode("title")
            self.setNodeValue(dis_title,"优质问答聚合")
            self.addNode(dis_title,display)

            #imglist
            for one in data:
                list_item = one

                imglist = self.createNode("imglist")

                list_title = self.createNode('title')
                self.setNodeValue(list_title,list_item['title'])
                self.addNode(list_title,imglist)

                list_url = self.createNode('url')
                self.setNodeValue(list_url,list_item['url'])
                self.addNode(list_url,imglist)

                #IMG IS NULL
                list_img = self.createNode('img')
                #self.setNodeValue(list_img,"")
                self.addNode(list_img,imglist)

                list_comments = self.createNode('comments')
                self.setNodeValue(list_comments,str(list_item['answer_count']) + "个回答")
                self.addNode(list_comments,imglist)

                list_text = self.createNode('text')
                self.setNodeValue(list_text,list_item['abstract'])
                self.addNode(list_text,imglist)

                list_resource = self.createNode('resource')
                self.setNodeValue(list_resource,list_item['source'])
                self.addNode(list_resource,imglist)

                list_date = self.createNode('date')
                self.setNodeValue(list_date,list_item['time'])
                self.addNode(list_date,imglist)
                #imglist
                self.addNode(imglist,display)
            #/display
            self.addNode(display,item)
            #/item
            self.addNode(item,root_node)
            count += 1
            line_count += 1
            if line_count == len(result):
                item = root_node.getElementsByTagName("item")
                if len(item) != 0:
                    self.xml_name = docname + str(doc_count) + ".xml"
                    self.genXml()
        return doc_count
    #生成子卡xml,source_id: 31893
    def res2xml_zika(self,result,docname):
        """
        convert intermediate variable to xmlfile
        Args: self.result
        Returns: xml file
        }
        """
        #DOCUMENT
        self.doc = Dom.Document()
        root_node = self.createNode("DOCUMENT")
        self.setNodeAttr(root_node,"content_method","full")
        self.addNode(node = root_node)
        #将存入部分数据的中间变量result转成xml文件
        doc_count = 0
        count = 0
        line_count = 0
        file_count_max = 6000
        for city in result:
            data = result[city]
            if count == file_count_max:
                self.xml_name = docname + str(doc_count) + ".xml"
                self.genXml()
                doc_count += 1
                self.doc = Dom.Document()
                root_node = self.createNode("DOCUMENT")
                self.setNodeAttr(root_node,"content_method","full")
                self.addNode(node = root_node)
                count = 0
            else:
                item = self.createNode("item")
                key = self.createNode("key")
                self.setNodeValue(key,city)
                self.addNode(key,item)

                #display
                display = self.createNode("display")

                dis_url = self.createNode("url")
                self.setNodeValue(dis_url,"https://baidu.com/")
                self.addNode(dis_url,display)

                dis_title = self.createNode("title")
                self.setNodeValue(dis_title,"优质问答聚合")
                self.addNode(dis_title,display)

                #args
                commentnum = 0
                for one in data:
                    list_item = one

                    args = self.createNode("args")

                    list_url = self.createNode('url')
                    self.setNodeValue(list_url,list_item['url'])
                    self.addNode(list_url,args)

                    list_title = self.createNode('title')
                    self.setNodeValue(list_title,list_item['title'])
                    self.addNode(list_title,args)

                    list_resource = self.createNode('resource')
                    self.setNodeValue(list_resource,list_item['source'])
                    self.addNode(list_resource,args)

                    list_text = self.createNode('text')
                    self.setNodeValue(list_text,list_item['abstract'])
                    self.addNode(list_text,args)

                    list_comments = self.createNode('comments')
                    self.setNodeValue(list_comments,str(list_item['answer_count'])+"个回答")
                    self.addNode(list_comments,args)
                    #args
                    self.addNode(args,display)
                    commentnum += 1
                    if commentnum == 3:
                        break
                #/display
                self.addNode(display,item)
                #/item
                self.addNode(item,root_node)
            count += 1
            line_count += 1
            if line_count == len(result):
                item = root_node.getElementsByTagName("item")
                if len(item) != 0:
                    self.xml_name = docname + str(doc_count) + ".xml"
                    self.genXml()
        return doc_count
    #生成索引文件
    def genIndexDoc(self,n,typestr):
        self.doc = Dom.Document()
        root_node = self.createNode("sitemapindex")
        self.addNode(node = root_node)
        for i in xrange(n):
            locstr = "http://cq01-ps-dev211.cq01.baidu.com:8082/tourism/"+typestr+"/city_ask_"+typestr+"_"+str(i)+".xml"
            sitemap = self.createNode("sitemap")
            loc = self.createNode("loc")
            self.setNodeValue(loc,locstr)
            self.addNode(loc,sitemap)
            self.addNode(sitemap,root_node)
        self.xml_name = "city_ask_" + typestr + "_" + "index.xml"
        self.genXml()

    def genCityxml(self):
        '''
        划分为不超过10M的xml文件
        '''
        doc1_count = self.res2xml_qingjing(self.result_city,"city_ask_qingjing_")
        self.genIndexDoc(doc1_count + 1 , "qingjing")
        doc2_count = self.res2xml_zika(self.result_city,"city_ask_zika_")
        self.genIndexDoc(doc2_count + 1 , "zika")
    def genProvxml(self):
        doc1_count = self.res2xml_qingjing(self.result_prov,"prov_ask_qingjing_")
        self.genIndexDoc(doc1_count + 1 , "qingjing")
        doc2_count = self.res2xml_zika(self.result_prov,"prov_ask_zika_")
        self.genIndexDoc(doc2_count + 1 , "zika")
if __name__ == "__main__":
    Json2xml_obj = Json2xml("json.res")
    Json2xml_obj.load_url_data()
    Json2xml_obj.json2res()
    #Json2xml_obj.gen_random_query()
    #Json2xml_obj.genProvxml()
    Json2xml_obj.genCityxml()
    


