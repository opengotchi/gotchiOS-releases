"""gotchiOS Digital Clock — clean, modern, themed."""
import display, rtc, time, touch, system

W = display.WIDTH
H = display.HEIGHT
c = display.color

# ── Load device theme ──
THEMES = (
    ('pipboy',  (5,10,5),    (0,255,65),   (0,200,50),  (0,50,15),   (0,120,30)),
    ('amber',   (10,6,0),    (255,176,0),  (200,140,0), (50,35,0),   (140,100,0)),
    ('ice',     (2,5,15),    (0,200,255),  (0,160,220), (0,35,55),   (0,100,140)),
    ('hotpink', (10,2,8),    (255,50,150), (220,40,130),(50,10,30),  (140,25,85)),
    ('mono',    (0,0,0),     (220,220,220),(180,180,180),(40,40,40),  (100,100,100)),
)
t_idx = 3
_cfg = system.readfile('/littlefs/config/theme.txt')
if _cfg:
    _cfg = _cfg.strip()
    for _i in range(len(THEMES)):
        if THEMES[_i][0] == _cfg:
            t_idx = _i
            break

t = THEMES[t_idx]
BG  = c(*t[1])
FG  = c(*t[2])
ACC = c(*t[3])
DIM = c(*t[4])
BDR = c(*t[5])

# ── 7-segment rendering with beveled look ──
# Segment map:  _0_
#              |   |
#              1   2
#              |_3_|
#              |   |
#              4   5
#              |_6_|

# Digit cell: 36w x 60h
DW = 36
DH = 60
ST = 7   # segment thickness
SG = 2   # gap between segments

