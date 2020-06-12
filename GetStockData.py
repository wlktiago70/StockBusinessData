import io
import sys
import csv
import requests
import threading
import time
from lxml import html
import stock

# Following lines are not needed when running with Python 3
# reload(sys)
# sys.setdefaultencoding('UTF8')

FIELD_LEN = 20
VALUE_LEN = 8

fieldNames = [
    'Papel',              #0
    'Cotação',            #1
    'P/L',                #2
    'P/VP',               #3
    'PSR',                #4
    'Div.Yield',          #5
    'P/Ativo',            #6
    'P/Cap.Giro',         #7
    'P/EBIT',             #8
    'P/Ativ Circ.Liq',    #9
    'EV/EBIT',            #10
    'EV/EBITDA',          #11
    'Mrg Ebit',           #12
    'Mrg. Líq.',          #13
    'Liq. Corr.',         #14
    'ROIC',               #15
    'ROE',                #16
    'Liq.2meses',         #17
    'Patrim. Líq',        #18
    'Dív.Brut/ Patrim.',  #19
    'Cresc. Rec.5a']      #20

def processValue(result):
    string = str(result)
    string = string.replace(".", "")
    string = string.replace(",", ".")
    string = string.replace("%", "")
    string = string.replace("R$", "")
    string = string.strip()
    try:
        return float(string)
    except:
        return 0.0

class StockBasicInfo:
    def __init__(self, tableHeader, tableBody):
        self.tableHeader = tableHeader.xpath("//th//text()")
        self.tableBody = []
        for i in range(len(tableBody)):
            self.tableBody.append(tableBody[i].xpath("//tr["+str(i)+"]//td//text()"))
        self.stockDict = {}

class Business:
    def __init__(self, code, url):
        self.code = code
        self.url = url + str(self.code)
        self.page = requests.get(self.url)
        self.tree = html.fromstring(self.page.content)
        tblHead = self.tree.xpath(stock.TABLE_HEADER)
        tblBody = self.tree.xpath(stock.TABLE_BODY)
        self.tableHeader = tblHead[0].xpath("//th//text()")
        self.tableBody = [tblBody[i].xpath("//tr["+str(i+1)+"]//td//text()") for i in range(len(tblBody))]
        self.businessStockData = self.buildBusinessStockData()
        self.average = self.buildAverage()
        self.maximum = self.buildMaximum()

    def buildBusinessStockData(self):
        businessStockData = {}
        for row in self.tableBody:
            dict = {self.tableHeader[i+1]:processValue(row[i+1]) for i in range(len(self.tableHeader)-1)}
            businessStockData[row[0]] = dict
        return businessStockData

    def buildAverage(self):
        result = {self.tableHeader[i+1]:0.0 for i in range(len(self.tableHeader)-1)}
        for stock in self.businessStockData:
            for key in result.keys():
                result[key] += self.businessStockData[stock][key]
        for key in result.keys():
            result[key] /= len(self.businessStockData)
        return result

    def buildMaximum(self):
        result = {self.tableHeader[i+1]:-999999999.9 for i in range(len(self.tableHeader)-1)}
        for stock in self.businessStockData:
            for key in result.keys():
                if result[key] < self.businessStockData[stock][key]:
                    result[key] = self.businessStockData[stock][key]
        return result

    def getAverage(self):
        return self.average

    def getMaximum(self):
        return self.maximum

    def printAverage(self):
        Business.printData(self.average)

    def printMaximum(self):
        Business.printData(self.maximum)

    def printStocks(self):
        result = ""
        for s in self.businessStockData.keys():
            result += (" | " + s)
        print(result + " |")

    @staticmethod
    def printData(businessStockData):
        print(fieldNames[1].ljust(FIELD_LEN,'.') + ": R$ {:.2f}".format(businessStockData[fieldNames[1]]))
        print(fieldNames[2].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[2]]))
        print(fieldNames[3].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[3]]))
        print(fieldNames[4].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[4]]))
        print(fieldNames[5].ljust(FIELD_LEN,'.') + ": {:.2f}%".format(businessStockData[fieldNames[5]]))
        print(fieldNames[6].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[6]]))
        print(fieldNames[7].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[7]]))
        print(fieldNames[8].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[8]]))
        print(fieldNames[9].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[9]]))
        print(fieldNames[10].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[10]]))
        print(fieldNames[11].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[11]]))
        print(fieldNames[12].ljust(FIELD_LEN,'.') + ": {:.2f}%".format(businessStockData[fieldNames[12]]))
        print(fieldNames[13].ljust(FIELD_LEN,'.') + ": {:.2f}%".format(businessStockData[fieldNames[13]]))
        print(fieldNames[14].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[14]]))
        print(fieldNames[15].ljust(FIELD_LEN,'.') + ": {:.2f}%".format(businessStockData[fieldNames[15]]))
        print(fieldNames[16].ljust(FIELD_LEN,'.') + ": {:.2f}%".format(businessStockData[fieldNames[16]]))
        print(fieldNames[17].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[17]]))
        print(fieldNames[18].ljust(FIELD_LEN,'.') + ": R$ {:.2f}".format(businessStockData[fieldNames[18]]))
        print(fieldNames[19].ljust(FIELD_LEN,'.') + ": {:.2f}".format(businessStockData[fieldNames[19]]))
        print(fieldNames[20].ljust(FIELD_LEN,'.') + ": {:.2f}%".format(businessStockData[fieldNames[20]]))

