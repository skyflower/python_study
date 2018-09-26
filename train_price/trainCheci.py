

import urllib
import bs4
import os
import sys
import chardet
import xlwt


RootSite = "http://www.jt2345.com"
checiSubSite = "/huoche/checi/"


def getUrlContent(url):
    try:
        f = urllib.request.urlopen(url)
        if f is None:
            return None
        response = f.read()
        f.close()
    except urllib.error.URLError:
        print("url = %s, Error" % url)
        return None

    try:

        code = chardet.detect(response)
        if 'encoding' not in code:
            return None

        content = response.decode(code['encoding'], "ignore")
        #content = str(response, code['encoding'], )
        return content
    except :
        print("content to str encoding Failed")
        return None


def parseStationList(content):
    Num = content.count("/huoche/zhan/")

    i = 0
    length = len(content)

    result = []

    while i < length:
        index = content.find("/huoche/zhan/", i)
        if index == -1:
            i = i + 10
            continue

        tmpIndex = content.find("htm", index + 1, index + 150)
        if tmpIndex == -1:
            i = index + 4
            continue

        tmpNameBegin = content.find(">", tmpIndex + 1, tmpIndex + 10)
        if tmpNameBegin == -1:
            i = tmpIndex + 4

            continue
        tmpNameEnd = content.find("</a>" ,tmpNameBegin + 1, tmpNameBegin + 20)
        if tmpNameEnd == -1:
            i = tmpNameBegin + 4
            continue

        stationName = content[tmpNameBegin + 1 : tmpNameEnd]

        tmpBegin = content.find("<td>", tmpIndex + 4, tmpIndex + 30)
        if tmpBegin == -1:
            i = tmpIndex +  4
            continue
        tmpEnd = content.find("</td>", tmpBegin + 1, tmpBegin + 20)
        if tmpEnd == -1:
            i = tmpBegin + 1
            continue
        startTime = content[tmpBegin + 4 : tmpEnd]
        tmpBegin = content.find("<td>", tmpEnd + 4, tmpEnd + 20)
        if tmpBegin == -1:
            i = tmpEnd + 4
            continue
        tmpEnd = content.find("</td>", tmpBegin + 1, tmpBegin + 20)
        if tmpEnd == -1:
            i = tmpBegin + 1

            continue
        endTime = content[tmpBegin + 4 : tmpEnd]

        tmpLine = "%s,%s,%s\n" %(stationName, startTime, endTime)
        result.append(tmpLine)
        i = tmpEnd + 4
    return result



def getTrainList(urlRoot):

    global  RootSite
    content = getUrlContent(urlRoot)
    if (content == None) or (len(content) < 100):
        print("get Url content Failed")
        return None

    length = content.count("href")
    print("length = %u" % length)
    i = 0
    tmpIndex = 0
    value = []
    while i < length:
        #print(tmpIndex)
        tmpIndex = content.find('href', tmpIndex + 4)
        #print(content[tmpIndex : tmpIndex + 20])
        if tmpIndex == -1:
            break
        tmpBeginOne = content.find('"', tmpIndex, tmpIndex + 10)
        tmpBeginTwo = content.find("'", tmpIndex, tmpIndex + 10)
        tmpBegin = 0
        if (tmpBeginOne == -1) and(tmpBeginTwo == -1):
            tmpBegin = min(tmpBeginOne, tmpBeginTwo)
        elif tmpBeginOne == -1:
            tmpBegin = tmpBeginTwo
        elif tmpBeginTwo == -1:
            tmpBegin = tmpBeginOne

        if tmpBegin == 0:
            continue

        tmpEndOne = content.find('"', tmpBegin + 5, tmpBegin + 100)
        tmpEndTwo = content.find("'", tmpBegin + 5, tmpBegin + 100)

        tmpEnd = 0
        if (tmpEndOne == -1) and (tmpEndTwo == -1):
            tmpEnd = min(tmpEndOne, tmpEndTwo)
        elif tmpEndOne == -1:
            tmpEnd = tmpEndTwo
        elif tmpEndTwo == -1:
            tmpEnd = tmpEndOne

        if tmpEnd == 0:
            continue

        value.append(content[tmpBegin + 1:tmpEnd])
        i = i + 1

    print(len(value))
    os.mkdir("./tmpSite")

    dirList = os.walk("./tmpSite")
    tmpResult = []
    for rootDir, subDir, filename in dirList:
        for i in filename:
            if '.' in i:
                tmpIndex = i.find('.')
                tmpResult.append(i[:tmpIndex])
        break

    TrainNum = []
    invalidCount = 0
    for i in value:
        #print(i)
        beginIndex = i.rfind("/")
        endIndex = i.find('.htm')
        if (beginIndex != -1) and(endIndex != -1) and(endIndex > beginIndex + 1):
            TrainNum.append(i[beginIndex + 1:endIndex])
        else:
            TrainNum.append(0)
            invalidCount = invalidCount + 1

    print("invalidCount = %u" % invalidCount)

    invalidCount = 0
    TrainNumLength = len(TrainNum)
    for i in range(TrainNumLength):
        if TrainNum[i] in tmpResult:
            TrainNum[i] = 0
            invalidCount = invalidCount + 1
    print("invalidCount = %u" % invalidCount)

    j = -1
    tmpCount = 0

    for i in value:
        j = j + 1
        if TrainNum[j] == 0:
            continue
        if "htm" not in i:
            continue

        tmpIndex = i.find("htm")
        tmpUrl = RootSite + i[:tmpIndex + len("htm")]
        print(tmpUrl)
        content = getUrlContent(tmpUrl)

        if (content is None) or (len(content) < 100):
            print("j = %u, get Url = %s, content Failed" %(j, tmpUrl))

        else:
            result = parseStationList(content)
            if (result != None) and (len(result) > 1):
                tmpBegin = i.rfind("/")
                if tmpBegin != -1:
                    trainName = i[tmpBegin + 1 : tmpIndex]
                    fp = open("./tmpSite/" + trainName + "txt", "w+")
                    for tmp in result:
                        fp.write(tmp + " ")
                    fp.close()

    return value


