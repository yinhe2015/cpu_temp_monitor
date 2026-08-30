from 配置 import *
from 路径与日志记录 import 主目录, 温度记录文件
from 自定义http服务器 import 自定义HTTP服务器, 页面_404, 页面_405
from threading import Thread
import os

线程 = None

def 处理函数(
    请求: 自定义HTTP服务器.请求,
    操作器: 自定义HTTP服务器.操作,
):
    if 请求.类型 == 'GET':
        if 请求.相对URL == '/' or 请求.相对URL == '/index.html':
            操作器.发送文件(os.path.join(主目录, '图表.html'))
        elif 请求.相对URL == '/data':
            if not os.path.exists(温度记录文件):
                操作器.发送响应(200)
                操作器.结束头()
                操作器.写入(b'')
            操作器.发送文件(温度记录文件, MIME类型='text/csv')
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

    # 为开启或已启动, 则不重复启动
    if not 是否启动网页 or 线程:
        return

    服务器 = 自定义HTTP服务器(
        处理函数,
        端口=网页端口,
    )

    线程 = Thread(
        target=服务器.启动,
        daemon=True,
    )
    线程.start()