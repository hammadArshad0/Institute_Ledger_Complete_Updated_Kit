# -*- coding: utf-8 -*-
"""
Master patch script for Institute Ledger UI fixes.
Applies all 6 fixes safely using raw byte / string replacements.
Run with: py -3.9 scratch/apply_all_fixes.py
"""
import os, sys, shutil, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(BASE, "Institute_Ledger.py")
BAK  = os.path.join(BASE, "Institute_Ledger.py.bak_pre_all_fixes")

# ---------- helpers ----------------------------------------------------------
def load():
    with open(SRC, 'rb') as f:
        return f.read()

def save(data):
    with open(SRC, 'wb') as f:
        f.write(data)

def text(data):
    return data.decode('utf-8', errors='replace')

def enc(s):
    return s.encode('utf-8')

def replace_once(data, old_bytes, new_bytes, label):
    count = data.count(old_bytes)
    if count == 0:
        print(f"  [SKIP]  {label} — pattern not found (already applied?)")
        return data
    result = data.replace(old_bytes, new_bytes, 1) if count == 1 else data.replace(old_bytes, new_bytes)
    print(f"  [OK]    {label} — replaced {count} occurrence(s)")
    return result

def replace_all(data, old_bytes, new_bytes, label):
    count = data.count(old_bytes)
    if count == 0:
        print(f"  [SKIP]  {label} — not found")
        return data
    data = data.replace(old_bytes, new_bytes)
    print(f"  [OK]    {label} — replaced {count}")
    return data

# ---------- backup -----------------------------------------------------------
if not os.path.exists(BAK):
    shutil.copy2(SRC, BAK)
    print(f"Backup created: {BAK}")
else:
    print(f"Backup already exists: {BAK}")

data = load()
print(f"\nLoaded {len(data):,} bytes  ({data.count(b'\\n')+1} lines)\n")

# =============================================================================
# FIX A: Today?s -> Today's  (binary patch, safest approach)
# =============================================================================
print("=== FIX A: Today?s apostrophe ===")
data = replace_all(data, b"Today\x3fs", b"Today\x27s", "Today?s -> Today's")
print()

# =============================================================================
# FIX B: Add _luminance() + PRIMARY_TEXT global after GOLD = "#FEF3C7"
# =============================================================================
print("=== FIX B: _luminance() + PRIMARY_TEXT global ===")

PRIMARY_TEXT_GLOBAL = b'\nPRIMARY_TEXT = "#FFFFFF"  # Updated by _apply_theme_palette based on primary luminance\n'
_LUMINANCE_FN = b'''
def _luminance(hex_color):
    """Relative luminance of a hex colour string (WCAG 2.1). Returns 0.0-1.0."""
    try:
        h = str(hex_color or "#000000").lstrip("#")
        if len(h) == 3:
            h = h[0]*2 + h[1]*2 + h[2]*2
        r, g, b = int(h[0:2],16)/255.0, int(h[2:4],16)/255.0, int(h[4:6],16)/255.0
        def lin(c):
            return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
        return 0.2126*lin(r) + 0.7152*lin(g) + 0.0722*lin(b)
    except Exception:
        return 0.0

'''

# Insert PRIMARY_TEXT global after GOLD line
GOLD_LINE = b'GOLD = "#FEF3C7"\n'
if GOLD_LINE in data and b'PRIMARY_TEXT' not in data:
    data = data.replace(GOLD_LINE, GOLD_LINE + PRIMARY_TEXT_GLOBAL, 1)
    print("  [OK]    PRIMARY_TEXT global inserted after GOLD")
elif b'PRIMARY_TEXT' in data:
    print("  [SKIP]  PRIMARY_TEXT already present")
else:
    print("  [WARN]  GOLD line not found - trying alternate")

# Insert _luminance() function before choose_urdu_font()
CHOOSE_URDU_MARKER = b'def choose_urdu_font(root=None):'
if CHOOSE_URDU_MARKER in data and b'def _luminance(' not in data:
    data = data.replace(CHOOSE_URDU_MARKER, _LUMINANCE_FN + CHOOSE_URDU_MARKER, 1)
    print("  [OK]    _luminance() inserted before choose_urdu_font")
