import sys
import os
sys.path.append(os.path.join(os.path.expanduser('~'), 'disk-d', 'pylib'))

from 配置 import *
from 时间 import 格式化当前时间, 默认格式_日志
from 启用coretemp import 检查并加载模块 as 启用coretemp
from 网页 import 启动 as 启动网页
from 获取cpu温度 import 获取各核心温度
from cpu频率控制 import *
from 温度记录管理器 import 温度记录管理器
from 错误高温处理 import 错误高温处理
from 路径与日志记录 import 日志, 温度记录文件
import time

当前npp = 获取npp()
当前xpp = 获取xpp()
# 初始xpp = 当前xpp

def 减少xpp(幅度: int):
    当前xpp -= 幅度
    if 当前xpp < 最低xpp:
        日志.警告(f'{当前xpp=} < {最低xpp=}, 设为最低')
        当前xpp = 最低xpp

    # 防止 max < min
    if 当前xpp < 当前npp:
        当前npp = 当前xpp - 10
        if 当前npp < 1:
            当前npp = 1
        设置npp(当前npp)
    
    设置xpp(当前xpp)

def 处理温度(名称: str, 温度: float, 需要降频: bool = True):
    if 温度 > 错误温度:
        日志.错误(f'⚠️⚠️⚠️ {名称} 温度{温度:.2f}°C > {错误温度=}°C, 危险 ⚠️⚠️⚠️')
        错误高温处理()
    elif 温度 > 严重降频温度:
        日志.警告(f'{名称} 温度{温度:.2f}°C > {严重降频温度=}°C, 降频{严重降频幅度}%')
        if 需要降频:
            减少xpp(严重降频幅度)
    elif 温度 > 中度降频温度:
        日志.警告(f'{名称} 温度{温度:.2f}°C > {中度降频温度=}°C, 降频{中度降频幅度}%')
        if 需要降频:
            减少xpp(中度降频幅度)
    elif 温度 > 轻度降频温度:
        日志.警告(f'{名称} 温度{温度:.2f}°C > {轻度降频温度=}°C, 降频{轻度降频幅度}%')
        if 需要降频:
            减少xpp(轻度降频幅度)
    elif 温度 > 警告温度:
        日志.警告(f'{名称} 温度{温度:.2f}°C > {警告温度=}°C')

def 警告与降频处理(主温度: float, 温度列表: list[float]):
    最热温度 = max(温度列表)
    最热核心 = ','.join([f'最热核心 {核心}' for 核心, 温度 in enumerate(温度列表, 1) if 温度 == 最热温度])

    if 主温度 > 最热温度:
        最热核心 += ', 总'
        最热温度 = 主温度
    else:
        处理温度('总', 主温度, 需要降频=False)

    处理温度(最热核心, 最热温度)

    for 核心, 温度 in enumerate(温度列表, 1):
        if 核心 != 最热核心:
            处理温度(f'核心 {核心}', 温度, 需要降频=False)

def 监控温度(温度记录: 温度记录管理器):
    上一个温度列表 = 获取各核心温度()

    while True:
        # 获取温度
        主温度, 温度列表 = 获取各核心温度()
        时间 = 格式化当前时间(默认格式_日志)

        # 高温警告/降频
        警告与降频处理(主温度, 温度列表)

        # 记录
        温度记录.添加记录(时间, 主温度, 温度列表)

        # 等待
        time.sleep(温度检测间隔)

def 主函数():
    启用coretemp()
    启动网页() # 如果未设置启动, 则会跳过

    温度记录 = 温度记录管理器(温度记录文件)
    监控温度(温度记录)

if __name__ == '__main__':
    主函数()