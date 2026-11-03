# -*- coding: utf-8 -*-
with open("Institute_Ledger.py", "r", encoding="utf-8") as f:
    code = f.read()

old_loop = '''        for label, callback in buttons:
            holder = ttk.Frame(nav, style="Workspace.TFrame")'''

new_loop = '''        group_headers = {
            "🏠 Dashboard": "📊 OVERVIEW / عمومی جائزہ",
            "👨‍🎓 Students": "📖 ACADEMICS / تعلیمی امور",
            "💳 Fees & Payments": "💰 FINANCE / مالیات",
            "👩‍🏫 Teachers": "👥 STAFF & ANALYTICS / عملہ و تجزیہ",
            "\\u2699\\ufe0f Settings": "⚙️ SYSTEM / ترتیبات",
            "👨‍🎓 My Students": "📖 ACADEMICS / تعلیمی امور",
        }
        for label, callback in buttons:
            if self._nav_orientation == "column" and label in group_headers:
                hdr = tk.Frame(nav, bg=PALE, pady=3, padx=8)
                hdr.pack(fill="x", padx=6, pady=(10, 2))
                smart_label(tk.Label, hdr, text=group_headers[label], font=(UI_FONT, 8, "bold"), fg=MUTED, bg=PALE, anchor="w").pack(side="left")
            holder = ttk.Frame(nav, style="Workspace.TFrame")'''

assert old_loop in code, "old_loop not found"
code = code.replace(old_loop, new_loop, 1)

with open("Institute_Ledger.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated grouped navigation in sidebar successfully.")

