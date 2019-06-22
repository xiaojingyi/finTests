#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Jingyi Xiao
#
# Encoding: UTF-8
# Author: Jingyi Xiao <kxwarning@126.com>
# Created time: $2015-4-7 21:28:13$
# Note: This source file is NOT a freeware
# Version: main.py 0.1 jingyi Exp $

__author__="jingyi"
__date__ ="$2015-4-7 21:28:13$"

import os, sys, time
os.environ['NLS_LANG'] = "SIMPLIFIED CHINESE_CHINA.UTF8"

if __name__ == "__main__":
#    import server_test_only_updown_vol as run
#    import np_test as run

#    import analyse_test as run
#    run.main()

#    import indexes_test as run
#    run.main()

#    import ClassDraw as run
#    run.main()
    
#    import InstanceEla as run
#    run.main()

    import InstanceDnn as run
    run.main()