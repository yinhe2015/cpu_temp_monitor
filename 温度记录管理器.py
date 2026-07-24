from 配置 import *
from 时间 import 获取时间戳
import os

class 温度记录管理器:
    def __init__(self, 温度记录文件: str):
        self.温度记录文件 = 温度记录文件
        self.缓存 = []
        self.上次写入时间 = 获取时间戳()

        self.第一次写入 =  not os.path.exists(self.温度记录文件)

    def 添加记录(self, 时间, 主温度, 温度: list[float]):
        self.缓存.append((时间, 主温度, 温度))
        时间戳 = 获取时间戳()
        if 时间戳 - self.上次写入时间 >= 温度记录写入间隔:
            self.上次写入时间 = 时间戳
            self.写入缓存()

    def 写入缓存(self):
        if not self.缓存:
            return

        if self.第一次写入:
            样本长度 = len(self.缓存[0][2])
            from 路径与日志记录 import 日志
            日志.信息(f'第一次写入, {样本长度} 个核心')
            文本 = '时间,总温度,' + ','.join(
                [f'核心{i}' for i in range(1, 样本长度 + 1)]
            ) + '\n'
            with open(self.温度记录文件, 'w') as 文件:
                文件.write(文本)
            self.第一次写入 = False

        with open(self.温度记录文件, 'a') as 文件:
            for 记录 in self.缓存:
                文件.write(f'{记录[0]},{记录[1]},{','.join(map(str, 记录[2]))}\n')
        self.缓存.clear()
