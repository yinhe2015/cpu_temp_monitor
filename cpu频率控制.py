import os

# 注意: 这里因为太长被简写
# ip = intel_pstate
# npp = min_perf_pct
# xpp = max_perf_pct

ip_dir = '/sys/devices/system/cpu/intel_pstate'

def 获取npp() -> int:
    with open(os.path.join(ip_dir, 'min_perf_pct'), 'r') as f:
        return int(f.read().strip())
def 获取xpp() -> int:
    with open(os.path.join(ip_dir, 'max_perf_pct'), 'r') as f:
        return int(f.read().strip())

def 设置npp(最小频率_pct: int) -> None:
    with open(os.path.join(ip_dir, 'min_perf_pct'), 'w') as f:
        f.write(str(最小频率_pct))
def 设置xpp(最大频率_pct: int) -> None:
    with open(os.path.join(ip_dir, 'max_perf_pct'), 'w') as f:
        f.write(str(最大频率_pct))