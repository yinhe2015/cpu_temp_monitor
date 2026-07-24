def 获取min_perf_pct() -> int:
    with open('/sys/devices/system/cpu/intel_pstate/min_perf_pct', 'r') as f:
        return int(f.read().strip())
def 获取max_perf_pct() -> int:
    with open('/sys/devices/system/cpu/intel_pstate/max_perf_pct', 'r') as f:
        return int(f.read().strip())

def 设置min_perf_pct(最小频率_pct: int) -> None:
    with open('/sys/devices/system/cpu/intel_pstate/min_perf_pct', 'w') as f:
        f.write(str(最小频率_pct))
def 设置max_perf_pct(最大频率_pct: int) -> None:
    with open('/sys/devices/system/cpu/intel_pstate/max_perf_pct', 'w') as f:
        f.write(str(最大频率_pct))