import csv
import pandas as pd

"""
主要进行线性插值的工作，提升信号的频率，使得SENSOR DELAY FASTEST模式 带来的频率不一的问题得到解决
"""


class Sensor:

    # 获取数据
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
        # print(gyroscope)
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
                sensor[cur:i].to_csv("D:\studyFile\项目\音频\data_preprocessing\data\gyroscope/gyroscope1.csv",
                                            index_label="id", mode='a', header=False)
                cur = i
            if i >= length - 1:
                # 如果达到长度值,结束
                sensor[cur:length + 1].to_csv("D:\studyFile\项目\音频\data_preprocessing\data\gyroscope/gyroscope1.csv",
                                            index_label="id", mode='a', header=False)
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


# 目的:获取两个数据条目时间之间的差值
# input:
#   start_time:格式为"HH:MM:SS:mmm"->string
#   end_time:格式为"HH:MM:SS:mmm"->string
# output:
#   t_difference:以毫秒为单位的两个数据之间的差值->int      注意，两个数据间应该添加的数据条数为t_difference-1
def get_time_difference(start_time, end_time):
    # 预处理:得到int类型的sh(开始小时),sM,ss,sm,eh,eM,es,em
    start_hour = 10 * int(start_time[0]) + int(start_time[1])
    start_min = 10 * int(start_time[3]) + int(start_time[4])
    start_sec = 10 * int(start_time[6]) + int(start_time[7])
    start_mili = 100 * int(start_time[9]) + 10 * int(start_time[10]) + int(start_time[11])
    end_hour = 10 * int(end_time[0]) + int(end_time[1])
    end_min = 10 * int(end_time[3]) + int(end_time[4])
    end_sec = 10 * int(end_time[6]) + int(end_time[7])
    end_mili = 100 * int(end_time[9]) + 10 * int(end_time[10]) + int(end_time[11])

    # 情况1:当开始时间和结束时间不在同一小时内
    if start_hour != end_hour:
        st_difference = 60000 * (60 - start_min) + 1000 * (60 - start_sec) + 1000 - start_mili
        et_difference = 60000 * end_min + 1000 * end_sec + end_mili
        t_difference = st_difference + et_difference
    # 情况2:当开始时间和结束时间在同一小时，但不在同一分钟内
    elif start_min != end_min:
        st_difference = 1000 * (60 - start_sec) + 1000 - start_mili
        et_difference = 1000 * end_sec + end_mili
        t_difference = st_difference + et_difference
    # 情况3:开始和结束时间不在一秒内
    elif start_sec != end_sec:
        st_difference = 1000 - start_mili
        et_difference = end_mili
        t_difference = st_difference + et_difference
    # 情况4:在1秒内
    else:
        t_difference = end_mili - start_mili
    return t_difference


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


# 目的:获取下一个插值数据的时间戳
# input:
#   cur_time:当前时间戳，组织形式->dict,同interpolation中的cur_time
# output:
#   next_time:下一个插入数据的时间戳,格式->str,形式:"HH:MM:SS:mmm"
def get_next_time(cur_time):
    hour = cur_time['hour']
    min = cur_time['min']
    sec = cur_time['sec']
    mili = cur_time['mili']
    n_mili = mili + 1
    n_sec = sec
    n_min = min
    n_hour = hour
    if n_mili > 999:
        n_mili = 0
        n_sec = sec + 1
        if n_sec > 59:
            n_sec = 0
            n_min = min + 1
            if n_min > 59:
                n_min = 0
                h_hour = hour + 1
                if n_hour > 24:
                    n_hour = 0
    next_time = ""
    # 书写小时
    if n_hour == 0:
        next_time = next_time + "00:"
    elif n_hour < 10:
        next_time = next_time + "0" + str(n_hour) + ":"
    else:
        next_time = next_time + str(n_hour) + ":"

    # 书写分钟
    if n_min == 0:
        next_time = next_time + "00:"
    elif n_min < 10:
        next_time = next_time + "0" + str(n_min) + ":"
    else:
        next_time = next_time + str(n_min) + ":"

    # 书写秒
    if n_sec == 0:
        next_time = next_time + "00:"
    elif n_sec < 10:
        next_time = next_time + "0" + str(n_sec) + ":"
    else:
        next_time = next_time + str(n_sec) + ":"

    # 书写毫秒
    if n_mili == 0:
        next_time = next_time + "000"
    elif n_mili < 10:
        next_time = next_time + "00" + str(n_mili)
    elif n_mili < 100:
        next_time = next_time + "0" + str(n_mili)
    else:
        next_time = next_time + str(n_mili)
    return next_time


# 目的:将字符串类型的time变成字典类型
# input:
#   time:字符串类型的时间->"HH:MM:SS:mmm"
# output:
#   dict_time:字典型时间->dict
def to_time_dict(time):
    dict_time = {
        'hour': int(time[0]) * 10 + int(time[1]),
        'min': int(time[3]) * 10 + int(time[4]),
        'sec': int(time[6]) * 10 + int(time[7]),
        'mili': int(time[9]) * 100 + int(time[10]) * 10 + int(time[11])
    }
    return dict_time


# 目的:把日期的年月日去掉
# input:
#   time:YYYY-MM-DD HH:MM:SS:mmm
# output:
#   cut_time:HH:MM:SS:mmm
def cut_time(time):
    c_time = time[11:]
    return c_time
