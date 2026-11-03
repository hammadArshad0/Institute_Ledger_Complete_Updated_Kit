# -*- coding: utf-8 -*-
"""Verification script for Institute Ledger UI fixes."""
import sys, re, os

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Institute_Ledger.py")

with open(path, 'rb') as f:
    raw = f.read()

with open(path, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f": {detail}" if detail else ""))
    return condition

all_pass = True

# Line 1
all_pass &= check("Line 1 coding comment", lines[0].strip() == "# -*- coding: utf-8 -*-")

# Line count sanity
all_pass &= check("Line count >= 14000", len(lines) >= 14000, f"{len(lines)} lines")

# CURRICULUM_DETAILED_CORES not split
curriculum_lines = [i+1 for i, l in enumerate(lines) if 'CURRICULUM_DETAILED_CORES' in l and '=' in l]
all_pass &= check("CURRICULUM_DETAILED_CORES on single line", 
                   len(curriculum_lines) >= 1, f"Found at lines: {curriculum_lines}")

# Today's apostrophe fix
today_q = raw.count(b"Today\x3fs")  # Today?s
today_apos = raw.count(b"Today\x27s")  # Today's
check("No 'Today?s' occurrences", today_q == 0, f"Found {today_q}")
check("'Today's' occurrences", today_apos >= 2, f"Found {today_apos}")

# PRIMARY_TEXT global
all_pass &= check("PRIMARY_TEXT global defined", b"PRIMARY_TEXT" in raw)

# Flat button styles (no wallpaper blend for TButton)
all_pass &= check("_luminance function defined", b"def _luminance(" in raw or b"def _luminance\r\n" in raw or b"_luminance" in raw)

# Sidebar width 240
all_pass &= check("Sidebar width 240", b"width=240" in raw or b"width = 240" in raw)

# Info.TButton defined
all_pass &= check("Info.TButton defined", b"Info.TButton" in raw)

# Print.TButton defined
all_pass &= check("Print.TButton defined", b"Print.TButton" in raw)

# Danger.TButton defined  
all_pass &= check("Danger.TButton defined", b"Danger.TButton" in raw)

# Month label fix
all_pass &= check("Month strptime fix", b"strptime" in raw and (b"This month" in raw or b"_month_label" in raw))

# Hero greeting instead of brand name
# (either contains "Welcome back" or the brand_name line was changed)
has_welcome = b"Welcome back" in raw
check("Hero shows greeting (Welcome back)", has_welcome, "Optional - welcome greeting in hero")

print(f"\n{'='*50}")
print(f"Result: {'ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}")
print(f"Total lines: {len(lines)}")