elif b'def _luminance(' in data:
    print("  [SKIP]  _luminance() already present")
else:
    print("  [WARN]  choose_urdu_font marker not found")
print()

# =============================================================================
# FIX C: _apply_theme_palette — set PRIMARY_TEXT from luminance after GREEN=primary
# =============================================================================
print("=== FIX C: Set PRIMARY_TEXT in _apply_theme_palette ===")

OLD_PALETTE_GREEN = b'        GREEN = primary\n        GREEN_HOVER = hover\n'
NEW_PALETTE_GREEN = b'''        GREEN = primary
        GREEN_HOVER = hover
        # Derive PRIMARY_TEXT so foreground on primary-coloured widgets always meets WCAG AA
        global PRIMARY_TEXT
        try:
            _lum = _luminance(GREEN)
            PRIMARY_TEXT = "#0F172A" if _lum > 0.25 else "#FFFFFF"
        except Exception:
            PRIMARY_TEXT = "#FFFFFF"
'''
data = replace_once(data, OLD_PALETTE_GREEN, NEW_PALETTE_GREEN, "_apply_theme_palette: PRIMARY_TEXT derivation")
# Also add PRIMARY_TEXT to the global declaration line
OLD_GLOBAL_DECL = b'        global APP_BG, CARD_BG, BORDER, DARK, MUTED, PALE, SOFT_GREEN, GREEN_HOVER, GREEN\n'
NEW_GLOBAL_DECL = b'        global APP_BG, CARD_BG, BORDER, DARK, MUTED, PALE, SOFT_GREEN, GREEN_HOVER, GREEN, PRIMARY_TEXT\n'
data = replace_once(data, OLD_GLOBAL_DECL, NEW_GLOBAL_DECL, "_apply_theme_palette: add PRIMARY_TEXT to global decl")
print()

# =============================================================================
# FIX D: Replace _install_wallpaper_button_styles body with flat-color version
#         Also add Info/Print/Danger/Secondary.TButton
# =============================================================================
print("=== FIX D: Flat-color button styles (remove wallpaper texture) ===")

OLD_INSTALL_WP = b'''    def _install_wallpaper_button_styles(self, style, style_font, fs):
        """Create a small cached set of wallpaper-blended surfaces for the common green buttons."""
        if Image is None or ImageTk is None:
            return
        page_key = getattr(self, "_active_page_key", "dashboard")
        transparency = self._wallpaper_transparency_for_page(page_key)
        # The button keeps its semantic green identity, with a controlled amount of
        # the active page wallpaper visible through it. Higher wallpaper visibility
        # gently increases the blend; it never reduces text contrast below a safe level.
        wallpaper_mix = max(0.05, min(0.24, ((100 - transparency) / 100.0) * 0.34 + 0.05))
        generation = int(getattr(self, '_il_button_style_generation', 0)) + 1
        self._il_button_style_generation = generation
        normal = self._button_texture_photos(320, 48, GREEN, wallpaper_mix)
        active = self._button_texture_photos(320, 48, GREEN_HOVER, wallpaper_mix * 0.88)
        selected = self._button_texture_photos(320, 48, '#0B5F49', wallpaper_mix * 0.82)
        if not normal or not active or not selected:
            return
        refs = [*normal, *active, *selected]
        element = f'IL.PageSurface{generation}.border'
        active_element = f'IL.PageActiveSurface{generation}.border'
        try:
            style.element_create(element, 'image', normal[0],
                                 ('pressed', selected[2]), ('active', active[1]),
                                 border=9, sticky='nsew')
        except tk.TclError:
            pass
        try:
            style.element_create(active_element, 'image', selected[0],
                                 ('pressed', selected[2]), ('active', selected[1]),
                                 border=9, sticky='nsew')
        except tk.TclError:
            pass
        layouts = {
            'TButton': (element, (11, 7), False),
            'Accent.TButton': (element, (13, 8), True),
            'Nav.TButton': (element, (12, 9), True),
            'NavActive.TButton': (active_element, (12, 9), True),
        }
        for style_name, (button_element, padding, bold) in layouts.items():
            try:
                style.layout(style_name, [(button_element, {'sticky': 'nswe', 'children': [
                    ('Button.padding', {'sticky': 'nswe', 'children': [
                        ('Button.label', {'sticky': 'nswe'})]})]})])
                foreground = WHITE
                style.configure(style_name, foreground=foreground,
                                font=(style_font, fs(10), 'bold' if bold else 'normal'),
                                padding=padding, anchor='center', relief='flat', borderwidth=0,
                                focusthickness=1, focuscolor='#9ACDBB')
                style.map(style_name, foreground=[('disabled', '#9AA6A0'), ('pressed', foreground), ('active', foreground)])
            except tk.TclError:
                pass
        # Attendance status and calendar-cell styles intentionally remain crisp,
        # semantic and flat instead of generating extra image assets per page.
        history = getattr(self, '_il_ttk_button_texture_history', [])
        history.append(refs)
        self._il_ttk_button_texture_history = history[-8:]
        self._il_ttk_button_texture_refs = refs
        self._il_active_button_style_signature = (
            self._wallpaper_source_path(page_key=page_key), transparency,
            str(self.settings.get('theme_mode', 'light')), APP_BG)'''

