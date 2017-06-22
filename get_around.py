#!/usr/bin/env python
# -*- coding: utf-8 -*-
# json2xml
"""
calculate surrounding scenery rank
project:tianningdao jingdian
Author : wuyingjiao01(wuyingjiao01@baidu.com)
Date : 2017/04/13
"""
import json
import sys
import re
import requests
import json
import os
from math import radians, cos, sin, asin, sqrt,log
import time
reload(sys)
sys.setdefaultencoding('utf-8')
class SceneRank(object):
    def __init__(self):
        self.scene_dict = {}
        self.city_min_score = {}
        self.scene_id_dict = {} #原始数据提取出的景点排序相关数据存入此中间变量，key为景点id
        self.min_score = 0 #默认景点热度，打算取城市中的景点热度最低分
        self.ori_scenenum = 0  #原数据景点个数
        self.scenenum = 0 #有经纬度的景点个数
        self.adjust = 1  #策略公式的lambda系数
        self.excptnum = 0 #post请求没有正常返回数据的个数
        self.hotnum = 0   #统计有热度数据的景点个数
        self.aroundnum = 0 #统计获取到周边景点集，且不为空的景点个数
    #提取原始数据中与景点排序相关的数据 
    def load_scene_data(self):
        id_set = set()
	with open('scene_data2') as f:
            for line in f:
                self.ori_scenenum += 1
                scene_data = {}
                data = json.loads(line)
		#景点名称
                name = data['name'][0]['@value']
		#景点id
                scenid = data['@id']
		subscen = ""
                if "subScenicOf" in data.keys():
                    subscen = data["subScenicOf"][0]["name"]
                if scenid in id_set:
                    print "repeat id:",id.encode('utf-8')
                    continue
                id_set.add(name)
		#景点热度
                hotscore = float(data.get("hotScore",self.min_score))
                if hotscore > 0:
                    self.hotnum += 1
		#景点经纬度
                if "latitude" in data.keys() and "longitude" in data.keys():
                    lat = float(data["latitude"][0]['@value'])
                    lon= float(data["longitude"][0]['@value'])
		    #获取景点的周边景点集
                    around_set = self.get_around_set(lat,lon,20,10)
		    #周边景点排除自己，排除上下级景点
                    if scenid in around_set:
                        around_set.remove(scenid)
                    if subscen != "" and subscen in around_set:
                        around_set.remove(subscen)
                    #将提取出的景点排序相关数据存入字典,key为景点id
                    self.scene_id_dict[scenid] = {"name":name,"latitude":lat,"longitude":lon,"hotscore":hotscore,"subscen":subscen,"around_set":around_set}
		    #统计有经纬度的景点个数
                    self.scenenum += 1
    #周边景点获取，post请求影娣接口
    def get_around_set(self,lat,lon,scope,limt):
        around_set = []
        query_dict = ["g.query().has('logicname',MATCH,'tianningdao_tourist').around(" +str(lat)+ "," +str(lon)+ ","+str(scope)+ ").limit("+str(limt)+ ").with('*')"]
        param_dict = [{"tn":"jiayingdi","token":"15108453913832913547","resource_name":"tianningdao_tourist","query":query_dict,"action":"getentities","query_type":"1"}]
        param = {'method':"CommonQueryService",'params':param_dict}
        res = requests.post("http://kgopen-batch-yq.baidu.com/1",data = json.dumps(param))
        res_data = json.loads(res.text)
        ret = res_data['result']['_ret']
	#如果返回有结果
        if ret:
            try:
                #获取周边景点数据集
                around_set = ret[0]['aroundScene']
                self.aroundnum += 1
            except:
                self.excptnum += 1
                return around_set
        return around_set
    #将获取到周边景点的景点数据写入txt文件，下次就不用发post请求了
    def gen_around_set(self):
        with open("scene_around2.txt","w") as f:
            for item in self.scene_id_dict:
                data = self.scene_id_dict[item]
		if data["around_set"]:
                    name = data["name"]
		    lat = str(data["latitude"])
		    lon = str(data["longitude"])
		    around_str = ",".join(data["around_set"])
		    f.write('\t'.join([item,name,lat,lon,around_str])+'\n')
if __name__ == "__main__":
    scenerank = SceneRank()
    scenerank.load_scene_data()
    scenerank.gen_around_set()