class BusinessSector(Business):
    def __init__(self, code):
        super().__init__(code, stock.SECTOR_LINK)

class BusinessSegment(Business):
    def __init__(self, code):
        super().__init__(code, stock.SEGMENT_LINK)

class BusinessSectorThread (threading.Thread):
   def __init__(self, code):
        threading.Thread.__init__(self)
        self.code = code
        self.businessSector = None

   def run(self):
        self.businessSector = BusinessSector(self.code)

class BusinessSegmentThread (threading.Thread):
   def __init__(self, code):
        threading.Thread.__init__(self)
        self.code = code
        self.businessSegment = None

   def run(self):
        self.businessSegment = BusinessSegment(self.code)

class Stock:
    def __init__(self, name):
        self.name = name.upper()
        self.url = stock.STOCK_LINK + self.name
        self.page = requests.get(self.url)
        self.tree = html.fromstring(self.page.content)
        bSectorCode = (self.tree.xpath(stock.STOCK_BUSINESS_SECTOR + '@href')[0]).split('=').pop()
        bSegmntCode = (self.tree.xpath(stock.STOCK_BUSINESS_SEGMENT + '@href')[0]).split('=').pop()
        bSectorThread = BusinessSectorThread(bSectorCode)
        bSegmntThread = BusinessSegmentThread(bSegmntCode)
        bSectorThread.start()
        bSegmntThread.start()
        bSectorThread.join()
        bSegmntThread.join()
        self.sector = (self.tree.xpath(stock.STOCK_BUSINESS_SECTOR + 'text()')[0])
        self.segment = (self.tree.xpath(stock.STOCK_BUSINESS_SEGMENT + 'text()')[0])
        self.businessSector = bSectorThread.businessSector
        self.businessSegment = bSegmntThread.businessSegment
        self.stockData = self.businessSegment.businessStockData[self.name]

    def compareTo(self, business):
        for ref in business:
            try:
                val = "{:.2f}%".format((self.stockData[ref] - business[ref])*100.0/abs(business[ref]))
            except:
                val = "N/A"
            print(ref.ljust(FIELD_LEN,'.') + ": " + val.rjust(VALUE_LEN,' '))

    def getBusinessSector(self):
        return self.businessSector

    def getBusinessSegment(self):
        return self.businessSegment

def showStockInfo(stockCode):
    try:
        s = Stock(stockCode)
        print(">>> Dados de " + s.name + ": ")
        print("Setor...............: " + s.sector)
        print("Segmento............: " + s.segment)
        Business.printData(s.stockData)
        print()
        # print(">>> Máximo do setor " + s.sector + ": ")
        # s.getBusinessSector().printMaximum()
        # print()
        # print(">>> Média do setor " + s.sector + ": ")
        # s.getBusinessSector().printAverage()
        # print()
        # print(">>> Máximo do segmento " + s.segment + ": ")
        # s.getBusinessSegment().printMaximum()
        # print()
        # print(">>> Média do segmento " + s.segment + ": ")
        # s.getBusinessSegment().printAverage()
        # print()
        print(">>> Setor " + s.sector + ": ")
        s.getBusinessSector().printStocks()
        print()
        print(">>> " + s.name + " em comparação ao máximo do setor " + s.sector + ": ")
        s.compareTo(s.getBusinessSector().getMaximum())
        print()
        print(">>> " + s.name + " em comparação à média do setor " + s.sector + ": ")
        s.compareTo(s.getBusinessSector().getAverage())
        print()
        print(">>> Segmento " + s.segment + ": ")
        s.getBusinessSegment().printStocks()
        print()
        print(">>> " + s.name + " em comparação ao máximo do segmento " + s.segment + ": ")
        s.compareTo(s.getBusinessSegment().getMaximum())
        print()
        print(">>> " + s.name + " em comparação à média do segmento " + s.segment + ": ")
        s.compareTo(s.getBusinessSegment().getAverage())
        print()
    except:
        print("Masoquê??!!")

while True:
    stockCode = input(">>> Código do papel: ")
    showStockInfo(stockCode)
    print()