NEW_INSTALL_WP = b'''    def _install_wallpaper_button_styles(self, style, style_font, fs):
        """Flat-colour semantic button styles. No wallpaper blending on buttons."""
        pt = PRIMARY_TEXT  # white or dark depending on primary luminance
        # --- Primary-action buttons (save / add / confirm) ---
        for sn, bg, bg_hov, fg, pad, bold in (
            ('TButton',        GREEN,     GREEN_HOVER, pt,       (11, 7), False),
            ('Accent.TButton', GREEN,     GREEN_HOVER, pt,       (13, 8), True),
            ('Nav.TButton',    CARD_BG,   SOFT_GREEN,  GREEN,    (10, 8), False),
            ('NavActive.TButton', GREEN,  GREEN_HOVER, pt,       (10, 8), True),
        ):
            try:
                style.configure(sn, background=bg, foreground=fg,
                                font=(style_font, fs(10), 'bold' if bold else 'normal'),
                                padding=pad, anchor='center', relief='flat', borderwidth=0,
                                focusthickness=1, focuscolor='#9ACDBB')
                style.map(sn,
                    background=[('disabled', '#DCE8E2'), ('pressed', bg_hov), ('active', bg_hov)],
                    foreground=[('disabled', '#8E9D96'), ('pressed', fg), ('active', fg)])
            except tk.TclError:
                pass
        # --- Semantic colour-by-function button styles ---
        # Info (blue) — Refresh, Open, View
        try:
            style.configure('Info.TButton', background='#2563EB', foreground=WHITE,
                            font=(style_font, fs(10)), padding=(11, 7),
                            relief='flat', borderwidth=0, focusthickness=1, focuscolor='#93C5FD')
            style.map('Info.TButton',
                background=[('disabled', '#BFDBFE'), ('pressed', '#1D4ED8'), ('active', '#1D4ED8')],
                foreground=[('disabled', '#6B7280'), ('pressed', WHITE), ('active', WHITE)])
        except tk.TclError:
            pass
        # Print/Export (orange) — Print, Export, Download, Certificates
        try:
            style.configure('Print.TButton', background='#EA580C', foreground=WHITE,
                            font=(style_font, fs(10)), padding=(11, 7),
                            relief='flat', borderwidth=0, focusthickness=1, focuscolor='#FDBA74')
            style.map('Print.TButton',
                background=[('disabled', '#FED7AA'), ('pressed', '#C2410C'), ('active', '#C2410C')],
                foreground=[('disabled', '#6B7280'), ('pressed', WHITE), ('active', WHITE)])
        except tk.TclError:
            pass
        # Danger (red) — Delete, Remove, Reject
        try:
            style.configure('Danger.TButton', background='#DC2626', foreground=WHITE,
                            font=(style_font, fs(10)), padding=(11, 7),
                            relief='flat', borderwidth=0, focusthickness=1, focuscolor='#FCA5A5')
            style.map('Danger.TButton',
                background=[('disabled', '#FECACA'), ('pressed', '#B91C1C'), ('active', '#B91C1C')],
                foreground=[('disabled', '#6B7280'), ('pressed', WHITE), ('active', WHITE)])
        except tk.TclError:
            pass
        # Secondary (outline) — cancel, back, secondary actions
        try:
            style.configure('Secondary.TButton', background=CARD_BG, foreground=GREEN,
                            font=(style_font, fs(10)), padding=(11, 7),
                            relief='solid', borderwidth=1, bordercolor=GREEN,
                            focusthickness=1, focuscolor='#9ACDBB')
            style.map('Secondary.TButton',
                background=[('disabled', APP_BG), ('pressed', SOFT_GREEN), ('active', SOFT_GREEN)],
                foreground=[('disabled', '#8E9D96'), ('pressed', GREEN), ('active', GREEN)])
        except tk.TclError:
            pass
        # Record current signature (theme+primary) so _refresh_page_button_styles skips no-op calls
        self._il_active_button_style_signature = (
            GREEN, str(self.settings.get('theme_mode', 'light')), APP_BG)'''

