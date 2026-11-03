# -*- coding: utf-8 -*-
import sys, os, sqlite3, tempfile
from datetime import datetime

sys.path.insert(0, os.getcwd())
import Institute_Ledger

print("Testing SchoolApp methods...")
temp_dir = tempfile.mkdtemp()
db_file = os.path.join(temp_dir, "test.db")
db = Institute_Ledger.SchoolDB(db_file)

# Test teacher slots
db.conn.execute("INSERT INTO teachers(full_name, status) VALUES('Qari Ahmad', 'Active')")
tid = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

db.conn.execute("INSERT INTO students(full_name, status) VALUES('Zaid Khan', 'Active')")
sid = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

db.conn.execute("INSERT INTO weekly_class_schedule(student_id, teacher_id, weekday, start_time, end_time, created_at) VALUES(?,?,?,?,?,?)",
                (sid, tid, "Monday", "04:00 PM", "04:45 PM", "2026-11-03 12:00:00"))
db.conn.commit()

class DummyApp:
    def __init__(self, db):
        self.db = db
        self.brand_name = "Taha Quran Institute"
        self.brand_name_ur = "طہٰ قران انسٹی ٹیوٹ"
        self.logo_path = ""
        self.theme_mode = "light"
        
    _get_teacher_slots = Institute_Ledger.SchoolApp.__dict__.get("_get_teacher_slots")
    _calculate_end_time = lambda self, s, d=45: "04:45 PM"

print("Class created successfully")

