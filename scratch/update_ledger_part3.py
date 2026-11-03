# -*- coding: utf-8 -*-
import sys, os

def get_enhanced_settings_page():
    return '''    def settings_page(self, parent):
        """Central offline settings for institution identity and branding with live preview, presets, and persistent backup."""
        is_admin = bool(self.user and self.user.get("role") == "admin")
        self.page_title(parent, "⚙️ Institution Settings / ادارے کی ترتیبات",
                        "Changes are saved locally in this database. No internet or cloud account is required.")
        if not is_admin:
            info_card = tk.Frame(parent, bg=PALE, highlightbackground=BORDER, highlightthickness=1, padx=14, pady=10)
            info_card.pack(fill="x", pady=(0, 10))
            smart_label(tk.Label, info_card,
                        text="🔒 Read-only view: Only an administrator can modify institution identity, branding, and colors. / صرف ایڈمن ترتیبات تبدیل کر سکتے ہیں۔",
                        bg=PALE, fg=DARK, font=(UI_FONT, 10, "bold"), anchor="w").pack(anchor="w")

        entry_state = "normal" if is_admin else "disabled"
        combo_state = "readonly" if is_admin else "disabled"

        form = ttk.LabelFrame(parent, text="Institution identity & Branding / ادارے کی شناخت اور برانڈنگ", padding=16)
        form.pack(fill="x", pady=(0, 12))

        en_var = tk.StringVar(value=self.brand_name)
        ur_var = tk.StringVar(value=self.brand_name_ur)
        slogan_en_var = tk.StringVar(value=self.settings.get("institution_slogan_en", getattr(self, "slogan_en", "")) or "")
        slogan_ur_var = tk.StringVar(value=self.settings.get("institution_slogan_ur", getattr(self, "slogan_ur", "")) or "")
        logo_var = tk.StringVar(value=self.logo_path)
        primary_var = tk.StringVar(value=self.settings.get("primary_color", GREEN))
        bg_var = tk.StringVar(value=self.settings.get("background_color", APP_BG))
        text_color_var = tk.StringVar(value=self.settings.get("text_color", DARK))
        font_size_var = tk.StringVar(value=str(self.settings.get("font_size", "12")))

        preset_keys = ["emerald", "royal_blue", "teal", "purple", "charcoal", "custom"]
        preset_labels = {
            "emerald": "Emerald & Gold (Default) / زمرد اور سنہری",
            "royal_blue": "Royal Blue & Gold / شاہی نیلا اور سنہری",
            "teal": "Teal & Amber / نیلگوں اور عنبری",
            "purple": "Deep Purple & Mint / گہرا جامنی اور پودینہ",
            "charcoal": "Charcoal & Green / کوئلہ اور سبز",
            "custom": "Custom Color / اپنی مرضی کا رنگ",
        }
        current_preset = str(self.settings.get("theme_preset", "emerald") or "emerald").strip().lower()
        if current_preset not in preset_labels:
            current_preset = "emerald"
        theme_preset_var = tk.StringVar(value=preset_labels[current_preset])

        try:
            installed_fonts = sorted({str(x) for x in self.root.tk.call("font", "families")}, key=str.casefold)
        except Exception:
            installed_fonts = ["Aptos", "Segoe UI", "Arial", "Tahoma", "Jameel Noori Nastaleeq", "Noto Nastaliq Urdu"]
        english_options = [x for x in ("Aptos", "Segoe UI", "Arial", "Tahoma", "Calibri") if x.casefold() in {f.casefold() for f in installed_fonts}]
        english_options += [x for x in installed_fonts if x not in english_options and x.casefold() not in {y.casefold() for y in english_options}]
        urdu_options = [x for x in ("Jameel Noori Nastaleeq", "Noto Nastaliq Urdu", "Noto Nastaliq Urdu UI", "Urdu Typesetting", "Nafees Nastaleeq", "Segoe UI") if x.casefold() in {f.casefold() for f in installed_fonts}]
        if not urdu_options:
            urdu_options = [choose_urdu_font(self.root)]
        english_font_var = tk.StringVar(value=self.settings.get("english_font", UI_FONT))
        urdu_font_var = tk.StringVar(value=self.settings.get("urdu_font", URDU_FONT))

        # Row 0: English Name
        smart_label(ttk.Label, form, text="Institution name (English) / ادارے کا انگریزی نام").grid(row=0, column=0, sticky="w", padx=7, pady=6)
        ttk.Entry(form, textvariable=en_var, width=38, state=entry_state).grid(row=0, column=1, sticky="w", padx=7, pady=6)

        # Row 1: Urdu Name
        smart_label(ttk.Label, form, text="Institution name (Urdu) / ادارے کا اردو نام").grid(row=1, column=0, sticky="w", padx=7, pady=6)
        ttk.Entry(form, textvariable=ur_var, width=38, state=entry_state).grid(row=1, column=1, sticky="w", padx=7, pady=6)

        # Row 2: English Slogan
        smart_label(ttk.Label, form, text="Tagline / Slogan (English) / انگریزی سلوگن").grid(row=2, column=0, sticky="w", padx=7, pady=6)
        ttk.Entry(form, textvariable=slogan_en_var, width=38, state=entry_state).grid(row=2, column=1, sticky="w", padx=7, pady=6)

        # Row 3: Urdu Slogan
        smart_label(ttk.Label, form, text="Tagline / Slogan (Urdu) / اردو سلوگن").grid(row=3, column=0, sticky="w", padx=7, pady=6)
        ttk.Entry(form, textvariable=slogan_ur_var, width=38, state=entry_state).grid(row=3, column=1, sticky="w", padx=7, pady=6)

        # Row 4: Logo image + Live Preview Canvas
        smart_label(ttk.Label, form, text="Logo image / ادارے کا لوگو").grid(row=4, column=0, sticky="w", padx=7, pady=6)
        logo_area = ttk.Frame(form)
        logo_area.grid(row=4, column=1, sticky="ew", padx=7, pady=6)

        preview_canvas = tk.Canvas(logo_area, width=84, height=84, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        preview_canvas.pack(side="left", padx=(0, 12))
        preview_ref = {"img": None}

        def update_logo_preview():
            path = logo_var.get().strip()
            preview_canvas.delete("all")
            if path and os.path.isfile(path) and Image is not None and ImageTk is not None:
                try:
                    photo = self._circular_logo_photo(path, 76, GREEN, 2)
                    preview_ref["img"] = photo
                    preview_canvas.create_image(42, 42, image=photo)
                    return
                except Exception:
                    pass
            # Fallback circle
            preview_canvas.create_oval(8, 8, 76, 76, fill=PALE, outline=GREEN, width=2)
            preview_canvas.create_text(42, 42, text="📖", font=("Segoe UI Emoji", 26))

        logo_controls = ttk.Frame(logo_area)
        logo_controls.pack(side="left", fill="both", expand=True)
        ttk.Entry(logo_controls, textvariable=logo_var, state=entry_state).pack(fill="x", pady=(0, 6))

        def crop_selected_logo(path):
            try:
                branding_dir = os.path.join(os.path.dirname(os.path.abspath(self.db.path)), "branding")
                os.makedirs(branding_dir, exist_ok=True)
                target = os.path.join(branding_dir, "institution_logo.png")
                if self._show_logo_cropper(path, target):
                    logo_var.set(target)
                    update_logo_preview()
            except OSError as exc:
                messagebox.showerror("Logo could not be saved / لوگو محفوظ نہیں ہوا",
                                     "Could not save the adjusted logo in the local branding folder:\\n" + str(exc), parent=self.root)

        def pick_logo():
            path = filedialog.askopenfilename(
                parent=self.root, title="Choose institution logo",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tif *.tiff"), ("All files", "*.*")])
            if path:
                crop_selected_logo(path)

        def edit_logo():
            path = logo_var.get().strip()
            if not path or not os.path.isfile(path):
                pick_logo()
            else:
                crop_selected_logo(path)

        def remove_logo():
            logo_var.set("")
            update_logo_preview()

        btn_row_logo = ttk.Frame(logo_controls)
        btn_row_logo.pack(anchor="w")
        ttk.Button(btn_row_logo, text="Choose & crop… / منتخب کریں", command=pick_logo, state=entry_state).pack(side="left")
        ttk.Button(btn_row_logo, text="Adjust / فریم درست کریں", command=edit_logo, state=entry_state).pack(side="left", padx=6)
        ttk.Button(btn_row_logo, text="Remove logo / ڈیفالٹ", command=remove_logo, state=entry_state).pack(side="left", padx=6)
        update_logo_preview()

        # Row 5: Theme Presets Dropdown & Reset Theme
        smart_label(ttk.Label, form, text="Theme preset / ڈیزائن و رنگ").grid(row=5, column=0, sticky="w", padx=7, pady=6)
        preset_row = ttk.Frame(form)
        preset_row.grid(row=5, column=1, sticky="ew", padx=7, pady=6)
        preset_combo = ttk.Combobox(preset_row, textvariable=theme_preset_var, values=list(preset_labels.values()), state=combo_state, width=36)
        preset_combo.pack(side="left")

        def on_preset_selected(_e=None):
            sel_val = theme_preset_var.get()
            chosen_key = "emerald"
            for k, label in preset_labels.items():
                if label == sel_val:
                    chosen_key = k
                    break
            if chosen_key in THEME_PRESETS:
                p_col = THEME_PRESETS[chosen_key]["primary"]
                primary_var.set(p_col)

        preset_combo.bind("<<ComboboxSelected>>", on_preset_selected)

        def reset_to_emerald():
            theme_preset_var.set(preset_labels["emerald"])
            primary_var.set(THEME_PRESETS["emerald"]["primary"])
            bg_var.set("#F8FAF8")
            text_color_var.set("#132D23")

        ttk.Button(preset_row, text="Reset to Default Theme / اصل تھیم", command=reset_to_emerald, state=entry_state).pack(side="left", padx=(8, 0))

        # Row 6: Primary Color
        smart_label(ttk.Label, form, text="Primary color / بنیادی رنگ (HEX)").grid(row=6, column=0, sticky="w", padx=7, pady=6)
        color_row = ttk.Frame(form)
        color_row.grid(row=6, column=1, sticky="ew", padx=7, pady=6)
        ttk.Entry(color_row, textvariable=primary_var, width=16, state=entry_state).pack(side="left")
        ttk.Button(color_row, text="Choose…", command=lambda: self._choose_color(primary_var), state=entry_state).pack(side="left", padx=6)

        # Row 7: Background & Text Colors
        smart_label(ttk.Label, form, text="Background color / پس منظر کا رنگ").grid(row=7, column=0, sticky="w", padx=7, pady=6)
        bg_row = ttk.Frame(form)
        bg_row.grid(row=7, column=1, sticky="ew", padx=7, pady=6)
        ttk.Entry(bg_row, textvariable=bg_var, width=16, state=entry_state).pack(side="left")
        ttk.Button(bg_row, text="Choose…", command=lambda: self._choose_color(bg_var), state=entry_state).pack(side="left", padx=6)

        smart_label(ttk.Label, form, text="Text color / تحریر کا رنگ").grid(row=8, column=0, sticky="w", padx=7, pady=6)
        text_row = ttk.Frame(form)
        text_row.grid(row=8, column=1, sticky="w", padx=7, pady=6)
        ttk.Entry(text_row, textvariable=text_color_var, width=16, state=entry_state).pack(side="left")
        ttk.Button(text_row, text="Choose…", command=lambda: self._choose_color(text_color_var), state=entry_state).pack(side="left", padx=6)

        # Row 9: Fonts
        smart_label(ttk.Label, form, text="English font / انگریزی فونٹ").grid(row=9, column=0, sticky="w", padx=7, pady=6)
        ttk.Combobox(form, textvariable=english_font_var, values=english_options, state=combo_state, width=34).grid(row=9, column=1, sticky="w", padx=7, pady=6)

        smart_label(ttk.Label, form, text="Urdu font / اردو فونٹ").grid(row=10, column=0, sticky="w", padx=7, pady=6)
        ttk.Combobox(form, textvariable=urdu_font_var, values=urdu_options, state=combo_state, width=34).grid(row=10, column=1, sticky="w", padx=7, pady=6)

        smart_label(ttk.Label, form, text="Font size / فونٹ سائز").grid(row=11, column=0, sticky="w", padx=7, pady=6)
        font_row = ttk.Frame(form)
        font_row.grid(row=11, column=1, sticky="w", padx=7, pady=6)
        ttk.Spinbox(font_row, from_=9, to=24, increment=1, textvariable=font_size_var, width=6, state=entry_state).pack(side="left")
        ttk.Label(font_row, text="  9 = Small   12 = Normal   16 = Large   24 = Extra large").pack(side="left")

        # Separate font-size controls
        area_size_vars = {
            "heading": tk.StringVar(value=str(self.settings.get("font_size_heading", "14"))),
            "body": tk.StringVar(value=str(self.settings.get("font_size_body", "12"))),
            "fields": tk.StringVar(value=str(self.settings.get("font_size_fields", "12"))),
            "buttons": tk.StringVar(value=str(self.settings.get("font_size_buttons", "12"))),
            "tables": tk.StringVar(value=str(self.settings.get("font_size_tables", "11"))),
        }
        area_rows = [
            ("Headings / عنوان", "heading"),
            ("General text / عام متن", "body"),
            ("Form fields / فارم کے خانے", "fields"),
            ("Buttons / بٹن", "buttons"),
            ("Tables / ٹیبل", "tables"),
        ]
        area_box = ttk.LabelFrame(form, text="Separate font sizes / مختلف حصوں کے الگ فونٹ سائز", padding=10)
        area_box.grid(row=12, column=0, columnspan=2, sticky="ew", padx=7, pady=(8, 4))
        def set_all_area_sizes(*_):
            value = font_size_var.get().strip()
            for var in area_size_vars.values():
                var.set(value)
        ttk.Button(font_row, text="Set all sizes / سب پر لاگو", command=set_all_area_sizes, state=entry_state).pack(side="left", padx=(8, 0))
        for idx, (label_text, key) in enumerate(area_rows):
            smart_label(ttk.Label, area_box, text=label_text).grid(row=idx // 3, column=(idx % 3) * 2, sticky="w", padx=(6, 3), pady=5)
            ttk.Spinbox(area_box, from_=9, to=24, increment=1, textvariable=area_size_vars[key], width=5, state=entry_state).grid(row=idx // 3, column=(idx % 3) * 2 + 1, sticky="w", padx=(0, 12), pady=5)

        form.grid_columnconfigure(1, weight=1)

        buttons = ttk.Frame(parent)
        buttons.pack(anchor="w", pady=10)

        def save_settings():
            nonlocal en_var, ur_var, slogan_en_var, slogan_ur_var, logo_var, primary_var, bg_var
            if not is_admin:
                messagebox.showerror("Permission denied", "Only an administrator can change institution settings.", parent=self.root)
                return
            en = en_var.get().strip() or DEFAULT_INSTITUTION_NAME
            ur = ur_var.get().strip() or DEFAULT_INSTITUTION_NAME_UR
            s_en = slogan_en_var.get().strip()
            s_ur = slogan_ur_var.get().strip()
            pc = primary_var.get().strip()
            bc = bg_var.get().strip()
            tc = text_color_var.get().strip()
            try:
                self.root.winfo_rgb(pc)
                self.root.winfo_rgb(bc)
                self.root.winfo_rgb(tc)
            except tk.TclError:
                messagebox.showerror("Invalid color", "Enter valid Tk color values, such as #0F7457 and #EAF4F0.", parent=self.root)
                return
            lp = logo_var.get().strip()
            if lp and not os.path.isfile(lp):
                if not messagebox.askyesno("Logo not found", "The selected logo file is not currently accessible. Save its path anyway?", parent=self.root):
                    return
            try:
                chosen_font_size = int(font_size_var.get())
                if not 9 <= chosen_font_size <= 24:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid font size", "Choose a font size between 9 and 24.", parent=self.root)
                return

            sel_preset = "custom"
            for k, label in preset_labels.items():
                if label == theme_preset_var.get():
                    sel_preset = k
                    break

            area_sizes = {}
            try:
                for key, var in area_size_vars.items():
                    value = int(var.get())
                    if not 9 <= value <= 24:
                        raise ValueError
                    area_sizes["font_size_" + key] = str(value)
            except ValueError:
                messagebox.showerror("Invalid font size", "Each area font size must be between 9 and 24.", parent=self.root)
                return

            values = {
                "institution_name_en": en,
                "institution_name_ur": ur,
                "institution_slogan_en": s_en,
                "institution_slogan_ur": s_ur,
                "logo_path": lp,
                "theme_preset": sel_preset,
                "primary_color": pc,
                "background_color": bc,
                "text_color": tc,
                "english_font": english_font_var.get().strip() or "Aptos",
                "urdu_font": urdu_font_var.get().strip() or "Jameel Noori Nastaleeq",
                "font_size": str(chosen_font_size),
                **area_sizes
            }
            self.db.conn.executemany("INSERT INTO app_settings(setting_key,setting_value) VALUES(?,?) ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value", values.items())
            self.db.conn.commit()
            self.settings.update(values)
            self.brand_name = en
            self.brand_name_ur = ur
            self.slogan_en = s_en
            self.slogan_ur = s_ur
            self.logo_path = lp

            global GREEN, GREEN_HOVER, APP_BG, DARK, FONT_SCALE, UI_FONT, UI_BOLD_FONT, URDU_FONT
            GREEN = pc
            GREEN_HOVER = pc
            APP_BG = bc
            DARK = tc
            FONT_SCALE = chosen_font_size / 10.0
            self.root._taha_font_sizes = {
                "global": chosen_font_size,
                "heading": int(values["font_size_heading"]),
                "body": int(values["font_size_body"]),
                "fields": int(values["font_size_fields"]),
                "buttons": int(values["font_size_buttons"]),
                "tables": int(values["font_size_tables"]),
            }
            UI_FONT = values["english_font"]
            UI_BOLD_FONT = UI_FONT
            URDU_FONT = values["urdu_font"]
            self._apply_theme_palette()
            self.root.title(en)
            self.style()
            messagebox.showinfo("Settings saved / ترتیبات محفوظ", "Institution identity and branding saved locally. Changes are applied live across the dashboard and reports.", parent=self.root)
            self.dashboard()
            apply_script_fonts(self.root)

        if is_admin:
            ttk.Button(buttons, text="💾 Save & Apply / محفوظ کریں", style="Accent.TButton", command=save_settings).pack(side="left", padx=(0, 8))
            ttk.Button(buttons, text="🎨 Customize Header / ہیڈر کسٹمائز کریں", command=self.header_customizer).pack(side="left", padx=8)

        # -----------------------------------------------------------------
        # Dedicated Persistent Database Backup & Relink Box
        # -----------------------------------------------------------------
        backup_card = ttk.LabelFrame(parent, text="Persistent Database Backup & Restore / ڈیٹا بیس بیک اپ و بحالی", padding=14)
        backup_card.pack(fill="x", pady=(10, 0))

        default_backup_path = self.settings.get("backup_primary_folder", _default_backup_dir())
        prim_var = tk.StringVar(value=default_backup_path)
        last_b_time = self.settings.get("backup_last_auto", "")
        last_b_text = f"Last backup: {last_b_time}" if last_b_time else "No backup recorded yet"

        b_row1 = ttk.Frame(backup_card)
        b_row1.pack(fill="x", pady=4)
        smart_label(ttk.Label, b_row1, text="Primary Backup Folder / مرکزی بیک اپ فولڈر: ").pack(side="left")
        ttk.Label(b_row1, textvariable=prim_var, font=(UI_FONT, 9, "bold")).pack(side="left", padx=6)

        def choose_primary_backup_dir():
            p = filedialog.askdirectory(parent=self.root, title="Choose Primary Backup Folder", initialdir=prim_var.get())
            if p:
                prim_var.set(p)
                self._save_setting("backup_primary_folder", p)

        ttk.Button(b_row1, text="Change Folder / منتخب کریں", command=choose_primary_backup_dir, state=entry_state).pack(side="left", padx=6)
        ttk.Button(b_row1, text="📂 Open Folder", command=lambda: self.open_folder(prim_var.get())).pack(side="left", padx=4)

        b_row2 = ttk.Frame(backup_card)
        b_row2.pack(fill="x", pady=6)
        ttk.Label(b_row2, text=f"Status: {last_b_text}", style="Sub.TLabel").pack(side="left")

        b_actions = ttk.Frame(backup_card)
        b_actions.pack(anchor="w", pady=(6, 0))

        def trigger_instant_backup():
            folder = prim_var.get().strip() or _default_backup_dir()
            try:
                os.makedirs(folder, exist_ok=True)
                target = os.path.join(folder, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3")
                self.make_verified_backup(target)
                self._save_setting("backup_last_auto", timestamp())
                messagebox.showinfo("Backup Complete / بیک اپ مکمل", "Verified backup successfully created:\\n" + target, parent=self.root)
            except Exception as exc:
                messagebox.showerror("Backup Failed", str(exc), parent=self.root)

        ttk.Button(b_actions, text="🛡️ Back up now / ابھی بیک اپ", style="Accent.TButton", command=trigger_instant_backup, state=entry_state).pack(side="left", padx=(0, 8))
        ttk.Button(b_actions, text="📁 Link Existing Backup Folder / پرانا فولڈر منسلک کریں", command=lambda: self.link_and_restore_backup_folder(), state=entry_state).pack(side="left", padx=6)
        ttk.Button(b_actions, text="♻️ Direct Restore from Backup File…", command=self.restore_backup, state=entry_state).pack(side="left", padx=6)

        # -----------------------------------------------------------------
        # Interface Background & Layout (Wallpaper)
        # -----------------------------------------------------------------
        appearance_box = ttk.LabelFrame(parent, text="Interface Background & Layout / انٹرفیس کا پس منظر اور ترتیب", padding=12)
        appearance_box.pack(fill="x", pady=(10, 0))
        wallpaper_path_var = tk.StringVar(value=str(self.settings.get("background_image_path", "") or ""))
        wallpaper_trans_var = tk.IntVar(value=max(0, min(100, int(self.settings.get("background_transparency", "68") or 68))) if str(self.settings.get("background_transparency", "68")).strip().isdigit() else 68)
        nav_orientation_var = tk.StringVar(value=str(self.settings.get("nav_orientation", "row") or "row"))
        wallpaper_path_row = ttk.Frame(appearance_box)
        wallpaper_path_row.pack(fill="x", pady=(0, 5))
        ttk.Label(wallpaper_path_row, text="Background image / پس منظر کی تصویر").pack(side="left", padx=(0, 8))
        ttk.Entry(wallpaper_path_row, textvariable=wallpaper_path_var, state=entry_state).pack(side="left", fill="x", expand=True, padx=4)
        def browse_wallpaper():
            selected = filedialog.askopenfilename(parent=self.root, title="Choose background image / پس منظر کی تصویر منتخب کریں",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp"), ("All files", "*.*")])
            if selected:
                wallpaper_path_var.set(os.path.abspath(selected))
                self._refresh_page_wallpaper(parent, wallpaper_path_var.get(), wallpaper_trans_var.get())
        ttk.Button(wallpaper_path_row, text="Browse / منتخب کریں", command=browse_wallpaper, state=entry_state).pack(side="left", padx=(4, 0))
        def remove_wallpaper():
            wallpaper_path_var.set("")
            self._refresh_page_wallpaper(parent, "", 68)
        ttk.Button(wallpaper_path_row, text="Remove / Default / پس منظر ہٹائیں", command=remove_wallpaper, state=entry_state).pack(side="left", padx=(4, 0))

        trans_row = ttk.Frame(appearance_box)
        trans_row.pack(fill="x", pady=4)
        ttk.Label(trans_row, text="Background transparency 0 = visible • 100 = hidden / شفافیت ۰ = نمایاں، ۱۰۰ = پوشیدہ").pack(side="left", padx=(0, 8))
        transparency_value = ttk.Label(trans_row, text=f"{wallpaper_trans_var.get()}%", width=6)
        transparency_value.pack(side="right")
        def on_transparency(value):
            try:
                amount = max(0, min(100, int(float(value))))
            except (TypeError, ValueError):
                amount = 68
            transparency_value.configure(text=f"{amount}%")
            self._refresh_page_wallpaper(parent, wallpaper_path_var.get(), amount)
        tk.Scale(appearance_box, from_=0, to=100, resolution=1, orient="horizontal", variable=wallpaper_trans_var,
                 command=on_transparency, showvalue=True, bg=APP_BG, fg=DARK, activebackground=GREEN,
                 troughcolor="#DCE8E2", highlightthickness=0, font=(UI_FONT, 9)).pack(fill="x", padx=6)
'''

def main():
    with open("Institute_Ledger.py", "r", encoding="utf-8") as f:
        code = f.read()

    # Find settings_page start and appearance_box start
    start_tag = "    def settings_page(self, parent):"
    end_tag = "        # Individual page backgrounds: each tab stores its own image/transparency,"

    assert start_tag in code, "start_tag not found"
    assert end_tag in code, "end_tag not found"

    pos_start = code.find(start_tag)
    pos_end = code.find(end_tag)

    enhanced = get_enhanced_settings_page()
    code = code[:pos_start] + enhanced + "\n" + code[pos_end:]
    print("Replaced settings_page.")

    with open("Institute_Ledger.py", "w", encoding="utf-8") as f:
        f.write(code)

    print("Successfully wrote updated settings_page.")

if __name__ == "__main__":
    main()