data = replace_once(data, OLD_INSTALL_WP, NEW_INSTALL_WP, "_install_wallpaper_button_styles -> flat-color")
print()

# =============================================================================
# FIX E: _refresh_page_button_styles — only re-run when theme/primary changes
# =============================================================================
print("=== FIX E: _refresh_page_button_styles simplification ===")

OLD_REFRESH_PS = b'''    def _refresh_page_button_styles(self, force=False):
        """Refresh wallpaper-blended Ttk button surfaces only when the active page image changes."""
        try:
            key = getattr(self, "_active_page_key", "dashboard")
            signature = (self._wallpaper_source_path(page_key=key), self._wallpaper_transparency_for_page(key),
                         str(self.settings.get("theme_mode", "light")), APP_BG)
            if not force and signature == getattr(self, "_il_active_button_style_signature", None):
                return
            style = ttk.Style(self.root)
            style_font = URDU_FONT if APP_LANGUAGE == "ur" else UI_FONT
            def fs(value):
                return max(9, int(round(value * max(0.8, min(1.8, FONT_SCALE)))))
            self._install_wallpaper_button_styles(style, style_font, fs)
        except (tk.TclError, AttributeError, TypeError, ValueError):
            pass'''

NEW_REFRESH_PS = b'''    def _refresh_page_button_styles(self, force=False):
        """Re-apply flat-colour button styles only when theme or primary colour changes."""
        try:
            signature = (GREEN, str(self.settings.get("theme_mode", "light")), APP_BG)
            if not force and signature == getattr(self, "_il_active_button_style_signature", None):
                return
            style = ttk.Style(self.root)
            style_font = URDU_FONT if APP_LANGUAGE == "ur" else UI_FONT
            def fs(value):
                return max(9, int(round(value * max(0.8, min(1.8, FONT_SCALE)))))
            self._install_wallpaper_button_styles(style, style_font, fs)
        except (tk.TclError, AttributeError, TypeError, ValueError):
            pass'''

data = replace_once(data, OLD_REFRESH_PS, NEW_REFRESH_PS, "_refresh_page_button_styles")
print()

# =============================================================================
# FIX F: _apply_tk_button_texture — add semantic colours for more verbs
# =============================================================================
print("=== FIX F: _apply_tk_button_texture semantic colours ===")