def MergeSearchSort():
    fileDir = "D:\\Cache\\Pycharm\\GetTrainPrice\\SearchResult\\"
    fileList = os.listdir(fileDir)
    print(fileList)

    fp = open(fileDir + "total.txt", "w+")
    if fp is None:
        print("create total.txt Failed")
        return
    for tmpFile in fileList:
        print(tmpFile)
        tmpFp = open(fileDir + tmpFile, "r")
        if tmpFp is None:
            continue
        tmpSize = os.path.getsize(fileDir + tmpFile)
        tmpContent = tmpFp.read(tmpSize)
        tmpFp.close()
        tmpLineList = tmpContent.splitlines()
        #tmpResult = []
        for tmpLine in tmpLineList:
            tmpQuoteCount = tmpLine.count(',')
            if tmpQuoteCount == 7:
                fp.write(tmpLine + "\n")


    fp.close()

def delRundunt():
    filename = "D:\\Cache\\Pycharm\\GetTrainPrice\\SearchResult\\total.txt"
    fileNoSame = "D:\\Cache\\Pycharm\\GetTrainPrice\\SearchResult\\NoSame.txt"

    nSize = os.path.getsize(filename)
    fp = open(filename, "r")
    if fp is None:
        print("open %s Failed" % filename)
        return
    content = fp.read(nSize)
    fp.close()
    lineList = content.splitlines()
    result = []
    for i in lineList:
        if i in result:
            continue
        result.append(i)

    fp = open(fileNoSame, "w+")
    if fp is None:
        print("Open %s Failed" % fileNoSame)
        return
    for i in result:
        fp.write(i + "\n")
    fp.close()


def writeToExcel():

    xlsx = "D:\\Cache\\Pycharm\\GetTrainPrice\\SearchResult\\TrainData.xlsx"
    configFile = "D:\\Cache\\Pycharm\\GetTrainPrice\\config.txt"
    fileNoSame = "D:\\Cache\\Pycharm\\GetTrainPrice\\SearchResult\\NoSame.txt"

    fp = open(configFile, "r")
    if fp is None:
        print("Open File %s Failed" % configFile)
        return
    nSize = os.path.getsize(configFile)
    content = fp.read(nSize)
    fp.close()
    TrainName = content.splitlines()


    fp = open(fileNoSame, "r")
    if fp is None:
        print("Open File %s Failed" % configFile)
        return
    nSize = os.path.getsize(fileNoSame)
    content = fp.read(nSize)
    fp.close()
    LineList = content.splitlines()



    book = xlwt.Workbook(encoding='utf-8')
    sheetTime = book.add_sheet("Time", cell_overwrite_ok=True)
    sheetPrice = book.add_sheet("Price", cell_overwrite_ok=True)
    sheetCount = book.add_sheet("Count", cell_overwrite_ok=True)

    sheetTimeCopy = book.add_sheet("TimeCopy", cell_overwrite_ok=True)
    sheetPriceCopy = book.add_sheet("PriceCopy", cell_overwrite_ok=True)
    sheetCountCopy = book.add_sheet("CountCopy", cell_overwrite_ok=True)

    Step = 250

    TrainNameCount = len(TrainName)
    for i in range(TrainNameCount):
        if i + 1 < Step:
            sheetTime.write(i + 1, 0, TrainName[i])
            sheetTime.write(0, i + 1, TrainName[i])

            sheetPrice.write(i + 1, 0, TrainName[i])
            sheetPrice.write(0, i + 1, TrainName[i])

            sheetCount.write(i + 1, 0, TrainName[i])
            sheetCount.write(0, i + 1, TrainName[i])
        else:
            sheetTime.write(i + 1, 0, TrainName[i])
            sheetTimeCopy.write(0, i + 1 - Step, TrainName[i])

            sheetPrice.write(i + 1, 0, TrainName[i])
            sheetPriceCopy.write(0, i + 1 - Step, TrainName[i])

            sheetCount.write(i + 1, 0, TrainName[i])
            sheetCountCopy.write(0, i + 1 - Step, TrainName[i])

    for i in LineList:
        tmpList = i.split(',')
        beginIndex = TrainName.index(tmpList[0])
        endIndex = TrainName.index(tmpList[1])
        if (beginIndex == -1) or (endIndex == -1):
            continue
        if endIndex + 1 < Step:
            sheetTime.write(beginIndex + 1, endIndex + 1, tmpList[5])
            sheetPrice.write(beginIndex + 1, endIndex + 1, tmpList[7])
            sheetCount.write(beginIndex + 1, endIndex + 1, tmpList[6])
        else:
            sheetTimeCopy.write(beginIndex + 1, endIndex + 1 - Step, tmpList[5])
            sheetPriceCopy.write(beginIndex + 1, endIndex + 1 - Step, tmpList[7])
            sheetCountCopy.write(beginIndex + 1, endIndex + 1 - Step, tmpList[6])


    book.save(xlsx)
    print("saveFile = %s" % xlsx)

if __name__ == "__main__":
    getTrainList(RootSite + checiSubSite)
    #MergeSearchSort()
    #delRundunt()
    #writeToExcel()

