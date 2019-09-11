import os
import mdfreader
import xlwt
import numpy as np
import xlsxwriter
import matplotlib.pyplot as plt
import sys
import numpy as np
from collections import Counter

path = r"D:\woocal_code\20190910"
datas = []
newDir = ''

def eachFile(filepath):
    for root,dirs,files in os.walk(filepath):
        for file in files:
            name=os.path.splitext(file)[0]
            suffix=os.path.splitext(file)[1]
            print(name)
            print(suffix)
            if os.path.splitext(file)[1] == ".dat":
                print(file)
                file_abs=os.path.join(root,file)
                datas.append(file_abs)

if __name__ == "__main__":
    # book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    # sheet = book.add_sheet('mysheet', cell_overwrite_ok=True)
    workbook = xlsxwriter.Workbook(path + '/0827_测试数据统计.xlsx')
    worksheet = workbook.add_worksheet('汇总表')
    # workbook=xlsxwriter.workbook(r'E:\360MoveData\Users\Season\Desktop\Dat_file_summary.xlsx')
    # worksheet=workbook.add_worksheet()
    eachFile(path)
    print(datas)
    # print(datas)
    i=1
    mean_value=0
    median_value=0
    for xm1 in datas:
        yop = mdfreader.Mdf(xm1)
        kys = yop.keys()
        # print(xm1)
        # T5_start = min((yop.get_channel_data("time_5")))
        # T5_finish = min(int(yop.get_channel_data("time_5")))
        for item in kys:
            manyx_dict={}
            data_list=yop.get_channel_data(item)
            print(data_list)
            print(data_list.dtype)
            maxvalue=max(data_list)
            minvalue = min(data_list)
            try:
                meanx=np.mean(data_list)
            except TypeError as e:
                meanx=None
            count=Counter(data_list)
            max_count=max(count.values())
            for key,value in count.items():
                if value == max_count:
                    manyx=key
                    manyxproportion = '{:.4%}'.format(value / len(data_list))
            # mean_value=np.mean(yop.get_channel_data(item))
            # median_value = np.median(yop.get_channel_data(item))

            worksheet.write(0, 0, '文件路径')
            worksheet.write(0, 1, '通道名称')
            worksheet.write(0, 2, '最小值')
            worksheet.write(0, 3, '最大值')
            worksheet.write(0, 4, '平均数')
            worksheet.write(0, 5 , '众数')
            worksheet.write(0, 6, '众数比例')
            worksheet.write(i, 0, xm1)
            worksheet.write(i, 1, item)
            worksheet.write(i, 2, str(minvalue))
            worksheet.write(i, 3, str(maxvalue))
            worksheet.write(i, 4, str(meanx))
            worksheet.write(i, 5, str(manyx))
            worksheet.write(i, 6, str(manyxproportion))
            i = i + 1

    workbook.close()
