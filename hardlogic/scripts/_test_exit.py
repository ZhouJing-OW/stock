import json
import struct
from datetime import datetime, date, timedelta
from pathlib import Path

TDX_DIR = Path("C:/new_tdx/vipdoc")
data_path = Path(r"E:\Hanako_WorkSpace\研报\个股研究\hardlogic\data\hardlogic.json")

with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)


def check_exit_signal(code, added_str):
    added = datetime.strptime(added_str, "%Y-%m-%d").date()

    if code.startswith("6"):
        subdir, fname = TDX_DIR / "sh" / "lday", f"sh{code}.day"
    else:
        subdir, fname = TDX_DIR / "sz" / "lday", f"sz{code}.day"
    filepath = subdir / fname
    if not filepath.exists():
        return ("ok", "NO_FILE")

    records = []
    with open(filepath, "rb") as f:
        raw = f.read()
    for i in range(0, len(raw), 32):
        if i + 32 > len(raw):
            break
        d_int = struct.unpack("I", raw[i:i+4])[0]
        dt = date(d_int // 10000, (d_int % 10000) // 100, d_int % 100)
        close = struct.unpack("I", raw[i+16:i+20])[0] / 100.0
        records.append({"date": dt, "close": close})

    if len(records) < 60:
        return ("ok", "SHORT")

    post = [r for r in records if r["date"] >= added]
    if len(post) < 5:
        return ("ok", "POST_SHORT")

    activated = False
    for r in post:
        hist = [x for x in records if x["date"] <= r["date"]]
        if len(hist) < 60:
            continue
        ma10 = sum(x["close"] for x in hist[-10:]) / 10
        ma60 = sum(x["close"] for x in hist[-60:]) / 60
        if ma10 > ma60 * 1.10:
            activated = True
            break

    if not activated:
        return ("ok", "NOT_ACTIVATED")

    for r in post[-5:]:
        r_date = r["date"]
        hist = [x for x in records if x["date"] <= r_date and x["date"] >= r_date - timedelta(days=90)]
        if len(hist) >= 40:
            ma60 = sum(x["close"] for x in hist[-60:]) / 60
            if r["close"] < ma60:
                pct = (r["close"] / ma60 - 1) * 100
                return ("exit", f"跌破60日线({pct:.1f}%) | {r_date}")
    return ("ok", "STILL_ABOVE")


# 检查几只之前标记退出的股票
test_codes = ["002916", "603256", "000636", "002436", "688535"]
print(f"通达信目录存在: {TDX_DIR.exists()}")
for code in test_codes:
    s = next((x for x in data["stocks"] if x["code"] == code), None)
    if s:
        status, desc = check_exit_signal(code, s["conceptAdded"])
        print(f"  {s['name']}({code}): {status} - {desc}")
