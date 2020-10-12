import matplotlib.pyplot as plt
import numpy as np


# 绘制短时傅里叶变换STFT的时频图
# input:
#   t:时间序列
#   f:频率
#   Zxx:数据的STFT
def stft_plot(t, f, Zxx):
    plt.pcolormesh(t, f, np.abs(Zxx))
    plt.title('Sensor Data STFT')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()
