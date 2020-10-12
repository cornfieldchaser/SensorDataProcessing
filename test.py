from sensor import Sensor

file_dir = './res/1.csv'
gyroscope = Sensor(file_dir)
gyroscope, length = gyroscope.linear_interpolation()
print("数据已存储完成")
