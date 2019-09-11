# -*- coding: utf-8 -*- 
#! /usr/bin/env python
"""
提取出Dcm中的信息到Listäﾸ?
功能：提取出Dcm中的信息到Listäﾸ?

作è?: Bao wl  <2018/12/12>
"""

import re
import DcmA2LRead
import sys

def GetDcmInf(DcmFilePath, A2lPath):
    # input：Dcm File Path
    # output：[ [ParnameName0,[data0,data1,....] ], [ParnameName1,[data0,data1,....] ], [ParnameName2,[data0,data1,....] ] ,...]


    # import sys
    # stdi, stdo, stde = sys.stdin, sys.stdout, sys.stderr
    # reload(sys)
    # sys.setdefaultencoding('utf-8')
    # sys.stdin, sys.stdout, sys.stderr = stdi, stdo, stde

    DcmFilePath = DcmFilePath.encode('GBK')
    A2lPath = A2lPath.encode('gbk')
    #init
    with open(DcmFilePath) as file:
        content = file.read()
    DcmA2lObject = DcmA2LRead.IncaA2L(A2lPath)
    RetList = []   #定义äﾸ?ﾸﾪ空的list用于存放返回数据

    # 找出æﾉ?ﾜﾉ的Value的区åﾟ?
    Value = re.findall(r'FESTWERT ([\S\s]*?)^END', content, re.M | re.I)
    for i in Value:
        # 去除其中某个描述数据类型块的前后空白字符
        i = i.strip()
        # 创建äﾸ?ﾸﾪ临时的list,以行分隔
        TempList = re.split(r'\n', i)
        CharName = re.split('[\s]*', TempList[0].strip())[0]
        # CharName = TempList[0].strip()
        try:
            LineList = re.split(r'[\s]*', TempList[3].strip())
        except:
            print (TempList)
            print (i)
        if LineList[0] == 'WERT':
            CharValue = LineList[1]

        elif LineList[0] == 'TEXT':
            CharValue = LineList[1].strip('"')
            try:
                CharValue = DcmA2lObject.ReadA2L(0, CharValue, CharName)
            except:
                print ('---------------could not Copy %s,A2l Information was wrong' % (CharName))
                CharValue = 'wrong'
                break
        ListDescription = re.findall('"([\s\S]*)"',TempList[1])
        Description = ListDescription[0]

        LineList = re.split(r'[\s]*', TempList[2].strip())
        Unit = LineList[1]
        RetList.append([CharName, [float(CharValue)], Description, Unit])


    # 找出æﾉ?ﾜﾉ的Value的区åﾟ?
    ValueBlock = re.findall(r'FESTWERTEBLOCK ([\S\s]*?)^END', content, re.M | re.I)
    for i in ValueBlock:
        CharValue = []
        # 去除其中某个描述数据类型块的前后空白字符
        i = i.strip()
        # 创建äﾸ?ﾸﾪ临时的list,以行分隔
        TempList = re.split('\n', i)
        CharName = re.split('[\s]*', TempList[0].strip())[0]

        ListDescription = re.findall('"([\s\S]*)"', TempList[1])
        Description = ListDescription[0]
        LineList = re.split(r'[\s]*', TempList[2].strip())
        Unit = LineList[1]
        for j in TempList:
            LineList = re.split('[\s]*', j.strip())
            if LineList[0] == 'WERT':
                for m in range(1,len(LineList)):
                    CharValue.append(float(LineList[m]))
            elif LineList[0] == 'TEXT':
                for m in range(1,len(LineList)):
                    try:
                        LineList[m] = DcmA2lObject.ReadA2L(0, LineList[m].strip('"'), CharName)
                    except:
                        print ('---------------could not Copy %s,A2l Information was wrong' % (CharName))
                        LineList[m] = 'wrong'
                        break
                    CharValue.append(float(LineList[m]))
        RetList.append([CharName, CharValue, Description, Unit])

    # 找出æﾉ?ﾜﾉ的Curve的区åﾟ?
    Curve = re.findall(r'GRUPPENKENNLINIE ([\S\s]*?)^END', content, re.M | re.I)
    for i in Curve:
        CharValue = []
        XaxisValue = []
        # 去除其中某个描述数据类型块的前后空白字符
        i = i.strip()
        # 创建äﾸ?ﾸﾪ临时的list,以行分隔
        TempList = re.split('\n', i)
        CharName = re.split('[\s]*', TempList[0].strip())[0]
        CharNameX = CharName + 'X'
        ListDescription = re.findall('"([\s\S]*)"', TempList[1])
        Description = ListDescription[0]
        LineList = re.split(r'[\s]*', TempList[3].strip())
        Unit = LineList[1]
        LineList = re.split(r'[\s]*', TempList[2].strip())
        UnitX = LineList[1]
        for j in TempList:
            LineList = re.split('[\s]*', j.strip())
            if LineList[0] == 'WERT':
                for m in range(1,len(LineList)):
                    CharValue.append(float(LineList[m]))
            elif LineList[0] == 'TEXT':   #if 数据是枚举型
                for m in range(1,len(LineList)):
                    try:
                        LineList[m] = DcmA2lObject.ReadA2L(0, LineList[m].strip('"'), CharName)
                    except:
                        print ('---------------could not Copy %s,A2l Information was wrong' % (CharName))
                        LineList[m] = 'wrong'
                        break
                    CharValue.append(float(LineList[m]))
            if LineList[0] == 'ST/X':
                for m in range(1, len(LineList)):
                    XaxisValue.append(float(LineList[m]))
        RetList.append([CharName, CharValue, Description, Unit])
        RetList.append([CharNameX, XaxisValue, Description, UnitX])

    # 找出æﾉ?ﾜﾉ的Map的区åﾟ?
    Map = re.findall(r'GRUPPENKENNFELD ([\S\s]*?)^END', content, re.M | re.I)
    for i in Map:
        # 去除其中某个描述数据类型块的前后空白字符
        i = i.strip()
        # 创建äﾸ?ﾸﾪ临时的list,以行分隔
        TempList = re.split('\n', i)
        CharName = re.split('[\s]*', TempList[0].strip())[0]
        XaxisNum = int(re.split('[\s]*', TempList[0].strip())[2])
        YaxisNum = int(re.split('[\s]*', TempList[0].strip())[1])
        

        ListDescription = re.findall('"([\s\S]*)"', TempList[1])
        Description = ListDescription[0]
        LineList = re.split(r'[\s]*', TempList[3].strip())
        UnitY = LineList[1]
        LineList = re.split(r'[\s]*', TempList[2].strip())
        UnitX = LineList[1]
        LineList = re.split(r'[\s]*', TempList[4].strip())
        Unit = LineList[1]
        LineList = re.split('[\s]*', TempList[5].strip())

        CharNameX = CharName + 'X'
        CharNameY = CharName + 'Y'
        CharValue = []
        XaxisValue = []
        YaxisValue = []
        if LineList[1] != CharName + 'X':
            print ('%s :Xaxis and Yaxis were wrong'%(CharName))
            break

        for j in TempList:
            LineList = re.split('[\s]*', j.strip())
            if LineList[0] == 'WERT':
                for m in range(1, len(LineList)):
                    CharValue.append(float(LineList[m]))

            elif LineList[0] == 'TEXT':  # if 数据是枚举型
                for m in range(1, len(LineList)):
                    try:
                        LineList[m] = DcmA2lObject.ReadA2L(0, LineList[m].strip('"'), CharName)
                    except:
                        print ('---------------could not Copy %s,A2l Information was wrong' % (CharName))
                        LineList[m] = 'wrong'
                        break
                    CharValue.append(float(LineList[m]))

            if LineList[0] == 'ST/X':
                for m in range(1, len(LineList)):
                    XaxisValue.append(float(LineList[m]))

            if LineList[0] == 'ST/Y':
                for m in range(1, len(LineList)):
                    YaxisValue.append(float(LineList[m]))
        RetList.append([CharName, CharValue, Description, Unit])
        RetList.append([CharNameX, XaxisValue, Description, UnitX])
        RetList.append([CharNameY, YaxisValue, Description, UnitY])

        # CharValueTransf = [0] * (XaxisNum * YaxisNum)
        # for i in range(XaxisNum):
        #     for j in range(YaxisNum):
        #         index = j * XaxisNum + i
        #         CharValueTransf[index / YaxisNum + (index % YaxisNum) * XaxisNum] = CharValue[index]

    return RetList

if __name__ == "__main__":
    # DCMPath = r'E:\One drive file\OneDrive - 上海沃开汽车技术有限公司\Work folder\Season Guo\1. CaliPal-OBD项目\CaliPal-OBD simulink Model\DCM2Parameters\Dcm2VarPar\A2L\SCR release.DCM'
    # A2LPath = r'E:\One drive file\OneDrive - 上海沃开汽车技术有限公司\Work folder\Season Guo\1. CaliPal-OBD项目\CaliPal-OBD simulink Model\DCM2Parameters\Dcm2VarPar\A2L\340.a2l'
    DCMPath=r"D:\woocal_code\Dcm2VarPar\A2L\SCR release.DCM"
    A2LPath=r"D:\woocal_code\Dcm2VarPar\A2L\340.a2l"
    a =  GetDcmInf(DCMPath, A2LPath)
    print (a)
