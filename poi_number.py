#!/usr/bin/env python
# -*- coding: utf-8 -*-
# json2xml
"""
convert json to xml
schemaID:6308
project:tianningdao around destination  data
Author : wuyingjiao01(wuyingjiao01@baidu.com)
Date : 2017/05/01
"""
import json
import xml.dom.minidom as Dom
import sys
import urllib
import datetime
import time
import re
reload(sys)
sys.setdefaultencoding( "utf-8" )

class Json2xml(object):
    def __init__(self, filename):
        self.filename = filename
        self.xmlname = None
        self.doc = None
        self.repeat_key = {}
	self.record_repeat = []
    def res2xml2(self,docname):
        """
        convert intermediate variable to xmlfile
        Args: self.result
        Returns: xml file number
        }
        """
        doc_count = 0
        count = 0
        line_count = 0
        file_count_max = 10000
        regex = re.compile(r'\\(?![/u"])')
        #DOCUMENT
        self.doc = Dom.Document()
        root_node = self.createNode("DOCUMENT")
        self.setNodeAttr(root_node,"content_method","full")
        self.addNode(node = root_node)
        with open(self.filename) as f1:
            for line in f1:
		line_count += 1
                decode_line = line.strip()
		escp_line = regex.sub(r"\\\\", decode_line)
                try:
                    data = json.loads(escp_line)
                    bid = data["bid"]
                    phone_list = data["phone"]
		    if len(phone_list) > 3:
                        phone_list = phone_list[:3]
                    name = data["name"].encode('utf-8')
                    city = data["city"].encode('utf-8')
                    uid = data["uid"]
                except ValueError, e:
		    print "ValueError:",line_count,line
                    continue
	        #生成XML数据中的KEY
	        city_name = city.replace("市","")
		#poi名称中含有“XX市”
		if name.find(city) == 0:
		    #去掉“市”，便于query解析
		    title1 = name.replace(city,city_name)
		    title2 = name
		else:
		    #poi名称中含有城市名称，没有“市”字
		    if name.find(city_name) == 0:
                        title1 = name
			title2 = name.replace(city_name,city)
                    else:
			title1 = city_name + name
			title2 = city + name
		#跟进重复的key表，判断key是否需要去重
		if title1 in self.repeat_key:
		    continue
		else:
		    self.repeat_key[title1] = 0
                #将存入部分数据的中间变量result转成xml文件
                if count == file_count_max:
                    self.xmlname = docname + str(doc_count) + ".xml"
                    self.genXml()
                    doc_count += 1
                    self.doc = Dom.Document()
                    root_node = self.createNode("DOCUMENT")
                    self.setNodeAttr(root_node,"content_method","full")
                    self.addNode(node = root_node)
                    count = 0
                #1-itme
                item = self.createNode("item")
                #2-key
                key = self.createNode("key")
                self.setNodeValue(key,title1)
                self.addNode(key,item)
                #2-display
                display = self.createNode("display")
                #3-url
                url = self.createNode("url")
                self.setNodeValue(url,"https://baidu.com")
                self.addNode(url,display)
                #3-title1
                title1 = self.createNode("title1")
                self.setNodeValue(title1,title2)
                self.addNode(title1,display)
                #3-title2
                title2 = self.createNode("title2")
                self.setNodeValue(title2,"电话")
                self.addNode(title2,display)
                #3-tellist
                for tel in phone_list:
                    phone = tel.replace('(','').replace(')','-')
                    tellist = self.createNode("tellist")
                    self.setNodeValue(tellist,phone)
                    self.addNode(tellist,display)
                #3-showLeftText
                showLeftText = self.createNode("showLeftText")
                self.setNodeValue(showLeftText,"智能搜索聚合")
                self.addNode(showLeftText,display)
                #3-showRightText
                showRightText = self.createNode("showRightText")
                self.setNodeValue(showRightText,"报错")
                self.addNode(showRightText,display)
                #3-sshowRightUrl
                showRightUrl = self.createNode("showRightUrl")
                url_str = self.genUrl(uid)
                self.setNodeValue(showRightUrl,url_str)
                self.addNode(showRightUrl,display)
                #/2-display
                self.addNode(display,item)
                #/1-item
                self.addNode(item,root_node)
                count += 1
		if line_count == 14519163:
                    item = root_node.getElementsByTagName("item")
                    if len(item) != 0:
                        self.xmlname = docname + str(doc_count) + ".xml"
                        self.genXml()
        return doc_count
    def genIndexDoc(self,n):
        self.doc = Dom.Document()
        root_node = self.createNode("sitemapindex")
        self.addNode(node = root_node)
        for i in xrange(n):
            locstr = "http://cq01-ps-dev211.cq01.baidu.com:8082/poi/poi_phone_"+str(i)+".xml"
            sitemap = self.createNode("sitemap")
            loc = self.createNode("loc")
            self.setNodeValue(loc,locstr)
            self.addNode(loc,sitemap)
            self.addNode(sitemap,root_node)
        self.xmlname = "poi_phone_index.xml"
        self.genXml()
    def load_repeat_title(self):
	with open("repeat_title0525.txt") as f:
	    for line in f:
		title = line.strip()
		self.repeat_key.append(title)
    def genUrl(self,uid):
        url_str = "http://i.map.baidu.com/api/page/poicorrect/proposemodifyadvice?business_trigger=30&uid="+ uid
        return url_str
    def json2res(self):
        with open(self.filename) as f:
            for line in f:
                scene = line.strip().split('\t')[0].decode('gbk')
                self.scene_list.append(scene)
            print len(self.scene_list)
    #生成xml文件
    def genXml(self):
        f = open(self.xmlname,"w")
        f.write(self.doc.toprettyxml(indent = "\t", newl = "\n", encoding = "utf-8"))
        f.close()
    def createNode(self, node_name):
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
if __name__ == "__main__":
    Json2xml_obj = Json2xml("poi.phone_number.0523")
    count = Json2xml_obj.res2xml2("poi_phone_")
    Json2xml_obj.genIndexDoc(count+1)
