from 配置 import *
from 路径与日志记录 import 主目录, 温度记录文件
from 自定义http服务器 import 自定义HTTP服务器, 页面_404, 页面_405
from threading import Lock, Thread
import base64
import csv
import hashlib
import json
import os
import struct


线程 = None


class CSV范围读取器:
    """用字节偏移索引按记录行范围读取 CSV，文件追加时只索引新增部分。"""

    def __init__(self, 文件路径: str):
        self.文件路径 = 文件路径
        self.锁 = Lock()
        self.文件标识 = None
        self.已索引大小 = 0
        self.表头 = []
        self.行偏移 = []

    def _重置(self):
        self.文件标识 = None
        self.已索引大小 = 0
        self.表头 = []
        self.行偏移 = []

    def _刷新索引(self):
        if not os.path.exists(self.文件路径):
            self._重置()
            return

        状态 = os.stat(self.文件路径)
        当前标识 = (状态.st_dev, 状态.st_ino)
        if self.文件标识 != 当前标识 or 状态.st_size < self.已索引大小:
            self._重置()
            self.文件标识 = 当前标识

        with open(self.文件路径, 'rb') as 文件:
            if not self.表头:
                表头字节 = 文件.readline()
                if not 表头字节:
                    return
                表头文本 = 表头字节.decode('utf-8-sig').rstrip('\r\n')
                self.表头 = next(csv.reader([表头文本]))
                self.已索引大小 = 文件.tell()

            文件.seek(self.已索引大小)
            while True:
                行开始 = 文件.tell()
                数据 = 文件.readline()
                if not 数据:
                    break
                if not 数据.endswith(b'\n'):
                    break
                self.行偏移.append(行开始)
                self.已索引大小 = 文件.tell()

    def 元数据(self):
        with self.锁:
            self._刷新索引()
            return {'header': self.表头, 'total': len(self.行偏移)}

    def 读取范围(self, 开始: int, 数量: int):
        with self.锁:
            self._刷新索引()
            总数 = len(self.行偏移)
            开始 = max(0, min(开始, 总数))
            结束 = min(开始 + 数量, 总数)
            记录 = []
            if 开始 < 结束:
                with open(self.文件路径, 'rb') as 文件:
                    for 行号 in range(开始, 结束):
                        文件.seek(self.行偏移[行号])
                        文本 = 文件.readline().decode('utf-8').rstrip('\r\n')
                        记录.append({
                            'index': 行号,
                            'values': next(csv.reader([文本])),
                        })
            return {
                'header': self.表头,
                'total': 总数,
                'start': 开始,
                'rows': 记录,
            }


class WebSocket客户端:
    def __init__(self, 操作器):
        self.操作器 = 操作器
        self.写入锁 = Lock()

    def 发送(self, 数据):
        载荷 = json.dumps(数据, ensure_ascii=False).encode('utf-8')
        长度 = len(载荷)
        if 长度 < 126:
            头 = bytes((0x81, 长度))
        elif 长度 <= 0xffff:
            头 = bytes((0x81, 126)) + struct.pack('!H', 长度)
        else:
            头 = bytes((0x81, 127)) + struct.pack('!Q', 长度)
        with self.写入锁:
            self.操作器.写入(头 + 载荷)
            self.操作器.wfile.flush()


数据读取器 = CSV范围读取器(温度记录文件)
WebSocket客户端集合 = set()
WebSocket客户端锁 = Lock()


def _读取确切字节(操作器, 数量):
    数据 = b''
    while len(数据) < 数量:
        块 = 操作器.读取(数量 - len(数据))
        if not 块:
            raise ConnectionError
        数据 += 块
    return 数据


