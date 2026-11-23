import ctypes, sys
from pathlib import Path

site = Path(sys.prefix) / "Lib" / "site-packages"
blocked, other = [], 0
for pyd in sorted(site.rglob("*.pyd")):
    try:
        ctypes.WinDLL(str(pyd))
    except OSError as e:
        if "Application Control" in str(e):
            blocked.append(pyd.relative_to(site))
        else:
            other += 1

print(f"Blocked by policy: {len(blocked)}")
for b in blocked:
    print("  ", b)
print(f"Failed for other reasons (ignore): {other}")
