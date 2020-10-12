# coding=utf-8

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
