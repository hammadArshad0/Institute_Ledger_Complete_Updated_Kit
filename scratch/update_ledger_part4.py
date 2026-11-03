# -*- coding: utf-8 -*-
import sys, os

def get_enhanced_assign_students():
    return '''    def assign_students(self):
        """Interactive teacher-student assignment dialog with live free-slot picker."""
        teachers = self.db.conn.execute("SELECT id, full_name, availability FROM teachers WHERE status='Active' ORDER BY full_name").fetchall()
        if not teachers:
            teachers = self.db.conn.execute("SELECT id, full_name, availability FROM teachers ORDER BY full_name").fetchall()
        students = self.db.conn.execute("SELECT id, full_name, class_time, course FROM students WHERE status='Active' ORDER BY full_name").fetchall()
        if not students:
            students = self.db.conn.execute("SELECT id, full_name, class_time, course FROM students ORDER BY full_name").fetchall()
        if not teachers or not students:
            messagebox.showwarning("Records needed / ریکارڈ درکار ہے", "Add at least one teacher and one student first.", parent=self.root)
            return

        win = tk.Toplevel(self.root)
        win.title("Assign Teacher & Class Slot / استاد اور وقت متعین کریں")
        win.geometry("820x600")
        win.minsize(700, 480)
        win.configure(bg=CARD_BG)
        win.transient(self.root)
        win.grab_set()

        body = ttk.Frame(win, padding=16)
        body.pack(fill="both", expand=True)

        smart_label(ttk.Label, body, text="Assign Student to Teacher & Reserve Slot", style="Title.TLabel").pack(anchor="w")
        smart_label(ttk.Label, body, text="Select teacher and student, then choose an available weekly slot. This assigns the student, sets their class time, and updates the weekly timetable in one step.", style="Sub.TLabel", wraplength=760).pack(anchor="w", pady=(2, 10))

        top_grid = ttk.Frame(body)
        top_grid.pack(fill="x", pady=(0, 10))

        smart_label(ttk.Label, top_grid, text="Teacher / استاد").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        teacher_box = ttk.Combobox(top_grid, state="readonly", width=34,
                                   values=[f"{r['id']} - {r['full_name']}" for r in teachers])
        teacher_box.grid(row=0, column=1, sticky="w", padx=6, pady=4)
        teacher_box.current(0)

        smart_label(ttk.Label, top_grid, text="Student / طالب علم").grid(row=0, column=2, sticky="w", padx=(16, 6), pady=4)
        student_box = ttk.Combobox(top_grid, state="readonly", width=34,
                                   values=[f"{r['id']} - {r['full_name']}" for r in students])
        student_box.grid(row=0, column=3, sticky="w", padx=6, pady=4)
        student_box.current(0)

        tree_frame = ttk.Frame(body)
        tree_frame.pack(fill="both", expand=True, pady=6)
        cols = ("slot", "status", "booked_by")
        stree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=13)
        stree.heading("slot", text="Day and Time Slot / دن اور وقت")
        stree.heading("status", text="Availability / صورتحال")
        stree.heading("booked_by", text="Booked By / متعین طالب علم")
        stree.column("slot", width=220)
        stree.column("status", width=140)
        stree.column("booked_by", width=240)
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=stree.yview)
        stree.configure(yscrollcommand=sb.set)
        stree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        stree.tag_configure("available", foreground="#0F7457")
        stree.tag_configure("current", foreground="#1D4ED8")
        stree.tag_configure("booked", foreground="#B42318")
        stree.tag_configure("off", foreground="#6B7280")

        only_free_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(body, text="Show only available free slots / صرف خالی اوقات دکھائیں",
                        variable=only_free_var, command=lambda: refresh_slots()).pack(anchor="w", pady=(2, 6))

        def refresh_slots(_e=None):
            stree.delete(*stree.get_children())
            try:
                tid = int(teacher_box.get().split(" - ", 1)[0])
                sid = int(student_box.get().split(" - ", 1)[0])
            except (ValueError, IndexError):
                return
            all_slots = self._get_teacher_slots(tid, sid)
            only_free = only_free_var.get()
            for s in all_slots:
                status = s["status"]
                if only_free and status != "AVAILABLE" and status != "CURRENT SLOT":
                    continue
                tag = "available" if status == "AVAILABLE" else ("current" if status == "CURRENT SLOT" else ("booked" if status == "BOOKED" else "off"))
                stree.insert("", "end", values=(s["slot"], status, s["booked_by"]), tags=(tag,))

        teacher_box.bind("<<ComboboxSelected>>", refresh_slots)
        student_box.bind("<<ComboboxSelected>>", refresh_slots)
        refresh_slots()

        def save_assignment():
            selected = stree.selection()
            if not selected:
                messagebox.showwarning("Select Slot / وقت چنیں", "Please select a time slot from the list.", parent=win)
                return
            vals = stree.item(selected[0], "values")
            slot, status, booked_by = vals[0], vals[1], vals[2]
            if status not in ("AVAILABLE", "CURRENT SLOT"):
                messagebox.showwarning("Slot Not Available / وقت دستیاب نہیں", f"This slot is {status} ({booked_by}). Please choose an available green slot.", parent=win)
                return
            try:
                tid = int(teacher_box.get().split(" - ", 1)[0])
                sid = int(student_box.get().split(" - ", 1)[0])
            except (ValueError, IndexError):
                return
            parts = slot.split(" ", 1)
            day = parts[0]
            start = parts[1] if len(parts) > 1 else ""
            end = self._calculate_end_time(start, 45)

            try:
                self.db.conn.execute("UPDATE students SET class_time=? WHERE id=?", (slot, sid))
                self.db.conn.execute("INSERT OR IGNORE INTO teacher_students(teacher_id, student_id) VALUES(?,?)", (tid, sid))
                self.db.conn.execute("DELETE FROM weekly_class_schedule WHERE student_id=? AND weekday=?", (sid, day))
                self.db.conn.execute("INSERT INTO weekly_class_schedule(student_id, teacher_id, weekday, start_time, end_time, created_at) VALUES(?,?,?,?,?,?)",
                                     (sid, tid, day, start, end, timestamp()))
                self.db.conn.commit()
                messagebox.showinfo("Assigned Successfully / کامیابی سے تفویض", f"Student assigned to teacher.\\nSlot: {slot}\\nWeekly timetable and class schedule updated.", parent=win)
                win.destroy()
            except Exception as exc:
                messagebox.showerror("Assignment Error", str(exc), parent=win)

        btn_row = ttk.Frame(body)
        btn_row.pack(fill="x", pady=(8, 0))
        ttk.Button(btn_row, text="💾 Assign Slot & Update Timetable / تفویض اور محفوظ کریں",
                   style="Accent.TButton", command=save_assignment).pack(side="left")
        ttk.Button(btn_row, text="Close / بند کریں", command=win.destroy).pack(side="right")'''

