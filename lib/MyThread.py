#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2010 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: 2010-12-14 11:26:21
# Note: This source file is NOT a freeware
# Version: Thread.py 2010-12-14 11:26:21 jingyi Exp $

__author__="jingyi"
__date__ ="$2010-12-14 11:26:21$"

import threading, sys
from threading import Thread
import time

# the container of all threads
class WorkerManager:
    def __init__( self, num_of_workers=10):
        self.pool_max = num_of_workers
        self.workers = []

    def wait_for_complete( self ):
        for one in self.workers:
            one.join()
        print "All jobs are all completed."

    def add_job( self, callable, args ):
        print "start new thread: ", args
        while threading.activeCount() >= self.pool_max:
            #print "max: ", threading.activeCount()
            time.sleep(0.1)

        t = threading.Thread(target=callable, args=args)
        t.start()
        self.workers.append(t)

def simple_job(id):
    for i in range (10000000):
        b = 2**11
    print id
    return id

def main():
    wm = WorkerManager(3)
    for i in range(100):
        param = [i, 2]
        wm.add_job(simple_job, [param])

    wm.wait_for_complete()

if __name__ == "__main__":
    main()
