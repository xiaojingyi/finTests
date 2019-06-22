#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-5-16 15:49:04$
# Note: This source file is NOT a freeware
# Version: InstanceEla.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-5-16 15:49:04$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
import numpy as np
from Instance import *
from datetime import datetime
from elasticsearch import Elasticsearch

class InstanceEla(Instance):
    def __init__(self, config):
        if not config:
            self.bail(-1, "no config: InstanceEla init")
        self.config = config
        self.debug = config["debug"]
        self.es = Elasticsearch(config["nodes"])
        
        super(InstanceEla, self).__init__(config)
    
    def createIndex(self):
        self.es.indices.delete("gold")
        res = self.es.indices.create(index="gold")
        print res
        self.es.indices.flush("gold")
        return
    
    def search(self, imgdata, dt):
        q = {
            "query": {
                "function_score": {
                    "functions": [
                        {
                        "script_score": {
                            "params": imgdata,
                            "script": "distance_gold"
                            }
                        }
                    ],
                    "query": {
                        "match_all": {}
                    },
                    "score_mode": "first"
                }
            },
#            "aggs" : {
#                "single_avg_price": {
#                    "terms" : { 
#                        "field" : "date",
#                        "size": 0,
#                    },
#                }
#            },
            "_source": ["futrue", "date", "time"], 
            "from": 0,
            "size": self.config["search_limit"], 
        }

        res = self.es.search(index="gold", body=q, timeout=100)
        return res
    
    def mkIndexData(self, pool_data):
        start_p = pool_data[0][5]
        walk = 0 #TODO
        chg_price = {}
        diff_arr = []
        for i in range(len(pool_data)):
            diff = (pool_data[i][5] - start_p)*1.0/start_p*self.config["diff_normal"]
            diff_arr.append(diff)
        diff_arr.sort(reverse=True)
        for i in range(len(pool_data)):
            chg_price["m"+str(i)] = diff_arr[i]
#        print chg_price
        return chg_price
    
    def groovyCode(self):
        print "groovy code is: "
        code = "-sqrt("
        for i in range(self.config["item_len"]):
            code += "pow(doc['m%d'].value-m%d, 2 ) + " % (i, i)
        code += "0)"
        print code
        writeToFile(self.config["groovy_path"]+self.config['groovy_file'], code)
        return 
    
    def loopIndex(self, one):
        self.pool_price.add(one)
        if self.pool_price.isFull():
            data = self.pool_price.getData()
            if self.config["pool_clean"]:
                self.pool_price.clean()
            else:
                self.pool_price.afterAdd()
            future_data_m = self.loop_data.split(self.loop_data.i, self.config["future_sizes"])
            future_datas = future_data_m.getChild()
            future_walk = future_datas[-1][5] - future_datas[0][9]
            
#            print data[-1][5], one[5], one[0], one[1]
#            print future_datas[0]
            doc = self.mkIndexData(data)
            doc["date"] = one[0]
            doc["time"] = one[1]
            doc["futrue"] = future_walk
            res = self.es.index(index="gold", doc_type="trade", body=doc)
#            print "--------------"
        return
    
    def index(self, start, end):
        self.mkt.reInit()
        self.groovyCode()
        self.pool_price = Pool(self.config['item_len'])
        self.dataLoop(10000, self.loopIndex, self.config["src"], start, end)
        return
    
    def bail(self, sig, msg):
        print sig, ": ", msg
        exit()
        
    def priceTest(self, one):
        self.order.tick(one[6], one[7], one[5])
        
        self.pool_test.add(one)
        if self.pool_test.isFull():
            data = self.pool_test.getData()
            if self.config["pool_clean"]:
                self.pool_test.clean()
            else:
                self.pool_test.afterAdd()
            future_data_m = self.loop_data.split(self.loop_data.i, self.config["future_sizes"])
            future_datas = future_data_m.getChild()
            future_walk = future_datas[-1][5] - future_datas[0][9]
            
