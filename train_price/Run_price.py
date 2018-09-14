'''@author: yzw
'''
#!/usr/bin/python  
# -*- coding:utf-8 -*- 
import re
import json
import urllib
from urllib import request
import requests
from prettytable import PrettyTable
import station
import time
import os
import sys


SearchListFile = "searchList.txt"
SearchBegin = 95000
SearchEnd = 97900
SearchIntervalTime = 6


def getCityList(configFile):
    fp = open(configFile, "r")
    if fp is None:
        return
    city = []
    nSize = os.path.getsize(configFile)
    content = fp.read(nSize)
    tmpList = content.split("\n")
    print(tmpList)
    for i in tmpList:
        if i not in station.stations:
            print(i)
            continue
        if len(i) > 0:
            city.append(i)
    print("city len = %d" % (len(city)))
    return city


def generateQueryUrl(start, end):

    f = station.stations[start]
    t = station.stations[end]

    localTime = time.localtime(time.time())
    date = ("%d-%02d-%02d" %(localTime.tm_year, localTime.tm_mon, localTime.tm_mday + 5))
    print(localTime)
    print('正在查询' + f + '至' + t + '的列车......')
    url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=' + date + '&leftTicketDTO.from_station=' + f + '&leftTicketDTO.to_station=' + t + '&purpose_codes=ADULT'
    return url

def auxGetPriceByTrain(row):

    tmpList = row.split("|")
    tmpLength = len(tmpList)

    train_no = tmpList[2]
    train_name  = tmpList[3]
    cost_time = tmpList[10]

    from_station_no = tmpList[16]
    to_station_no = tmpList[17]
    seat_types = tmpList[35]
    localTime = time.localtime(time.time())
    date = ("%d-%02d-%02d" % (localTime.tm_year, localTime.tm_mon, localTime.tm_mday + 5))
    url_price = "https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no=" + train_no + "&from_station_no=" + \
                from_station_no + "&to_station_no=" + to_station_no + "&seat_types=" + seat_types + "&train_date=" + date

    r_price = ""
    try:
        req = urllib.request.Request(url_price)
        r_price = urllib.request.urlopen(req).read().decode('utf-8')
    except :
        print("get price request Failed")
        return
    try:
        r_price = json.loads(r_price)

    except json.decoder.JSONDecodeError:
        print(r_price)
        return
    price = ""
    if 'data' in r_price:
        price = r_price['data']
    else:
        print("r_price data invalid")
        return None
    price = dict(price)
    minPrice = 0xFFFFFFFF
    for i in price.keys():
        if "¥" in price[i]:
            index = price[i].find("¥")
            tmpPrice = price[i][index + 1:]
            tmpPrice = float(tmpPrice)
            if tmpPrice < minPrice:
                minPrice = tmpPrice
    return minPrice

