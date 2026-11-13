from 配置 import *
from 时间 import 获取时间戳
import os

class 温度记录管理器:
    def __init__(self, 温度记录文件: str):
        self.温度记录文件 = 温度记录文件
        self.缓存 = []
        self.上次写入时间 = 获取时间戳()
        self.写入回调列表 = []

        self.第一次写入 =  not os.path.exists(self.温度记录文件)

    def 注册写入回调(self, 回调函数: callable):
        if 回调函数 not in self.写入回调列表:
            self.写入回调列表.append(回调函数)

    def 添加记录(self, 时间, 主温度, 温度: list[float]):
        记录 = (时间, 主温度, 温度)
        self.缓存.append(记录)
        # 实时订阅者每次采样后立即收到记录；CSV 仍按原间隔批量落盘。
        for 回调函数 in self.写入回调列表:
            try:
                回调函数(记录)
            except Exception as 错误:
                print(f'温度记录写入回调失败: {错误}')

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

        已写入记录 = self.缓存.copy()
        with open(self.温度记录文件, 'a') as 文件:
            for 记录 in 已写入记录:
                文件.write(f'{记录[0]},{记录[1]},{','.join(map(str, 记录[2]))}\n')
        self.缓存.clear()