def _保持WebSocket连接(客户端):
    操作器 = 客户端.操作器
    while True:
        头 = _读取确切字节(操作器, 2)
        操作码 = 头[0] & 0x0f
        已遮罩 = bool(头[1] & 0x80)
        长度 = 头[1] & 0x7f
        if 长度 == 126:
            长度 = struct.unpack('!H', _读取确切字节(操作器, 2))[0]
        elif 长度 == 127:
            长度 = struct.unpack('!Q', _读取确切字节(操作器, 8))[0]
        遮罩 = _读取确切字节(操作器, 4) if 已遮罩 else None
        载荷 = _读取确切字节(操作器, 长度) if 长度 else b''
        if 遮罩:
            载荷 = bytes(字节 ^ 遮罩[下标 % 4] for 下标, 字节 in enumerate(载荷))
        if 操作码 == 0x8:
            return
        if 操作码 == 0x9 and len(载荷) < 126:
            with 客户端.写入锁:
                操作器.写入(bytes((0x8a, len(载荷))) + 载荷)
                操作器.wfile.flush()


def _升级WebSocket(请求, 操作器):
    密钥 = 请求.头.get('sec-websocket-key')
    if not 密钥 or 请求.头.get('upgrade', '').lower() != 'websocket':
        操作器.发送文本('WebSocket 升级请求无效', 400)
        return

    魔数 = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    接受值 = base64.b64encode(
        hashlib.sha1((密钥 + 魔数).encode('ascii')).digest()
    ).decode('ascii')
    操作器.发送响应(101)
    操作器.发送头('Upgrade', 'websocket')
    操作器.发送头('Connection', 'Upgrade')
    操作器.发送头('Sec-WebSocket-Accept', 接受值)
    操作器.结束头()

    客户端 = WebSocket客户端(操作器)
    with WebSocket客户端锁:
        WebSocket客户端集合.add(客户端)
    try:
        客户端.发送({'type': 'ready', **数据读取器.元数据()})
        _保持WebSocket连接(客户端)
    except (ConnectionError, BrokenPipeError, ConnectionResetError, OSError):
        pass
    finally:
        with WebSocket客户端锁:
            WebSocket客户端集合.discard(客户端)


def 新记录回调(记录):
    """注册给温度记录管理器；记录落盘后向所有网页客户端广播。"""
    时间, 主温度, 温度列表 = 记录
    总数 = 数据读取器.元数据()['total']
    消息 = {
        'type': 'record',
        'index': 总数 - 1,
        'values': [时间, 主温度, *温度列表],
        'total': 总数,
    }
    with WebSocket客户端锁:
        客户端列表 = list(WebSocket客户端集合)
    for 客户端 in 客户端列表:
        try:
            客户端.发送(消息)
        except (BrokenPipeError, ConnectionResetError, OSError):
            with WebSocket客户端锁:
                WebSocket客户端集合.discard(客户端)


def _获取整数参数(请求, 名称, 默认值):
    try:
        return int(请求.参数.get(名称, 默认值))
    except (TypeError, ValueError):
        return 默认值


def 处理函数(
    请求: 自定义HTTP服务器.请求,
    操作器: 自定义HTTP服务器.操作,
):
    if 请求.类型 == 'GET':
        if 请求.相对URL == '/' or 请求.相对URL == '/index.html':
            操作器.发送文件(os.path.join(主目录, '图表.html'))
        elif 请求.相对URL == '/data/meta':
            操作器.发送JSON(数据读取器.元数据())
        elif 请求.相对URL == '/data/range':
            开始 = max(0, _获取整数参数(请求, 'start', 0))
            数量 = max(1, min(_获取整数参数(请求, 'limit', 500), 5000))
            操作器.发送JSON(数据读取器.读取范围(开始, 数量))
        elif 请求.相对URL == '/data':
            # 保留旧接口兼容其他工具；新网页只使用范围接口。
            if not os.path.exists(温度记录文件):
                操作器.发送文本('')
            else:
                操作器.发送文件(温度记录文件, MIME类型='text/csv')
        elif 请求.相对URL == '/ws':
            _升级WebSocket(请求, 操作器)
        else:
            操作器.发送响应(404)
            操作器.结束头()
            操作器.写入(页面_404.format(请求.相对URL))
    else:
        操作器.发送响应(405)
        操作器.结束头()
        操作器.写入(页面_405.format(请求.类型))


def 启动():
    global 线程
    if not 是否启动网页 or 线程:
        return

    服务器 = 自定义HTTP服务器(处理函数, 端口=网页端口)
    线程 = Thread(target=服务器.启动, daemon=True)
    线程.start()