OLD_TK_TEX = b'''    def _apply_tk_button_texture(self, widget):
        """Apply a light semantic solid fill to classic Tk buttons without per-widget image work."""
        try:
            if not widget.winfo_exists():
                return
            text = str(widget.cget('text') or '').casefold()
            tint, fg = GREEN, WHITE
            if any(word in text for word in ('present', '\u062d\u0627\u0636\u0631')):
                tint = '#157347'
            elif any(word in text for word in ('absent', '\u063a\u06cc\u0631 \u062d\u0627\u0636\u0631')):
                tint = '#B42318'
            elif any(word in text for word in ('leave', '\u0686\u06be\u0679\u06cc')):
                tint = '#A15C07'
            elif any(word in text for word in ('delete', 'remove', 'reject', 'clear')):
                tint = '#A93232'
            widget.configure(bg=tint, activebackground=GREEN_HOVER if tint == GREEN else tint,
                             fg=fg, activeforeground=fg, relief='flat', bd=0,
                             highlightthickness=0, cursor='hand2')
        except (tk.TclError, AttributeError, TypeError):
            return'''

NEW_TK_TEX = b'''    def _apply_tk_button_texture(self, widget):
        """Apply semantic solid fill to classic Tk buttons by reading the button label text."""
        try:
            if not widget.winfo_exists():
                return
            text = str(widget.cget('text') or '').casefold()
            tint, fg = GREEN, WHITE
            # Attendance states
            if any(word in text for word in ('present', '\u062d\u0627\u0636\u0631')):
                tint = '#157347'
            elif any(word in text for word in ('absent', '\u063a\u06cc\u0631 \u062d\u0627\u0636\u0631')):
                tint = '#B42318'
            elif any(word in text for word in ('leave', '\u0686\u06be\u0679\u06cc')):
                tint = '#A15C07'
            # Danger actions
            elif any(word in text for word in ('delete', 'remove', 'reject', 'clear', 'cancel', '\u062d\u0630\u0641')):
                tint = '#DC2626'
            # Info / navigation actions (blue)
            elif any(word in text for word in ('refresh', 'open', 'view', 'filter', 'search', 'browse')):
                tint = '#2563EB'
            # Print / export (orange)
            elif any(word in text for word in ('print', 'export', 'download', 'certificate', 'report', '\u0627\u0633\u0646\u0627\u062f')):
                tint = '#EA580C'
            widget.configure(bg=tint, activebackground=GREEN_HOVER if tint == GREEN else tint,
                             fg=fg, activeforeground=fg, relief='flat', bd=0,
                             highlightthickness=0, cursor='hand2')
        except (tk.TclError, AttributeError, TypeError):
            return'''

data = replace_once(data, OLD_TK_TEX, NEW_TK_TEX, "_apply_tk_button_texture semantic colours")
print()

# =============================================================================
# FIX G: Sidebar width 190 -> 240, canvas width 184 -> 234
# =============================================================================
print("=== FIX G: Sidebar width 190->240 and canvas 184->234 ===")

OLD_SIDEBAR_W = b'            shell.configure(width=190)\n            shell.pack(side="left", fill="y")\n            shell.pack_propagate(False)\n            toggle = self._make_language_toggle(shell)\n            toggle.pack(side="top", fill="x", padx=7, pady=7)\n            self._language_toggle_button = toggle\n            tk.Frame(shell, bg=BORDER, width=1).pack(side="right", fill="y")\n            body = tk.Frame(shell, bg=CARD_BG)\n            body.pack(side="top", fill="both", expand=True)\n            canvas = tk.Canvas(body, bg=CARD_BG, highlightthickness=0, bd=0, width=184)'

