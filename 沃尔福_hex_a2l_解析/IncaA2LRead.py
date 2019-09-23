#-*- coding:utf-8 -*-
import re
from pandas import DataFrame as pd_DataFrame
import pandas as pd
import time

class IncaA2L:
    def __init__(self, filename):
        self.filename = filename
        self.CharacDaF = pd.DataFrame()
        self.RecDaF = pd.DataFrame()
        self.ConvMothDaF = pd.DataFrame()
        try:
            self.filename = self.filename.decode('utf-8')
        except:
            pass
        with open(self.filename, 'r') as self.read_file:
            self.content = self.read_file.read()
        self.content = re.sub(r"(/\*.*\*/)", "", self.content)             #删除注释

    #---------------------------------------------------#
    # description:通过datatype来确定data的长度
    # 输入：数据类型对应的字符
    # 返回值为长度：1,2,4
    #---------------------------------------------------#
    def FindLength(self, DataType):
        if DataType == 'UBYTE':
            return 1
        elif DataType == 'SBYTE':
            return 1
        elif DataType == 'UWORD':
            return 2
        elif DataType == 'SWORD':
            return 2
        elif DataType == 'ULONG':
            return 4
        elif DataType == 'SLONG':
            return 4
        else:
            return 4
    #----------------------------------------#
    # 返回值为DataFrame：DataTypeName DataType
    #
    #----------------------------------------#
    def RECORD_LAYOUT_Export(self):

        #找出所有的描述数据类型块的区域
        DataType = re.findall( r'/begin *?RECORD_LAYOUT([\S\s]*?)/end *?RECORD_LAYOUT', self.content, re.M|re.I)


        #创建一个空白dataframe用于存放所有数据类型信息
        DFDataTypeInfo = pd_DataFrame()
        #创建一个空白list用于存放name
        ListDataTypeName = []
        #创建一个空白list用于存放具体信息
        ListDataTypeInfo = []

        #处理具体一个的数据类型块
        for i in DataType:
            #去除其中某个描述数据类型块的前后空白字符
            i = i.strip()

            #创建一个临时的list用于提取数据类型name,以空白字符分隔
            TempList = re.split('[\s]*', i)
            ListDataTypeName.append(TempList[0])

            #对该块进行按行分隔,
            DataTypeInfoLine = re.split('\n', i)

            #创建一个空白字典用于存放具体数据类型信息
            DicDataTypeInfo = {}

            #对该块信息描述进行提取
            for j in DataTypeInfoLine:
                #去除信息描述行的前后空白字符
                j = j.strip()
                #如果j不是数据类型name那一行
                if j != TempList[0]:

                    #对信息描述行按空白符进行分隔
                    DataTypeInfo = j.split()

                    '''
                    /begin RECORD_LAYOUT ValA_Ws16
                      FNC_VALUES 1.0 SWORD COLUMN_DIR DIRECT 
                      ALIGNMENT_WORD 2.0
                      ALIGNMENT_LONG 4.0
                      ALIGNMENT_FLOAT32_IEEE 4.0
                      ALIGNMENT_FLOAT64_IEEE 4.0
                    /end RECORD_LAYOUT
                    '''

                    #数据类型对应的描述对象行，分隔后都大于3个成员，过滤掉不需要的信息，如上
                    if len(DataTypeInfo) >= 3:
                        #DataTypeInfo[0]:数据类型对应的描述对象，DataTypeInfo[2]：数据类型
                        DicDataTypeInfo[DataTypeInfo[0]] = DataTypeInfo[2]
            #将数据类型信息字典添加到list
            ListDataTypeInfo.append(DicDataTypeInfo)

        #将数据类型name跟数据类型信息2个list添加到dataframe
        DFDataTypeInfo['Name'] = ListDataTypeName
        DFDataTypeInfo['Info'] = ListDataTypeInfo

        return DFDataTypeInfo

    #---------------------------------------------------#
    # 返回值为DataFrame：ConvFormuleName  a b c d e f
    #
    #---------------------------------------------------#
    def COMPU_METHOD_Export(self):

        #找出所有的描述转换公式的区域
        ConvMoth = re.findall( r'/begin *?COMPU_METHOD([\S\s]*?)/end *?COMPU_METHOD', self.content, re.M|re.I)

        #创建一个空白dataframe用于存放所有数据类型信息
        DFConvInfo = pd_DataFrame()
        #创建一个空白list用于存放name
        ListConvName = []
        #创建一个空白list用于存放unit
        ListUnit = []
        #创建一个空白list用于存放A
        ListA = []
        #创建一个空白list用于存放B
        ListB = []
        #创建一个空白list用于存放C
        ListC = []
        #创建一个空白list用于存放D
        ListD = []
        #创建一个空白list用于存放E
        ListE = []
        #创建一个空白list用于存放F
        ListF = []

        #处理具体一个的转换公式块
        for i in ConvMoth:
            #去除其中某个描述转换公式块的前后空白字符
            i = i.strip()

            #将所有“  ”都替换成“Description”，去除''中空格的作用
           # i = re.sub(r"\"\s+\"", "Description", i)

            #将描述转换公式块以空白符分隔
            TempList = re.split('[\s]*', i)
            #name
            ListConvName.append(TempList[0])

            #unit
            # try:
            # print TempList[4]
            TempList[4] = TempList[4].decode('gbk')
            # print u'%s'%(TempList[4])
            # except:
            #     pass
            ListUnit.append(TempList[4])

            #暂时只做RAT_FUNC类型的公式
            if TempList[2] == 'RAT_FUNC':
                #重新将描述转换公式块以换行符分隔
                ConvInfoList = re.split('[\n]*', i)
                #对分隔后的行进行选择性提取
                for j in ConvInfoList:
                    #去除行前后的空格
                    j = j.strip()
                    #将行按空格进行分隔
                    ListLine = j.split()
                    #如果读到COEFFS开头的行，则提取数据
                    if ListLine[0] == 'COEFFS':
                        ListA.append(float(ListLine[1]))
                        ListB.append(float(ListLine[2]))
                        ListC.append(float(ListLine[3]))
                        ListD.append(float(ListLine[4]))
                        ListE.append(float(ListLine[5]))
                        ListF.append(float(ListLine[6]))
            else:
                ListA.append(0)
                ListB.append(1)
                ListC.append(0)
                ListD.append(0)
                ListE.append(0)
                ListF.append(1)
        ListConvName.append('NO_COMPU_METHOD')
        ListUnit.append('')
        ListA.append(0)
        ListB.append(1)
        ListC.append(0)
        ListD.append(0)
        ListE.append(0)
        ListF.append(1)
        #将数据类型name跟公式信息2个list添加到dataframe
        DFConvInfo['Name'] = ListConvName
        DFConvInfo['Unit'] = ListUnit
        DFConvInfo['A'] = ListA
        DFConvInfo['B'] = ListB
        DFConvInfo['C'] = ListC
        DFConvInfo['D'] = ListD
        DFConvInfo['E'] = ListE
        DFConvInfo['F'] = ListF

        return DFConvInfo

    #---------------------------------------------------#
    # 返回值为DataFrame：
    #
    #---------------------------------------------------#
    def AXIS_PTS_Export(self):

        #找出所有的描述轴信息的区域
        AxisPoints = re.findall( r'/begin *?AXIS_PTS([\S\s]*?)/end *?AXIS_PTS', self.content, re.M|re.I)

        Length = len(AxisPoints)
        #创建一个空白dataframe用于存放所有轴信息
        DFAxisInfo = pd_DataFrame()
        #创建一个空白list用于存放name
        ListAxisName = [0] * Length
        #创建一个空白list用于存放AxisAdd
        ListAxisAdd = [0] * Length
        #创建一个空白list用于存放AxisDataType
        ListAxisDataType = [0] * Length
        #创建一个空白list用于存放AxisConv
        ListAxisConv = [0] * Length
        #创建一个空白list用于存放AxisPointNum
        ListAxisPointNum = [0] * Length

        #处理具体一个的轴信息块
        for i in range(Length):
            #去除其中某个描述轴信息块的前后空白字符
            AxisPoints[i] = AxisPoints[i].strip()

            #将所有“....”都替换成“Description”，去除''中空格的作用
            AxisPoints[i] = re.sub(r"\".*?(?<!\\)\"", "Description", AxisPoints[i])

            #将描述轴信息块以空白符分隔
            TempList = re.split('[\s]*', AxisPoints[i])
            #name
            ListAxisName[i] = TempList[0]
            #AxisAdd
            ListAxisAdd[i] = int(TempList[2], 16)
            #AxisDataType
            ListAxisDataType[i] = TempList[4]
            #AxisConv
            ListAxisConv[i] = TempList[6]
            #AxisPointNum
            ListAxisPointNum[i] = TempList[7]

        #将数据类型name跟公式信息2个list添加到dataframe
        DFAxisInfo['Name'] = ListAxisName
        DFAxisInfo['AxisAdd'] = ListAxisAdd
        DFAxisInfo['AxisDataType'] = ListAxisDataType
        DFAxisInfo['AxisConv'] = ListAxisConv
        DFAxisInfo['AxisPointNum'] = ListAxisPointNum


        return DFAxisInfo

    #---------------------------------------------------#
    # 返回值为DataFrame：
    #
    #---------------------------------------------------#
    def CHARACTERISTIC_Export(self):
        #找出所有的描述标定量的区域
        Character = re.findall( r'/begin *?CHARACTERISTIC([\S\s]*?)/end *?CHARACTERISTIC', self.content, re.M|re.I)

        CharacterLen = len(Character)
        self.CharLength = len(Character)
        #创建一个空白dataframe用于存放所有标定量信息
        DFCharacter = pd_DataFrame()
        #创建一个空白list用于存放Charname
        ListCharName = [0] * CharacterLen
        #创建一个空白list用于存放CharType
        ListCharType = [0] * CharacterLen
        #创建一个空白list用于存放CharAdd
        ListCharAdd = [0] * CharacterLen
        #创建一个空白list用于存放CharDataType
        ListChaDataType = [0] * CharacterLen
        #创建一个空白list用于存放CharConv
        ListCharConv = [0] * CharacterLen
        #创建一个空白list用于存放CharNum
        ListCharPNum = [1] * CharacterLen
        #创建一个空白list用于存放CharNum
        ListCharMax = [0] * CharacterLen
        #创建一个空白list用于存放CharNum
        ListCharMin = [0] * CharacterLen

        #创建一个空白list用于存放ListXaxisType X轴曲线类型
        ListXaxisType = [0] * CharacterLen
        #创建一个空白list用于存放ListXaxisPNumDataType  曲线类型STD_AXIS时，X轴点数的数据类型
        ListXaxisPNumDataType = [0] * CharacterLen
        #创建一个空白list用于存放ListXaxisOffset
        ListXaxisOffset = [0] * CharacterLen
        #创建一个空白list用于存放ListXaxisShift
        ListXaxisShift = [0] * CharacterLen
        #创建一个空白list用于存放ListXaxisPNum
        ListXaxisPNum = [1] * CharacterLen
        #创建一个空白list用于存放ListXaxisPRef
        ListXaxisPRef = [0] * CharacterLen
        #创建一个空白list用于存放ListXaxisConv
        ListXaxisConv = [0] * CharacterLen
        #创建一个空白list用于存放CharNum
        ListXaxisMax = [0] * CharacterLen
        #创建一个空白list用于存放CharNum
        ListXaxisMin = [0] * CharacterLen

        #创建一个空白list用于存放ListYaxisType Y轴曲线类型
        ListYaxisType = [0] * CharacterLen
        #创建一个空白list用于存放ListYaxisPNumDataType  曲线类型STD_AXIS时，Y轴点数的数据类型
        ListYaxisPNumDataType = [0] * CharacterLen
        #创建一个空白list用于存放ListYaxisOffset
        ListYaxisOffset = [0] * CharacterLen
        #创建一个空白list用于存放ListYaxisShift
        ListYaxisShift = [0] * CharacterLen
        #创建一个空白list用于存放ListYaxisPNum
        ListYaxisPNum = [1] * CharacterLen
        #创建一个空白list用于存放ListYaxisPRef
        ListYaxisPRef = [0] * CharacterLen
        #创建一个空白list用于存放LisYaxisConv
        ListYaxisConv = [0] * CharacterLen
        #创建一个空白list用于存放CharNum
        ListYaxisMax = [0] * CharacterLen
        #创建一个空白list用于存放CharNum
        ListYaxisMin = [0] * CharacterLen


        #处理具体一个的标定量块Name Long-Identifier Type Address Deposit MaxDiff
                               #Conversion Lower-Limit Upper-Limit
        for i in range(CharacterLen):
            #去除其中某个标定量块的前后空白字符
            CharChunk = Character[i].strip()

            #将所有“....”都替换成“Description”，去除''中空格的作用
            CharChunk = re.sub(r"\".*?(?<!\\)\"", "Description", CharChunk)

            #将标定量块以空白符分隔
            TempList = re.split('[\s]*', CharChunk)
            #name
            ListCharName[i] = TempList[0]
            #ListCharType
            ListCharType[i] = TempList[2]
            #添加排序字母，方便excel排序
            if (ListCharType[i] == 'VALUE') :
                ListCharType[i] = 'a_VALUE'
            if (ListCharType[i] == 'VAL_BLK') :
                ListCharType[i] = 'b_VAL_BLK'
            if (ListCharType[i] == 'ASCII') :
                ListCharType[i] = 'c_ASCII'
            if (ListCharType[i] == 'CURVE') :
                ListCharType[i] = 'd_CURVE'
            if (ListCharType[i] == 'MAP') :
                ListCharType[i] = 'e_MAP'

            #ListCharAdd
            ListCharAdd[i] = int(TempList[3], 16)
            #ListChaDataType
            ListChaDataType[i] = TempList[4]
            #ListCharConv
            ListCharConv[i] = TempList[6]
            #ListCharMax
            ListCharMax[i] = TempList[8]
            #ListCharMin
            ListCharMin[i] = TempList[7]

            #数组类型的数据暂时看到有2中表示数组个数的方式，MATRIX_DIM跟NUMBER
            if (TempList[2] == 'b_VAL_BLK') :
                #将标定量块以行分隔
                TempList = re.split('[\n]*', CharChunk)
                for j in TempList:
                    #去除其中行前后空白字符
                    j = j.strip()
                    #将行以空白符分隔
                    TempLineList = re.split('[\s]*', j)
                    if TempLineList[0] == 'MATRIX_DIM':
                        PointNumber = int(TempLineList[1]) * int(TempLineList[2]) * int(TempLineList[3])
                        ListCharPNum[i] = PointNumber
                    if TempLineList[0] == 'NUMBER':
                        ListCharPNum[i] = int(TempLineList[1])
            elif (TempList[2] == 'c_ASCII') :
                TempList = re.split('[\n]*', CharChunk)
                for j in TempList:
                    # 去除其中行前后空白字符
                    j = j.strip()
                    # 将行以空白符分隔
                    TempLineList = re.split('[\s]*', j)
                    if TempLineList[0] == 'NUMBER':
                        ListCharPNum[i] = int(TempLineList[1])
            #曲线类型
            elif (ListCharType[i] == 'd_CURVE') or (ListCharType[i] == 'e_MAP'):
                #从CharChunk中提取AXIS_DESCR块
                AxisDescrChunk = re.findall( r'/begin *?AXIS_DESCR([\S\s]*?)/end *?AXIS_DESCR', CharChunk, re.M|re.I)
                #Attribute InputQuantity Conversion MaxAxisPoints LowerLimit UpperLimit
                #去除其中行前后空白字符
                AxisDescrChunk[0] = AxisDescrChunk[0].strip()
                #将X轴描述块以空白符分隔
                TempList = re.split('[\s]*', AxisDescrChunk[0])
                ListXaxisType[i] = TempList[0]
                ListXaxisConv[i] = TempList[2]
                #ListXaxisMax
                ListXaxisMax[i] = TempList[5]
                #ListXaxisMin
                ListXaxisMin[i] = TempList[4]

                #如果X轴类型为标准轴
                if TempList[0] == 'STD_AXIS':
                    ListXaxisPNumDataType[i] = ListChaDataType[i]
                    #暂时以最大轴点数来确定轴点数，而不是从内存里去读取点数
                    ListXaxisPNum[i] = int(TempList[3])
                #如果X轴类型为等间距轴
                if TempList[0] == 'FIX_AXIS':
                    #将X轴描述块从新以换行符分隔
                    TempList = re.split('[\n]*', AxisDescrChunk[0])
                    for j in TempList:
                        j = j.strip()
                        #将行以空白符分隔
                        TempLineList = re.split('[\s]*', j)
                        if TempLineList[0] == 'FIX_AXIS_PAR':
                            ListXaxisOffset[i] = int(TempLineList[1])
                            ListXaxisShift[i] = int(TempLineList[2])
                            ListXaxisPNum[i] = int(TempLineList[3])
                if TempList[0] == 'COM_AXIS':
                    #将X轴描述块从新以换行符分隔
                    TempList = re.split('[\n]*', AxisDescrChunk[0])
                    for j in TempList:
                        j = j.strip()
                        #将行以空白符分隔
                        TempLineList = re.split('[\s]*', j)
                        if TempLineList[0] == 'AXIS_PTS_REF':
                            ListXaxisPRef[i] = TempLineList[1]
                #ListCharPNum[i] = ListXaxisPNum[i]

                if ListCharType[i] == 'e_MAP':
                    #去除其中行前后空白字符
                    AxisDescrChunk[1] = AxisDescrChunk[1].strip()
                    #将X轴描述块以空白符分隔
                    TempList = re.split('[\s]*', AxisDescrChunk[1])
                    ListYaxisType[i] = TempList[0]
                    ListYaxisConv[i] = TempList[2]
                    #ListYaxisMax
                    ListYaxisMax[i] = TempList[5]
                    #ListYaxisMin
                    ListYaxisMin[i] = TempList[4]
                    #如果X轴类型为标准轴
                    if TempList[0] == 'STD_AXIS':
                        ListYaxisPNumDataType[i] = ListChaDataType[i]
                        #暂时以最大轴点数来确定轴点数，而不是从内存里去读取点数
                        ListYaxisPNum[i] = int(TempList[3])
                    #如果X轴类型为等间距轴
                    if TempList[0] == 'FIX_AXIS':
                        #将X轴描述块从新以换行符分隔
                        TempList = re.split('[\n]*', AxisDescrChunk[1])
                        for j in TempList:
                            j = j.strip()
                            #将行以空白符分隔
                            TempLineList = re.split('[\s]*', j)
                            if TempLineList[0] == 'FIX_AXIS_PAR':
                                ListYaxisOffset[i] = int(TempLineList[1])
                                ListYaxisShift[i] = int(TempLineList[2])
                                ListYaxisPNum[i] = int(TempLineList[3])
                    if TempList[0] == 'COM_AXIS':
                        #将X轴描述块从新以换行符分隔
                        TempList = re.split('[\n]*', AxisDescrChunk[1])
                        for j in TempList:
                            j = j.strip()
                            #将行以空白符分隔
                            TempLineList = re.split('[\s]*', j)
                            if TempLineList[0] == 'AXIS_PTS_REF':
                                ListYaxisPRef[i] = TempLineList[1]
                    #ListCharPNum[i] = ListXaxisPNum[i] * ListYaxisPNum[i]

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
        #return DFCharacter[DFCharacter['CharName'] =='ACComp_trqDyn_MAP']

    #---------------------------------------------------#
    # 返回值为DataFrame：
    #
    #---------------------------------------------------#
    def ReadA2L(self):
        #获取转换公式与数据类型信息
        DFConvInfo = self.COMPU_METHOD_Export()
        DFDataTypeInfo = self.RECORD_LAYOUT_Export()
        DFCharacter = self.CHARACTERISTIC_Export()
        DFAxisInfo = self.AXIS_PTS_Export()
        #print DFAxisInfo

        ListCharName = list(DFCharacter['CharName'])
        ListCharType = list(DFCharacter['CharType'])
        ListCharAdd = list(DFCharacter['CharAdd'])
        ListChaDataType = list(DFCharacter['ChaDataType'])
        ListCharPNum = list(DFCharacter['CharPNum'])
        ListCharMin = DFCharacter['CharMin']
        ListCharMax = DFCharacter['CharMax']
        ListCharUnit = [''] * self.CharLength
        ListCharA = [0] * self.CharLength
        ListCharB = [1] * self.CharLength
        ListCharC = [0] * self.CharLength
        ListCharD = [0] * self.CharLength
        ListCharE = [0] * self.CharLength
        ListCharF = [1] * self.CharLength

        ListXaxisName = ['Xaxis'] * self.CharLength
        ListXaxisType = list(DFCharacter['XaxisType'])
        ListXaxisBegin = list(DFCharacter['XaxisOffset'])
        ListXaxisShift = list(DFCharacter['XaxisShift'])
        ListXaxisAdd = [0] * self.CharLength
        ListXaxisDataType = [0] * self.CharLength
        ListXaxisPNum = list(DFCharacter['XaxisPNum'])
        ListXaxisMin = DFCharacter['XaxisMin']
        ListXaxisMax = DFCharacter['XaxisMax']
        ListXaxisUnit = [''] * self.CharLength
        ListXaxisA = [0] * self.CharLength
        ListXaxisB = [1] * self.CharLength
        ListXaxisC = [0] * self.CharLength
        ListXaxisD = [0] * self.CharLength
        ListXaxisE = [0] * self.CharLength
        ListXaxisF = [1] * self.CharLength

        ListYaxisName = ['Yaxis'] * self.CharLength
        ListYaxisType = list(DFCharacter['YaxisType'])
        ListYaxisBegin = list(DFCharacter['YaxisOffset'])
        ListYaxisShift = list(DFCharacter['YaxisShift'])
        ListYaxisAdd = [0] * self.CharLength
        ListYaxisDataType = [0] * self.CharLength
        ListYaxisPNum = list(DFCharacter['YaxisPNum'])
        ListYaxisMin = DFCharacter['YaxisMin']
        ListYaxisMax = DFCharacter['YaxisMax']
        ListYaxisUnit = [''] * self.CharLength
        ListYaxisA = [0] * self.CharLength
        ListYaxisB = [1] * self.CharLength
        ListYaxisC = [0] * self.CharLength
        ListYaxisD = [0] * self.CharLength
        ListYaxisE = [0] * self.CharLength
        ListYaxisF = [1] * self.CharLength


        for i in range(self.CharLength):

            #ListCharAdd,只有MAP或CRUVE时，且相应的轴类型为STD_AXIS时，CharAdd才会改变
            #ListCharPNum，只有当只有MAP或CRUVE时，需要计算，其他的类型之前已经计算好
            #ListXaxisDataType,ListYaxisDataType:相应的轴类型为COM_AXIS时datatype需要去AXIS_PTS寻找
            #ListXaxisAdd,ListYaxisAdd:轴类型为COM_AXIS时XaxisAdd需要去AXIS_PTS寻找，STD_AXIS时需要计算，FIX_AXIS时内存不存放Xaxis数据
            #ListXaxisPNum,ListYaxisPNum:只有轴类型为COM_AXIS时需要去AXIS_PTS中寻找，其他类型已经在初始化时已经写好值
            #ListXaxisA-F,ListYaxisA-F:需要去DFConvInfo寻找

            if (DFCharacter['CharType'][i] == 'e_MAP') or (DFCharacter['CharType'][i] == 'd_CURVE'):
                if DFCharacter['XaxisType'][i] == 'STD_AXIS':
                    #找出XaxisPNumDataType对应的数据长度，即XaxisPNum的字节数
                    DFSelectTemp = DFDataTypeInfo[DFDataTypeInfo['Name'] == DFCharacter['XaxisPNumDataType'][i]]

                    #按照ASAP2标准X轴数据类型必须是AXIS_PTS_X，但是我看到有的A2L文件2个轴只定义一个类型，所以用try，下同
                    try:
                        LengthXaxisPNum = self.FindLength(list(DFSelectTemp['Info'])[0]['NO_AXIS_PTS_X'])
                    except:
                        try:
                            LengthXaxisPNum = self.FindLength(list(DFSelectTemp['Info'])[0]['NO_AXIS_PTS_Y'])
                        except:
                            LengthXaxisPNum = self.FindLength(list(DFSelectTemp['Info'])[0]['FNC_VALUES'])

                    DFSelectTemp = DFDataTypeInfo[DFDataTypeInfo['Name'] == DFCharacter['ChaDataType'][i]]
                    #按照ASAP2标准X轴数据类型必须是AXIS_PTS_X，但是我看到有的A2L文件2个轴只定义一个类型，所以用try，下同
                    try:
                        ListXaxisDataType[i] = list(DFSelectTemp['Info'])[0]['AXIS_PTS_X']               #ListXaxisDataType
                    except:
                        try:
                            ListXaxisDataType[i] = list(DFSelectTemp['Info'])[0]['AXIS_PTS_Y']               #ListXaxisDataType
                        except:
                            ListXaxisDataType[i] = list(DFSelectTemp['Info'])[0]['FNC_VALUES']               #ListXaxisDataType

                    LengthXaxisP = int(self.FindLength(ListXaxisDataType[i])) * int(DFCharacter['XaxisPNum'][i])


                    ListCharAdd[i] = ListCharAdd[i] + LengthXaxisPNum + LengthXaxisP                    #ListCharAdd
                    ListXaxisAdd[i] = ListCharAdd[i] - LengthXaxisP                                  #ListXaxisAdd

                if DFCharacter['XaxisType'][i] == 'FIX_AXIS':
                    DFSelectTemp = DFDataTypeInfo[DFDataTypeInfo['Name'] == DFCharacter['ChaDataType'][i]]
                    try:
                        ListXaxisDataType[i] = list(DFSelectTemp['Info'])[0]['AXIS_PTS_X']               #ListXaxisDataType
                    except:
                        try:
                            ListXaxisDataType[i] = list(DFSelectTemp['Info'])[0]['AXIS_PTS_Y']               #ListXaxisDataType
                        except:
                            ListXaxisDataType[i] = list(DFSelectTemp['Info'])[0]['FNC_VALUES']               #ListXaxisDataType


                if DFCharacter['XaxisType'][i] == 'COM_AXIS':
                    ListXaxisName[i] = DFCharacter['XaxisPRef'][i]
                    DFSelectTemp = DFAxisInfo[DFAxisInfo['Name'] == DFCharacter['XaxisPRef'][i]]
                    try:
                        ListXaxisAdd[i] = list(DFSelectTemp['AxisAdd'])[0]                               #ListXaxisAdd
                        ListXaxisPNum[i] = list(DFSelectTemp['AxisPointNum'])[0]                         #ListXaxisPNum
                    except:
                        print DFCharacter['XaxisPRef'][i]
                    #此时只是将数据类型名字取出
                    XaxisDataTypeName = list(DFSelectTemp['AxisDataType'])[0]
                    DFSelectTemp1 = DFDataTypeInfo[DFDataTypeInfo['Name'] == XaxisDataTypeName]


                    try:
                        ListXaxisDataType[i] = list(DFSelectTemp1['Info'])[0]['AXIS_PTS_X']               #ListXaxisDataType
                    except:
                        try:
                            ListXaxisDataType[i] = list(DFSelectTemp1['Info'])[0]['AXIS_PTS_Y']               #ListXaxisDataType
                        except:
                            ListXaxisDataType[i] = list(DFSelectTemp1['Info'])[0]['FNC_VALUES']               #ListXaxisDataType                if DFCharacter['YaxisType'][i] == 'STD_AXIS':

                if DFCharacter['YaxisType'][i] == 'STD_AXIS':
                    #找出YaxisPNumDataType对应的数据长度，即YaxisPNum的字节数
                    DFSelectTemp = DFDataTypeInfo[DFDataTypeInfo['Name'] == DFCharacter['YaxisPNumDataType'][i]]
                    try:
                        LengthYaxisPNum = self.FindLength(list(DFSelectTemp['Info'])[0]['NO_AXIS_PTS_Y'])
                    except:
                        try:
                            LengthYaxisPNum = self.FindLength(list(DFSelectTemp['Info'])[0]['NO_AXIS_PTS_X'])
                        except:
                            LengthYaxisPNum = self.FindLength(list(DFSelectTemp['Info'])[0]['FNC_VALUES'])
                    #找出YaxisDataType对应的数据长度，YaxisData的字节数为YaxisDataType * YaxisPNum
                    DFSelectTemp = DFDataTypeInfo[DFDataTypeInfo['Name'] == DFCharacter['ChaDataType'][i]]
                    try:
                        ListYaxisDataType[i] = list(DFSelectTemp['Info'])[0]['AXIS_PTS_Y']               #ListYaxisDataType
                    except:
                        try:
                            ListYaxisDataType[i] = list(DFSelectTemp['Info'])[0]['AXIS_PTS_X']               #ListYaxisDataType
                        except:
                            ListYaxisDataType[i] = list(DFSelectTemp['Info'])[0]['FNC_VALUES']               #ListYaxisDataType
                    LengthYaxisP = int(self.FindLength(ListYaxisDataType[i])) * int(DFCharacter['YaxisPNum'][i])

                    ListCharAdd[i] = ListCharAdd[i] + LengthYaxisPNum + LengthYaxisP                 #ListCharAdd
                    ListYaxisAdd[i] = ListCharAdd[i] - LengthYaxisP                                  #ListYaxisAdd
                    if DFCharacter['XaxisType'][i] == 'STD_AXIS':
                        ListXaxisAdd[i] = ListCharAdd[i] - LengthXaxisP - LengthYaxisP              #ListXaxisAdd

                if DFCharacter['YaxisType'][i] == 'FIX_AXIS':
                    DFSelectTemp = DFDataTypeInfo[DFDataTypeInfo['Name'] == DFCharacter['ChaDataType'][i]]
                    try:
                        ListYaxisDataType[i] = list(DFSelectTemp['Info'])[0]['AXIS_PTS_Y']               #ListYaxisDataType
                    except:
                        try:
                            ListYaxisDataType[i] = list(DFSelectTemp['Info'])[0]['AXIS_PTS_X']               #ListYaxisDataType
                        except:
                            ListYaxisDataType[i] = list(DFSelectTemp['Info'])[0]['FNC_VALUES']               #ListYaxisDataType
                if DFCharacter['YaxisType'][i] == 'COM_AXIS':
                    ListYaxisName[i] = DFCharacter['YaxisPRef'][i]
                    DFSelectTemp = DFAxisInfo[DFAxisInfo['Name'] == DFCharacter['YaxisPRef'][i]]
                    try:
                        ListYaxisAdd[i] = list(DFSelectTemp['AxisAdd'])[0]                               #ListYaxisAdd
                        ListYaxisPNum[i] = list(DFSelectTemp['AxisPointNum'])[0]                         #ListYaxisPNum
                    except:
                        print DFCharacter['YaxisPRef'][i]
                        #print DFAxisInfo['Name']
                    #此时只是将数据类型名字取出
                    YaxisDataTypeName = list(DFSelectTemp['AxisDataType'])[0]
                    DFSelectTemp1 = DFDataTypeInfo[DFDataTypeInfo['Name'] == YaxisDataTypeName]
                    try:
                        ListYaxisDataType[i] = list(DFSelectTemp1['Info'])[0]['AXIS_PTS_Y']               #ListYaxisDataType
                    except:
                        try:
                            ListYaxisDataType[i] = list(DFSelectTemp1['Info'])[0]['AXIS_PTS_X']               #ListYaxisDataType
                        except:
                            ListYaxisDataType[i] = list(DFSelectTemp1['Info'])[0]['FNC_VALUES']               #ListYaxisDataType

                DFSelectTemp = DFConvInfo[DFConvInfo['Name'] == DFCharacter['XaxisConv'][i]]
                ListXaxisUnit[i] = list(DFSelectTemp['Unit'])[0]
                ListXaxisA[i] = list(DFSelectTemp['A'])[0]                                      #ListXaxisScale
                ListXaxisB[i] = list(DFSelectTemp['B'])[0]                                    #ListXaxisOffset
                ListXaxisC[i] = list(DFSelectTemp['C'])[0]
                ListXaxisD[i] = list(DFSelectTemp['D'])[0]
                ListXaxisE[i] = list(DFSelectTemp['E'])[0]
                ListXaxisF[i] = list(DFSelectTemp['F'])[0]

                ListCharPNum[i] = ListXaxisPNum[i]
                if DFCharacter['CharType'][i] == 'e_MAP':
                    ListCharPNum[i] = int(ListXaxisPNum[i]) * int(ListYaxisPNum[i])
                    DFSelectTemp = DFConvInfo[DFConvInfo['Name'] == DFCharacter['YaxisConv'][i]]
                    ListYaxisUnit[i] = list(DFSelectTemp['Unit'])[0]
                    ListYaxisA[i] = list(DFSelectTemp['A'])[0]                                      #ListYaxisScale
                    ListYaxisB[i] = list(DFSelectTemp['B'])[0]                                      #ListYaxisOffset
                    ListYaxisC[i] = list(DFSelectTemp['C'])[0]
                    ListYaxisD[i] = list(DFSelectTemp['D'])[0]
                    ListYaxisE[i] = list(DFSelectTemp['E'])[0]
                    ListYaxisF[i] = list(DFSelectTemp['F'])[0]

            #ListCharScale,ListCharOffset
            DFSelectTemp = DFConvInfo[DFConvInfo['Name'] == DFCharacter['CharConv'][i]]
            ListCharUnit[i] = list(DFSelectTemp['Unit'])[0]
            ListCharA[i] = list(DFSelectTemp['A'])[0]
            ListCharB[i] = list(DFSelectTemp['B'])[0]
            ListCharC[i] = list(DFSelectTemp['C'])[0]
            ListCharD[i] = list(DFSelectTemp['D'])[0]
            ListCharE[i] = list(DFSelectTemp['E'])[0]
            ListCharF[i] = list(DFSelectTemp['F'])[0]

            DFSelectTemp = DFDataTypeInfo[DFDataTypeInfo['Name'] == ListChaDataType[i]]
            ListChaDataType[i] = list(DFSelectTemp['Info'])[0]['FNC_VALUES']

        #创建一个空白dataframe用于存放所有标定量信息
        DaFChar = pd_DataFrame()

        DaFChar['CharName'] = ListCharName
        DaFChar['CharType'] = ListCharType
        DaFChar['CharAdd']= ListCharAdd
        DaFChar['CharDataType'] = ListChaDataType
        DaFChar['CharPNum'] = ListCharPNum
        DaFChar['CharMin'] = ListCharMin
        DaFChar['CharMax'] = ListCharMax
        DaFChar['CharUnit'] = ListCharUnit
        DaFChar['CharA'] = ListCharA
        DaFChar['CharB'] = ListCharB
        DaFChar['CharC'] = ListCharC
        DaFChar['CharD'] = ListCharD
        DaFChar['CharE'] = ListCharE
        DaFChar['CharF'] = ListCharF

        DaFChar['XaxisName'] = ListXaxisName
        DaFChar['XaxisType'] = ListXaxisType
        DaFChar['XaxisDataType'] = ListXaxisDataType
        DaFChar['XaxisAdd'] = ListXaxisAdd
        DaFChar['XaxisPNum'] = ListXaxisPNum
        DaFChar['XaxisBegin'] = ListXaxisBegin
        DaFChar['XaxisShift'] = ListXaxisShift
        DaFChar['XaxisMin'] = ListXaxisMin
        DaFChar['XaxisMax'] = ListXaxisMax
        DaFChar['XaxisUnit'] = ListXaxisUnit
        DaFChar['XaxisA'] = ListXaxisA
        DaFChar['XaxisB'] = ListXaxisB
        DaFChar['XaxisC'] = ListXaxisC
        DaFChar['XaxisD'] = ListXaxisD
        DaFChar['XaxisE'] = ListXaxisE
        DaFChar['XaxisF'] = ListXaxisF

        DaFChar['YaxisName'] = ListYaxisName
        DaFChar['YaxisType'] = ListYaxisType
        DaFChar['YaxisDataType'] = ListYaxisDataType
        DaFChar['YaxisAdd'] = ListYaxisAdd
        DaFChar['YaxisPNum'] = ListYaxisPNum
        DaFChar['YaxisBegin'] = ListYaxisBegin
        DaFChar['YaxisShift'] = ListYaxisShift
        DaFChar['YaxisMin'] = ListYaxisMin
        DaFChar['YaxisMax'] = ListYaxisMax
        DaFChar['YaxisUnit'] = ListYaxisUnit
        DaFChar['YaxisA'] = ListYaxisA
        DaFChar['YaxisB'] = ListYaxisB
        DaFChar['YaxisC'] = ListYaxisC
        DaFChar['YaxisD'] = ListYaxisD
        DaFChar['YaxisE'] = ListYaxisE
        DaFChar['YaxisF'] = ListYaxisF

        #return  DaFChar[DaFChar['CharName'] ==  'ACComp_trqDyn_MAP']
        return   DaFChar

    # ---------------------------------------------------#
    # 返回值为DataFrame：
    # 读取轴信息
    # ---------------------------------------------------#
    def ReadA2LAxis(self):
        DFAxisInfo = self.AXIS_PTS_Export()
        DFDataTypeInfo = self.RECORD_LAYOUT_Export()
        DFConvInfo = self.COMPU_METHOD_Export()

        DaFChar = pd_DataFrame()
        len_Axis = len(DFAxisInfo['Name'])
        list_AxisName = DFAxisInfo['Name']
        list_AxisAdd = DFAxisInfo['AxisAdd']
        list_AxisDataType = [0] * len_Axis
        list_AxisPointNum = DFAxisInfo['AxisPointNum']
        ListAxisUnit = [''] * len_Axis
        ListAxisA = [0] * len_Axis
        ListAxisB = [1] * len_Axis
        ListAxisC = [0] * len_Axis
        ListAxisD = [0] * len_Axis
        ListAxisE = [0] * len_Axis
        ListAxisF = [1] * len_Axis
        for i in range(len(DFAxisInfo['Name'])):
            DFSelectTemp = DFDataTypeInfo[DFDataTypeInfo['Name'] == DFAxisInfo['AxisDataType'][i]]
            try:
                list_AxisDataType[i] = list(DFSelectTemp['Info'])[0]['AXIS_PTS_Y']  # ListYaxisDataType
            except:
                try:
                    list_AxisDataType[i] = list(DFSelectTemp['Info'])[0]['AXIS_PTS_X']  # ListYaxisDataType
                except:
                    list_AxisDataType[i] = list(DFSelectTemp['Info'])[0]['FNC_VALUES']  # ListYaxisDataType
            DFSelectTemp = DFConvInfo[DFConvInfo['Name'] == DFAxisInfo['AxisConv'][i]]
            ListAxisUnit[i] = list(DFSelectTemp['Unit'])[0]
            ListAxisA[i] = list(DFSelectTemp['A'])[0]
            ListAxisB[i] = list(DFSelectTemp['B'])[0]
            ListAxisC[i] = list(DFSelectTemp['C'])[0]
            ListAxisD[i] = list(DFSelectTemp['D'])[0]
            ListAxisE[i] = list(DFSelectTemp['E'])[0]
            ListAxisF[i] = list(DFSelectTemp['F'])[0]

        DaFChar['AxisName'] = list_AxisName
        DaFChar['AxisAdd'] = list_AxisAdd
        DaFChar['AxisDataType'] = list_AxisDataType
        DaFChar['AxisPointNum'] = list_AxisPointNum
        DaFChar['AxisUnit'] = ListAxisUnit
        DaFChar['AxisA'] = ListAxisA
        DaFChar['AxisB'] = ListAxisB
        DaFChar['AxisC'] = ListAxisC
        DaFChar['AxisD'] = ListAxisD
        DaFChar['AxisE'] = ListAxisE
        DaFChar['AxisF'] = ListAxisF
        return DaFChar

if __name__ == '__main__':
    #add = r'C:\Users\Desktop\1\demo0 - 1\一拖4缸机非道路标定数据（bosch）\一拖4缸机非道路标定数据（bosch）\不带EGR\P1819_V100.a2l'
    add = r'C:\Users\Desktop\1\demo0 - 1\lvk\lvkhb.a2l'
    add = unicode(add , "utf8")
    a = IncaA2L(add)
    #print a.AXIS_PTS_Export()
    #print a.CHARACTERISTIC_Export()
    #print a.RECORD_LAYOUT_Export()
    #print a.COMPU_METHOD_Export()
    #print a.ReadA2L()

