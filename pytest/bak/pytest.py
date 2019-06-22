# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="jingyi"
__date__ ="$2014-12-20 21:17:02$"

from lib.Util import *

d_file = "data/detail.csv"
dt_file = "data/dt.csv"

max_week = 0
min_week = 5000
volume_week = 0
amount_week = 0

if __name__ == "__main__":
    dt = readFileLines(dt_file)
    price = []
    data = readFileLines(d_file)
    index = 0
    for one in data:
        one = one.split(",")
        day = one[0]
        max = float(one[1])
        min = float(one[2])
        volume = float(one[3])
        if (day <= dt[index]):
            volume_week += volume
            amount_week += volume * (max + min) / 2
            if max_week < max:
                max_week = max
            if min_week > min:
                min_week = min
        else:
            avg = (max_week + min_week) / 2
            cost_avg = amount_week / volume_week
            print str(cost_avg)
            
            volume_week = volume
            amount_week = volume * (max + min) / 2
            max_week = 0
            min_week = 5000
            if max_week < max:
                max_week = max
            if min_week > min:
                min_week = min
            index += 1
            if index >= len(dt):
                break
#            print day + ": " + str(avg)
#        break
#        max = one[]
