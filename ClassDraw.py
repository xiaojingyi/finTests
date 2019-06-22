import random
#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-5-9 21:40:12$
# Note: This source file is NOT a freeware
# Version: ClassDraw.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-5-9 21:40:12$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"
import numpy as np
from ClassDataSrc import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ClassPool import *
import random
from PIL import Image 
from lib.Util import *
import shutil

class ClassDraw(object):
    def __init__(self, config):
        if not config:
            self.bail(-1, "no config: ClassDraw init")
        self.config = config
        self.debug = config["debug"]
        self.root_path = config["root_path"] + "/"
        self.img_path = self.root_path + config["img_path"] + "/"
        self.pools = []
        for one in self.config["pool_sizes"]:
            self.pools.append(Pool(one))
        self.i = 0
        self.fname = "img-"
        if not os.path.exists(self.img_path):
            os.mkdir(self.img_path)
    
    def filePath(self):
        return self.img_path + self.fname + str(int(time.time())) + "-" + str(random.randint(11111,99999))+".png"
    
    def createImgDB(self):
        config = {
            "src": self.config["src"],
            "item_len": 60,
            "train_len": 200,
            "test_len": 50,
        }
        datas = DataMatrixGen(config)
        fhandle = open(self.img_path+"label.txt", "w")
        while(1):
            self.i += 1
            one = datas.getLine()
            if not one:
                break
            tm = one[0] + " " + one[1]
            price = one[5]
            prices = self.poolsAdd(price, tm)
            if len(prices) > 0:
                file_name = self.plot(prices, tm)
                future_data_m = datas.split(datas.i, self.config["pool_sizes"][-1]/2)
                future_datas = future_data_m.getChild()
                walk = future_datas[-1][5] - future_datas[0][9]
                label = 0
                if abs(walk) > 2:
                    label = int(abs(walk) / walk)
                label += 2
                print walk, label
                fhandle.write(file_name + " " + str(label) + "\n")
#                print np.array(future_data_m.getChild())
#                exit()
        fhandle.flush()
        fhandle.close()
        self.mkCaffeData(self.img_path+"label.txt")
        return
    
    def mkCaffeData(self, lbfile):
        lines = readFileLines(lbfile)
        len_f = len(lines)
        print "len: ", len_f
        
        train_lines = []
        val_lines = []
        
        for i in range(len_f):
            rd_choose = random.randint(1,len_f*100-1)
#            print rd_choose, len_f * self.config["caffe_val_per"]
            one = lines[i].split(" ")
            if rd_choose < len_f * self.config["caffe_val_per"]*100:
                val_path = self.img_path + "val/"
                if not os.path.exists(val_path):
                    os.mkdir(val_path)
                new_path = one[0].replace(self.img_path, val_path)
                one.append(new_path)
                shutil.move(one[0], new_path)
                val_lines.append(one)
            else:
                train_path = self.img_path + "train/"
                if not os.path.exists(train_path):
                    os.mkdir(train_path)
                train_path = self.img_path + "train/trend" + str(one[1]) + "/"
                if not os.path.exists(train_path):
                    os.mkdir(train_path)
                new_path = one[0].replace(self.img_path, train_path)
                one.append(new_path)
                shutil.move(one[0], new_path)
#                print one
                train_lines.append(one)
        print len(val_lines), len(train_lines)
        self.createCaffeFile(self.img_path + "train.txt", train_lines)
        self.createCaffeFile(self.img_path + "val.txt", val_lines)
        return
    
    def createCaffeFile(self, fname, data):
        fhandle = open(fname, "w")
        for one in data:
            fhandle.write(one[2] + " " + one[1] + "\n")
        fhandle.flush()
        fhandle.close()
        return
    
    def plot(self, datas, tm):
#        plt.figure(1)
        i = 1
        len_datas = len(datas)
        for one in datas:
            index = len_datas * 100 + 10 + i
            
            ax = plt.subplot(index)
            plt.axis("off")
#            ax.set_axis_bgcolor('red')
            plt.plot(one)
            i += 1
        file_name = self.filePath()
        plt.savefig(file_name)
        plt.close("all")
        img = Image.open(file_name)   
        new_img = img.resize((800/self.config["resize"],600/self.config["resize"]),Image.BILINEAR)   
        new_img.save(file_name)
#        while True:
#            try:
#                img = Image.open(file_name)   
#                new_img = img.resize((800/self.config["resize"],600/self.config["resize"]),Image.BILINEAR)   
#                new_img.save(file_name)
#                break
#            except:
#                print "error"
#                continue

#        plt.show()
        return file_name
        
    def poolsAdd(self, price, tm):
        is_full = True
        ret = []
        p_len = len(self.pools)
        i = 0
        for one in self.pools:
            one.add(price)
            ret.append(one.getData(False))
            if one.reach_max != True:
                is_full = False
            else:
                1
#                if i == p_len - 1:
#                    one.clean()
#            print one.len
            i += 1
        if is_full:
            print tm
            for one in ret:
                print one[0],
            print
            for one in ret:
                print one[-1],
            print
            return ret
        return []
    
    def bail(self, sig, msg):
        print sig, ": ", msg
        exit()
    
    def main(self):
        self.createImgDB()
        
    def test(self):
        print "debug: ", self.debug
        self.mkCaffeData(self.img_path+"label.txt")
        
def main():
    config = {
        "src": "data/XAUUSD1-hst-new.csv",
#        "src": "data/XAUUSD1.csv",
#        "src": "data/XAUUSD60.csv",
        "debug": True,
        "root_path": ".",
        "img_path": "images",
#        "pool_sizes": [14400, 7200, 720, 72],
        "pool_sizes": [7200, 1440, 600, 300, 120],
        "caffe_val_per": 0.08,
        "resize": 3,
    }
    model = ClassDraw(config)
    model.test()
    return

if __name__ == "__main__":
    main()
