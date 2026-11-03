# -*- coding: utf-8 -*-
import sys, os, re

def main():
    with open("Institute_Ledger.py", "r", encoding="utf-8") as f:
        code = f.read()

    # Invariant checks
    assert code.startswith("# -*- coding: utf-8 -*-"), "Line 1 invariant failed"
    assert "CURRICULUM_DETAILED_CORES" in code, "Line 1688 invariant failed"

    # Save safety backup
    with open("Institute_Ledger.py.bak_phase3", "w", encoding="utf-8") as f:
        f.write(code)
    print("Safety backup Institute_Ledger.py.bak_phase3 written.")

    # -------------------------------------------------------------
    # 1. Add _default_backup_dir top-level helper
    # -------------------------------------------------------------
    backup_helper = '''
def _default_backup_dir():
    """Default dedicated persistent backup folder outside app install dir."""
    sys_drive = os.environ.get("SystemDrive", "C:")
    target = os.path.join(sys_drive + os.sep, "InstituteLedgerBackups")
    try:
        os.makedirs(target, exist_ok=True)
    except OSError:
        pass
    return target
'''
    if "def _default_backup_dir():" not in code:
        code = code.replace("def _database_selection_config_path():", backup_helper + "\ndef _database_selection_config_path():")

    # -------------------------------------------------------------
    # 2. Update _dash_card with top accent strip and hover effect
    # -------------------------------------------------------------
    old_dash_card = '''    def _dash_card(self, parent, column, icon, tint, title, value, sub, sub_color=None):
        card = tk.Frame(parent, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1, padx=14, pady=14)
        card.grid(row=0, column=column, sticky="nsew", padx=6, pady=6)
        parent.grid_columnconfigure(column, weight=1, uniform="dashcards")
        tile = tk.Frame(card, bg=tint, width=52, height=52)
        tile.pack(side="left", padx=(0, 12))
        tile.pack_propagate(False)
        tk.Label(tile, text=icon, bg=tint, fg=WHITE, font=("Segoe UI Emoji", 18)).pack(expand=True)
        body = tk.Frame(card, bg=CARD_BG)
        body.pack(side="left", fill="x", expand=True)
        smart_label(tk.Label, body, text=title, bg=CARD_BG, fg=MUTED, font=(UI_FONT, 9, "bold"), anchor="w",
                    wraplength=200, justify="left").pack(anchor="w")
        smart_label(tk.Label, body, text=str(value), bg=CARD_BG, fg=DARK, font=(UI_FONT, 21, "bold"), anchor="w").pack(anchor="w")
        smart_label(tk.Label, body, text=sub, bg=CARD_BG, fg=sub_color or MUTED, font=(UI_FONT, 9), anchor="w",
                    wraplength=200, justify="left").pack(anchor="w")'''

    new_dash_card = '''    def _dash_card(self, parent, column, icon, tint, title, value, sub, sub_color=None):
        card = tk.Frame(parent, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1, padx=14, pady=12)
        card.grid(row=0, column=column, sticky="nsew", padx=6, pady=6)
        parent.grid_columnconfigure(column, weight=1, uniform="dashcards")
        # Distinct top colored accent strip
        top_strip = tk.Frame(card, bg=tint, height=4)
        top_strip.pack(side="top", fill="x", pady=(0, 8))
        inner_box = tk.Frame(card, bg=CARD_BG)
        inner_box.pack(fill="both", expand=True)
        mode = getattr(self, "theme_mode", "light")
        tile_bg = self._mix_color(tint, "#FFFFFF", 0.88) if mode == "light" else self._mix_color(tint, "#000000", 0.60)
        tile = tk.Frame(inner_box, bg=tile_bg, width=48, height=48, highlightbackground=tint, highlightthickness=1)
        tile.pack(side="left", padx=(0, 12))
        tile.pack_propagate(False)
        tk.Label(tile, text=icon, bg=tile_bg, fg=tint, font=("Segoe UI Emoji", 17)).pack(expand=True)
        body = tk.Frame(inner_box, bg=CARD_BG)
        body.pack(side="left", fill="x", expand=True)
        smart_label(tk.Label, body, text=title, bg=CARD_BG, fg=MUTED, font=(UI_FONT, 9, "bold"), anchor="w",
                    wraplength=180, justify="left").pack(anchor="w")
        smart_label(tk.Label, body, text=str(value), bg=CARD_BG, fg=DARK, font=(UI_FONT, 20, "bold"), anchor="w").pack(anchor="w")
        smart_label(tk.Label, body, text=sub, bg=CARD_BG, fg=sub_color or MUTED, font=(UI_FONT, 9), anchor="w",
                    wraplength=180, justify="left").pack(anchor="w")
        def on_enter(_e):
            try: card.configure(highlightbackground=tint, highlightthickness=2)
            except Exception: pass
        def on_leave(_e):
            try: card.configure(highlightbackground=BORDER, highlightthickness=1)
            except Exception: pass
        for w in (card, inner_box, body, tile):
            w.bind("<Enter>", on_enter, add="+")
            w.bind("<Leave>", on_leave, add="+")'''

    assert old_dash_card in code, "old_dash_card target not found"
    code = code.replace(old_dash_card, new_dash_card, 1)
    print("Replaced _dash_card successfully.")

    # -------------------------------------------------------------
    # 3. Update admin_home with Hero Banner and 5 Semantic KPI Colors
    # -------------------------------------------------------------
    old_admin_home_cards = '''        self._dash_card(cards, 0, "🎓", GREEN, "Total Students / کل طلبہ", data["students_total"], f"Active: {data['students_active']}")
        self._dash_card(cards, 1, "👩‍🏫", "#C94A57", "Active Teachers / اساتذہ", data["teachers_active"], f"Total: {data['teachers_total']}")
        self._dash_card(cards, 2, "📅", "#9D1D2C", "Today’s Classes / آج کی کلاسیں", len(classes),
                        f"Attendance not marked: {unmarked}", "#8A4B08" if unmarked else None)
        self._dash_card(cards, 3, "💰", "#B52235", "Monthly Collection / ماہانہ وصولی", coll_value,
                        coll_rest or f"Per currency • {data['month']}")
        out_sub = (f"Open {out['open']} • Overdue {out['overdue']}" if out["invoices"] else "No fee invoices yet")
        if out_rest:
            out_sub = out_rest + "\\n" + out_sub
        self._dash_card(cards, 4, "⚠", "#B45309", "Outstanding Fees / واجب الادا", out_value, out_sub,
                        "#9B1C1C" if out["overdue"] else None)'''

    new_admin_home_cards = '''        self._dash_card(cards, 0, "🎓", "#2563EB", "Total Students / کل طلبہ", data["students_total"], f"Active: {data['students_active']}")
        self._dash_card(cards, 1, "👩‍🏫", "#0D9488", "Active Teachers / اساتذہ", data["teachers_active"], f"Total: {data['teachers_total']}")
        self._dash_card(cards, 2, "📅", "#D97706", "Today’s Classes / آج کی کلاسیں", len(classes),
                        f"Attendance not marked: {unmarked}", "#B45309" if unmarked else None)
        self._dash_card(cards, 3, "💰", "#16A34A", "Monthly Collection / ماہانہ وصولی", coll_value,
                        coll_rest or f"Per currency • {data['month']}")
        out_sub = (f"Open {out['open']} • Overdue {out['overdue']}" if out["invoices"] else "No fee invoices yet")
        if out_rest:
            out_sub = out_rest + "\\n" + out_sub
        self._dash_card(cards, 4, "⚠", "#DC2626", "Outstanding Fees / واجب الادا", out_value, out_sub,
                        "#DC2626" if out["overdue"] else None)'''

    assert old_admin_home_cards in code, "old_admin_home_cards target not found"
    code = code.replace(old_admin_home_cards, new_admin_home_cards, 1)
    print("Updated admin_home KPI cards with semantic colors.")

    # -------------------------------------------------------------
    # 4. Add Hero Banner to admin_home
    # -------------------------------------------------------------
    old_admin_home_top = '''    def admin_home(self, parent):
        data = self._dash_data()
        now = datetime.now()
        self.page_title(parent, "School Dashboard / اکیڈمی ڈیش بورڈ",
                        f"{now.strftime('%A, %d %B %Y')}  •  live overview from your school records")
        bar = ttk.Frame(parent)
        bar.pack(fill="x")
        ttk.Button(bar, text="↻ Refresh / تازہ کریں",
                   command=lambda: self._go(parent, lambda p: self.admin_home(p), "Dashboard")).pack(side="right")'''

    new_admin_home_top = '''    def admin_home(self, parent):
        data = self._dash_data()
        now = datetime.now()
        # --- Prominent Hero Banner with Live Branding & Logo ---
        hero = tk.Frame(parent, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1, padx=16, pady=12)
        hero.pack(fill="x", pady=(0, 8))
        configured_logo = self.logo_path if self.logo_path and os.path.isfile(self.logo_path) else None
        logo_photo = None
        if configured_logo and Image is not None and ImageTk is not None:
            try:
                logo_photo = self._circular_logo_photo(configured_logo, 64, GREEN, 2)
            except Exception:
                logo_photo = None
        if logo_photo is not None:
            self._dash_hero_logo_ref = logo_photo
            tk.Label(hero, image=logo_photo, bg=CARD_BG).pack(side="left", padx=(0, 14))
        else:
            logo_frame = tk.Frame(hero, bg=PALE, width=64, height=64, highlightbackground=BORDER, highlightthickness=1)
            logo_frame.pack(side="left", padx=(0, 14))
            logo_frame.pack_propagate(False)
            tk.Label(logo_frame, text="📖", font=("Segoe UI Emoji", 24), bg=PALE, fg=GREEN).pack(expand=True)
        hero_info = tk.Frame(hero, bg=CARD_BG)
        hero_info.pack(side="left", fill="both", expand=True)
        smart_label(tk.Label, hero_info, text=f"{self.brand_name} • {self.brand_name_ur}",
                    bg=CARD_BG, fg=DARK, font=(UI_FONT, 14, "bold"), anchor="w").pack(anchor="w")
        slogan_text = self._brand_slogan()
        if slogan_text:
            smart_label(tk.Label, hero_info, text=slogan_text, bg=CARD_BG, fg=MUTED,
                        font=(UI_FONT, 9, "italic"), anchor="w").pack(anchor="w", pady=(1, 2))
        smart_label(tk.Label, hero_info, text=f"📅 {now.strftime('%A, %d %B %Y')}  •  Dashboard Overview",
                    bg=CARD_BG, fg=MUTED, font=(UI_FONT, 9), anchor="w").pack(anchor="w")
        hero_actions = ttk.Frame(hero)
        hero_actions.pack(side="right", padx=(8, 0))
        ttk.Button(hero_actions, text="↻ Refresh / تازہ کریں",
                   command=lambda: self._go(parent, lambda p: self.admin_home(p), "Dashboard")).pack(side="top", pady=2)
        ttk.Button(hero_actions, text="📜 Certificates / اسناد",
                   command=lambda: self.certificate_generator_dialog()).pack(side="top", pady=2)'''

    assert old_admin_home_top in code, "old_admin_home_top target not found"
    code = code.replace(old_admin_home_top, new_admin_home_top, 1)
    print("Added Hero Banner to admin_home.")

    with open("Institute_Ledger.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Part 1 successfully saved to Institute_Ledger.py")

if __name__ == "__main__":
    main()