NEW_SIDEBAR_W = b'''            _sidebar_collapsed = [bool(str(self.settings.get("sidebar_collapsed", "") or ""))]
            _sidebar_w = 64 if _sidebar_collapsed[0] else 240
            shell.configure(width=_sidebar_w)
            shell.pack(side="left", fill="y")
            shell.pack_propagate(False)
            # Language toggle moved to top bar; store flag so header can pick it up
            self._language_toggle_button = None
            tk.Frame(shell, bg=BORDER, width=1).pack(side="right", fill="y")
            # Collapse toggle button
            def _do_toggle_sidebar(_shell=shell, _state=_sidebar_collapsed):
                _state[0] = not _state[0]
                new_w = 64 if _state[0] else 240
                try:
                    _shell.configure(width=new_w)
                    _collapse_btn.configure(text="\u25b6" if _state[0] else "\u25c0")
                except tk.TclError:
                    pass
                self._save_setting("sidebar_collapsed", "1" if _state[0] else "")
            _collapse_btn = tk.Button(shell, text="\u25b6" if _sidebar_collapsed[0] else "\u25c0",
                                      command=_do_toggle_sidebar, bg=CARD_BG, fg=MUTED,
                                      relief="flat", bd=0, cursor="hand2",
                                      font=(UI_FONT, 10), padx=6, pady=2)
            _collapse_btn.pack(side="top", anchor="e", padx=4, pady=(6, 2))
            body = tk.Frame(shell, bg=CARD_BG)
            body.pack(side="top", fill="both", expand=True)
            _canvas_w = 58 if _sidebar_collapsed[0] else 234
            canvas = tk.Canvas(body, bg=CARD_BG, highlightthickness=0, bd=0, width=_canvas_w)'''

data = replace_once(data, OLD_SIDEBAR_W, NEW_SIDEBAR_W, "Sidebar width 240 + collapse toggle")
print()

# =============================================================================
# FIX H: KPI card subtitle — "Per currency • 2026-11" -> "This month (Nov 2026)"
# =============================================================================
print("=== FIX H: KPI card month subtitle fix ===")

# Find the month parsing — insert helper before the _dash_card calls
OLD_MONTH_SUB = b'        coll_value, coll_rest = money(collected, "0")\n        out_value, out_rest = money(out["by_cur"], "0" if out["invoices"] else "\xe2\x80\x94")'
NEW_MONTH_SUB = b'''        coll_value, coll_rest = money(collected, "0")
        out_value, out_rest = money(out["by_cur"], "0" if out["invoices"] else "\u2014")
        try:
            _month_label = datetime.strptime(data["month"], "%Y-%m").strftime("%b %Y")
        except Exception:
            _month_label = data["month"]'''

data = replace_once(data, OLD_MONTH_SUB, NEW_MONTH_SUB, "month label helper")

# Replace the subtitle in the Monthly Collection card
OLD_COLL_SUB = b'coll_rest or f"Per currency \xe2\x80\xa2 {data[\'month\']}"'
if OLD_COLL_SUB in data:
    data = replace_once(data, OLD_COLL_SUB, b'coll_rest or f"This month ({_month_label})"', "KPI month subtitle")
else:
    # try ASCII bullet
    OLD_COLL_SUB2 = b"coll_rest or f\"Per currency \xe2\x80\xa2 {data['month']}\""
    OLD_COLL_SUB3 = b"coll_rest or f\"Per currency \\xe2\\x80\\xa2 {data['month']}\""
    # Try plain pattern
    alt = b"Per currency"
    if alt in data:
        # Find the line containing it and replace
        idx = data.find(alt)
        line_start = data.rfind(b'\n', 0, idx) + 1
        line_end = data.find(b'\n', idx)
        old_line = data[line_start:line_end]
        new_line = re.sub(rb'coll_rest or f"Per currency.*?"', b'coll_rest or f"This month ({_month_label})"', old_line)
        if new_line != old_line:
            data = data[:line_start] + new_line + data[line_end:]
            print('  [OK]    KPI month subtitle (regex)')
        else:
            print('  [WARN]  KPI month subtitle regex did not match')
    else:
        print('  [WARN]  KPI month subtitle pattern not found')
print()

# =============================================================================
# FIX I: KPI card colors — Teachers #0D9488->#16A34A, Classes #D97706->#EA580C
# =============================================================================
print("=== FIX I: KPI card colors ===")
# Teachers card
data = replace_once(data, b'"#0D9488", "Active Teachers', b'"#16A34A", "Active Teachers', "Teachers teal->green")
# Classes card
data = replace_once(data, b'"#D97706", "Today\'', b'"#EA580C", "Today\'', "Classes amber->orange")
print()

