import subprocess
from 路径与日志记录 import 日志

模块名 = 'coretemp'
查看模块命令 = ['lsmod']
启用模块命令 = ['modprobe', 模块名]

def 检查是否加载() -> bool:
    return 模块名 in subprocess.run(
        查看模块命令,
        capture_output=True,
        text=True,
        check=False,
    ).stdout

def 加载模块() -> None:
    try:
        subprocess.check_call(启用模块命令)
        日志.信息(f'模块 {模块名} 启用成功')
    except subprocess.CalledProcessError:
        日志.异常(f'模块 {模块名} 启用失败')

def 检查并加载模块() -> None:
    是否加载 = 检查是否加载()
    日志.调试(f'模块 {模块名} 是否加载: {是否加载}')
    if not 是否加载:
        日志.警告(f'模块 {模块名} 未加载, 尝试加载')
        加载模块()