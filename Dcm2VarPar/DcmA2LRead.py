# -*- coding:utf-8 -*-
import re
import pandas as pd
import time
import sys
import chardet


class IncaA2L:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename,"rb") as self.read_file:
            self.content = self.read_file.read()
            # self.content=str(self.content,encoding="gbk")
            # print(chardet.detect(self.content))
            print(self.content[:1024])
            print(sys.getsizeof(self.read_file))

        with open("test.a2l","w") as f:
            f.write(str(self.content))

        self.content = re.sub(r"(/\*.*\*/)", "", self.content)  # 删除注释
        sys.exit()
        # 获取转换公式与数据类型信息
        self.DFConvTable = self.COMPU_VTAB_Export()
        self.DFConvInfo = self.COMPU_METHOD_Export()
        self.DFCharacter = self.CHARACTERISTIC_Export()

    # ---------------------------------------------------#
    # 返回值为DataFrame：ConvFormuleName  a b c d e f
    #
    # ---------------------------------------------------#
    def COMPU_VTAB_Export(self):

        # 找出所有的描述转换公式的区域
        ConvMoth = re.findall(r'/begin *?COMPU_VTAB([\S\s]*?)/end *?COMPU_VTAB', self.content, re.M | re.I)

        # 创建一个空白dataframe用于存放所有数据类型信息
        DFConvInfo = pd.DataFrame()
        # 创建一个空白list用于存放name
        ListTableName = []
        ListEnum = []

        # 处理具体一个的转换公式块
        for i in ConvMoth:
            DicEnum = {}
            # 去除其中某个描述转换公式块的前后空白字符
            i = i.strip()

            # 将描述转换公式块以行分隔
            TempList = re.split('\n', i)
            # name
            ListTableName.append(TempList[0])
            EnumNum = int(TempList[3])
            for j in range(EnumNum):
                TempLine = re.split('[\s]*', TempList[4 + j].strip())

                DicName = TempLine[1].strip('"')
                DicEnum[DicName] = TempLine[0]
            ListEnum.append(DicEnum)
            # print DicEnum
        # 将数据类型name跟公式信息2个list添加到dataframe
        DFConvInfo['TableName'] = ListTableName
        DFConvInfo['Enum'] = ListEnum

        return DFConvInfo

    def COMPU_METHOD_Export(self):

        # 创建一个空白dataframe用于存放所有数据类型信息
        DFCompuInfo = pd.DataFrame()
        # 创建一个空白list用于存放name
        ListConvName = []
        ListConvTable = []
        # 找出所有的描述转换公式的区域
        ConvMoth = re.findall(r'/begin *?COMPU_METHOD([\S\s]*?)/end *?COMPU_METHOD', self.content, re.M | re.I)
        for i in ConvMoth:
            # 去除其中某个描述转换公式块的前后空白字符
            i = i.strip()
            # 将描述转换公式块以行分隔
            TempList = re.split('\n', i)
            if TempList[2].strip() == 'TAB_VERB':
                ListConvName.append(TempList[0])
                TempLine = re.split('[\s]*', TempList[5].strip())
                ListConvTable.append(TempLine[1])
        DFCompuInfo['ConvName'] = ListConvName
        DFCompuInfo['ConvTable'] = ListConvTable
        return DFCompuInfo

    # ---------------------------------------------------#
    # 返回值为DataFrame：
    #
    # ---------------------------------------------------#
    def CHARACTERISTIC_Export(self):
        # 找出所有的描述标定量的区域
        Character = re.findall(r'/begin *?CHARACTERISTIC([\S\s]*?)/end *?CHARACTERISTIC', self.content, re.M | re.I)

        CharacterLen = len(  )
        self.CharLength = len(Character)
        # 创建一个空白dataframe用于存放所有标定量信息
        DFCharacter = pd.DataFrame()
        # 创建一个空白list用于存放Charname
        ListCharName = [0] * CharacterLen
        # 创建一个空白list用于存放CharType
        ListCharType = [0] * CharacterLen
        # 创建一个空白list用于存放CharAdd
        ListCharAdd = [0] * CharacterLen
        # 创建一个空白list用于存放CharDataType
        ListChaDataType = [0] * CharacterLen
        # 创建一个空白list用于存放CharConv
        ListCharConv = [0] * CharacterLen
        # 创建一个空白list用于存放CharNum
        ListCharPNum = [1] * CharacterLen
        # 创建一个空白list用于存放CharNum
        ListCharMax = [0] * CharacterLen
        # 创建一个空白list用于存放CharNum
        ListCharMin = [0] * CharacterLen

        # 创建一个空白list用于存放ListXaxisType X轴曲线类型
        ListXaxisType = [0] * CharacterLen
        # 创建一个空白list用于存放ListXaxisPNumDataType  曲线类型STD_AXIS时，X轴点数的数据类型
        ListXaxisPNumDataType = [0] * CharacterLen
        # 创建一个空白list用于存放ListXaxisOffset
        ListXaxisOffset = [0] * CharacterLen
        # 创建一个空白list用于存放ListXaxisShift
        ListXaxisShift = [0] * CharacterLen
        # 创建一个空白list用于存放ListXaxisPNum
        ListXaxisPNum = [1] * CharacterLen
        # 创建一个空白list用于存放ListXaxisPRef
        ListXaxisPRef = [0] * CharacterLen
        # 创建一个空白list用于存放ListXaxisConv
        ListXaxisConv = [0] * CharacterLen
        # 创建一个空白list用于存放CharNum
        ListXaxisMax = [0] * CharacterLen
        # 创建一个空白list用于存放CharNum
        ListXaxisMin = [0] * CharacterLen

        # 创建一个空白list用于存放ListYaxisType Y轴曲线类型
        ListYaxisType = [0] * CharacterLen
        # 创建一个空白list用于存放ListYaxisPNumDataType  曲线类型STD_AXIS时，Y轴点数的数据类型
        ListYaxisPNumDataType = [0] * CharacterLen
        # 创建一个空白list用于存放ListYaxisOffset
        ListYaxisOffset = [0] * CharacterLen
        # 创建一个空白list用于存放ListYaxisShift
        ListYaxisShift = [0] * CharacterLen
        # 创建一个空白list用于存放ListYaxisPNum
        ListYaxisPNum = [1] * CharacterLen
        # 创建一个空白list用于存放ListYaxisPRef
        ListYaxisPRef = [0] * CharacterLen
        # 创建一个空白list用于存放LisYaxisConv
        ListYaxisConv = [0] * CharacterLen
        # 创建一个空白list用于存放CharNum
        ListYaxisMax = [0] * CharacterLen
        # 创建一个空白list用于存放CharNum
        ListYaxisMin = [0] * CharacterLen

        # 处理具体一个的标定量块Name Long-Identifier Type Address Deposit MaxDiff
        # Conversion Lower-Limit Upper-Limit
        for i in range(CharacterLen):
            # 去除其中某个标定量块的前后空白字符
            CharChunk = Character[i].strip()

            # 将所有“....”都替换成“Description”，去除''中空格的作用
            CharChunk = re.sub(r"\".*?(?<!\\)\"", "Description", CharChunk)

            # 将标定量块以空白符分隔
            TempList = re.split('[\s]*', CharChunk)
            # name
            ListCharName[i] = TempList[0]
            # ListCharType
            ListCharType[i] = TempList[2]
            # ListCharAdd
            ListCharAdd[i] = int(TempList[3], 16)
            # ListChaDataType
            ListChaDataType[i] = TempList[4]
            # ListCharConv
            ListCharConv[i] = TempList[6]
            # ListCharMax
            ListCharMax[i] = TempList[8]
            # ListCharMin
            ListCharMin[i] = TempList[7]

            # 数组类型的数据暂时看到有2中表示数组个数的方式，MATRIX_DIM跟NUMBER
            if TempList[2] == 'VAL_BLK':
                # 将标定量块以行分隔
                TempList = re.split('[\n]*', CharChunk)
                for j in TempList:
                    # 去除其中行前后空白字符
                    j = j.strip()
                    # 将行以空白符分隔
                    TempLineList = re.split('[\s]*', j)
                    if TempLineList[0] == 'MATRIX_DIM':
                        PointNumber = int(TempLineList[1]) * int(TempLineList[2]) * int(TempLineList[3])
                        ListCharPNum[i] = PointNumber
                    if TempLineList[0] == 'NUMBER':
                        ListCharPNum[i] = int(TempLineList[1])
            # 曲线类型
            if (ListCharType[i] == 'CURVE') or (ListCharType[i] == 'MAP'):
                # 从CharChunk中提取AXIS_DESCR块
                AxisDescrChunk = re.findall(r'/begin *?AXIS_DESCR([\S\s]*?)/end *?AXIS_DESCR', CharChunk, re.M | re.I)
                # Attribute InputQuantity Conversion MaxAxisPoints LowerLimit UpperLimit
                # 去除其中行前后空白字符
                AxisDescrChunk[0] = AxisDescrChunk[0].strip()
                # 将X轴描述块以空白符分隔
                TempList = re.split('[\s]*', AxisDescrChunk[0])
                ListXaxisType[i] = TempList[0]
                ListXaxisConv[i] = TempList[2]
                # ListXaxisMax
                ListXaxisMax[i] = TempList[5]
                # ListXaxisMin
                ListXaxisMin[i] = TempList[4]

                # 如果X轴类型为标准轴
                if TempList[0] == 'STD_AXIS':
                    ListXaxisPNumDataType[i] = ListChaDataType[i]
                    # 暂时以最大轴点数来确定轴点数，而不是从内存里去读取点数
                    ListXaxisPNum[i] = int(TempList[3])
                # 如果X轴类型为等间距轴
                if TempList[0] == 'FIX_AXIS':
                    # 将X轴描述块从新以换行符分隔
                    TempList = re.split('[\n]*', AxisDescrChunk[0])
                    for j in TempList:
                        j = j.strip()
                        # 将行以空白符分隔
                        TempLineList = re.split('[\s]*', j)
                        if TempLineList[0] == 'FIX_AXIS_PAR':
                            ListXaxisOffset[i] = int(TempLineList[1])
                            ListXaxisShift[i] = int(TempLineList[2])
                            ListXaxisPNum[i] = int(TempLineList[3])
                if TempList[0] == 'COM_AXIS':
                    # 将X轴描述块从新以换行符分隔
                    TempList = re.split('[\n]*', AxisDescrChunk[0])
                    for j in TempList:
                        j = j.strip()
                        # 将行以空白符分隔
                        TempLineList = re.split('[\s]*', j)
                        if TempLineList[0] == 'AXIS_PTS_REF':
                            ListXaxisPRef[i] = TempLineList[1]
                # ListCharPNum[i] = ListXaxisPNum[i]

                if ListCharType[i] == 'MAP':
                    # 去除其中行前后空白字符
                    AxisDescrChunk[1] = AxisDescrChunk[1].strip()
                    # 将X轴描述块以空白符分隔
                    TempList = re.split('[\s]*', AxisDescrChunk[1])
                    ListYaxisType[i] = TempList[0]
                    ListYaxisConv[i] = TempList[2]
                    # ListYaxisMax
                    ListYaxisMax[i] = TempList[5]
                    # ListYaxisMin
                    ListYaxisMin[i] = TempList[4]
                    # 如果X轴类型为标准轴
                    if TempList[0] == 'STD_AXIS':
                        ListYaxisPNumDataType[i] = ListChaDataType[i]
                        # 暂时以最大轴点数来确定轴点数，而不是从内存里去读取点数
                        ListYaxisPNum[i] = int(TempList[3])
                    # 如果X轴类型为等间距轴
                    if TempList[0] == 'FIX_AXIS':
                        # 将X轴描述块从新以换行符分隔
                        TempList = re.split('[\n]*', AxisDescrChunk[1])
                        for j in TempList:
                            j = j.strip()
                            # 将行以空白符分隔
                            TempLineList = re.split('[\s]*', j)
                            if TempLineList[0] == 'FIX_AXIS_PAR':
                                ListYaxisOffset[i] = int(TempLineList[1])
                                ListYaxisShift[i] = int(TempLineList[2])
                                ListYaxisPNum[i] = int(TempLineList[3])
                    if TempList[0] == 'COM_AXIS':
                        # 将X轴描述块从新以换行符分隔
                        TempList = re.split('[\n]*', AxisDescrChunk[1])
                        for j in TempList:
                            j = j.strip()
                            # 将行以空白符分隔
                            TempLineList = re.split('[\s]*', j)
                            if TempLineList[0] == 'AXIS_PTS_REF':
                                ListYaxisPRef[i] = TempLineList[1]
                    # ListCharPNum[i] = ListXaxisPNum[i] * ListYaxisPNum[i]

        DFCharacter['CharName'] = ListCharName
        DFCharacter['CharType'] = ListCharType
        DFCharacter['CharAdd'] = ListCharAdd
        DFCharacter['ChaDataType'] = ListChaDataType
        DFCharacter['CharConv'] = ListCharConv
        DFCharacter['CharPNum'] = ListCharPNum
        DFCharacter['CharMin'] = ListCharMin
        DFCharacter['CharMax'] = ListCharMax

        DFCharacter['XaxisType'] = ListXaxisType
        DFCharacter['XaxisPNumDataType'] = ListXaxisPNumDataType
        DFCharacter['XaxisOffset'] = ListXaxisOffset
        DFCharacter['XaxisShift'] = ListXaxisShift
        DFCharacter['XaxisPNum'] = ListXaxisPNum
        DFCharacter['XaxisPRef'] = ListXaxisPRef
        DFCharacter['XaxisConv'] = ListXaxisConv
        DFCharacter['XaxisMin'] = ListXaxisMin
        DFCharacter['XaxisMax'] = ListXaxisMax

        DFCharacter['YaxisType'] = ListYaxisType
        DFCharacter['YaxisPNumDataType'] = ListYaxisPNumDataType
        DFCharacter['YaxisOffset'] = ListYaxisOffset
        DFCharacter['YaxisShift'] = ListYaxisShift
        DFCharacter['YaxisPNum'] = ListYaxisPNum
        DFCharacter['YaxisPRef'] = ListYaxisPRef
        DFCharacter['YaxisConv'] = ListYaxisConv
        DFCharacter['YaxisMin'] = ListYaxisMin
        DFCharacter['YaxisMax'] = ListYaxisMax
        return DFCharacter
        # return DFCharacter[DFCharacter['CharName'] =='ACComp_trqDyn_MAP']

    # ---------------------------------------------------#
    # 返回值为DataFrame：
    # WhichAxis: 0表示Char，1表示XAxis，2表示YAxis
    # ---------------------------------------------------#
    def ReadA2L(self, WhichAxis, EnumName, CharName):
        DfTemp = self.DFCharacter[self.DFCharacter['CharName'] == CharName]
        # print DfTemp
        if WhichAxis == 0:
            ListCharConv = list(DfTemp['CharConv'])[0]
            ConvTable = list(self.DFConvInfo[self.DFConvInfo['ConvName'] == ListCharConv]['ConvTable'])[0]
            Enum = list(self.DFConvTable[self.DFConvTable['TableName'] == ConvTable]['Enum'])[0]
            return Enum[EnumName]
        elif WhichAxis == 1:
            ListXaxisConv = list(DfTemp['XaxisConv'])[0]
            ConvTable = list(self.DFConvInfo[self.DFConvInfo['ConvName'] == ListXaxisConv]['ConvTable'])[0]
            Enum = list(self.DFConvTable[self.DFConvTable['TableName'] == ConvTable]['Enum'])[0]
            return Enum[EnumName]
        elif WhichAxis == 2:
            ListYaxisConv = list(DfTemp['YaxisConv'])[0]
            ConvTable = list(self.DFConvInfo[self.DFConvInfo['ConvName'] == ListYaxisConv]['ConvTable'])[0]
            Enum = list(self.DFConvTable[self.DFConvTable['TableName'] == ConvTable]['Enum'])[0]
            return Enum[EnumName]


if __name__ == '__main__':
    # add = r'C:\Users\Desktop\1\demo0 - 1\一拖4缸机非道路标定数据（bosch）\一拖4缸机非道路标定数据（bosch）\不带EGR\P1819_V100.a2l'
    add = r"D:\woocal_code\Dcm2VarPar\A2L\340.a2l"
    # add = Str(add , "utf8")
    a = IncaA2L(add)
    # print a.ReadA2L(0, 'Clutch', 'ASDdc_numDflSt_C')
    # print a.AXIS_PTS_Export()
    # print a.CHARACTERISTIC_Export()
    # print a.RECORD_LAYOUT_Export()
    print(a.COMPU_METHOD_Export())
    # print a.ReadA2L()
