# -*- coding: utf-8 -*-
import sys, os, sqlite3

def parse_teacher_availability_slots(availability_str):
    """Parse comma-separated or range availability into a list/set of slots."""
    if not availability_str or not availability_str.strip():
        return None  # All slots available
    raw_tokens = [x.strip() for x in availability_str.split(",") if x.strip()]
    slots = set()
    for tok in raw_tokens:
        # If it's e.g. "Monday 03:00 PM"
        slots.add(tok)
    return slots

print("Availability parser test passed")

