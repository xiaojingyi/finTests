#! /usr/bin/python
# coding=utf8

# Copyright 2010 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: 2010-10-25 14:44:54
# Note: This source file is NOT a freeware
# Version: Mysql.py 2010-10-25 14:44:54 jingyi Exp $

__author__="jingyi"
__date__ ="$2010-10-25 14:44:54$"

import MySQLdb
import string
import Util
import sys

class Mysql:
    def __init__(self, ip, database, username, password, socket = "/var/lib/mysql/mysql.sock"):
        self._database = database
        self._user = username
        self._passwd = password
        self._host = ip
        self.socket = socket
        self.connect()
        return
    
    def connect(self):
        self.conn = MySQLdb.connect(host=self._host, user=self._user, \
                                 passwd=self._passwd,db=self._database, charset="utf8",\
                                 unix_socket=self.socket) 
        self.cursor = self.conn.cursor()
        return

    def truncateTable(self, tname):
        self.cursor.execute("truncate table " + tname)
        return
    
    def query(self,sql):
        self.cursor.execute(sql)
        res = []
        while True:
            tmp_res = []
            one_res = self.cursor.fetchone()
            if one_res == None:
                break
            for one_col in one_res:
                tmp_res.append(one_col)
            res.append(tmp_res)
        return res

    def execute(self,sql):
        self.cursor.execute(sql)
        return

    def getTableInfo(self, tname):
        res = {}
        sql = "desc " + tname
        self.cursor.execute(sql)
        sql_res = self.cursor.fetchall()
        res_col = ""
        for one_c in sql_res:
            res_col += one_c[0] + ","
        res["cols"] = res_col.strip(",")
        res["len"] = len(sql_res)
        res["cols_arr"] = sql_res
        res["table_name"] = tname
        return res

    def close(self):
        self.conn.close()
        return

if __name__ == "__main__":
    print "Hello World";
