# -*- coding: utf-8 -*-
def calc_luminance(hex_str):
    h = str(hex_str).strip().lstrip("#")
    if len(h) == 3: h = "".join(c*2 for c in h)
    r, g, b = (int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    def to_lin(c): return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * to_lin(r) + 0.7152 * to_lin(g) + 0.0722 * to_lin(b)

def derive_primary_tokens(primary_hex, is_dark=False):
    h = str(primary_hex).strip().lstrip("#")
    if len(h) == 3: h = "".join(c*2 for c in h)
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    primary = f"#{r:02X}{g:02X}{b:02X}"
    dr, dg, db = int(r * 0.76), int(g * 0.76), int(b * 0.76)
    primary_dark = f"#{dr:02X}{dg:02X}{db:02X}"
    if is_dark:
        lr = int(r * 0.25 + 29 * 0.75)
        lg = int(g * 0.25 + 40 * 0.75)
        lb = int(b * 0.25 + 35 * 0.75)
    else:
        lr = int(r * 0.12 + 248 * 0.88)
        lg = int(g * 0.12 + 250 * 0.88)
        lb = int(b * 0.12 + 248 * 0.88)
    primary_light = f"#{lr:02X}{lg:02X}{lb:02X}"
    lum = calc_luminance(primary)
    primary_text = "#0F172A" if lum > 0.42 else "#FFFFFF"
    return primary, primary_dark, primary_light, primary_text

# Test with green, blue, red, purple, orange
test_colors = [
    ("#0F5132", "Emerald Green"),
    ("#1E3A8A", "Royal Blue"),
    ("#DC2626", "Crimson Red"),
    ("#7C3AED", "Vibrant Purple"),
    ("#EA580C", "Deep Orange"),
    ("#EAB308", "Bright Amber/Yellow"),
]

for col, name in test_colors:
    for dark_mode in (False, True):
        p, pd, pl, pt = derive_primary_tokens(col, dark_mode)
        mode_str = "Dark" if dark_mode else "Light"
        lum_p = calc_luminance(p)
        lum_pt = calc_luminance(pt)
        l1, l2 = max(lum_p, lum_pt), min(lum_p, lum_pt)
        contrast = (l1 + 0.05) / (l2 + 0.05)
        print(f"[{name} - {mode_str}] PRIMARY={p}, DARK={pd}, LIGHT={pl}, TEXT={pt}, Contrast={contrast:.2f}:1")
        assert contrast >= 4.5, f"Contrast {contrast:.2f} failed WCAG AA for {name}"

print("All WCAG AA contrast tests PASSED!")

