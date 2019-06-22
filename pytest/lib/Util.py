# coding=utf8

# Copyright 2010 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: 2010-8-19 16:41:48
# Note: This source file is NOT a freeware
# Version: Util.py 2010-8-19 16:41:48 jingyi Exp $

__author__="jingyi"
__date__ ="$2010-8-19 16:41:48$"

import sys, os;
import re
import traceback
import time
import urllib
import urllib2
import urlparse
import requests
import base64
import json
import shutil
import numpy
import skimage
import skimage.io
import skimage.color
gpu = 0
try:
    import gnumpy
    gpu = 1
except:
    gpu = 0

def loadImg(imgfile, caffe=True):
    img = skimage.img_as_float(skimage.io.imread(imgfile)).astype(numpy.float32)
    if caffe:
        if img.ndim == 2:
            img = img[:, :, numpy.newaxis]
            img = numpy.tile(img, (1, 1, 3))
        elif img.shape[2] == 4:
            img = img[:, :, :3]
    return img

def loadImgGray(imgfile, caffe=True):
    img = skimage.img_as_float(skimage.io.imread(imgfile)).astype(numpy.float32)
    img = skimage.color.rgb2gray(img)
    if caffe:
        if img.ndim == 2:
            img = img[:, :, numpy.newaxis]
            img = numpy.tile(img, (1, 1, 3))
        elif img.shape[2] == 4:
            img = img[:, :, :3]
    return img

def cosSimilar(a, b):
    global gpu
    res = 0
    if gpu == 1:
#        print "gpu"
        a = gnumpy.garray(a)
        b = gnumpy.garray(b)
        len_a = gnumpy.sqrt(gnumpy.dot(a,a))
        len_b = gnumpy.sqrt(gnumpy.dot(b,b))
        res = gnumpy.dot(a, b) / (len_a * len_b)
    else:
        a = numpy.array(a)
        b = numpy.array(b)
        len_a = numpy.sqrt(numpy.dot(a,a))
        len_b = numpy.sqrt(numpy.dot(b,b))
        res = numpy.dot(a, b) / (len_a * len_b)
    return 0.5 + 0.5 * res

def euclidSimilar(a, b):
    global gpu
    res = 0
    if gpu == 1:
#        print "gpu"
        a = gnumpy.garray(a)
        b = gnumpy.garray(b)
        c = a - b
        res = gnumpy.sqrt(gnumpy.dot(c, c))
    else:
        a = numpy.array(a)
        b = numpy.array(b)
        c = a - b
        res = numpy.sqrt(numpy.dot(c, c))
    return 1.0 / (1 + res)

def pearsonSimilar(inA,inB):
    inA = numpy.array(inA)
    inB = numpy.array(inB)
    if len(inA)<3:
        return 1.0
    return 0.5+0.5*numpy.corrcoef(inA,inB,rowvar=0)[0][1]

def mkdirs(dirs):
    dir_len = len(dirs)
    if dir_len > 0:
        path = ""
        for i in range(dir_len):
            try:
                path = path + dirs[i] + "/"
                if not os.path.exists(path):
                    os.mkdir(path)  
            except:
                continue
    
def cpWithPath(file_from, file_to):
    if not os.path.exists(file_from):
        print file_from, "not exists"
        return 

    file_arr = file_to.split('/')
    path_one = ""
    for one in file_arr[:-1]:
        path_one += one + "/"
        if not os.path.exists(path_one):
            os.mkdir(path_one)
    shutil.copy(file_from, file_to);
    return

def printJson(data):
    print json.dumps(data, indent=4)
            
def base64encodeStr(dt):
    return base64.b64encode(dt)

def base64decodeStr(dt):
    return base64.b64decode(dt)  

def base64encodeFile(fname):
    f = open(fname, "rb")
    ret = base64encodeStr(f.read())
    f.close()
    return ret

def emptyNList(n=2, t="list"):
    res = []
    for i in range(n):
        if t == "list":
            res.append([])
        elif t == "dic":
            res.append({})
    return res
        
def EAvg(prev_num, crr_num, e_n=10):
    a = 2.0 / (1 + e_n)
    ret = crr_num * a + prev_num * (1 - a)
    return ret

def md5(obj):
    import hashlib
    m = hashlib.md5()   
    m.update(obj)
    return m.hexdigest()

def mkCsvFileWin(name, content_arr):
    content = ""
    for one in content_arr:
        for k in range(len(one)):
            try:
                one[k] = '"' + one[k].replace('"', "'").replace(",", " ") + '"'
            except:
                one[k] = '"' + str(one[k]) + '"'
        content += ",".join(one) + "\n"
    writeToFile(name, toGb18030(content))
    return
    
def getUrlParam(name, urlstr):
    parsed = urlparse.urlparse(urlstr)
    return urlparse.parse_qs(parsed.query)[name]

def getNumberFromStr(thestr):
    thestr = toUtf(thestr)
    return re.findall(r'\d+', str(thestr))

