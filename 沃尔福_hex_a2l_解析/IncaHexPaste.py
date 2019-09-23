#-*- coding:utf-8 -*-
import re
from pandas.core.frame import DataFrame as pandas_core_frame_DataFrame
import IncaA2LRead
import time
from numpy import array as np_array
from numpy import linspace as np_linspace

from scipy import interpolate

class IncaHexPaste:
    def __init__(self, filename , A2LFile, CharacterDF = 0):
        self.filename = filename
        self.A2LFile = A2LFile
        if type(CharacterDF) == int:
            #创建IncaA2L的类
            self.Character = IncaA2LRead.IncaA2L(self.A2LFile)
            print u'正在读取第2个A2L文件信息'
            #调用类中的Charac成员函数，得到包含A2L信息的Dataframe
            self.CharacterDF = self.Character.ReadA2L()
            print u'第2个A2L文件信息读取成功'
        if type(CharacterDF) == pandas_core_frame_DataFrame:
            self.CharacterDF = CharacterDF

        with open(self.filename) as self.read_file:
            self.content = self.read_file.read()

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
    # name：
    # parameter （Int： Int数据）
    # return：str
    #----------------------------------------#
    def ListToStr(self, List):
        Str = ''
        for i in List:
            Str = Str + i
        return Str


    #----------------------------------------#
    # name：Int型数据到16进制字符  10-->'A'
    # parameter （Int： Int数据） BitNum:16进制显示字符数目
    # return：str
    #----------------------------------------#
    def IntToStr(self, Int,BitNum):
        self.Int = Int
        tempStr = ''
        #去除前面的0x跟最后的L
        self.Int = hex(self.Int).lstrip('0x').rstrip('L')

        self.len = len(self.Int)
        while self.len < BitNum:
            self.Int = '0' + self.Int
            self.len += 1
        if self.len > BitNum:
            while BitNum:
                tempStr = tempStr + self.Int[self.len - BitNum]
                BitNum -= 1
            self.Int = tempStr
        return self.Int


    #----------------------------------------#
    # name：块分隔
    # parameter （Address： 输入32位地址）
    # return：str（整块的str） 0：未找到该区域
    #----------------------------------------#
    def ChunkSplit(self, Address):
        #算出高16位地址的字符
        AddHigh = self.IntToStr(Address >> 16, 4)
        #找出高地址所对应的数据块
        self.MatchChr1 = r'[\s\S]*?:(.{6}04%s[\s\S]*?:.{6}04)'%(AddHigh)
        self.MatchChr2 = r'[\s\S]*?:(.{6}04%s[\s\S]*?:.{6}05)'%(AddHigh)

        #写成用于匹配的匹配字符串
        #MatchChr = r'[\s\S]*?:\d{6}04%s[\s\S]*?:20(.{4})[\s\S]*?:02000004'%(self.AddHigh)

        #根据匹配字符串进行匹配来匹配出该高位地址对应的地位首地址
        Chunk = re.match(self.MatchChr1,self.content,re.M|re.I)
        if Chunk != None:
            return Chunk.group(1)
        else :
            Chunk = re.match(self.MatchChr2,self.content,re.M|re.I)
            if Chunk != None:
                return Chunk.group(1)
            else:
                return 0


    #----------------------------------------#
    # name：计算地址所在行的开始结束地址
    # parameter （Line）,(Add:低16位地址)
    # return：LineAddBegin, LineAddEnd,state,Line
    #         state:0(Add比行起始地址小),1(Add比行结束地址大),2(Add在行内)
    #----------------------------------------#
    def CalculateLineAdd(self, Line, Add):
        LengthLine = (int(Line[0], 16) << 4) + int(Line[1], 16)

        LineAddBegin = (int(Line[2], 16) << 12) + (int(Line[3], 16) << 8) +\
                       (int(Line[4], 16) << 4) + int(Line[5], 16)

        LineAddEnd = LineAddBegin + LengthLine - 1    #0x00 - 0x00为1个长度
        if Add < LineAddBegin:
            state = 0
        else:
            if Add > LineAddEnd:
                state = 1
            else:
                state = 2
        #
        # print state
        return [LineAddBegin, LineAddEnd, state, Line]


    #----------------------------------------#
    # name：根据地址进行行定位
    # parameter:定位到的行的起始地址，结束地址
    # return : Add[Addbegin,Addend]
    #----------------------------------------#
    def DataAddLocation(self, Address):

        #算出高16位地址的字符
        self.AddHigh = self.IntToStr(Address >> 16, 4)
        #print self.AddHigh

        #算出低16位地址的字符
        self.AddLow = self.IntToStr(Address & 0xffff, 4)
        #print self.AddLow

        #算出4-16位地址的字符
        self.AddLow1 = re.match(r'(.{3}).',self.AddLow,re.I).group(1)


        #找出高地址所对应的数据块
        LineAdd = 0
        self.AddHighChunk = self.ChunkSplit(Address)

        if self.AddHighChunk == 0:
            print u'hex文件中不含此地址区域数据1'
            return 0
        else:
            #搜索条件,先进行大概位置定位
            self.MatchChr1 = r'[\s\S]*?:(.{2}%s[\s\S]*?)\s:'%(self.AddLow1)
            Line = re.match(self.MatchChr1, self.AddHighChunk,re.M|re.I)


            #如果匹配成功
            if Line != None:
                LineAdd = self.CalculateLineAdd(Line.group(1), (Address & 0xffff))

            #否则4-8位地址-1继续匹配
            else:
                self.AddLow1 = self.IntToStr((int(self.AddLow1, 16) - 1), 3)
                self.MatchChr1 = r'[\s\S]*?:(.{2}%s[\s\S]*?)\s:'%(self.AddLow1)
                Line = re.match(self.MatchChr1, self.AddHighChunk,re.M|re.I)
                if Line != None:
                    LineAdd = self.CalculateLineAdd(Line.group(1), (Address & 0xffff))
                else:
                    print u'hex文件中不含%s地址区域数据2'%(hex(Address))
                    return 0

            #判断地址定位是否在定位的行中，不在就进行精确定位
            while  LineAdd[2] != 2:
                #如果标定量地址比行起始地址小
                if LineAdd[2] == 0:
                    #向上1行重新搜索
                    self.AddLow1 = self.IntToStr((int(self.AddLow1, 16) - 2), 3)
                    self.MatchChr1 = r'[\s\S]*?:(.{2}%s[\s\S]*?)\s:'%(self.AddLow1)
                    Line = re.match(self.MatchChr1, self.AddHighChunk,re.M|re.I)
                    LineAdd = self.CalculateLineAdd(Line.group(1), (Address & 0xffff))
                    #如果此时发现标定量地址比行结束地址大
                    if LineAdd[2] == 1:
                        print u'hex文件中不含%s地址区域数据3'%(hex(Address))
                        return 0


                #如果标定量地址比行结束地址大
                elif LineAdd[2] == 1:
                    #向下1行重新搜索
                    self.AddLow1 = self.IntToStr((int(self.AddLow1, 16) + 2), 3)
                    self.MatchChr1 = r'[\s\S]*?:(.{2}%s[\s\S]*?)\s:'%(self.AddLow1)
                    Line = re.match(self.MatchChr1, self.AddHighChunk,re.M|re.I)
                    LineAdd = self.CalculateLineAdd(Line.group(1), (Address & 0xffff))   ######why its disappeared
                    #如果此时发现标定量地址比行起始地址小
                    if LineAdd[2] == 0:
                        print u'hex文件中不含%s地址区域数据4'%(hex(Address))
                        return 0
            #地址补全
            LineAdd[0] = LineAdd[0] + (Address & 0xffff0000)
            LineAdd[1] = LineAdd[1] + (Address & 0xffff0000)
            #此时已经找到标定量地址起始地址在哪一行
            return LineAdd


    #----------------------------------------#
    # descropy:提取标定数据信息，并检查与Copy文件中的信息是否匹配
    # parameter: CharacName, ChaPhyValue:copy回来的结果
    # return：
    #----------------------------------------#
    def GetCheckChaInfo(self, CharacName, ChaPhyValue):
        SelectCharacterDF = self.CharacterDF[self.CharacterDF['CharName'] == CharacName]
        #通过name刷选出地址
        try:
            self.AddressBegin = int(list(SelectCharacterDF['CharAdd'])[0])
            self.XaxisAdd = int(list(SelectCharacterDF['XaxisAdd'])[0])
            self.YaxisAdd = int(list(SelectCharacterDF['YaxisAdd'])[0])
        except:
            print u'无法在A2L文件中找到变量:%s'%(CharacName)
            return 0
        #通过name刷选出类型
        self.CharateristicType = list(SelectCharacterDF['CharType'])[0]

        #通过name刷选出公式
        self.CharA = list(SelectCharacterDF['CharA'])[0]
        self.CharB = list(SelectCharacterDF['CharB'])[0]
        self.CharC = list(SelectCharacterDF['CharC'])[0]
        self.CharD = list(SelectCharacterDF['CharD'])[0]
        self.CharE = list(SelectCharacterDF['CharE'])[0]
        self.CharF = list(SelectCharacterDF['CharF'])[0]
        self.XaxisA = list(SelectCharacterDF['XaxisA'])[0]
        self.XaxisB = list(SelectCharacterDF['XaxisB'])[0]
        self.XaxisC = list(SelectCharacterDF['XaxisC'])[0]
        self.XaxisD = list(SelectCharacterDF['XaxisD'])[0]
        self.XaxisE = list(SelectCharacterDF['XaxisE'])[0]
        self.XaxisF = list(SelectCharacterDF['XaxisF'])[0]
        self.YaxisA = list(SelectCharacterDF['YaxisA'])[0]
        self.YaxisB = list(SelectCharacterDF['YaxisB'])[0]
        self.YaxisC = list(SelectCharacterDF['YaxisC'])[0]
        self.YaxisD = list(SelectCharacterDF['YaxisD'])[0]
        self.YaxisE = list(SelectCharacterDF['YaxisE'])[0]
        self.YaxisF = list(SelectCharacterDF['YaxisF'])[0]

        #计算具体标定量
        self.CharPNum = int(list(SelectCharacterDF['CharPNum'])[0])
        self.XaxisPNum = int(list(SelectCharacterDF['XaxisPNum'])[0])
        self.YaxisPNum = int(list(SelectCharacterDF['YaxisPNum'])[0])
        self.CharDataType = list(SelectCharacterDF['CharDataType'])[0]
        self.XaxisDataType = list(SelectCharacterDF['XaxisDataType'])[0]
        self.YaxisDataType = list(SelectCharacterDF['YaxisDataType'])[0]
        self.XaxisType = list(SelectCharacterDF['XaxisType'])[0]
        self.YaxisType = list(SelectCharacterDF['YaxisType'])[0]

        self.XaxisBegin = list(SelectCharacterDF['XaxisBegin'])[0]
        self.YaxisBegin = list(SelectCharacterDF['YaxisBegin'])[0]
        self.XaxisShift = list(SelectCharacterDF['XaxisShift'])[0]
        self.YaxisShift = list(SelectCharacterDF['YaxisShift'])[0]

        self.CharacLen = int(self.CharPNum) * self.FindLength(self.CharDataType)


        #判断copy paste双方的类型，成员数量是否一样
        if self.CharateristicType  == 'VALUE':
            if int(ChaPhyValue[0]) != 0:
                print u'%sPaste标定量类型为：VALUE,Copy标定量不是！'%(CharacName)
                return 0

        if self.CharateristicType  == 'VAL_BLK':
            if int(ChaPhyValue[0]) != 1:
                print u'%sPaste标定量类型为：VAL_BLK,Copy标定量不是！'%(CharacName)
                return 0

            if self.CharPNum != len(ChaPhyValue[1]):
                print u'%sPaste标定量(VAL_BLK)长度为：%d,Copy标定量长度为：%d'%(CharacName, self.CharaterMatrix,
                                                                  len(ChaPhyValue[1]))
                return 0


        if self.CharateristicType  == 'CURVE':
            self.XaxisDataLen = int(self.XaxisPNum) * self.FindLength(self.XaxisDataType)
            if int(ChaPhyValue[0]) != 2:
                print u'%sPaste标定量类型为：CURVE,Copy标定量不是！'%(CharacName)
                return 0

            if int(self.XaxisPNum) != len(ChaPhyValue[1]):
                ChaPhyValue = self.InterpFun1D(ChaPhyValue)



        if self.CharateristicType  == 'MAP':
            self.XaxisDataLen = int(self.XaxisPNum) * self.FindLength(self.XaxisDataType)
            self.YaxisDataLen = int(self.YaxisPNum) * self.FindLength(self.YaxisDataType)
            if int(ChaPhyValue[0]) != 3:
                print u'%sPaste标定量为：MAP,Copy标定量不是！'%(CharacName)
                return 0

            #如果维度不一样，进行插值处理
            if (int(self.YaxisPNum) != len(ChaPhyValue[3])) or (int(self.XaxisPNum) != len(ChaPhyValue[2])):
                try:
                    ChaPhyValue = self.InterpFun2D(ChaPhyValue)
                except:
                    print u'原Y轴维度：%d，原X轴维度：%d' %(int(self.YaxisPNum), int(self.XaxisPNum))
                    print u'现Y轴维度：%d，现X轴维度：%d' %(len(ChaPhyValue[3]), len(ChaPhyValue[2]))
        return ChaPhyValue
    #----------------------------------------#
    # descropy:CURVE插值
    # parameter:ChaPhyValue:copy回来的结果
    # return：返回插值完的数据
    #----------------------------------------#
    def InterpFun1D(self, ChaPhyValue):
        if self.XaxisType == 'FIX_AXIS':
            TempList = []
            for i in range(ChaPhyValue[2][2]):
                XaxisValue = ChaPhyValue[2][0] + (i) * pow(2, ChaPhyValue[2][1])
                TempList.append(XaxisValue)
            ChaPhyValue[2] = TempList

        ValueArray = np_array(ChaPhyValue[1])
        XaxisArray = np_array(ChaPhyValue[2])

        CurveFun = interpolate.interp1d(XaxisArray, ValueArray, kind='cubic')

        if self.XaxisType == 'FIX_AXIS':
            TempList = []
            for i in range(self.XaxisPNum):
                XaxisValue = self.XaxisBegin + (i) * pow(2, self.XaxisShift)
                TempList.append(XaxisValue)
            x = np_array(TempList)
        else:
            x = np_linspace(min(ChaPhyValue[2]), max(ChaPhyValue[2]), self.XaxisPNum)

        ValueArrayNew = CurveFun(x)
        ChaPhyValue[1] = list(ValueArrayNew)
        ChaPhyValue[2] = list(x)

        return ChaPhyValue
    #----------------------------------------#
    # descropy:MAP插值
    # parameter:ChaPhyValue:copy回来的结果
    # return：返回插值完的数据
    #----------------------------------------#
    def InterpFun2D(self, ChaPhyValue):

        if self.XaxisType == 'FIX_AXIS':
            TempList = []
            for i in range(ChaPhyValue[2][2]):
                XaxisValue = ChaPhyValue[2][0] + (i) * pow(2, ChaPhyValue[2][1])
                TempList.append(XaxisValue)
            ChaPhyValue[2] = TempList

        if self.YaxisType == 'FIX_AXIS':
            TempList = []
            for i in range(ChaPhyValue[3][2]):
                YaxisValue = ChaPhyValue[3][0] + (i) * pow(2, ChaPhyValue[3][1])
                TempList.append(YaxisValue)
            ChaPhyValue[3] = TempList

        XaxLenOld = len(ChaPhyValue[2])
        YaxLenOld = len(ChaPhyValue[3])
        #XaxListOld = [ChaPhyValue[2]] * YaxLenOld
        #YaxListOld = [ChaPhyValue[3]] * XaxLenOld

        ValueList = []
        for x in range(XaxLenOld):
            ValueLineList = []
            for y in range(YaxLenOld):
                ValueLineList += [ChaPhyValue[1][y + x * YaxLenOld]]
            ValueLineList = np_array(ValueLineList)
            ValueList += [ValueLineList]
        ValueArray = np_array(ValueList)
        XaxisArray = np_array([np_array(ChaPhyValue[2])] * YaxLenOld)
        YaxisArray = np_array([np_array(ChaPhyValue[3])] * XaxLenOld)

        MapFun = interpolate.interp2d(XaxisArray, YaxisArray, ValueArray, kind='cubic')

        if self.YaxisType == 'FIX_AXIS':
            TempList = []
            for i in range(self.YaxisPNum):
                YaxisValue = self.YaxisBegin + (i) * pow(2, self.YaxisShift)
                TempList.append(YaxisValue)
            y = np_array(TempList)
        else:
            y = np_linspace(min(ChaPhyValue[3]), max(ChaPhyValue[3]), self.YaxisPNum)

        if self.XaxisType == 'FIX_AXIS':
            TempList = []
            for i in range(self.XaxisPNum):
                XaxisValue = self.XaxisBegin + (i) * pow(2, self.XaxisShift)
                TempList.append(XaxisValue)
            x = np_array(TempList)
        else:
            x = np_linspace(min(ChaPhyValue[2]), max(ChaPhyValue[2]), self.XaxisPNum)

        #print x

        #print y
        ValueArrayNew = MapFun(x , y)

        ValueListNew = []
        for Ynum in range(self.YaxisPNum):
            for Xnum in range(self.XaxisPNum):
                ValueListNew += [ValueArrayNew[Ynum][Xnum]]
        #print ValueListNew
        ChaPhyValue[1] = ValueListNew
        ChaPhyValue[2] = list(x)
        ChaPhyValue[3] = list(y)
        return ChaPhyValue

    #----------------------------------------#
    # descropy:物理值转成内存值
    # parameter:ChaPhyValue:copy回来的结果
    # return：转成hex格式的值
    #----------------------------------------#
    def PhysicalToMemValue(self, DataType, A, B, C, D, E, F, ChaPhyValue, DataInMemory):
        j = 0
        for i in ChaPhyValue:
            i = float(i)
            if DataType == 'UBYTE':
                #temp = int((A * i ** 2 + B * i +C)/(D * i ** 2 + E * i + F))
                temp = int(round((A * i * i + B * i + C) / (D * i * i + E * i + F)))
                DataInMemory[j] = ((temp & 0xf0) >> 4)
                j += 1
                DataInMemory[j] = (temp & 0xf)
                j += 1

            if DataType == 'SBYTE':
                temp = int((round(A * i * i + B * i + C) / (D * i * i + E * i + F)))

                if temp < 0:
                    temp = temp + pow(2, 8)

                DataInMemory[j] = ((temp & 0xf0) >> 4)
                j += 1
                DataInMemory[j] = (temp & 0xf)
                j += 1

            if DataType == 'UWORD':
                temp = int((round(A * i * i + B * i + C) / (D * i * i + E * i + F)))
                #0X   F F F F
                #     2 3 0 1
                DataInMemory[j + 0] = ((temp & 0xf000) >> 12)
                DataInMemory[j + 1] = ((temp & 0xf00) >> 8)
                DataInMemory[j + 2] = ((temp & 0xf0) >> 4)
                DataInMemory[j + 3] = (temp & 0xf)
                j += 4

            if DataType == 'SWORD':
                temp = int((round(A * i * i + B * i + C) / (D * i * i + E * i + F)))

                if temp < 0:
                    temp = temp + pow(2, 16)

                #0X   F F F F
                #     2 3 0 1
                DataInMemory[j + 0] = ((temp & 0xf000) >> 12)
                DataInMemory[j + 1] = ((temp & 0xf00) >> 8)
                DataInMemory[j + 2] = ((temp & 0xf0) >> 4)
                DataInMemory[j + 3] = (temp & 0xf)
                j += 4

            if DataType == 'ULONG':
                temp = int((round(A * i * i + B * i + C) / (D * i * i + E * i + F)))
                #0X F F F F F F F F
                #   6 7 4 5 2 3 0 1
                DataInMemory[j + 0] = ((temp & 0xf0000000) >> 28)
                DataInMemory[j + 1] = ((temp & 0xf000000) >> 24)
                DataInMemory[j + 2] = ((temp & 0xf00000) >> 20)
                DataInMemory[j + 3] = ((temp & 0xf0000) >> 16)
                DataInMemory[j + 4] = ((temp & 0xf000) >> 12)
                DataInMemory[j + 5] = ((temp & 0xf00) >> 8)
                DataInMemory[j + 6] = ((temp & 0xf0) >> 4)
                DataInMemory[j + 7] = (temp & 0xf)
                j += 8

            if DataType == 'SLONG':
                temp = int((round(A * i * i + B * i + C) / (D * i * i + E * i + F)))

                if temp < 0:
                    temp = temp + pow(2, 32)

                #0X F F F F F F F F
                #   6 7 4 5 2 3 0 1
                DataInMemory[j + 0] = ((temp & 0xf0000000) >> 28)
                DataInMemory[j + 1] = ((temp & 0xf000000) >> 24)
                DataInMemory[j + 2] = ((temp & 0xf00000) >> 20)
                DataInMemory[j + 3] = ((temp & 0xf0000) >> 16)
                DataInMemory[j + 4] = ((temp & 0xf000) >> 12)
                DataInMemory[j + 5] = ((temp & 0xf00) >> 8)
                DataInMemory[j + 6] = ((temp & 0xf0) >> 4)
                DataInMemory[j + 7] = (temp & 0xf)
                j += 8

        StrDataInMemory = ''
        for i in DataInMemory:
            StrDataInMemory = StrDataInMemory + self.IntToStr(i,1)

        StrDataInMemory = StrDataInMemory.upper()
        return StrDataInMemory

    #----------------------------------------#
    # name：拷贝数据到内存
    # parameter:AddressBegin, CharacLen, DataInMemory(需要paste的内存数据)
    # return: 1success  0fail
    #----------------------------------------#
    def MemValueToCopy(self, AddressBegin, CharacLen, DataInMemory):
        #根据高位地址找出内存块
        self.AddHighChunkOld = self.ChunkSplit(AddressBegin)   #旧内存块
        self.AddHighChunkNew = self.AddHighChunkOld
        #算出标定量结束地址
        AddressEnd = AddressBegin + CharacLen - 1    ####

        #找到标定量起始位置所在行
        self.LineAdd = self.DataAddLocation(AddressBegin)
        if  self.LineAdd == 0:
            return 0

        #找出标定量起始位置所在行的具体索引,行偏移量
        AddLineIndex = 8 + (AddressBegin - self.LineAdd[0])*2 #偏移8是因为数据从第8位开始 ，*2因为一个字节对应2位

        #如果标定量结束地址小于该行结束地址，单行
        if AddressEnd <= self.LineAdd[1]:
            #StrLineBeginLow = IntToStr(self.LineAdd[0] & 0xffff)  #取出行开始地址的低16位的字符串，用于定位‘正则表达替换行’
            StrOld = self.LineAdd[3]                      #需要被替换的行的内容

            #算出用于替换的字符串内容
            StrNew = list(StrOld)                         #用于替换的行的内容
            StrLinePaste = DataInMemory                   #替换的具体内容
            StrLinePasteLen = CharacLen * 2               #替换的具体内容的字符长度(hex中1个字符0.5byte)
            LineOffset = AddLineIndex                     #用于定位行的具体开始替换位置

            i = 0
            while i < StrLinePasteLen:
                StrNew[LineOffset + i] = StrLinePaste[i]
                i += 1

            #和校验
            Sum = 0
            for j in range((len(self.LineAdd[3]) - 2) / 2):
                Sum = Sum + (int(StrNew[2 * j], 16) << 4) + int(StrNew[2 * j + 1], 16)
            CheackSum = self.IntToStr(0x100 -  (Sum & 0xff) , 2).upper()
            # if CheackSum == '100':
            #     CheackSum = '00'
            StrNew[len(self.LineAdd[3]) - 2] = CheackSum[0]
            StrNew[len(self.LineAdd[3]) - 1] = CheackSum[1]

            StrNew = self.ListToStr(StrNew)
            StrREOld = r':%s'%(StrOld)             #被替代字符串
            StrRENew = r':%s'%(StrNew)             #替代字符串
            self.AddHighChunkNew = re.sub(StrREOld, StrRENew, self.AddHighChunkNew, 1)
        #如果标定量结束地址大于该行结束地址,跨行
        else:
            VecMemory = 0      #DataInMemory中提取字符的指针
            #如果标定量结束地址大于该行结束地址
            while AddressEnd > self.LineAdd[1]:

                #找出标定量起始位置所在行的具体索引
                AddLineIndex = 8 + (AddressBegin - self.LineAdd[0])*2            #偏移8是因为数据从第8位开始 ，*2因为一个字节对应2位
                PasteNum = self.LineAdd[1] - AddressBegin + 1                    #该行需要替代的地址长度
                StrOld = self.LineAdd[3]                                         #需要被替换的行的内容

                StrNew = list(StrOld)                                            #算出用于替换的字符串内容
                StrLinePaste = DataInMemory                                      #替换的具体内容
                LineOffset = AddLineIndex                                        #用于定位行的具体开始替换位置

                tempHighAdd = ((AddressBegin & 0xffff0000) >> 16)

                i = 0
                while i < PasteNum:
                    StrNew[LineOffset + 2*i] = StrLinePaste[VecMemory]
                    StrNew[LineOffset + 2*i + 1] = StrLinePaste[VecMemory + 1]
                    i += 1
                    AddressBegin += 1
                    VecMemory += 2
                #和校验
                Sum = 0
                for j in range((len(self.LineAdd[3]) - 2) / 2):
                    Sum = Sum + (int(StrNew[2 * j], 16) << 4) + int(StrNew[2 * j + 1], 16)

                CheackSum = self.IntToStr(0x100 - (Sum & 0xff) , 2).upper()
                # if CheackSum == '100':
                #     CheackSum = '00'
                StrNew[len(self.LineAdd[3]) - 2] = CheackSum[0]
                StrNew[len(self.LineAdd[3]) - 1] = CheackSum[1]

                StrNew = self.ListToStr(StrNew)
                #替换行内容
                StrREOld = r':%s'%(StrOld)             #被替代字符串
                StrRENew = r':%s'%(StrNew)             #替代字符串

                self.AddHighChunkNew = re.sub(StrREOld, StrRENew, self.AddHighChunkNew, 1)

                #如果高4位地址进1，重新搜索高地址对应内存块
                if ((AddressBegin & 0xffff0000) >> 16) > tempHighAdd:
                    #替换块内容
                    self.content = re.sub(self.AddHighChunkOld, self.AddHighChunkNew, self.content, 1)
                    #读取下一个块
                    self.AddHighChunkNew = self.ChunkSplit(AddressBegin)
                    self.AddHighChunkOld = self.AddHighChunkNew
                #找到标定量当前位置所在行
                self.LineAdd = self.DataAddLocation(AddressBegin)
                if  self.LineAdd == 0:
                    return 0

            #找出标定量起始位置所在行的具体索引
            AddLineIndex = 8 + (AddressBegin - self.LineAdd[0])*2 #偏移8是因为数据从第8位开始 ，*2因为一个字节对应2位

            #计算出多行最后一行的copy数量
            PasteNum = AddressEnd - AddressBegin + 1

            StrOld = self.LineAdd[3]                                         #需要被替换的行的内容

            StrNew = list(self.LineAdd[3])                                    #算出用于替换的字符串内容
            StrLinePaste = DataInMemory                                      #替换的具体内容
            LineOffset = AddLineIndex                                        #用于定位行的具体开始替换位置
            i = 0
            while i < PasteNum:
                StrNew[LineOffset + 2*i] = StrLinePaste[VecMemory]
                StrNew[LineOffset + 2*i + 1] = StrLinePaste[VecMemory + 1]
                i += 1
                AddressBegin += 1
                VecMemory += 2

            #和校验
            Sum = 0
            for j in range((len(self.LineAdd[3]) - 2) / 2):
                Sum = Sum + (int(StrNew[2 * j], 16) << 4) + int(StrNew[2 * j + 1], 16)
            CheackSum = self.IntToStr(0x100 - (Sum & 0xff) , 2).upper()
            # if CheackSum == '100':
            #     CheackSum = '00'
            StrNew[len(self.LineAdd[3]) - 2] = CheackSum[0]
            StrNew[len(self.LineAdd[3]) - 1] = CheackSum[1]

            StrNew = self.ListToStr(StrNew)
            #替换行内容
            StrREOld = r':%s'%(StrOld)             #被替代字符串
            StrRENew = r':%s'%(StrNew)             #替代字符串
            self.AddHighChunkNew = re.sub(StrREOld, StrRENew, self.AddHighChunkNew, 1)
            #print self.AddHighChunkNew
        #替换块内容
        self.content = re.sub(self.AddHighChunkOld, self.AddHighChunkNew, self.content, 1)
        return 1

    #----------------------------------------#
    # descropy:拷贝到内存地址
    # parameter:ChaPhyValue:[Type,ChaPhyValue ,XaxiasPhyValue, YaxisPhyValue]
    # return：得出拷贝的内容
    #----------------------------------------#
    def CopyToMemory(self, CharacName, ChaPhyValue):
        ChaPhyValue = self.GetCheckChaInfo(CharacName, ChaPhyValue)
        if ChaPhyValue == 0:
            return 0
        DataInMemory = [0] * (self.CharacLen * 2)


        if (self.CharateristicType  == 'VALUE') or (self.CharateristicType  == 'VAL_BLK'):
            DataInMemory = self.PhysicalToMemValue(self.CharDataType,self.CharA, self.CharB, self.CharC, self.CharD,
                                                   self.CharE, self.CharF, ChaPhyValue[1], DataInMemory)

            if self.MemValueToCopy(self.AddressBegin, self.CharacLen, DataInMemory) != 1:
                return 0
            return self.content
        if (self.CharateristicType  == 'CURVE'):
            DataInMemory = self.PhysicalToMemValue(self.CharDataType, self.CharA, self.CharB, self.CharC, self.CharD,
                                                   self.CharE, self.CharF, ChaPhyValue[1], DataInMemory)
            if self.MemValueToCopy(self.AddressBegin, self.CharacLen, DataInMemory) != 1:
                return 0

            XaiaxDataInMemory = [0] * (self.XaxisDataLen * 2)
            XaiaxDataInMemory = self.PhysicalToMemValue(self.XaxisDataType, self.XaxisA, self.XaxisB, self.XaxisC, self.XaxisD,
                                                   self.XaxisE, self.XaxisF, ChaPhyValue[2], XaiaxDataInMemory)
            if self.MemValueToCopy(self.XaxisAdd, self.XaxisDataLen, XaiaxDataInMemory) != 1:
                return 0


            return self.content
        if (self.CharateristicType  == 'MAP'):
            #print ChaPhyValue
            DataInMemory = self.PhysicalToMemValue(self.CharDataType, self.CharA, self.CharB, self.CharC, self.CharD,
                                                   self.CharE, self.CharF, ChaPhyValue[1], DataInMemory)
            if self.MemValueToCopy(self.AddressBegin, self.CharacLen, DataInMemory) != 1:
                return 0
            XaiaxDataInMemory = [0] * (self.XaxisDataLen * 2)

            XaiaxDataInMemory = self.PhysicalToMemValue(self.XaxisDataType, self.XaxisA, self.XaxisB, self.XaxisC, self.XaxisD,
                                                   self.XaxisE, self.XaxisF, ChaPhyValue[2], XaiaxDataInMemory)
            if self.MemValueToCopy(self.XaxisAdd, self.XaxisDataLen, XaiaxDataInMemory) != 1:
                return 0
            YaiaxDataInMemory = [0] * (self.YaxisDataLen * 2)
            YaiaxDataInMemory = self.PhysicalToMemValue(self.YaxisDataType, self.YaxisA, self.YaxisB, self.YaxisC, self.YaxisD,
                                                   self.YaxisE, self.YaxisF, ChaPhyValue[3], YaiaxDataInMemory)
            if self.MemValueToCopy(self.YaxisAdd, self.YaxisDataLen, YaiaxDataInMemory) != 1:
                return 0

            return self.content