#            print data[-1][5], one[5], one[0], one[1]
#            print future_datas[0]
            doc = self.mkIndexData(data)
            res = self.search(doc, one[0])
            #print one[0], one[1], future_walk
#            print printJson(res)
#            print res['hits']["hits"][0]["_source"], res['hits']["hits"][0]["sort"]
#            print res['hits']["hits"][1]["_source"], res['hits']["hits"][1]["sort"]
            up = sell = 0
            same = 1
            p_future = 0
            for one_hit in  res['hits']["hits"]:
                print one_hit["_source"]["date"],
                print one_hit["_source"]["time"],
                print one_hit["_score"],
                print one_hit["_source"]["futrue"]
                score = abs(one_hit["_score"])
                if score != 0 and score < 10:
                    #print one_hit["_source"], one_hit["sort"]
#                    if one_hit["_source"]["futrue"] > 0:
#                        p_future += 1
#                    elif one_hit["_source"]["futrue"] < 0:
#                        p_future -= 1
                    p_future += one_hit["_source"]["futrue"]
#            print up, sell
            check = p_future * future_walk
            if check < 0:
                self.test_err += 1
                self.profit -= abs(future_walk)
            elif check > 0:
                self.profit += abs(future_walk)
            else:
                self.profit += 0
            
            if p_future > 0:
                self.deal(2, one)
            elif p_future < 0:
                self.deal(1, one)
            else:
                self.deal(3, one)
            self.test_count += 1
            print res['hits']['total'], self.test_count, self.test_err, self.profit, p_future
            self.order.info()
#            print "-------------------"
        return 
    
    def validate(self, start, end):
        self.mkt.reInit()
        self.pool_test = Pool(self.config['item_len'])
        self.test_count = self.test_err = self.profit = 0
        self.order = Order(self.config["lose_move"], self.stop_lose)
        last_one = self.dataLoop(10000, self.priceTest, self.config["test_src"], start, end)
        self.order.close(last_one[0]+" "+last_one[1], last_one[5], STOP_T_CMD)
        res = self.order.info()
        if res:
            mkCsvFileWin("test_deals_info.csv", res)
        print self.test_count, self.test_err
        
def main():
    config = {
        "debug": True,
        "src": "data/XAUUSD1-hst-new.csv",
#        "src": "data/XAUUSD1.csv",
#        "src": "data/XAUUSD60.csv",
#        "test_src": "data/XAUUSD1.csv",
#        "test_src": "data/XAUUSD60.csv",
        "test_src": "data/XAUUSD1-hst-new.csv",
        "nodes": ["http://localhost:9200"],
        "stop_lose": 1000,
        "stop_win": 1000,
        "lose_move": True,
        "item_len": 200,
        "future_sizes": 2,
        "search_limit": 3,
        "diff_normal": 1000,
        "mkt_type": "time",
        "pool_clean": True,
        "groovy_path": "D:\\Program Files (x86)\\elasticsearch-1.5.2\\elasticsearch-1.5.2\\config\\scripts\\",
        "groovy_file": "distance_gold.groovy",
    }
    model = InstanceEla(config)    
#    model.createIndex()
#    model.index(0, 500000)
#    model.index(0+config["item_len"]/2, 500000+config["item_len"]/2)
    model.validate(500000, 600000)
    return

if __name__ == "__main__":
    main()


#        q = {
#            "query" : {
#                "match_all":{}
##                "bool": {
##                    "must_not": {
###                        "match": {
###                          "date": dt
###                        }
##                      }
##                }
#            },
##            "fields": ["m*"], 
#            "_source": ["futrue", "date", "time"], 
#            "from": 0,
#            "size": self.config["search_limit"], 
#            "sort" : {
#                "_script" : {
#                    "script" : "distance_gold",
#                    "type" : "number",
#                    "order" : "asc",
#                    "params" : imgdata
#                }
#            }
#        }