H_SEGS = (
    (SG + ST, 0, DW - 2*ST - 2*SG, ST),                    # 0: top
    (SG + ST, (DH - ST) // 2, DW - 2*ST - 2*SG, ST),       # 3: middle
    (SG + ST, DH - ST, DW - 2*ST - 2*SG, ST),               # 6: bottom
)
V_SEGS = (
    (0, SG + ST, ST, (DH - 3*ST) // 2 - SG),                # 1: top-left
    (DW - ST, SG + ST, ST, (DH - 3*ST) // 2 - SG),          # 2: top-right
    (0, (DH + ST) // 2 + SG, ST, (DH - 3*ST) // 2 - SG),    # 4: bottom-left
    (DW - ST, (DH + ST) // 2 + SG, ST, (DH - 3*ST) // 2 - SG), # 5: bottom-right
)

# Segment indices: 0=top, 1=tl, 2=tr, 3=mid, 4=bl, 5=br, 6=bot
# Map to our arrays: H_SEGS[0]=seg0, V_SEGS[0]=seg1, V_SEGS[1]=seg2,
#                    H_SEGS[1]=seg3, V_SEGS[2]=seg4, V_SEGS[3]=seg5, H_SEGS[2]=seg6
SEG_MAP = (
    ('h', 0), ('v', 0), ('v', 1), ('h', 1), ('v', 2), ('v', 3), ('h', 2)
)

DIGITS = (
    (1,1,1,0,1,1,1),  # 0
    (0,0,1,0,0,1,0),  # 1
    (1,0,1,1,1,0,1),  # 2
    (1,0,1,1,0,1,1),  # 3
    (0,1,1,1,0,1,0),  # 4
    (1,1,0,1,0,1,1),  # 5
    (1,1,0,1,1,1,1),  # 6
    (1,0,1,0,0,1,0),  # 7
    (1,1,1,1,1,1,1),  # 8
    (1,1,1,1,0,1,1),  # 9
)

def draw_seg(ox, oy, seg_type, seg_idx, on):
    """Draw a single segment."""
    col = FG if on else DIM
    if seg_type == 'h':
        sx, sy, sw, sh = H_SEGS[seg_idx]
    else:
        sx, sy, sw, sh = V_SEGS[seg_idx]
    display.rect_filled(ox + sx, oy + sy, sw, sh, col)

def draw_digit(ox, oy, d):
    """Draw a full 7-segment digit."""
    pat = DIGITS[d]
    for i in range(7):
        st, si = SEG_MAP[i]
        draw_seg(ox, oy, st, si, pat[i])

def draw_colon(x, y, on):
    """Draw blinking colon dots."""
    col = FG if on else DIM
    dot_r = 4
    display.circle_filled(x, y + DH // 3, dot_r, col)
    display.circle_filled(x, y + 2 * DH // 3, dot_r, col)

# ── Layout ──
# Large HH:MM centered, smaller :SS to the right
MAIN_GAP = 4
COL_GAP = 8
MAIN_W = DW * 4 + MAIN_GAP * 3 + COL_GAP * 2
SEC_W = DW * 2 + MAIN_GAP  # seconds pair (smaller, but same size for now)

# Seconds rendered at ~60% scale
SD_W = 22
SD_H = 38
S_ST = 4
S_SG = 1

S_H_SEGS = (
    (S_SG + S_ST, 0, SD_W - 2*S_ST - 2*S_SG, S_ST),
    (S_SG + S_ST, (SD_H - S_ST) // 2, SD_W - 2*S_ST - 2*S_SG, S_ST),
    (S_SG + S_ST, SD_H - S_ST, SD_W - 2*S_ST - 2*S_SG, S_ST),
)
S_V_SEGS = (
    (0, S_SG + S_ST, S_ST, (SD_H - 3*S_ST) // 2 - S_SG),
    (SD_W - S_ST, S_SG + S_ST, S_ST, (SD_H - 3*S_ST) // 2 - S_SG),
    (0, (SD_H + S_ST) // 2 + S_SG, S_ST, (SD_H - 3*S_ST) // 2 - S_SG),
    (SD_W - S_ST, (SD_H + S_ST) // 2 + S_SG, S_ST, (SD_H - 3*S_ST) // 2 - S_SG),
)

def draw_small_digit(ox, oy, d):
    """Draw a smaller 7-segment digit for seconds."""
    pat = DIGITS[d]
    for i in range(7):
        st, si = SEG_MAP[i]
        if st == 'h':
            sx, sy, sw, sh = S_H_SEGS[si]
        else:
            sx, sy, sw, sh = S_V_SEGS[si]
        col = ACC if pat[i] else DIM
        display.rect_filled(ox + sx, oy + sy, sw, sh, col)

def draw_small_colon(x, y, on):
    col = ACC if on else DIM
    display.circle_filled(x, y + SD_H // 3, 3, col)
    display.circle_filled(x, y + 2 * SD_H // 3, 3, col)

# Compute positions
# Main time: HH:MM centered, seconds anchored to the right of MM
hm_w = DW * 4 + MAIN_GAP * 3 + COL_GAP * 2  # full HH:MM width
ss_w = SD_W * 2 + MAIN_GAP + COL_GAP          # :SS width
total_w = hm_w + ss_w
base_x = (W - total_w) // 2
base_y = (H - DH) // 2 - 4

# Digit X positions for HH:MM
hm_x = [0] * 4
colon_x = [0] * 1
_x = base_x
hm_x[0] = _x; _x += DW + MAIN_GAP
hm_x[1] = _x; _x += DW + COL_GAP
colon_hm = _x; _x += COL_GAP
hm_x[2] = _x; _x += DW + MAIN_GAP
hm_x[3] = _x; _x += DW + COL_GAP

# Seconds X positions (aligned to bottom-right of main digits)
ss_base_x = _x
colon_ss = ss_base_x
ss_x0 = ss_base_x + COL_GAP
ss_x1 = ss_x0 + SD_W + MAIN_GAP
ss_y = base_y + DH - SD_H  # bottom-aligned with main digits

# ── Decorative line ──
line_y = base_y + DH + 14

# ── Date ──
MONTHS = ('JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC')
DAYS = ('SUN','MON','TUE','WED','THU','FRI','SAT')

fr = 0

while True:
    g = touch.gesture()
    if g == 'swipe_left':
        system.exit()

    year, month, day, hrs, mins, secs = rtc.now()

    display.clear(BG)

    # ── Main digits: HH:MM ──
    draw_digit(hm_x[0], base_y, hrs // 10)
    draw_digit(hm_x[1], base_y, hrs % 10)
    draw_colon(colon_hm, base_y, secs % 2 == 0)
    draw_digit(hm_x[2], base_y, mins // 10)
    draw_digit(hm_x[3], base_y, mins % 10)

    # ── Seconds: :SS (smaller, bottom-aligned) ──
    draw_small_colon(colon_ss, ss_y, secs % 2 == 0)
    draw_small_digit(ss_x0, ss_y, secs // 10)
    draw_small_digit(ss_x1, ss_y, secs % 10)

    # ── Decorative separator line ──
    display.line(base_x, line_y, base_x + total_w, line_y, BDR)

    # ── Date line: clean, minimal ──
    m_str = MONTHS[month - 1] if 1 <= month <= 12 else '???'
    date_str = '%02d %s %04d' % (day, m_str, year)
    date_w = len(date_str) * 12
    display.text((W - date_w) // 2, line_y + 6, date_str, 1, ACC)

    display.flush()
    fr += 1
    time.sleep_ms(100)
