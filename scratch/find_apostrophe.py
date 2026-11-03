# -*- coding: utf-8 -*-
with open("Institute_Ledger.py", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if "today" in line.lower() and "class" in line.lower():
            # print with ascii safe
            safe = line.strip().encode("ascii", "replace").decode("ascii")
            print(f"{idx+1}: {safe}")