def get_price(start, end):
    url = generateQueryUrl(start, end)
    if url is None:
        return None
    r = ""
    try:
        r = requests.get(url, verify=False)
    except requests.exceptions.ConnectionError:
        print("start = %s, end = %s, request failed" %(start, end))
        return None
    print(url)
    if r is None:
        print("start = %s, end = %s, request failed" % (start, end))
        return None
    tmpJson = ""
    try:
        tmpJson = r.json()
    except json.decoder.JSONDecodeError:
        print("request json error")
        return None
    rows = ""
    if tmpJson['status'] != True:
        print("return status error")
        #print(tmpJson)
        return None
    if "data" in tmpJson:
        tmpData = tmpJson['data']
        #print(type(tmpData))
        if 'result' in tmpData:
            rows = tmpData['result']

    if rows == '':
        print("over=====")
        return None
    trains= PrettyTable()
    #header = '车次 车站 时间 历时 商务座/价格 特等座/价格  一等座/价格  二等座/价格  高级软卧/价格  软卧/价格   硬卧/价格  软座/价格  硬座/价格  无座/价格 '.split()
    trains.field_names=["车次","车站","时间","历时","商务座/价格","特等座/价格","一等座/价格","二等座/价格","高级软卧/价格","软卧/价格","硬卧/价格 ","软座/价格 ","硬座/价格","无座/价格"]
    trains.align["车次"] = "l"
    trains.padding_width = 2
    num = len(rows)
    minTime = "99:99"
    minTimeIndex = -1
    validCount = 0
    for i in range(num):
        tmpList = rows[i].split("|")
        if tmpList is None:
            continue
        if len(tmpList) < 36:
            continue
        if "99:59" == tmpList[10]:
            validCount = validCount + 1
        #print("trainName = %s, beginTime = %s, endTime = %s, costTime = %s" %(tmpList[3], tmpList[8], tmpList[9], tmpList[10]))
        if tmpList[10] < minTime:
            minTime = tmpList[10]
            minTimeIndex = i
    if minTimeIndex == -1:
        print("get min cost Time Failed, num = %u" %(num))
        return None
    validCount = num - validCount
    if validCount < 1:
        print("no valid Train")
        return None
    row = rows[minTimeIndex]
    price = auxGetPriceByTrain(row)

    tmpList = row.split("|")
    if price is None:
        print("trainName = %s, costTime = %s, Get Price Failed" %(tmpList[3], tmpList[10]))
        return None
    print("price = %f" % price)
    result = (start, end, tmpList[3], tmpList[8], tmpList[9], tmpList[10], validCount, price)
    print(result)
    return result

def getCityTrainPrice():
    #cityList = getCityList("config.txt")
    #length = len(cityList)

    global SearchBegin
    global SearchEnd
    global SearchListFile
    global SearchIntervalTime

    searchList = getSearchList(SearchListFile, SearchBegin, SearchEnd)
    length = len(searchList)
    fp = None
    Num = 0
    while True:
        logFile = "search%d.log" % Num

        if os.access(logFile, os.F_OK):
            Num = Num + 1
        else:
            fp = open(logFile, "w+")
            break
    if fp is None:
        print("open log File Failed")
        return None

    for i in searchList:
        if ',' not in i:
            continue
        tmpList = i.split(',')
        time.sleep(SearchIntervalTime)
        tmpResult = get_price(tmpList[0], tmpList[1])
        writeStr = ""
        if tmpResult is None:
            writeStr = "%s,%s,NULL\n" %(tmpList[0], tmpList[1])
        else:
            writeStr = "%s,%s,%s,%s,%s,%s,%d,%f\n" %(tmpResult[0], tmpResult[1], tmpResult[2], tmpResult[3], tmpResult[4], tmpResult[5], tmpResult[6], tmpResult[7])
        fp.write(writeStr)

    fp.close()
    return True

def getValidSearch():
    fp = open("search.log", "r")
    if fp is None:
        return None
    nSize = os.path.getsize("search.log")
    content = fp.read(nSize)
    lineList = content.split('\n')
    fp.close()
    result = []
    for i in lineList:
        if len(i) == 0:
            continue
        if "NULL" in i:
            continue
        print(i)
        result.append(i)
    print(len(result))
    return result

def generateSearchList(configFile):
    cities =  getCityList(configFile)
    length = len(cities)
    global SearchListFile
    searchListFile = SearchListFile
    fp = open(searchListFile, "w+")
    if fp is None:
        return None
    for i in range(length):
        for j in range(length):
            if i == j:
                continue
            writeStr = "%s,%s\n" % (cities[i], cities[j])
            fp.write(writeStr)
    fp.close()
    return True

def getSearchList(searchListFile, start, end):
    fp = open(searchListFile, "r")
    if fp is None:
        return None
    nSize = os.path.getsize(searchListFile)
    content = fp.read(nSize)
    lineList = content.splitlines()
    fp.close()
    if len(lineList) >= end:
        return lineList[start : end]
    return lineList[start:]


if __name__ == "__main__":
    #getValidSearch()
    #generateSearchList("config.txt")
    getCityTrainPrice()

    #url = generateQueryUrl("武汉", "北京")
    #print(url)
    #result = get_price("南充", "岳阳")
    #print(result)

