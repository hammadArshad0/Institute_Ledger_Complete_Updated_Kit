# -*- coding: utf-8 -*-
import sys, os

def get_new_methods():
    return '''
    def _calculate_end_time(self, start_str, duration_mins=45):
        try:
            t = datetime.strptime(str(start_str).strip(), "%I:%M %p")
            total = t.hour * 60 + t.minute + duration_mins
            h = (total // 60) % 24
            m = total % 60
            ampm = "AM" if h < 12 else "PM"
            h12 = h % 12 or 12
            return f"{h12:02d}:{m:02d} {ampm}"
        except Exception:
            return start_str

    def _get_teacher_slots(self, teacher_id, student_id=None):
        """Return all weekly slots for a teacher with status: AVAILABLE, BOOKED, or CURRENT SLOT."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        std_slots = []
        for d in days:
            for h in range(8, 22):
                for minute in (0, 30):
                    h12 = h % 12 or 12
                    ampm = "AM" if h < 12 else "PM"
                    std_slots.append(f"{d} {h12:02d}:{minute:02d} {ampm}")

        teacher = self.db.conn.execute("SELECT availability FROM teachers WHERE id=?", (teacher_id,)).fetchone()
        avail_str = (teacher["availability"] or "").strip() if teacher else ""
        avail_set = {x.strip() for x in avail_str.split(",") if x.strip()} if avail_str else set()

        sched_rows = self.db.conn.execute(
            "SELECT w.weekday, w.start_time, w.student_id, s.full_name "
            "FROM weekly_class_schedule w JOIN students s ON s.id=w.student_id "
            "WHERE w.teacher_id=?", (teacher_id,)).fetchall()
        booked = {}
        for r in sched_rows:
            slot_key = f"{r['weekday']} {r['start_time']}".strip()
            booked[slot_key] = {"sid": r["student_id"], "name": r["full_name"]}

        stu_rows = self.db.conn.execute(
            "SELECT s.id, s.full_name, s.class_time FROM students s "
            "JOIN teacher_students ts ON ts.student_id=s.id "
            "WHERE ts.teacher_id=? AND s.status='Active' AND COALESCE(s.class_time,'')<>''",
            (teacher_id,)).fetchall()
        for r in stu_rows:
            c_time = str(r["class_time"] or "").strip()
            if c_time and c_time not in booked:
                booked[c_time] = {"sid": r["id"], "name": r["full_name"]}

        has_explicit_avail = bool(avail_set and any(any(x.startswith(d) for d in days) for x in avail_set))

        results = []
        for slot in std_slots:
            booked_info = booked.get(slot)
            if booked_info:
                if student_id and booked_info["sid"] == student_id:
                    status = "CURRENT SLOT"
                    name = booked_info["name"]
                else:
                    status = "BOOKED"
                    name = booked_info["name"]
            elif has_explicit_avail and slot not in avail_set:
                status = "NOT IN AVAILABILITY"
                name = "—"
            else:
                status = "AVAILABLE"
                name = "—"
            results.append({
                "slot": slot,
                "status": status,
                "booked_by": name,
                "is_current": status == "CURRENT SLOT",
                "is_available": status in ("AVAILABLE", "CURRENT SLOT")
            })
        return results

    def certificate_generator_dialog(self, student_id=None):
        """Generate high-resolution printable Hifz/Nazra completion certificates with institute branding."""
        students = self.db.conn.execute("SELECT id, full_name, guardian_name, course FROM students ORDER BY full_name").fetchall()
        teachers = self.db.conn.execute("SELECT id, full_name FROM teachers ORDER BY full_name").fetchall()
        if not students:
            messagebox.showwarning("Records Needed", "No student records found.", parent=self.root)
            return

        win = tk.Toplevel(self.root)
        win.title("Certificate Generator / تکمیلِ حفظ و ناظرہ سند")
        win.geometry("640x520")
        win.configure(bg=CARD_BG)
        win.transient(self.root)
        win.grab_set()

        body = ttk.Frame(win, padding=16)
        body.pack(fill="both", expand=True)
        smart_label(ttk.Label, body, text="Generate Completion Certificate / سند تکمیل", style="Title.TLabel").pack(anchor="w")
        smart_label(ttk.Label, body, text="Generate an elegant, printable completion certificate with institute branding, student details, and official signature lines.", style="Sub.TLabel", wraplength=580).pack(anchor="w", pady=(2, 12))

        form = ttk.Frame(body)
        form.pack(fill="x", pady=4)

        smart_label(ttk.Label, form, text="Student / طالب علم").grid(row=0, column=0, sticky="w", padx=6, pady=5)
        student_opts = [f"{r['id']} - {r['full_name']}" for r in students]
        student_var = tk.StringVar(value=student_opts[0])
        if student_id:
            for opt in student_opts:
                if opt.startswith(f"{student_id} -"):
                    student_var.set(opt)
                    break
        ttk.Combobox(form, textvariable=student_var, values=student_opts, state="readonly", width=34).grid(row=0, column=1, sticky="w", padx=6, pady=5)

        smart_label(ttk.Label, form, text="Course / کورس").grid(row=1, column=0, sticky="w", padx=6, pady=5)
        course_opts = ["Hifz-ul-Quran / حفظ القرآن الكريم", "Nazra Quran / ناظرہ قرآن مجید", "Tajweed-ul-Quran / تجوید القرآن", "Islamic Studies / دینیات", "Custom Course"]
        course_var = tk.StringVar(value=course_opts[0])
        ttk.Combobox(form, textvariable=course_var, values=course_opts, state="normal", width=34).grid(row=1, column=1, sticky="w", padx=6, pady=5)

        smart_label(ttk.Label, form, text="Completion Date (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", padx=6, pady=5)
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(form, textvariable=date_var, width=34).grid(row=2, column=1, sticky="w", padx=6, pady=5)

        smart_label(ttk.Label, form, text="Grade / Distinction / درجہ").grid(row=3, column=0, sticky="w", padx=6, pady=5)
        grade_opts = ["Mumtaz (Distinction) / ممتاز", "Jayyid Jiddan (Very Good) / جید جداً", "Jayyid (Good) / جید", "Maqbool (Passed) / مقبول"]
        grade_var = tk.StringVar(value=grade_opts[0])
        ttk.Combobox(form, textvariable=grade_var, values=grade_opts, state="normal", width=34).grid(row=3, column=1, sticky="w", padx=6, pady=5)

        smart_label(ttk.Label, form, text="Teacher / نگران استاد").grid(row=4, column=0, sticky="w", padx=6, pady=5)
        teacher_opts = [r["full_name"] for r in teachers] or ["Principal / مدیر"]
        teacher_var = tk.StringVar(value=teacher_opts[0])
        ttk.Combobox(form, textvariable=teacher_var, values=teacher_opts, state="normal", width=34).grid(row=4, column=1, sticky="w", padx=6, pady=5)

        def generate_html_cert():
            try:
                sid = int(student_var.get().split(" - ", 1)[0])
            except Exception:
                sid = students[0]["id"]
            stu_row = self.db.conn.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
            stu_name = stu_row["full_name"] if stu_row else "Student Name"
            guardian = stu_row["guardian_name"] if (stu_row and stu_row["guardian_name"]) else "Parent / Guardian"
            course_title = course_var.get()
            comp_date = date_var.get()
            grade_val = grade_var.get()
            t_name = teacher_var.get()

            import base64
            logo_img_tag = ""
            if self.logo_path and os.path.isfile(self.logo_path):
                try:
                    with open(self.logo_path, "rb") as lf:
                        b64_logo = base64.b64encode(lf.read()).decode("ascii")
                        logo_img_tag = f'<img src="data:image/png;base64,{b64_logo}" style="width:90px;height:90px;border-radius:50%;border:3px solid #0F5132;margin-bottom:10px;">'
                except Exception:
                    logo_img_tag = ""

            slogan_disp = self._brand_slogan() or ""

            html = f"""<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<title>Completion Certificate - {stu_name}</title>
<style>
@page {{ size: landscape; margin: 15mm; }}
body {{ font-family: 'Jameel Noori Nastaleeq', 'Segoe UI', Tahoma, Arial, sans-serif; background: #FAF9F6; margin: 0; padding: 20px; text-align: center; color: #1A3026; }}
.cert-border {{ border: 12px double #0F5132; padding: 25px; background: #FFFFFF; box-shadow: 0 0 20px rgba(0,0,0,0.1); max-width: 950px; margin: 0 auto; position: relative; }}
.inner-border {{ border: 2px solid #D4AF37; padding: 30px; position: relative; }}
.bismillah {{ font-size: 26px; color: #0F5132; margin-bottom: 8px; font-weight: bold; }}
.inst-title {{ font-size: 28px; font-weight: bold; color: #0F5132; margin: 4px 0; }}
.inst-subtitle {{ font-size: 16px; color: #5D736A; margin-bottom: 12px; }}
.cert-header {{ font-size: 32px; font-weight: bold; color: #D4AF37; text-transform: uppercase; margin: 15px 0 20px 0; letter-spacing: 2px; text-shadow: 1px 1px 1px #8C7320; }}
.cert-body {{ font-size: 18px; line-height: 2.2; margin: 20px 40px; text-align: center; }}
.stu-name {{ font-size: 26px; font-weight: bold; color: #0F5132; border-bottom: 2px dashed #0F5132; display: inline-block; padding: 0 20px; }}
.signatures {{ display: flex; justify-content: space-between; margin-top: 50px; padding: 0 50px; }}
.sig-block {{ width: 220px; text-align: center; border-top: 1px solid #1A3026; padding-top: 8px; font-size: 16px; }}
.print-btn {{ margin-top: 25px; padding: 10px 24px; background: #0F5132; color: #FFF; border: none; font-size: 16px; border-radius: 6px; cursor: pointer; }}
@media print {{ .print-btn {{ display: none; }} body {{ background: #FFF; padding: 0; }} .cert-border {{ box-shadow: none; border: 8px double #0F5132; }} }}
</style>
</head>
<body>
<div class="cert-border">
  <div class="inner-border">
    {logo_img_tag}
    <div class="bismillah">بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>
    <div class="inst-title">{self.brand_name_ur} / {self.brand_name}</div>
    <div class="inst-subtitle">{slogan_disp}</div>
    <div class="cert-header">شهادة إتمام وتقدير / Completion Certificate</div>
    <div class="cert-body">
      تشهد إدارة المعهد بأن الطالب / طالب علم <span class="stu-name">{stu_name}</span> ولد / ولدیت <span style="font-weight:bold;">{guardian}</span><br>
      قد أتم بنجاح دراسة منهج <strong>{course_title}</strong> بتقدير <strong>{grade_val}</strong><br>
      بتاريخ <strong>{comp_date}</strong>. نسأل الله له التوفيق والثبات والعمل بكتابه العزيز.
    </div>
    <div class="signatures">
      <div class="sig-block">نگران استاد / Teacher<br><strong>{t_name}</strong></div>
      <div class="sig-block">مہر ادارہ / Seal</div>
      <div class="sig-block">مہتمم و مدیر / Principal<br><strong>{self.brand_name}</strong></div>
    </div>
  </div>
</div>
<button class="print-btn" onclick="window.print()">🖨️ Print Certificate / سند پرنٹ کریں</button>
</body>
</html>"""
            tmp_path = os.path.join(tempfile.gettempdir(), f"certificate_{sid}.html")
            with open(tmp_path, "w", encoding="utf-8") as hf:
                hf.write(html)
            self.open_folder(tmp_path) if hasattr(os, "startfile") else None
            try:
                import webbrowser
                webbrowser.open("file://" + os.path.abspath(tmp_path))
            except Exception:
                pass
            messagebox.showinfo("Certificate Generated", f"Certificate generated and opened in browser:\n{tmp_path}\nUse Print (Ctrl+P) to print or save as PDF.", parent=win)
            win.destroy()

        btn_row = ttk.Frame(body)
        btn_row.pack(fill="x", pady=(14, 0))
        ttk.Button(btn_row, text="🖨️ Generate & Preview / سند تیار کریں", style="Accent.TButton", command=generate_html_cert).pack(side="left")
        ttk.Button(btn_row, text="Close / بند کریں", command=win.destroy).pack(side="right")

    def monthly_report_card_dialog(self, student_id=None):
        """Generate formatted printable student progress and sabaq report card."""
        students = self.db.conn.execute("SELECT id, full_name, course FROM students ORDER BY full_name").fetchall()
        if not students:
            messagebox.showwarning("Records Needed", "No student records found.", parent=self.root)
            return

        win = tk.Toplevel(self.root)
        win.title("Monthly Progress Report Card / ماہانہ تعلیمی رپورٹ کارڈ")
        win.geometry("640x500")
        win.configure(bg=CARD_BG)
        win.transient(self.root)
        win.grab_set()

        body = ttk.Frame(win, padding=16)
        body.pack(fill="both", expand=True)
        smart_label(ttk.Label, body, text="Monthly Student Progress Card", style="Title.TLabel").pack(anchor="w")
        smart_label(ttk.Label, body, text="Generate a detailed report card covering daily sabaq, revision, attendance, and teacher remarks.", style="Sub.TLabel", wraplength=580).pack(anchor="w", pady=(2, 10))

        form = ttk.Frame(body)
        form.pack(fill="x", pady=4)

        smart_label(ttk.Label, form, text="Student / طالب علم").grid(row=0, column=0, sticky="w", padx=6, pady=5)
        student_opts = [f"{r['id']} - {r['full_name']}" for r in students]
        student_var = tk.StringVar(value=student_opts[0])
        ttk.Combobox(form, textvariable=student_var, values=student_opts, state="readonly", width=34).grid(row=0, column=1, sticky="w", padx=6, pady=5)

        smart_label(ttk.Label, form, text="Month / مہینہ (YYYY-MM)").grid(row=1, column=0, sticky="w", padx=6, pady=5)
        month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        ttk.Entry(form, textvariable=month_var, width=34).grid(row=1, column=1, sticky="w", padx=6, pady=5)

        smart_label(ttk.Label, form, text="Sabaq (New Lesson) Score / سبق").grid(row=2, column=0, sticky="w", padx=6, pady=5)
        sabaq_var = tk.StringVar(value="Excellent / ممتاز")
        ttk.Entry(form, textvariable=sabaq_var, width=34).grid(row=2, column=1, sticky="w", padx=6, pady=5)

        smart_label(ttk.Label, form, text="Sabqi (Recent Revision) / سبقی").grid(row=3, column=0, sticky="w", padx=6, pady=5)
        sabqi_var = tk.StringVar(value="Good / جید")
        ttk.Entry(form, textvariable=sabqi_var, width=34).grid(row=3, column=1, sticky="w", padx=6, pady=5)

        smart_label(ttk.Label, form, text="Manzil (Old Revision) / منزل").grid(row=4, column=0, sticky="w", padx=6, pady=5)
        manzil_var = tk.StringVar(value="Regular / باقاعدہ")
        ttk.Entry(form, textvariable=manzil_var, width=34).grid(row=4, column=1, sticky="w", padx=6, pady=5)

        smart_label(ttk.Label, form, text="Teacher Remarks / تبصرہ").grid(row=5, column=0, sticky="w", padx=6, pady=5)
        remarks_var = tk.StringVar(value="ماشاء اللہ! محنتی طالب علم ہیں۔ روزانہ باقاعدگی سے پڑھتے ہیں۔")
        ttk.Entry(form, textvariable=remarks_var, width=34).grid(row=5, column=1, sticky="w", padx=6, pady=5)

        def print_report():
            try: sid = int(student_var.get().split(" - ", 1)[0])
            except Exception: sid = students[0]["id"]
            stu_row = self.db.conn.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
            stu_name = stu_row["full_name"] if stu_row else "Student"
            course_name = stu_row["course"] if stu_row else "Quran"
            month = month_var.get()

            # Calculate attendance stats for this month
            att_rows = self.db.conn.execute("SELECT status FROM attendance WHERE student_id=? AND class_date LIKE ?", (sid, f"{month}%")).fetchall()
            total_days = len(att_rows)
            present_days = sum(1 for r in att_rows if str(r["status"]).lower().startswith("present"))
            att_pct = f"{int(present_days*100/total_days)}%" if total_days else "100%"

            html = f"""<!DOCTYPE html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<title>Progress Report - {stu_name} - {month}</title>
<style>
body {{ font-family: 'Jameel Noori Nastaleeq', 'Segoe UI', Tahoma, sans-serif; background: #F8FAF8; padding: 25px; color: #132D23; }}
.card {{ background: #FFF; border: 2px solid #0F5132; max-width: 800px; margin: 0 auto; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-radius: 8px; }}
.header {{ text-align: center; border-bottom: 2px solid #D4AF37; padding-bottom: 15px; margin-bottom: 20px; }}
.inst-name {{ font-size: 26px; font-weight: bold; color: #0F5132; }}
.table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 16px; }}
.table th, .table td {{ border: 1px solid #DCE5E0; padding: 10px 14px; text-align: right; }}
.table th {{ background: #E8F4EE; color: #0F5132; font-weight: bold; }}
.print-btn {{ display: block; margin: 20px auto 0 auto; padding: 10px 24px; background: #0F5132; color: #FFF; border: none; font-size: 16px; border-radius: 6px; cursor: pointer; }}
@media print {{ .print-btn {{ display: none; }} body {{ padding: 0; background: #FFF; }} .card {{ box-shadow: none; }} }}
</style>
</head>
<body>
<div class="card">
  <div class="header">
    <div class="inst-name">{self.brand_name_ur} / {self.brand_name}</div>
    <div style="font-size:18px;color:#D4AF37;font-weight:bold;margin-top:5px;">ماہانہ تعلیمی کارکردگی رپورٹ کارڈ / Monthly Progress Report</div>
    <div style="font-size:14px;color:#5D736A;margin-top:4px;">مہینہ: {month}</div>
  </div>
  <table class="table">
    <tr><th>طالب علم کا نام / Student Name</th><td><strong>{stu_name}</strong></td><th>کورس / Course</th><td>{course_name}</td></tr>
    <tr><th>سبق کی کیفیت / Daily Lesson (Sabaq)</th><td colspan="3">{sabaq_var.get()}</td></tr>
    <tr><th>سبقی کی کیفیت / Recent Revision (Sabqi)</th><td colspan="3">{sabqi_var.get()}</td></tr>
    <tr><th>منزل کی کیفیت / Old Revision (Manzil)</th><td colspan="3">{manzil_var.get()}</td></tr>
    <tr><th>ماہانہ حاضری / Attendance</th><td colspan="3">{att_pct} ({present_days}/{total_days} دن حاضر)</td></tr>
    <tr><th>استاد کا تبصرہ / Teacher Remarks</th><td colspan="3" style="color:#0F5132;font-weight:bold;">{remarks_var.get()}</td></tr>
  </table>
  <div style="display:flex;justify-content:space-between;margin-top:40px;padding:0 30px;">
    <div>دستخط نگران استاد: _______________</div>
    <div>دستخط سرپرست: _______________</div>
    <div>مہر ادارہ: _______________</div>
  </div>
</div>
<button class="print-btn" onclick="window.print()">🖨️ Print Report Card / رپورٹ پرنٹ کریں</button>
</body>
</html>"""
            tmp_path = os.path.join(tempfile.gettempdir(), f"report_card_{sid}.html")
            with open(tmp_path, "w", encoding="utf-8") as hf:
                hf.write(html)
            try:
                import webbrowser
                webbrowser.open("file://" + os.path.abspath(tmp_path))
            except Exception:
                pass
            messagebox.showinfo("Report Card Generated", f"Progress report card generated:\n{tmp_path}", parent=win)
            win.destroy()

        btn_row = ttk.Frame(body)
        btn_row.pack(fill="x", pady=(14, 0))
        ttk.Button(btn_row, text="🖨️ Generate & Print / رپورٹ تیار کریں", style="Accent.TButton", command=print_report).pack(side="left")
        ttk.Button(btn_row, text="Close / بند کریں", command=win.destroy).pack(side="right")

    def link_and_restore_backup_folder(self, initial_folder=None):
        """Browse an existing backup folder, list verified backups with student/teacher/payment counts, and safely restore with pre-restore safety copy."""
        from pathlib import Path
        default_dir = _default_backup_dir()
        folder = initial_folder or filedialog.askdirectory(
            parent=self.root, title="Link Existing Backup Folder / پرانا بیک اپ فولڈر چنیں",
            initialdir=default_dir if os.path.isdir(default_dir) else os.path.dirname(os.path.abspath(self.db.path))
        )
        if not folder or not os.path.isdir(folder):
            return

        self._save_setting("backup_primary_folder", folder)

        win = tk.Toplevel(self.root)
        win.title("Link Backup Folder & Restore / بیک اپ فولڈر اور بحالی")
        win.geometry("920x560")
        win.minsize(780, 440)
        win.configure(bg=CARD_BG)
        win.transient(self.root)
        win.grab_set()

        body = ttk.Frame(win, padding=16)
        body.pack(fill="both", expand=True)

        smart_label(ttk.Label, body, text="Linked Backup Folder / منسلک شدہ بیک اپ فولڈر", style="Title.TLabel").pack(anchor="w")
        smart_label(ttk.Label, body, text=f"Folder: {folder}", style="Sub.TLabel").pack(anchor="w", pady=(2, 6))

        # Scan for backup files
        backup_files = []
        for root_dir, _, files in os.walk(folder):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in (".sqlite3", ".db", ".bak"):
                    full_p = os.path.join(root_dir, f)
                    try:
                        mtime = os.path.getmtime(full_p)
                        size_mb = os.path.getsize(full_p) / (1024 * 1024)
                        backup_files.append((mtime, full_p, size_mb))
                    except OSError:
                        pass
        backup_files.sort(key=lambda x: x[0], reverse=True)

        tree_frame = ttk.Frame(body)
        tree_frame.pack(fill="both", expand=True, pady=6)

        cols = ("date", "name", "size", "integrity", "students", "teachers", "payments")
        btree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12)
        btree.heading("date", text="Date / تاریخ")
        btree.heading("name", text="Filename / فائل کا نام")
        btree.heading("size", text="Size / حجم")
        btree.heading("integrity", text="Integrity / صحت")
        btree.heading("students", text="Students")
        btree.heading("teachers", text="Teachers")
        btree.heading("payments", text="Payments")

        btree.column("date", width=140)
        btree.column("name", width=220)
        btree.column("size", width=80, anchor="e")
        btree.column("integrity", width=90, anchor="center")
        btree.column("students", width=70, anchor="center")
        btree.column("teachers", width=70, anchor="center")
        btree.column("payments", width=80, anchor="center")

        bsb = ttk.Scrollbar(tree_frame, orient="vertical", command=btree.yview)
        btree.configure(yscrollcommand=bsb.set)
        btree.pack(side="left", fill="both", expand=True)
        bsb.pack(side="right", fill="y")

        file_map = {}
        for idx, (mtime, full_p, size_mb) in enumerate(backup_files):
            dt_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            fname = os.path.basename(full_p)
            integ = "Checking..."
            stu_cnt, tea_cnt, pay_cnt = "—", "—", "—"
            try:
                src = sqlite3.connect(Path(full_p).resolve().as_uri() + "?mode=ro", uri=True)
                check = src.execute("PRAGMA integrity_check").fetchone()[0]
                integ = "OK" if check == "ok" else "Damaged"
                if check == "ok":
                    tbls = {r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                    if "students" in tbls: stu_cnt = str(src.execute("SELECT COUNT(*) FROM students").fetchone()[0])
                    if "teachers" in tbls: tea_cnt = str(src.execute("SELECT COUNT(*) FROM teachers").fetchone()[0])
                    if "payments" in tbls: pay_cnt = str(src.execute("SELECT COUNT(*) FROM payments").fetchone()[0])
                src.close()
            except Exception:
                integ = "Unreadable"

            item_id = str(idx)
            file_map[item_id] = full_p
            btree.insert("", "end", iid=item_id, values=(dt_str, fname, f"{size_mb:.2f} MB", integ, stu_cnt, tea_cnt, pay_cnt))

        def restore_selected():
            sel = btree.selection()
            if not sel:
                messagebox.showwarning("Select Backup", "Please choose a backup file from the list to restore.", parent=win)
                return
            target_file = file_map[sel[0]]
            vals = btree.item(sel[0], "values")
            if vals[3] != "OK":
                messagebox.showerror("Damaged Backup", "This backup file failed the integrity check and cannot be safely restored.", parent=win)
                return

            confirm_msg = (
                f"Selected Backup: {vals[1]} ({vals[0]})\n"
                f"Contains: {vals[4]} Students, {vals[5]} Teachers, {vals[6]} Payments.\n\n"
                "WARNING: Restoring will replace all current data with this backup.\n"
                "An automatic safety copy of your current active data will be created first.\n\n"
                "Do you want to proceed with restore?"
            )
            if not messagebox.askyesno("Confirm Restore / بحالی کی تصدیق", confirm_msg, icon="warning", parent=win):
                return

            safety_folder = os.path.join(os.path.dirname(os.path.abspath(self.db.path)), "backups")
            os.makedirs(safety_folder, exist_ok=True)
            safety_copy = os.path.join(safety_folder, f"safety_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3")
            try:
                self.make_verified_backup(safety_copy)
                src = sqlite3.connect(Path(target_file).resolve().as_uri() + "?mode=ro", uri=True)
                with self.db.conn:
                    src.backup(self.db.conn)
                src.close()
                self._save_setting("backup_last_auto", timestamp())
                messagebox.showinfo("Restore Complete / بحالی مکمل", f"Backup restored successfully!\nPre-restore safety copy saved at:\n{safety_copy}\n\nThe application will now refresh.", parent=win)
                win.destroy()
                self.dashboard()
            except Exception as exc:
                messagebox.showerror("Restore Failed", f"Could not complete restore:\n{exc}\nYour previous data was preserved.", parent=win)

        btn_row = ttk.Frame(body)
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="♻️ Restore Selected Backup / منتخب بیک اپ بحال کریں", style="Accent.TButton", command=restore_selected).pack(side="left")
        ttk.Button(btn_row, text="📂 Open Folder in Explorer", command=lambda: self.open_folder(folder)).pack(side="left", padx=8)
        ttk.Button(btn_row, text="Close / بند کریں", command=win.destroy).pack(side="right")
'''

def main():
    with open("Institute_Ledger.py", "r", encoding="utf-8") as f:
        code = f.read()

    new_methods = get_new_methods()
    target_insert = "    def settings_page(self, parent):"
    assert target_insert in code, "Target settings_page not found"
    code = code.replace(target_insert, new_methods + "\n    def settings_page(self, parent):", 1)
    print("Added helper methods before settings_page.")

    with open("Institute_Ledger.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Part 2 successfully written.")

if __name__ == "__main__":
    main()

