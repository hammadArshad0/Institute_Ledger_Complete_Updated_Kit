# -*- coding: utf-8 -*-
"""
Updater script to implement Phase C, D, E, F, G into Institute_Ledger.py
without modifying line 1 or line 1688 (CURRICULUM_DETAILED_CORES).
"""
import sys, os, re

def main():
    with open("Institute_Ledger.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Check invariant lines
    first_line = content.splitlines()[0]
    assert first_line.startswith("# -*- coding: utf-8 -*-"), f"First line changed: {first_line}"
    assert "CURRICULUM_DETAILED_CORES" in content, "CURRICULUM_DETAILED_CORES missing"

    # Backup before modifying
    with open("Institute_Ledger.py.bak_phase3_pre", "w", encoding="utf-8") as f:
        f.write(content)

    print("Backup created. Beginning updates...")

if __name__ == "__main__":
    main()

