import csv
import pandas as pd
import scipy.signal as signal
from time_stamp_service import *
from data_visualization import *

"""
主要进行线性插值的工作，提升信号的频率，使得SENSOR DELAY FASTEST模式 带来的频率不一的问题得到解决
"""


class Sensor:

    # 获取数据:数据格式必须为{'time','data1','data2','data3'}.
    def __init__(self, file_dir):
        # 读取传感器的数据
        # 1:打开文件
        file_sensor = open(file_dir, 'r')
        # 2:使用python csv模块读取数据
        reader_sensor = csv.reader(file_sensor)
        # 3:将数据转换为pandas Dataframe类型
        t_gyroscope = pd.DataFrame(reader_sensor)
        # 构建新的dataframe类型对象，来获取数据
        sensor = pd.DataFrame()
        sensor['time'] = t_gyroscope[0]  # 获取时间戳:格式是YYYY-MM-DD HH:MM:SS:mmm需要的是HH开始，所以[11:]
        sensor['data1'] = pd.to_numeric(t_gyroscope[1], errors='coerce')  # x轴数据
        sensor['data2'] = pd.to_numeric(t_gyroscope[2], errors='coerce')  # y轴数据
        sensor['data3'] = pd.to_numeric(t_gyroscope[3], errors='coerce')  # z轴数据
        # 这一部分将YYYY-MM-DD 去掉
        time_list = []
        for t in range(sensor.shape[0]):
            time_list.append(sensor['time'][t][11:])
        sensor.loc[:, "time"] = time_list
        # 把第一行删除，因为第一行是抬头
        # gyroscope.drop(0, inplace=True)
        # gyroscope.reset_index(drop=True)
        # print(sensor)
        self.sensor = sensor

    # 数据补充函数，用来完成整体线性插值的工作
    # output:
    #   sensor:线性插值后的传感器数据->dataframe
    #   length:数据长度->int
    def linear_interpolation(self):
        sensor = self.sensor
        # print(gyroscope)
        length = sensor.shape[0]
        i = 0
        cur = 0  # 记录当前进度
        while i <= length:
            # 获取dataframe的数据量长度
            if int(i / 1000) != int(cur / 1000):
                # 每前进1000条数据，播报进度，存储文件，并且更新cur
                print("第%d条数据写入完成,进度%.2f" % (i, i * 100 / length) + "%")
                sensor[cur:i].to_csv("D:\studyFile\项目\音频\Code\SensorDataProcessing\data\gyroscope/gyroscope1.csv",
                                     index=False, mode='a', header=False)
                cur = i
            if i >= length - 1:
                # 如果达到长度值,结束
                sensor[cur:length + 1].to_csv(
                    "D:\studyFile\项目\音频\Code\SensorDataProcessing\data\gyroscope/gyroscope1.csv",
                    mode='a', header=False, index=False)
                break
            time_difference = get_time_difference(sensor['time'][i], sensor['time'][i + 1])  # 获取时间差
            # 如果time_difference>1才需要插值，否则跳过
            if time_difference > 1:
                k1 = get_slope(sensor['data1'][i], sensor['data1'][i + 1], time_difference)  # 获取x轴数据的斜率
                k2 = get_slope(sensor['data2'][i], sensor['data2'][i + 1], time_difference)  # 获取y轴数据的斜率
                k3 = get_slope(sensor['data3'][i], sensor['data3'][i + 1], time_difference)  # 获取z轴数据的斜率
                insert_num, sensor = interpolation([k1, k2, k3], time_difference - 1, sensor, i)
                # length = length + insert_num 循环开始获得
                i = i + time_difference
            elif time_difference == 0:
                # 对于相同的时间戳,减去下一个
                sensor = sensor.drop(i + 1).reset_index(drop=True)
            else:
                i = i + 1
            length = sensor.shape[0]
        return sensor, length

    # 目的:完成对数据的短时傅里叶变换操作，提取数据的时频域数据
    # output:
    #   sensor_stft:短时傅里叶变换之后的数据->pd.dataframe格式
    def data_stft(self):
        """
            :param x: 输入信号->list
            :param params: {fs:采样频率；
                            window:窗。默认为汉明窗；
                            nperseg： 每个段的长度，默认为256，
                            noverlap:重叠的点数。指定值时需要满足COLA约束。默认是窗长的一半，
                            nfft：fft长度，
                            detrend：（str、function或False）指定如何去趋势，默认为Flase，不去趋势。
                            return_onesided：默认为True，返回单边谱。
                            boundary：默认在时间序列两端添加0
                            padded：是否对时间序列进行填充0（当长度不够的时候），
                            axis：可以不必关心这个参数}
            :return: f:采样频率数组；t:段时间数组；Zxx:STFT结果
        """
        sensor = self.sensor
        # 获取3轴数据，并转换为列表形式,因为stft的输入数据需要时列表的形式
        data1 = sensor['data1'].tolist()
        data2 = sensor['data2'].tolist()
        data3 = sensor['data3'].tolist()
        fs = 10e3  # 采样频率
        f1, t1, Zxx1 = signal.stft(data1, fs, nperseg=500)  # f为采样频率, t为时间, Zxx为data的stft
        f2, t2, Zxx2 = signal.stft(data2, fs, nperseg=500)
        f3, t3, Zxx3 = signal.stft(data3, fs, nperseg=500)
        stft_plot(t1, f1, Zxx1)


# 目的:获取data1,data2,data3的斜率
# input:
#   start_data:开始时间对应的数据->float
#   end_data:结束时间对应数据->格式同上
#   t_difference:时间差->int
# output:
#   k斜率->float
def get_slope(start_data, end_data, t_difference):
    k = (end_data - start_data) / t_difference
    return k


# 目的:进行插值操作
# input:
#   k_list:斜率列表->list(float)
#   insert_num:插值点数量->int(num = t_difference - 1)
#   gyroscope:数据对象，用来向里边添加插值数值->pd.Dataframe(同gyroscope构型)
#   i:这次插值的启示坐标->int
# output:
#   insert_num:添加的数值数量
#   gyroscope:改变后的gyroscope
def interpolation(k_list, intsert_num, sensor, i):
    cur_time = {
        'hour': int(sensor['time'][i][0:2]),
        'min': int(sensor['time'][i][3:5]),
        'sec': int(sensor['time'][i][6:8]),
        'mili': int(sensor['time'][i][9:])
    }
    insert_datas = pd.DataFrame({
        'time': [],
        'data1': [],
        'data2': [],
        'data3': []
    })
    for cur in range(1, intsert_num + 1):
        next_time = get_next_time(cur_time)  # 获取下一个列表时间戳
        n_data1 = sensor['data1'][i] * (1 + k_list[0] * cur)
        n_data2 = sensor['data2'][i] * (1 + k_list[1] * cur)
        n_data3 = sensor['data3'][i] * (1 + k_list[2] * cur)
        insert_datas = insert_datas.append({"time": next_time, "data1": n_data1, "data2": n_data2, "data3": n_data3},
                                           ignore_index=True)
        cur_time = to_time_dict(next_time)
    sensor1 = sensor[:i + 1]
    sensor2 = sensor[i + 1:]
    sensor = sensor1.append(insert_datas, ignore_index=True).append(sensor2, ignore_index=True)
    return intsert_num, sensor
