import os
import mdfreader
import xlwt
import numpy as np
import xlsxwriter
import matplotlib.pyplot as plt
import sys
import numpy as np
from collections import Counter
from matplotlib import pyplot as plt
import shutil
from collections import Counter
import time

DRAW_PIC = True
WRITE_EXCEL=True
PATH = r"D:\woocal_code\parse_dat"


class ECUChannel():
    def __init__(self):
        self.channel_name = ""
        self.channel_values = []
        self.channel_unit = ""
        self.sample_time = []
        self.time_channel = ""

    def set_channel_name(self, channel_name):
        self.channel_name = channel_name

    def set_channel_unit(self, channel_unit):
        self.channel_unit = channel_unit

    def set_sample_time(self, sample_time):
        self.sample_time = sample_time

    def set_channel_values(self, channel_values):
        self.channel_values = channel_values

    def set_time_channel(self, time_channel):
        self.time_channel = time_channel



class ParseDat():
    def __init__(self):
        self.datas = []
        self.dat_name = ""
        self.dat_path = ""
        self.current_dat = ""
        self.sample_mark = 10
        self.channels = []
        self.time_channel_info = {}
        self.time_list = []
        self.dat_name = ""

    def eachFile(self):
        for root, dirs, files in os.walk(PATH):
            for file in files:
                name = os.path.splitext(file)[0]
                suffix = os.path.splitext(file)[1]
                if os.path.splitext(file)[1] == ".dat":
                    file_abs = os.path.join(root, file)
                    self.datas.append(file_abs)

    def draw_picture(self, ecu_channel):
        dat_path = os.path.join(self.dat_path, self.dat_name)
        if not os.path.exists(dat_path):
            os.makedirs(dat_path)
        pic_name = "-".join(ecu_channel.channel_name.split("."))
        pic_path = os.path.join(dat_path, pic_name)
        # fig = plt.figure(figsize=(20, 8), dpi=80)
        x_n = len(ecu_channel.channel_values)
        sample_step = x_n // self.sample_mark

        time_list = self.time_channel_info[ecu_channel.time_channel]["value"]
        time_unit= self.time_channel_info[ecu_channel.time_channel]["unit"]
        # subscript_list=np.linspace(start,end,sample_step)
        x = [time_list[i] for i in range(0, x_n, self.sample_mark)]
        y = [ecu_channel.channel_values[i] for i in range(0, x_n, self.sample_mark)]

        plt.plot(x, y, color="red")
        plt.xlabel("time   ({})".format(time_unit))
        plt.ylabel(ecu_channel.channel_name + "   ({})".format(ecu_channel.channel_unit))
        plt.savefig(pic_path)
        plt.clf()

    def clean_data(self, ecu_channel):
        new_data_list = []
        for data in ecu_channel.channel_values:
            try:
                new_data = float(data)
                new_data_list.append(new_data)
            except Exception as e:
                print(e)

        ecu_channel.set_channel_values(new_data_list)
        return ecu_channel

    def time_channel_deal(self, yop):
        values = []
        for channel in self.channels:
            if "time" in channel:
                values = yop.get_channel_data(channel)
                length = len(values)
                unit=yop.get_channel_unit(channel)
                info = {
                    "value": values,
                    "length": length,
                    "unit" : unit
                }
                self.time_channel_info[channel] = info
        print(self.time_channel_info)

    def get_time_channel(self, ecu_channel):
        for key, value in self.time_channel_info.items():
            channel_length = len(ecu_channel.channel_values)
            if channel_length == value["length"]:
                ecu_channel.set_time_channel(key)
                break

    def traverse_channel(self):
        if WRITE_EXCEL:
            time_str = time.strftime("%m%d", time.localtime())
            workbook = xlsxwriter.Workbook(PATH + '/{}_测试数据统计.xlsx'.format(time_str))
            worksheet = workbook.add_worksheet('汇总表')
        ecu_channel = ECUChannel()
        i = 1
        count=0
        for xm1 in self.datas:
            count=count+1
            data_len=len(self.datas)
            self.dat_name = os.path.splitext(os.path.basename(xm1))[0]
            self.dat_path = os.path.dirname(xm1)
            dat=os.path.basename(xm1)
            self.current_dat = xm1
            yop = mdfreader.Mdf(xm1)
            self.channels = yop.keys()
            self.time_channel_deal(yop)
            print("一共{}个dat文件，正在解析第{}个dat文件。".format(data_len,count))

            for channel in self.channels:
                ecu_channel.set_channel_name(channel)
                values = yop.get_channel_data(channel)
                size=sys.getsizeof(list(values))
                lenx=len(values)
                ecu_channel.set_channel_values(values)
                unit = yop.get_channel_unit(channel)
                ecu_channel.set_channel_unit(unit)

                self.get_time_channel(ecu_channel)
                ecu_channel = self.clean_data(ecu_channel)

                if channel not in self.time_channel_info.keys():
                    # 画折线图
                    if ecu_channel.channel_values and DRAW_PIC:
                        self.draw_picture(ecu_channel)

                # 数据写到excel表格
                if WRITE_EXCEL:
                    maxvalue = max(values)
                    minvalue = min(values)
                    try:
                        meanx = np.mean(values)
                    except TypeError:
                        meanx = None
                    count_dict = Counter(values)
                    max_count = max(count_dict.values())
                    for key, value in count_dict.items():
                        if value == max_count:
                            manyx = key
                            manyxproportion = '{:.4%}'.format(value / len(values))

                    worksheet.write(0, 0, '文件路径')
                    worksheet.write(0, 1, '通道名称')
                    worksheet.write(0, 2, '最小值')
                    worksheet.write(0, 3, '最大值')
                    worksheet.write(0, 4, '平均数')
                    worksheet.write(0, 5, '众数')
                    worksheet.write(0, 6, '众数比例')
                    # self.worksheet.write(0,7,"折线图")
                    worksheet.write(i, 0, self.current_dat)
                    worksheet.write(i, 1, channel)
                    worksheet.write(i, 2, str(minvalue))
                    worksheet.write(i, 3, str(maxvalue))
                    worksheet.write(i, 4, str(meanx))
                    worksheet.write(i, 5, str(manyx))
                    worksheet.write(i, 6, str(manyxproportion))
                    # self.worksheet.insert_chart(i, 7, chart)
                    i = i + 1
        if WRITE_EXCEL:
            workbook.close()

    def draw_picture_test(self):
        pic_path = os.path.join(self.picture_path, "test")
        # fig = plt.figure(figsize=(20, 8), dpi=80)
        # final_list=[[1,2,3],[1,3,5],[2,4,6]]
        x = np.linspace(0, 10000, 40)
        y = np.random.randint(0, 100000, 40)
        plt.plot(x, y)
        plt.savefig(pic_path)


if __name__ == "__main__":
    # book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    # sheet = book.add_sheet('mysheet', cell_overwrite_ok=True)
    start=time.time()
    pd = ParseDat()
    # pd.draw_picture_test()
    pd.eachFile()
    print("Parse Dat File,please wait!")
    pd.traverse_channel()
    print("Done!")
    end=time.time()
    print("Totle {} seconds!".format(end-start))
    # pd.write_excel()