def fetchUrl(urlstr, param = {}):
    print "fetching: " + urlstr
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cache-Control": "max-age=0",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36",
        "Connection": "keep-alive",
        "Content-Type": "text/html; charset=utf-8",
        "Accept-Charset": "utf-8",
    }
    if param.has_key("referer"):
        headers['Referer'] = param['referer']
    try:
        res = requests.get(urlstr, headers=headers, timeout=10)
        res.encoding = "utf-8"
        return res.text
    except:
        print('We failed to reach a server.')

    return False

def mysqlEscape(string):
    return re.escape(string)

def transUrlAndStr(target_str, trans_t = ""):
    if (trans_t == "u2s"):
        return urllib.unquote(target_str)
    elif trans_t == "s2u":
        return urllib.quote(target_str)
    else:
        if target_str.find("%") >= 0:
            return transUrlAndStr(target_str, "u2s")
        else:
            return transUrlAndStr(target_str, "s2u")

def removeJsCssContent(html_str):
    p = re.compile("<script.*</script>")
    res = p.sub( '', html_str)
    p = re.compile("<SCRIPT.*</SCRIPT>")
    res = p.sub( '', res)
    p = re.compile("<style.*</style>")
    res = p.sub( '', res)
    p = re.compile("<STYLE.*</STYLE>")
    p = re.compile("<textarea.*</textarea>")
    res = p.sub( '', res)
    p = re.compile("<TEXTAREA.*</TEXTAREA>")
    res = p.sub( '', res)
    return res

def getTitle(file_str):
    title = file_str[file_str.find("<title") + len("<title"): file_str.find("</title>")]
    if title == "":
        title = file_str[file_str.find("<TITLE") + len("<TITLE"): file_str.find("</TITLE>")]
    return title.strip(">").strip()

def getUrlFromFname(rootdname, fname):
    res = fname[fname.find(rootdname) + len(rootdname):]
    return res

def rmFile(fname):
    os.system("rm -f '" + fname + "'")
    return

def fileName(file_path):
    return file_path[file_path.rfind("/")+1:]

def mkYear():
    return int(time.strftime('%Y'))

def mkNextYear():
    return int(time.strftime('%Y')) + 1

def mktime():
    #return time.strftime('%Y%m%d%H%M%S')
    return time.strftime('%Y%m%d%H%M%S')

def mkDate():
    return time.strftime('%Y-%m-%d')

def strTime2int(time_str):
    try:
        res = time.mktime(time.strptime( str(time_str), "%Y-%m-%d %X" ))
    except:
        res = 0
    return int(res)

def helpInfo(err_str = ""):
    if err_str != "":
        print err_str
    print "Usage: "
    print sys.argv[0] + " conf_file"
    return

def getFileContent(file_name):
    if not os.path.isfile(file_name):
        print "No such file! " + file_name
        return False
    content = ""
    if (len(file_name) > 0):
        try:
            fp = open(file_name, "r")
            content = fp.read()
            content = content.strip()
            content = content.strip("\n")
        except:
            print "No file: " + file_name
            content = ""
        try:
            fp.close()
        except:
            1
    return toUtf(content)

def writeToFile(file_name, content, flag="w"):
    fp = open(file_name, flag)
    fp.write(content)
    fp.flush()
    fp.close()
    return

def cleanNR(the_str):
    the_str = the_str.replace('\n', ' ')
    the_str = the_str.replace('\r', ' ')
    return the_str

def readFileLines(file_name):
    content = getFileContent(file_name)
    if content == False:
        return False
    source_ls = content.split("\n")
    return source_ls

def walkDir(dirname):
    if not os.path.exists(dirname):
        print "No such dir! " + dirname
        return False
    file_ls = []
    for root, dirs, files in os.walk(dirname, True):
        for name in files:
            one_path = os.path.join(root,name)
            file_ls.append(one_path)
    return file_ls

def exeCmd(command, isret = True):
    try:
        if isret:
            pipe = os.popen(command)
            res = pipe.read()
            pipe.close()
            return str(res).strip()
        else:
            os.system(command)
    except:
        print "error execute command: "
        print command
        sys.exit()
    return

def crrFileDir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
    
def toUtf(s):
    if isinstance(s, unicode):
        print "just encode"
        return s.encode('utf-8')
    else:
        try:
            try:
                return unicode(s, "GBK").encode('utf-8')
            except:
                try:
                    return unicode(s, "gb2312").encode('utf-8')
                except:
                    return unicode(s, "gb18030").encode('utf-8')
        except:
            try:
                return unicode(s, "ascii").encode('utf-8')
            except:
                print "use default encode"
                return s

def toGb18030(s):
    if isinstance(s, unicode):
        return s.encode('gb18030')
    else:
        try:
            return unicode(s, "utf-8").encode('GBK')
        except:
            try:
                return unicode(s, "ascii").encode('gb18030')
            except:
                return s

def traceBack(is_str = True):
    try:
        if is_str:
            return traceback.format_exc()
        else:
            return traceback.print_exc()
    except:
        return ""