def main():
    with open("Institute_Ledger.py", "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Replace assign_students
    old_assign = '''    def assign_students(self):
        teachers = self.db.conn.execute("SELECT id,full_name FROM teachers ORDER BY full_name").fetchall()
        students = self.db.conn.execute("SELECT id,full_name FROM students ORDER BY full_name").fetchall()
        if not teachers or not students:
            messagebox.showwarning("Records needed", "Add at least one teacher and one student first.")
            return
        teacher_opts = [f"{r['id']} - {r['full_name']}" for r in teachers]
        student_opts = [f"{r['id']} - {r['full_name']}" for r in students]
        fields = [("teacher","Teacher",teacher_opts[0]),("student","Student",student_opts[0])]
        def save(v, win):
            tid = int(v["teacher"].split(" - ",1)[0])
            sid = int(v["student"].split(" - ",1)[0])
            try:
                self.db.conn.execute("INSERT INTO teacher_students(teacher_id,student_id) VALUES(?,?)",(tid,sid))
                self.db.conn.commit()
                messagebox.showinfo("Assigned","Student assigned to teacher.",parent=win)
                return True
            except sqlite3.IntegrityError:
                messagebox.showwarning("Already assigned","This student is already assigned to that teacher.",parent=win)
                return False
        self.form_dialog("Assign Student to Teacher", fields, save, {"teacher":teacher_opts,"student":student_opts})'''

    new_assign = get_enhanced_assign_students()
    assert old_assign in code, "old_assign not found"
    code = code.replace(old_assign, new_assign, 1)
    print("Replaced assign_students with interactive slot picker.")

    # 2. Update allocate_class_time to write to weekly_class_schedule
    old_alloc_save = '''            self.db.conn.execute("UPDATE students SET class_time=? WHERE id=?", (slot, sid))
            self.db.conn.execute("INSERT OR IGNORE INTO teacher_students(teacher_id,student_id) VALUES(?,?)", (tid, sid))
            self.db.conn.commit()
            messagebox.showinfo("Saved", f"Class time saved: {slot}", parent=win)'''

    new_alloc_save = '''            parts = slot.split(" ", 1)
            day = parts[0]
            start = parts[1] if len(parts) > 1 else ""
            end = self._calculate_end_time(start, 45)
            self.db.conn.execute("UPDATE students SET class_time=? WHERE id=?", (slot, sid))
            self.db.conn.execute("INSERT OR IGNORE INTO teacher_students(teacher_id,student_id) VALUES(?,?)", (tid, sid))
            try:
                self.db.conn.execute("DELETE FROM weekly_class_schedule WHERE student_id=? AND weekday=?", (sid, day))
                self.db.conn.execute("INSERT INTO weekly_class_schedule(student_id,teacher_id,weekday,start_time,end_time,created_at) VALUES(?,?,?,?,?,?)",
                                     (sid, tid, day, start, end, timestamp()))
            except Exception:
                pass
            self.db.conn.commit()
            messagebox.showinfo("Saved", f"Class time saved: {slot}\\nWeekly timetable schedule updated.", parent=win)'''

    assert old_alloc_save in code, "old_alloc_save not found"
    code = code.replace(old_alloc_save, new_alloc_save, 1)
    print("Updated allocate_class_time to sync with weekly_class_schedule.")

    # 3. Update add_student to offer immediate teacher & slot assignment
    old_add_student_save = '''            self.db.conn.execute("""INSERT INTO students(full_name,guardian_name,phone,course,monthly_fee,currency,status,age,class_time,level,admission_date,email)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (v["full_name"],v["guardian_name"],v["phone"],v["course"],fee,v["currency"],v["status"],age,v["class_time"],v["level"],v["admission_date"],v["email"]))
            self.db.conn.commit()
            messagebox.showinfo("Saved", "Student profile saved.", parent=win)
            return True'''

    new_add_student_save = '''            self.db.conn.execute("""INSERT INTO students(full_name,guardian_name,phone,course,monthly_fee,currency,status,age,class_time,level,admission_date,email)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (v["full_name"],v["guardian_name"],v["phone"],v["course"],fee,v["currency"],v["status"],age,v["class_time"],v["level"],v["admission_date"],v["email"]))
            self.db.conn.commit()
            messagebox.showinfo("Saved", "Student profile saved.", parent=win)
            if messagebox.askyesno("Assign Slot?", "Would you like to assign a teacher and timetable slot for this student now?", parent=win):
                self.root.after(100, lambda: self.assign_students())
            return True'''

    assert old_add_student_save in code, "old_add_student_save not found"
    code = code.replace(old_add_student_save, new_add_student_save, 1)
    print("Updated add_student to offer immediate slot assignment.")

    with open("Institute_Ledger.py", "w", encoding="utf-8") as f:
        f.write(code)

    print("Successfully applied part 4.")

if __name__ == "__main__":
    main()

