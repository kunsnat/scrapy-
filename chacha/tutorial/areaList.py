#coding:utf-8

from openpyxl import Workbook
import xlrd
import xlwt
import os
import time


class Area(object):

    def __init__(self):
        self.initCodeName()

    def getAreaCode(self, index):

        if len(self.codeList) == 0:
            self.initCodeName()

        tmp = index % len(self.codeList)

        currentCode = self.codeList[tmp]

        return currentCode


    def initCodeName(self):
        codeName = {}
        codeList = []

        self.areacode = 'D:/pydemo/qichacha/chacha/download/areacode/'

        chinaExcel = self.areacode + 'china.xlsx'
        if os.path.exists(chinaExcel):
            china = xlrd.open_workbook(chinaExcel)
            chinaSheet = china.sheet_by_index(0)
            provinceNames = chinaSheet.col_values(1)
            provinceCodes = chinaSheet.col_values(4)

            for provinceIndex, provinceName in enumerate(provinceNames):
                if provinceIndex == 0: # 标题title跳过
                    continue
                provinceCode = provinceCodes[provinceIndex]
                codeName[provinceCode] = provinceName

                provinceExcel = self.areacode + provinceCode  + '.xlsx'

                if os.path.exists(provinceExcel):
                    province = xlrd.open_workbook(provinceExcel)
                    provinceSheet = province.sheet_by_index(0)
                    cityNames = provinceSheet.col_values(1)
                    cityCodes = provinceSheet.col_values(4)
                    for cityIndex, cityName in enumerate(cityNames):
                        if cityIndex == 0:
                            continue

                        cityCode = cityCodes[cityIndex]
                        codeName[cityCode] = cityName

                        cityExcel = self.areacode + cityCode + '.xlsx'
                        if os.path.exists(cityExcel):
                            city = xlrd.open_workbook(cityExcel)
                            citySheet = city.sheet_by_index(0) # sheet索引从0开始
                            distNames = citySheet.col_values(1)
                            distCodes = citySheet.col_values(4)
                            for distIndex, distName in enumerate(distNames):
                                if distIndex == 0:
                                    continue
                                distCode = distCodes[distIndex]
                                codeName[distCode] = distName

                                areaCode = {}
                                areaCode['provinceCode'] = provinceCode
                                areaCode['provinceName'] = provinceName
                                areaCode['cityName'] = cityName
                                areaCode['cityCode'] = cityCode
                                areaCode['distName'] = distName
                                areaCode['distCode'] = distCode
                                codeList.append(areaCode)

        self.codeList = codeList
        self.codeName = codeName