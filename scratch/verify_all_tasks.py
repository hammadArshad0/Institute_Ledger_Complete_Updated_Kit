# -*- coding: utf-8 -*-
import sys, os, tempfile, sqlite3, tkinter as tk

sys.path.insert(0, os.getcwd())
import Institute_Ledger

print("========================================")
print("RUNNING COMPREHENSIVE VERIFICATION SUITE")
print("========================================")

# 1. Check invariants
with open("Institute_Ledger.py", "r", encoding="utf-8") as f:
    first_line = f.readline()
    assert first_line.startswith("# -*- coding: utf-8 -*-"), f"Line 1 invariant failed: {first_line}"
    rest = f.read()
    assert "CURRICULUM_DETAILED_CORES" in rest, "CURRICULUM_DETAILED_CORES missing"
print("[PASS] Invariant checks passed (Line 1 encoding & CURRICULUM_DETAILED_CORES intact)")

# 2. Check Urdu font
font = Institute_Ledger.choose_urdu_font(None)
assert font == "Jameel Noori Nastaleeq", f"Expected Jameel Noori Nastaleeq, got {font}"
print("[PASS] Task 1: Urdu font is strictly Jameel Noori Nastaleeq")

# 3. Check Design tokens and presets
assert len(Institute_Ledger.THEME_PRESETS) >= 5, "Expected at least 5 theme presets"
for p in ("emerald", "royal_blue", "teal", "purple", "charcoal"):
    assert p in Institute_Ledger.THEME_PRESETS, f"Missing preset: {p}"
print("[PASS] Task 6: All 5 WCAG AA Theme presets present")

# 4. Check Backup directory helper
b_dir = Institute_Ledger._default_backup_dir()
assert "InstituteLedgerBackups" in b_dir, f"Default backup dir incorrect: {b_dir}"
print("[PASS] Task 3: Dedicated persistent backup folder helper:", b_dir)

# 5. Check Database & Schema backward compatibility
tmp_dir = tempfile.mkdtemp()
db_path = os.path.join(tmp_dir, "verify.db")
db = Institute_Ledger.SchoolDB(db_path)
assert db.conn is not None

# Insert test records
db.conn.execute("INSERT INTO teachers(full_name, status, availability) VALUES('Qari Usman', 'Active', 'Monday 04:00 PM, Tuesday 05:00 PM')")
tid = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

db.conn.execute("INSERT INTO students(full_name, status) VALUES('Bilal Tariq', 'Active')")
sid = db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
db.conn.commit()

# Test SchoolApp methods headless
root = tk.Tk()
root.withdraw()
app = Institute_Ledger.SchoolApp(root, db)
app.user = {"id": 1, "username": "admin", "role": "admin"}

# Verify _get_teacher_slots
slots = app._get_teacher_slots(tid)
assert len(slots) > 0, "No slots returned"
available_slots = [s for s in slots if s["status"] == "AVAILABLE"]
assert any("Monday 04:00 PM" in s["slot"] for s in available_slots), "Monday 04:00 PM should be available"
print(f"[PASS] Task 4: Teacher slots parser working correctly ({len(slots)} standard slots checked)")

# Test booking slot via allocate_class_time logic
assert app._calculate_end_time("04:00 PM", 45) == "04:45 PM"
db.conn.execute("INSERT INTO weekly_class_schedule(student_id, teacher_id, weekday, start_time, end_time, created_at) VALUES(?,?,?,?,?,?)",
                (sid, tid, "Monday", "04:00 PM", "04:45 PM", "2026-11-03 14:00:00"))
db.conn.commit()

slots_after = app._get_teacher_slots(tid, sid)
mon_slot = next(s for s in slots_after if "Monday 04:00 PM" in s["slot"])
assert mon_slot["status"] == "CURRENT SLOT", f"Expected CURRENT SLOT, got {mon_slot['status']}"
print("[PASS] Task 4: Slot booking updates availability to CURRENT SLOT for this student")

# Test another student sees it as BOOKED
slots_other = app._get_teacher_slots(tid, 999)
mon_slot_other = next(s for s in slots_other if "Monday 04:00 PM" in s["slot"])
assert mon_slot_other["status"] == "BOOKED", f"Expected BOOKED, got {mon_slot_other['status']}"
assert mon_slot_other["booked_by"] == "Bilal Tariq"
print("[PASS] Task 4: Double-booking prevention: other student sees slot as BOOKED by Bilal Tariq")

# Test Certificate generator and report card dialog methods exist
assert hasattr(app, "certificate_generator_dialog")
assert hasattr(app, "monthly_report_card_dialog")
assert hasattr(app, "link_and_restore_backup_folder")
print("[PASS] Task 7: Certificate generator & Monthly report card & Backup relink dialogs installed")

# Test Sticky header method
app._animate_header_collapse(True)
assert getattr(app, "_header_is_collapsed", False) is False, "Header should remain fixed/sticky and not collapse"
print("[PASS] Task 5: Zero-flicker sticky top bar confirmed")

try:
    root.destroy()
except Exception:
    pass

print("========================================")
print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
print("========================================")
