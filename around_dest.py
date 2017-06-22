#!/usr/bin/env python
# -*- coding: utf-8 -*-
# json2xml
"""
convert json to xml
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
reload(sys)
sys.setdefaultencoding( "utf-8" )

class Json2xml(object):
    def __init__(self, filename,xmlname):
        self.filename = filename
        self.xmlname = xmlname
        self.arround_dest = {}
        self.scene_list = []
        self.city_list = []
        self.title_scene = []
        self.title_city = []
        self.title_uncert = []
        self.title_key_map = {}
    #读取原数据，存入arround_dest字典里，key为城市名
    def json2res(self):
        self.load_city_list()
        self.load_scene_list()
        self.load_title_key()
        with open(self.filename) as f:
            for line in f:
                data = json.loads(line)
                #城市名称
                name = data["name"]
                #周边目的地去重,去除没有img的目的地
                dest_list =  data["list"]
                print "len list",len(dest_list)
                dest_set = []
                for item in dest_list:
                    dest_name = item['title'].strip().split(',')[0]
                    img = item['img']
                    if img:
                    	if dest_name not in dest_set and (dest_name in self.scene_list or dest_name in self.city_list or dest_name in self.title_key_map):
                    		dest_set.append(item)
                    else:
                    	print dest_name
                #目的景点数据集
                print "len list2",len(dest_set)
                if len(dest_list)>=3:
                    self.arround_dest[name] = dest_set
                else:
                    print "removed city:",name
    def res2xml(self):
        self.doc = Dom.Document()
        root_ndoe = self.createNode("DOCUMENT")
        self.setNodeAttr(root_ndoe,"content_method","full")
        self.addNode(node = root_ndoe)
        for name in self.arround_dest:
            dest_list = self.arround_dest[name]
            #1-itme
            item = self.createNode("item")
            #2-key
            key = self.createNode("key")
            self.setNodeValue(key,name)
            self.addNode(key,item)
            #2-display
            display = self.createNode("display")
            #3-url
            url = self.createNode("url")
            self.setNodeValue(url,"https://baidu.com")
            self.addNode(url,display)
            #3-list
            for one_item in dest_list:
                #list
                dis_list = self.createNode("list")
                #url2
                url2 = self.createNode("url")
                url_str = one_item["url"]
                title_str = one_item["title"]
                #判断url是否为空，否则自己的拼接url
                if url_str == "http://baidu.com":
                    if title_str in self.title_key_map:
                        key = self.title_key_map[title_str]["key"]
                        src_id = self.title_key_map[title_str]["src_id"]
                        print "map:",title_str,key,src_id
                        url_str = self.genUrl(key,src_id)
                    elif title_str in self.scene_list:
                        url_str = self.genUrl(title_str,4239)
                    elif title_str in self.city_list:
                        url_str = self.genUrl(title_str,4324)
                    else:
                    	print "gen url failed!",title_str
                else:
                    if title_str in self.city_list:
                        print "url_city:",title_str
                    if title_str in self.scene_list:
                    	print "url_scene:",title_str
                    #self.title_uncert.append(title_str)
                self.setNodeValue(url2,url_str)
                self.addNode(url2,dis_list)
                #title
                title = self.createNode("title")
                self.setNodeValue(title,title_str)
                self.addNode(title,dis_list)
                #img
                img = self.createNode("img")
                self.setNodeValue(img,one_item["img"])
                self.addNode(img,dis_list)
                #text
                text = self.createNode("text")
                self.setNodeValue(text,one_item["text"])
                self.addNode(text,dis_list)
                #abstract
                abstract = self.createNode("abstract")
                self.setNodeValue(abstract,one_item["abstract"])
                self.addNode(abstract,dis_list)
                #star
                star = self.createNode("star")
                self.setNodeValue(star,one_item["star"])
                self.addNode(star,dis_list)
                #commenttext
                commenttext = self.createNode("commenttext")
                self.setNodeValue(commenttext,one_item["commenttext"])
                self.addNode(commenttext,dis_list)
                #/3-list-
                self.addNode(dis_list,display)
                #/2-display
            self.addNode(display,item)
            #/1-item
            self.addNode(item,root_ndoe)
        self.genXml()
    def genUrl(self,title,source_id):
        word = urllib.quote(title.encode("utf-8"))
        url_str = "https://m.baidu.com/sf?pd=jingdian_detail&openapi=1&dspName=iphone&from_sf=1&resource_id="+str(source_id)+"&word="+word+"&title="+word
        #print url_str
        return url_str
    #加载景点列表
    def load_scene_list(self):
        with open("scene_list.txt") as f:
            for line in f:
                scene = line.strip().split('\t')[0].decode('gbk')
                self.scene_list.append(scene)
    #加载城市列表
    def load_city_list(self):
        with open("city_list") as f:
            for line in f:
                city = line.strip().split('\t')[0].decode('utf-8')
                self.city_list.append(city)
    #加载PM标注景点name-key映射
    def load_title_key(self):
        with open("title_key_list.txt") as f:
            for line in f:
                data = line.split("\t")
                title = data[0].decode('utf-8')
                key = data[1].decode('utf-8')
                src_id = data[2]
                #pm标准的对应key不为“无”
                if key != u'\u65e0':
                    self.title_key_map[title] = {"key":key,"src_id":int(src_id)}
                else:
                    print "none map",title
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
    output_file = sys.argv[1]
    Json2xml_obj = Json2xml("arround_dest.0502.json",output_file)
    Json2xml_obj.json2res()
    Json2xml_obj.res2xml()
