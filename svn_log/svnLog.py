#coding=utf-8

import xlwt
import os

class baseLog:
    def __init__(self):
        self.revision = ""
        self.author = ""
        self.time = ""
        self.message = ""
    def setRevision(self, revision):
        self.revision = revision
    def setAuthor(self, author):
        self.author = author
    def setTime(self, time):
        self.time = time
    def setMessage(self, msg):
        self.message = msg
    def getRevision(self):
        return self.revision
    def getAuthor(self):
        return self.author
    def getTime(self):
        return self.time
    def getMessage(self):
        return self.message
    def __str__(self):
        str = ("Revision : %s\nTime : %s\nAuthor : %s\nMessage : %s") %(self.revision, self.time, self.author, self.message)
        return str

class CConfig:

    def __init__(self):
        self.svnPath = ""
        self.startTime = ""
        self.endTime = ""
        self.saveFileName = ""
        self.validStatus = True
        fileName = "config.txt"
        fp = open(fileName, "rb")
        if fp is None:
            self.validStatus = False
            return
        while True:
            line = fp.readline()
            if (line is None) or (len(line) == 0):
                break
            if "rootDir" in line:
                tmpList = line.split('"')
                if len(tmpList) < 2:
                    print("rootDir invalid parameter")
                    self.validStatus = False
                    break
                self.svnPath = tmpList[1]
            elif "startDate" in line:
                tmpList = line.split('"')
                if len(tmpList) < 2:
                    print("startDate invalid parameter")
                    self.validStatus = False
                self.startTime = tmpList[1]
            elif "endDate" in line:
                tmpList = line.split('"')
                if len(tmpList) < 2:
                    print("endDate invalid parameter")
                    self.validStatus = False
                self.endTime = tmpList[1]
            elif "saveFile" in line:
                tmpList = line.split('"')
                if len(tmpList) < 2:
                    print("saveFile invliad parameter, please ckeck")
                    self.saveFileName = ""
                else:
                    self.saveFileName = tmpList[1]

        fp.close()
        if self.validStatus == False:
            return
        tmpList = self.startTime.split('-')
        if len(tmpList) < 6:
            print("startDate invalid parameter")
            self.validStatus = False
            return
        self.startTime = tmpList

        tmpList = self.endTime.split('-')
        if len(tmpList) < 6:
            print("endDate invalid parameter")
            self.validStatus = False
            return
        self.endTime = tmpList

        if self.saveFileName == "":
            tmpList = self.svnPath.split('/')
            if len(tmpList) > 1:
                self.saveFileName = "%s_%s.xlsx" %(tmpList[-2] ,tmpList[-1])
            else:
                self.saveFileName = tmpList[-1] + ".xlsx"
        self.validStatus = True

    def getStatus(self):
        return self.validStatus
    def getCommand(self):

        startTime = "{0[0]}-{0[1]}-{0[2]}T{0[3]}:{0[4]}:{0[5]}".format(self.startTime)
        endTime = "{0[0]}-{0[1]}-{0[2]}T{0[3]}:{0[4]}:{0[5]}".format(self.endTime)

        command = "svn log " + "-r{" + startTime + "}:{" + endTime + "}  " + self.svnPath
        return command
    def getFileName(self):
        if "." in self.saveFileName:
            index = self.saveFileName.rfind('.')
            pre = self.saveFileName[:index]
            last = self.saveFileName[index:]
            path = pre + ("_%s%s%s_%s%s%s" %(self.startTime[0], self.startTime[1], self.startTime[2], self.endTime[0], self.endTime[1], self.endTime[2])) + last
            return path
        else:
            path = self.saveFileName + ("_%s%s%s_%s%s%s.xlsx" %(self.startTime[0], self.startTime[1], self.startTime[2], self.endTime[0], self.endTime[1], self.endTime[2]))
            return path

    def getSVNPath(self):
        return self.svnPath
    def getStartTime(self):
        return self.startTime
    def getEndTime(self):
        return self.endTime

    def Print(self):
        print("svnpath--------startTime--------endTime---------saveFileName")
        print(self.svnPath)
        print(self.startTime)
        print(self.endTime)
        print(self.saveFileName)

def setHeaderStyle(sheet, parameter):
    stype = xlwt.XFStyle()
    fnt = xlwt.Font()

    fnt.name = u"宋体"

    stype.font.bold = True
    stype.font.font = fnt
    #stype.font.charset = u"courier new"
    stype.borders.left = 0xff
    stype.borders.right = 0xff
    stype.borders.top = 0xff
    stype.borders.bottom = 0xff

    sheet.write_merge(0, 0, 0, 8, u"平台驱动代码评审", stype)
    sheet.write_merge(1, 1, 0, 1, u"SVN评审目标", stype)
    sheet.write_merge(1, 1, 2, 8, parameter.getSVNPath(), stype)



    sheet.write(2, 0, u"评审范围", stype)
    startTime = parameter.getStartTime()
    endTime = parameter.getEndTime()
    timeStr = u"%s/%s/%s-%s/%s/%s" %(startTime[0], startTime[1], startTime[2], endTime[0], endTime[1], endTime[2])
    sheet.write_merge(2, 2, 1, 2, timeStr, stype)
    sheet.write_merge(2, 2, 3, 4, u"评审启动日期", stype)
    sheet.write_merge(2, 2, 5, 8, "", stype)
    sheet.write(3, 0, u"序号", stype)
    sheet.write(3, 1, u"SVN", stype)
    sheet.write(3, 2, u"审查单元", stype)
    sheet.write(3, 3, u"责任人", stype)
    sheet.write(3, 4, u"评审方式", stype)
    sheet.write(3, 5, u"评审日期", stype)
    sheet.write(3, 6, u"评审结论", stype)
    sheet.write(3, 7, u"是否预警", stype)
    sheet.write(3, 8, u"说明与备注", stype)
    return sheet


def readSVNLog(parameter):
    if (parameter is None) or (parameter.getStatus() == False):
        print("invalid paramter, please check")
        return

    xlsx = parameter.getFileName()
    command  = parameter.getCommand()

    print(command)
    rootLogList = os.popen(command)

    res = rootLogList.read()
    rootLogList.close()

    i = 0
    log = baseLog()
    message = ""
    result = []
    #style = xlwt.XFStyle()
    for line in res.splitlines():
        if line is None or (len(line) < 1):
            continue
        if '--------' in line:
            continue
        i = i + 1
        if line.count("|") >= 3:
            if len(message) > 0:
                #message = message[:-1]
                log.setMessage(message)
                message = ""
                if len(log.getMessage()) > 0:
                    result.append(log)
            log = baseLog()
            tmpList = line.split("|")
            log.setRevision(tmpList[0])
            log.setAuthor(tmpList[1])
            log.setTime(tmpList[2])
        else:
            #print("len(line) = %u, line = %s" %(len(line), line))
            message = message + line
    log.setMessage(message)
    result.append(log)

    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet("log", cell_overwrite_ok=True)
    sheet = setHeaderStyle(sheet, parameter)
    j = 4
    for i in result:
        tmpStr = str(i)
        sheet.write(j, 0, str(j - 4))
        sheet.write(j, 1, tmpStr)
        j = j + 1
    book.save(xlsx)
    print("saveFile = %s" % xlsx)

if __name__ == '__main__':
    parameter = CConfig()
    readSVNLog(parameter)