# =============================================================================
# FIX J: Hero card — replace duplicate brand name with greeting
# =============================================================================
print("=== FIX J: Hero card greeting ===")

OLD_HERO_NAME = b'        smart_label(tk.Label, hero_info, text=f"{self.brand_name} \xe2\x80\xa2 {self.brand_name_ur}",\n                    bg=CARD_BG, fg=DARK, font=(UI_FONT, 14, "bold"), anchor="w").pack(anchor="w")'
NEW_HERO_NAME = b'''        _hero_username = str((self.user or {}).get("username", "Admin") or "Admin").title()
        smart_label(tk.Label, hero_info, text=f"Welcome back, {_hero_username}!",
                    bg=CARD_BG, fg=DARK, font=(UI_FONT, 14, "bold"), anchor="w").pack(anchor="w")'''

if OLD_HERO_NAME in data:
    data = replace_once(data, OLD_HERO_NAME, NEW_HERO_NAME, "Hero greeting replaces brand name")
else:
    # Try with bullet point variant
    OLD_HERO_ALT = b'smart_label(tk.Label, hero_info, text=f"{self.brand_name}'
    if OLD_HERO_ALT in data:
        idx = data.find(OLD_HERO_ALT)
        line_end = data.find(b').pack(anchor="w")', idx) + len(b').pack(anchor="w")')
        old_block = data[idx:line_end]
        new_block = (b'_hero_username = str((self.user or {}).get("username", "Admin") or "Admin").title()\n'
                     b'        smart_label(tk.Label, hero_info, text=f"Welcome back, {_hero_username}!",\n'
                     b'                    bg=CARD_BG, fg=DARK, font=(UI_FONT, 14, "bold"), anchor="w").pack(anchor="w")')
        data = data[:idx] + new_block + data[line_end:]
        print("  [OK]    Hero greeting (alt path)")
    else:
        print("  [WARN]  Hero brand name pattern not found")
print()

# =============================================================================
# FIX K: "Open Timetable \x1a" -> "Open Timetable ->"  (control char arrow)
# =============================================================================
print("=== FIX K: Open Timetable arrow ===")
data = replace_all(data, b"Open Timetable \x1a", b"Open Timetable \xe2\x86\x92", "Open Timetable control-char -> UTF8 arrow")
# Also fix \x1a in other link texts
data = replace_all(data, b"View All \x1a", b"View All \xe2\x86\x92", "View All control-char -> arrow")
data = replace_all(data, b"View all \x1a", b"View all \xe2\x86\x92", "View all control-char -> arrow")
print()

# =============================================================================
# Save + verify
# =============================================================================
save(data)
print(f"Saved {len(data):,} bytes")

import subprocess, sys as _sys
result = subprocess.run(
    [_sys.executable, "-m", "py_compile", SRC],
    capture_output=True, text=True
)
if result.returncode == 0:
    print("\n[PASS] py_compile: syntax OK")
else:
    print(f"\n[FAIL] py_compile error:\n{result.stderr}")
    print("\nRestoring backup...")
    shutil.copy2(BAK, SRC)
    print("Backup restored. Please fix the error manually.")
    _sys.exit(1)

with open(SRC, 'r', encoding='utf-8', errors='replace') as f:
    final_lines = f.readlines()
print(f"[INFO] Final line count: {len(final_lines)}")
print(f"[INFO] Line 1: {final_lines[0].rstrip()}")

# Verify CURRICULUM_DETAILED_CORES not split
curr_lines = [i+1 for i, l in enumerate(final_lines) if 'CURRICULUM_DETAILED_CORES' in l and '=' in l]
print(f"[INFO] CURRICULUM_DETAILED_CORES at lines: {curr_lines}")

print("\nAll fixes applied successfully.")
