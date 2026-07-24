import os
import re

hwmon路径 = '/sys/class/hwmon'
匹配模式 = re.compile(r'^temp(\d+)_input$')

温度文件 = None

def _读取文件(路径: str) -> str:
    with open(路径, 'r', encoding='utf-8') as 文件:
        return 文件.read().strip()

def 获取温度文件() -> list[str]:
    global 温度文件
    for 根目录, _, 文件列表 in os.walk(hwmon路径, followlinks=True):
        名称路径 = os.path.join(根目录, 'name')
        if (not os.path.isfile(名称路径)) or _读取文件(名称路径) != 'coretemp':
            continue
        break
    else:
        raise OSError('未找到coretemp温度文件')

    温度文件数据 = []
    for 文件 in 文件列表:
        匹配 = 匹配模式.match(文件)
        if 匹配:
            路径 = os.path.join(根目录, 文件)
            温度文件数据.append((int(匹配.group(1)), 路径))

    温度文件数据.sort(key=lambda 数据: 数据[0])
    温度文件 = [路径 for 编号, 路径 in 温度文件数据]

def 获取各核心温度() -> list[float]:
    global 温度文件
    if 温度文件 is None:
        获取温度文件()

    return [int(_读取文件(路径)) / 1000.0 for 路径 in 温度文件]