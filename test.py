from sensor import Sensor
from sensor import high_pass_filter_20hz
from data_visualization import *

file_dir = './data/gyroscope/gyroscope1.csv'
gyroscope = Sensor(file_dir)
# gyroscope, length = gyroscope.linear_interpolation()
# print("数据已存储完成")
data1, data2, data3 = gyroscope.data_stft()
datas = high_pass_filter_20hz([data1, data2, data3])
for data in datas:
    stft_plot(data["t"], data["f"], data["Zxx"])


