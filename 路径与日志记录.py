from 配置 import *
from 温度记录管理器 import 温度记录管理器
from 日志 import 打开日志
import os

主目录 = os.path.dirname(os.path.abspath(__file__))
数据目录 = os.path.join(主目录, '数据')
os.makedirs(数据目录, exist_ok=True)

日志路径 = os.path.join(主目录, '日志.log')
温度记录文件 = os.path.join(数据目录, '温度记录.csv')

日志 = 打开日志(日志路径, 输出=True)