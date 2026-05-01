import display, touch, buttons, battery, system, time, gc, wifi, imu, rtc, buzzer, mqtt

W = display.WIDTH
H = display.HEIGHT
c = display.color

# ── Themes: (name, bg, fg, accent, dim, highlight, sel_bg, border) as RGB tuples ──
THEMES = (
    ('Pip-Boy',  (5,10,5),    (0,255,65),   (0,200,50),  (0,50,15),   (50,255,100), (0,30,8),    (0,120,30)),
    ('Amber',    (10,6,0),    (255,176,0),  (200,140,0), (50,35,0),   (255,210,60), (30,18,0),   (140,100,0)),
    ('Ice',      (2,5,15),    (0,200,255),  (0,160,220), (0,35,55),   (80,230,255), (0,15,30),   (0,100,140)),
    ('Hot Pink', (10,2,8),    (255,50,150), (220,40,130),(50,10,30),  (255,100,180),(30,5,18),   (140,25,85)),
    ('Mono',     (0,0,0),     (220,220,220),(180,180,180),(40,40,40), (255,255,255),(20,20,20),  (100,100,100)),
)
TNAMES = ('pipboy', 'amber', 'ice', 'hotpink', 'mono')
NT = len(THEMES)

# Load saved theme
t_idx = 3  # default to Hot Pink
_cfg = system.readfile('/littlefs/config/theme.txt')
if _cfg:
    _cfg = _cfg.strip()
    for _i in range(NT):
        if TNAMES[_i] == _cfg:
            t_idx = _i
            break

# Load scanline setting
scanlines = 0
_sl = system.readfile('/littlefs/config/scanlines.txt')
if _sl:
    scanlines = 1 if _sl.strip() == '1' else 0

def apply_theme(idx):
    global BG, FG, ACC, DIM, HI, SBG, BDR, t_idx
    t_idx = idx
    t = THEMES[idx]
    BG  = c(*t[1]); FG  = c(*t[2]); ACC = c(*t[3])
    DIM = c(*t[4]); HI  = c(*t[5]); SBG = c(*t[6]); BDR = c(*t[7])

apply_theme(t_idx)
BK = c(0, 0, 0)

def save_config():
    system.writefile('/littlefs/config/theme.txt', TNAMES[t_idx])
    system.writefile('/littlefs/config/scanlines.txt', '1' if scanlines else '0')

# ── 24x24 1-bit icons ──
I={
'c':b'\x00\x00\x00\x00\x7f\x00\x01\xff\xc0\x07\xff\xf0\x0f\xff\xf8\x1f\xe3\xfc\x1f\xe3\xfc\x3f\xe3\xfe\x3f\xe3\xfe\x7f\xe3\xff\x7f\xe3\xff\x7f\xe3\xff\x7f\xe3\xff\x7f\xe1\xff\x7f\xe0\xff\x7f\xf0\x7f\x3f\xf8\x7e\x3f\xfc\xfe\x1f\xff\xfc\x1f\xff\xfc\x0f\xff\xf8\x07\xff\xf0\x01\xff\xc0\x00\x7f\x00',
'e':b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff\xc0\x07\xe3\xf0\x0f\x80\xf8\x1f\x1c\x7c\x3e\x1e\x3e\x3e\x3f\x3e\x7c\xff\x9f\x7c\xff\x9f\x7c\xff\x9f\x3e\x7f\x3e\x3e\x3e\x3e\x1f\x1c\x7c\x0f\x80\xf8\x07\xe3\xf0\x01\xff\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
's':b'\x00\x00\x00\x00\x1c\x00\x00\x3e\x00\x00\x3e\x00\x00\x7f\x00\x00\x7f\x00\x00\xff\x80\x00\xff\x80\x7f\xff\xff\x7f\xff\xff\x7f\xff\xff\x3f\xff\xfe\x1f\xff\xfc\x0f\xff\xf8\x07\xff\xf0\x03\xff\xe0\x03\xff\xe0\x03\xff\xe0\x03\xff\xe0\x07\xff\xf0\x07\xff\xf0\x07\xf7\xf0\x07\xc1\xf0\x07\x00\x70',
'g':b'\x00\x00\x00\x00\x7f\x00\x01\x9c\xc0\x07\xff\xf0\x0f\xff\xf8\x1f\xff\xfc\x1f\xff\xfc\x3f\xff\xfe\x3f\xff\xfe\x7f\xff\xff\x7e\xff\xbf\x7f\xff\xff\x7f\xff\xff\x7f\xff\xff\x7e\xff\xbf\x7f\xff\xff\x3f\xff\xfe\x3f\xff\xfe\x1f\xff\xfc\x1f\xff\xfc\x0f\xff\xf8\x07\xff\xf0\x01\x9c\xc0\x00\x7f\x00',
'b':b'\x00\x00\x00\x00\x01\x80\x00\x03\x80\x00\x07\x80\x00\x0f\x00\x00\x1f\x00\x00\x3f\x00\x00\x7e\x00\x00\xfe\x00\x01\xfe\x00\x03\xff\xfc\x07\xff\xfc\x0f\xff\xf8\x1f\xff\xf0\x1f\xff\xe0\x00\x3f\xc0\x00\x3f\x80\x00\x3f\x00\x00\x7e\x00\x00\x7c\x00\x00\x78\x00\x00\xf0\x00\x00\xe0\x00\x00\xc0\x00',
'f':b'\x00\x00\x00\x00\x1c\x00\x00\x1e\x00\x00\x0f\x00\x00\x1f\x80\x00\x1f\x80\x00\x3f\xc0\x00\x7f\xc0\x00\xff\xc0\x01\xe7\xe0\x03\xe1\xf0\x03\xf1\xf0\x0f\xf8\xf0\x0f\xf8\xf8\x1f\xf0\xf8\x1f\xe0\xf8\x1f\xc0\xf8\x1f\x80\x38\x0f\x80\x38\x0f\x80\x30\x07\x80\x30\x03\x80\x60\x01\xc1\xc0\x00\xff\x80',
'h':b'\x00\x00\x00\x00\x1c\x00\x00\x3e\x00\x00\x7f\x00\x00\xff\x80\x01\xff\xc0\x03\xff\xe0\x07\xff\xf0\x0f\xff\xf8\x1f\xff\xfc\x3f\xff\xfe\x7f\xff\xff\x7f\xff\xff\x0f\xff\xf8\x0f\xff\xf8\x0f\xff\xf8\x0f\xff\xf8\x0f\xc1\xf8\x0f\xc1\xf8\x0f\xc1\xf8\x0f\xc1\xf8\x0f\xc1\xf8\x0f\xc1\xf8\x07\xc1\xf0',
'd':b'\x00\x00\x00\x3f\xe3\xfe\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x3f\xe3\xfe\x00\x00\x00\x3f\xe3\xfe\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x7f\xf7\xff\x3f\xe3\xfe',
}
IM={'clock':'c','digi':'c','eye':'e','laby':'s','pac':'f','wolf':'b','tilt':'g'}

# ── App discovery ──
APPS_DIR = '/littlefs/apps'
ICONS_DIR = '/littlefs/apps/icons'
apps = []
try:
    files = system.listdir(APPS_DIR)
    files.sort()
    for f in files:
        if f.endswith('.py') and f != 'launcher.py' and f != 'icons.py':
            name = f[:-3].replace('_', ' ')
            apps.append((name, APPS_DIR + '/' + f))
except:
    pass

# ── Load custom icons (separate from discovery so errors don't hide apps) ──
app_icons = {}
for _n, _p in apps:
    try:
        _bn = _p.split('/')[-1][:-3]
        _ico = system.readbytes(ICONS_DIR + '/' + _bn + '.icon')
        if _ico and len(_ico) == 72:
            app_icons[_bn] = _ico
    except:
        pass

def gi(name):
    n = name.lower()
    for k in IM:
        if k in n:
            return IM[k]
    return 'd'

# ── Pet stats (global, always active) ──
DECAY_HUNGRY_MS = 300000;  DECAY_HUNGRY_AMT = 20   # 5 min, -2%
DECAY_SLEEP_MS  = 240000;  DECAY_SLEEP_AMT  = 50   # 4 min, -5%
DECAY_HAPPY_MS  = 300000;  DECAY_HAPPY_AMT  = 50   # 5 min, -5%
DECAY_CLEAN_MS  = 360000;  DECAY_CLEAN_AMT  = 70   # 6 min, -7%
BOOST = 69
TELEM_MS = 30000
STATS_FILE = '/littlefs/config/pet_stats.txt'

def save_pet_stats():
    """Persist stats + system ticks to filesystem."""
    data = '%d,%d,%d,%d,%d,%d' % (p_hungry, p_sleep, p_happy, p_clean,
                                   1 if p_dead else 0, time.ticks_ms())
    system.writefile(STATS_FILE, data)

def load_pet_stats():
    """Load stats from file and apply decay for elapsed time. Returns True if loaded."""
    raw = system.readfile(STATS_FILE)
    if not raw:
        return False
    try:
        parts = raw.strip().split(',')
        if len(parts) < 6:
            return False
        h, s, hp, cl, dead, saved_t = int(parts[0]), int(parts[1]), int(parts[2]), \
                                       int(parts[3]), int(parts[4]), int(parts[5])
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, saved_t)
        if elapsed < 0:
            elapsed = 0  # ticks wrapped or reboot
        # Apply decay for time spent in mini-app
        if not dead:
            n = elapsed // DECAY_HUNGRY_MS
            if n > 0: h = max(0, h - DECAY_HUNGRY_AMT * n)
            n = elapsed // DECAY_SLEEP_MS
            if n > 0: s = max(0, s - DECAY_SLEEP_AMT * n)
            n = elapsed // DECAY_HAPPY_MS
            if n > 0: hp = max(0, hp - DECAY_HAPPY_AMT * n)
            n = elapsed // DECAY_CLEAN_MS
            if n > 0: cl = max(0, cl - DECAY_CLEAN_AMT * n)
            if h <= 0:
                dead = 1
        return (h, s, hp, cl, dead == 1)
    except:
        return False

# Load persisted stats. If we have saved stats (from a previous INIT sync),
# resume telemetry immediately — don't block waiting for INIT on app restart.
# Server INIT will override when it arrives.
_loaded = load_pet_stats()
if _loaded:
    p_hungry, p_sleep, p_happy, p_clean, p_dead = _loaded
    has_local_stats = True
    pet_inited = True  # resume telemetry with local stats
else:
    p_hungry = 800; p_sleep = 800; p_happy = 800; p_clean = 800
    p_dead = False
    has_local_stats = False
    pet_inited = False  # first boot — wait for server INIT

last_dh = time.ticks_ms()
last_ds = time.ticks_ms()
last_dp = time.ticks_ms()
last_dc = time.ticks_ms()
last_telem = 0

def _jval(s, key):
    """Extract numeric (int/float) or string value for a key from a JSON-ish string."""
    i = s.find('"' + key + '"')
    if i < 0: return None
    i = s.find(':', i)
    if i < 0: return None
    i += 1
    while i < len(s) and s[i] == ' ': i += 1
    if i >= len(s): return None
    if s[i] == '"':
        e = s.find('"', i + 1)
        return s[i+1:e] if e > 0 else None
    e = i
    while e < len(s) and s[e] not in ',} ':
        e += 1
    tok = s[i:e]
    try: return float(tok)
    except: return tok

def _sync_stats(srv_h, srv_s, srv_c, srv_p, srv_dead):
    """Compare server stats with local, log discrepancies, apply server values."""
    global p_hungry, p_sleep, p_happy, p_clean, p_dead
    local = (p_hungry, p_sleep, p_happy, p_clean, p_dead)
    server = (srv_h, srv_s, srv_c, srv_p, srv_dead)
    names = ('hungry', 'sleep', 'happy', 'clean', 'dead')
    diffs = []
    for i in range(5):
        if local[i] != server[i]:
            if i < 4:
                diffs.append('%s: %d.%d->%d.%d' % (names[i],
                    local[i] // 10, local[i] % 10,
                    server[i] // 10, server[i] % 10))
            else:
                diffs.append('%s: %s->%s' % (names[i], str(local[i]), str(server[i])))
    if diffs:
        print('[sync] server override:', ', '.join(diffs))
    else:
        print('[sync] local matches server')
    p_hungry, p_sleep, p_happy, p_clean, p_dead = server

def handle_init(line):
    """Parse INIT: payload, sync with local stats (server wins), update immediately."""
    global pet_inited, prev_mood, has_local_stats, connection_needed, state
    global last_dh, last_ds, last_dp, last_dc
    # line is like: "INIT: {\"status\":\"OK\",...}"
    j = line.find('{')
    if j < 0: return
    payload = line[j:]

    # Check for REPROVISION_NEEDED (uses "action" key) — handled at C level,
    # just lock the UI here so eyes/stats don't show during reprovision
    if 'REPROVISION_NEEDED' in payload:
        state = 4  # reprovision state — C shows error screen
        pet_inited = False
        print('[init] REPROVISION_NEEDED - UI locked')
        return

    status = _jval(payload, 'status')

    # USER_CONNECTION_NEEDED — show QR, stay locked until valid INIT
    if status == 'USER_CONNECTION_NEEDED':
        connection_needed = True
        pet_inited = False
        state = 3
        print('[init] USER_CONNECTION_NEEDED - showing QR')
        return

    # Valid statuses that mean a user is connected
    if status == 'OK':
        fi = _jval(payload, 'feed_index')
        si = _jval(payload, 'sleep_index')
        ci = _jval(payload, 'clean_index')
        pi = _jval(payload, 'pet_index')
        srv_h = int(fi * 10) if isinstance(fi, (int, float)) else 800
        srv_s = int(si * 10) if isinstance(si, (int, float)) else 800
        srv_c = int(ci * 10) if isinstance(ci, (int, float)) else 800
        srv_p = int(pi * 10) if isinstance(pi, (int, float)) else 800
        _sync_stats(srv_h, srv_s, srv_c, srv_p, False)
        pet_inited = True
        _now = time.ticks_ms()
        last_dh = _now; last_ds = _now; last_dp = _now; last_dc = _now
        save_pet_stats()
    elif status == 'RESURRECTION_NEEDED':
        _sync_stats(0, 0, 0, 0, True)
        pet_inited = True
        save_pet_stats()
    elif status == 'NOT_FOUND':
        _sync_stats(800, 800, 800, 800, False)
        pet_inited = True
        _now = time.ticks_ms()
        last_dh = _now; last_ds = _now; last_dp = _now; last_dc = _now
        save_pet_stats()
    else:
        return  # unknown status — don't change UI state

    # Valid INIT received — exit QR/reprovision screen if active
    if connection_needed or state == 3 or state == 4:
        connection_needed = False
        state = 0
        print('[init] User connected - resuming normal UI')
    has_local_stats = True
    prev_mood = -1

def get_mood():
    """Map pet stats to emotion index: 0=normal,1=happy,2=sad,3=angry,5=sleepy"""
    if p_dead: return 2
    lowest = min(p_hungry, p_sleep, p_happy, p_clean)
    if lowest < 200: return 3    # angry (critical)
    if p_sleep < 350: return 5   # sleepy
    if p_hungry < 350: return 2  # sad (hungry)
    if lowest > 600: return 1    # happy
    return 0                     # normal

def stat_col(v):
    if v > 600: return FG
    if v > 300: return ACC
    return c(255, 50, 50)

def pet_update():
    global p_hungry, p_sleep, p_happy, p_clean, p_dead
    global last_dh, last_ds, last_dp, last_dc, last_telem

    now = time.ticks_ms()

    # Stat decay (only after stats are initialized)
    if not p_dead and pet_inited:
        n = time.ticks_diff(now, last_dh) // DECAY_HUNGRY_MS
        if n > 0:
            p_hungry = max(0, p_hungry - DECAY_HUNGRY_AMT * n); last_dh = now
        n = time.ticks_diff(now, last_ds) // DECAY_SLEEP_MS
        if n > 0:
            p_sleep = max(0, p_sleep - DECAY_SLEEP_AMT * n); last_ds = now
        n = time.ticks_diff(now, last_dp) // DECAY_HAPPY_MS
        if n > 0:
            p_happy = max(0, p_happy - DECAY_HAPPY_AMT * n); last_dp = now
        n = time.ticks_diff(now, last_dc) // DECAY_CLEAN_MS
        if n > 0:
            p_clean = max(0, p_clean - DECAY_CLEAN_AMT * n); last_dc = now
        if p_hungry <= 0:
            p_dead = True

    # Drain MQTT log — handle INIT and ACTION responses
    while mqtt.log_count() > 0:
        line = mqtt.log_read()
        if not line: continue
        if 'INIT:' in line:
            handle_init(line)
        elif 'ACTION' in line:
            if 'FEED_OK' in line:
                p_hungry = min(1000, p_hungry + BOOST)
                trigger_hearts()
            elif 'SLEEP_OK' in line:
                p_sleep = min(1000, p_sleep + BOOST)
            elif 'PET_OK' in line:
                p_happy = min(1000, p_happy + BOOST)
                trigger_hearts()
            elif 'CLEAN_OK' in line:
                p_clean = min(1000, p_clean + BOOST)
                trigger_hearts()

    # Telemetry + persist stats (only after stats are initialized —
    # prevents overwriting server stats with defaults on clean flash)
    if pet_inited and mqtt.connected() and time.ticks_diff(now, last_telem) >= TELEM_MS:
        mqtt.send_telemetry(p_hungry / 10.0, p_sleep / 10.0, p_clean / 10.0, p_happy / 10.0)
        save_pet_stats()
        last_telem = now

def pet_cmd(cmd):
    """Send a pet command via MQTT if connected and alive."""
    if not p_dead and mqtt.connected():
        mqtt.send_command(cmd)

# ── Eye sprite system ──

# Emotion sprites: index → filename (loaded from /littlefs/apps/eyes/)
EMO_FILES = (
    'EyesClassic.bin',   # 0 = neutral
    'EyesHeart.bin',     # 1 = hearts (interaction)
    'EyesClosed.bin',    # 2 = happy/closed
    'EyesSleepy.bin',    # 3 = sleepy
    'EyesTeary.bin',     # 4 = teary (sad)
    'EyesCrying.bin',    # 5 = crying (dead)
    'EyesSpiral.bin',    # 6 = spiral (critical)
)
NE = len(EMO_FILES)
EYES_DIR = '/littlefs/apps/eyes/'
EYE_W, EYE_H = 280, 240

# Current loaded sprite
cur_emo = -1
eye_buf = None

# Blink state
bl = 0; bl_t = 0; nbl = 0
prev_mood = -1

# Interaction boost timer (hearts emotion)
heart_until = 0

# Frame counter (used for sync dot blink + periodic GC)
fr = 0

def load_eye(idx):
    """Load a 4-bit grayscale eye sprite — try embedded flash first, then LittleFS."""
    global cur_emo, eye_buf
    if idx == cur_emo and eye_buf:
        return
    fname = EMO_FILES[idx]
    # Try embedded firmware data first (no filesystem needed)
    data = system.eye_data(fname)
    if not data:
        # Fallback to LittleFS (for custom/user-uploaded eyes)
        data = system.readbytes(EYES_DIR + fname)
    if data:
        eye_buf = data
        cur_emo = idx
    else:
        eye_buf = None
        cur_emo = -1

def draw_eyes():
    """Blit the current eye sprite with theme coloring."""
    if eye_buf:
        display.gray4(0, 0, EYE_W, EYE_H, eye_buf, FG, BG)

def update_eyes():
    global bl, bl_t, nbl, prev_mood

    now = time.ticks_ms()

    # Check for interaction hearts (temporary override)
    if now < heart_until:
        mood_emo = 1  # hearts
    else:
        mood = get_mood()
        # Map mood → sprite index
        if mood == 0:   mood_emo = 0  # neutral → classic
        elif mood == 1: mood_emo = 0  # happy → classic (closed is blink only)
        elif mood == 2: mood_emo = 4  # sad → teary
        elif mood == 3: mood_emo = 6  # angry/critical → spiral
        elif mood == 5: mood_emo = 3  # sleepy
        else:           mood_emo = 0

    # Handle blink: swap to closed eyes briefly
    if bl == 0 and time.ticks_diff(now, nbl) > 0:
        bl = 6; bl_t = now
    if bl > 0 and time.ticks_diff(now, bl_t) > 40:
        bl -= 1; bl_t = now
        if bl == 0:
            nbl = now + 2000 + (now % 2500)

    # During blink, show closed eyes
    if bl > 0 and bl <= 4:
        target_emo = 2  # closed
    else:
        target_emo = mood_emo

    if target_emo != prev_mood:
        load_eye(target_emo)
        prev_mood = target_emo

def trigger_hearts(duration_ms=2000):
    """Show heart eyes for a duration after interaction."""
    global heart_until
    heart_until = time.ticks_ms() + duration_ms

# ── Drawing helpers ──
_CM = b'\x28\x1f\x1c\x19\x17\x15\x13\x11\x10\x0f\x0e\x0c\x0b\x0b\x0a\x09\x08\x07\x07\x06\x05\x05\x04\x04\x03\x03\x03\x02\x02\x02\x01\x01\x01\x01'
CR = len(_CM)

SL = _CM[6] + 2
SR = SL
ST = 4
SB = ST

def draw_corners():
    for i in range(CR):
        m = _CM[i]
        if m > 0:
            display.rect_filled(0, i, m, 1, BK)
            display.rect_filled(W - m, i, m, 1, BK)
            display.rect_filled(0, H - 1 - i, m, 1, BK)
            display.rect_filled(W - m, H - 1 - i, m, 1, BK)

def draw_bezel():
    bw = 2
    display.rect_filled(CR, 0, W - CR * 2, bw, BDR)
    display.rect_filled(CR, H - bw, W - CR * 2, bw, BDR)
    display.rect_filled(0, CR, bw, H - CR * 2, BDR)
    display.rect_filled(W - bw, CR, bw, H - CR * 2, BDR)
    for i in range(CR):
        m = _CM[i]
        display.rect_filled(m, i, bw, 1, BDR)
        display.rect_filled(W - m - bw, i, bw, 1, BDR)
        display.rect_filled(m, H - 1 - i, bw, 1, BDR)
        display.rect_filled(W - m - bw, H - 1 - i, bw, 1, BDR)
        if i > 0 and _CM[i] < _CM[i - 1]:
            display.rect_filled(m, i, _CM[i - 1] - m, bw, BDR)
            display.rect_filled(W - _CM[i - 1], i, _CM[i - 1] - m, bw, BDR)
            display.rect_filled(m, H - 1 - i, _CM[i - 1] - m, bw, BDR)
            display.rect_filled(W - _CM[i - 1], H - 1 - i, _CM[i - 1] - m, bw, BDR)

def draw_scanlines():
    if not scanlines:
        return
    for y in range(ST + 2, H - ST, 3):
        display.line(ST, y, W - ST - 1, y, DIM)

def draw_status():
    pass  # status bar removed — clean face screen

def _draw_sync_dot(x, y):
    """Draw a blinking dot to indicate waiting for server sync."""
    if (fr // 8) % 2:
        display.rect_filled(x, y, 5, 5, ACC)

def _draw_stat(x, y, label, val, right_edge=0):
    """Draw a single stat: label + value, with a sync dot next to label if not yet synced.
    If right_edge > 0, right-align the value text against that x coordinate."""
    display.text(x, y, label, 1, ACC)
    if not pet_inited:
        if right_edge:
            _draw_sync_dot(x - 9, y + 5)
        else:
            _draw_sync_dot(x + len(label) * 12 + 4, y + 5)
    if has_local_stats or pet_inited:
        vt = '%d.%d%%' % (val // 10, val % 10)
        vx = right_edge - len(vt) * 18 if right_edge else x
        display.text(vx, y + 18, vt, 2, stat_col(val))

def draw_pet_stats():
    """Draw pet stats around the face screen.
    Shows local LittleFS values immediately with a sync bar until server INIT.
    If no local stats exist, shows only the sync animation."""
    ty = ST + 18
    by = H - 52
    re = W - SR - 2  # right edge for right-aligned stats
    _draw_stat(SL + 2,       ty, 'Hunger', p_hungry)
    _draw_stat(W - SR - 42,  ty, 'Sleep',  p_sleep,  re)
    _draw_stat(SL + 2,       by, 'Happy',  p_happy)
    _draw_stat(W - SR - 42,  by, 'Clean',  p_clean,  re)

    # Dead overlay
    if p_dead:
        display.text(W // 2 - 40, H // 2 - 6, 'X    X', 2, c(255, 50, 50))
        display.text(W // 2 - 30, H // 2 + 30, 'PET DIED!', 2, c(255, 50, 50))



# ── Grid constants (3x2 paged) ──
GCOLS = 3
GROWS = 2
PER_PAGE = GCOLS * GROWS
GRID_TOP = 34
GRID_BOT = H - CR - 18
CELL_W = (W - SL - SR) // GCOLS
CELL_H = (GRID_BOT - GRID_TOP) // GROWS
grid_page = 0

def draw_grid(sel):
    na = len(apps)
    if na == 0:
        display.text(W // 2 - 54, H // 2 - 10, 'No Apps', 2, DIM)
        return

    n_pages = (na + PER_PAGE - 1) // PER_PAGE
    page = grid_page
    start = page * PER_PAGE
    end = min(start + PER_PAGE, na)

    # Title
    display.text(SL + 4, 6, 'Apps', 1, ACC)

    for idx in range(start, end):
        li = idx - start
        row = li // GCOLS
        col = li % GCOLS
        cx = SL + col * CELL_W
        cy = GRID_TOP + row * CELL_H
        is_sel = idx == sel

        if is_sel:
            display.rect_filled(cx + 2, cy + 2, CELL_W - 4, CELL_H - 4, SBG)
            display.rect(cx + 1, cy + 1, CELL_W - 2, CELL_H - 2, ACC)

        # Icon
        basename = apps[idx][1].split('/')[-1][:-3]
        if basename in app_icons:
            ico = app_icons[basename]
        else:
            ico = I[gi(apps[idx][0])]
        ix = cx + (CELL_W - 24) // 2
        iy = cy + 8
        display.bitmap(ix, iy, 24, 24, ico, FG if is_sel else ACC)

        # Label
        label = apps[idx][0]
        if len(label) > 8:
            label = label[:8]
        lx = cx + (CELL_W - len(label) * 6) // 2
        ly = cy + CELL_H - 16
        display.text(lx, ly, label, 0, FG if is_sel else ACC)

    # Grid lines
    for ci in range(1, GCOLS):
        gx = SL + ci * CELL_W
        display.line(gx, GRID_TOP, gx, GRID_BOT - 1, DIM)
    if end - start > GCOLS:
        display.line(SL, GRID_TOP + CELL_H, W - SR - 1, GRID_TOP + CELL_H, DIM)

    # Page dots
    if n_pages > 1:
        dot_y = GRID_BOT + 8
        total_w = n_pages * 10 - 4
        dot_x = (W - total_w) // 2
        for p in range(n_pages):
            px = dot_x + p * 10
            if p == page:
                display.rect_filled(px, dot_y, 6, 6, FG)
            else:
                display.rect(px, dot_y, 6, 6, DIM)

N_SET = NT + 2

def draw_settings(sel):
    display.rect_filled(SL, GRID_TOP, W - SL - SR, GRID_BOT - GRID_TOP, SBG)
    display.text(SL + 8, GRID_TOP + 6, 'SETTINGS', 1, ACC)
    display.line(SL, GRID_TOP + 22, W - SR, GRID_TOP + 22, DIM)

    rh = 30
    oy = GRID_TOP + 26

    for i in range(NT):
        y = oy + i * rh
        is_sel = i == sel
        if is_sel:
            display.rect_filled(SL + 2, y + 1, W - SL - SR - 4, rh - 2, BDR)
            display.rect_filled(SL + 2, y + 1, 4, rh - 2, ACC)
        nm = THEMES[i][0]
        if i == t_idx:
            nm = '> ' + nm
        display.text(SL + 12, y + 10, nm, 1, FG if is_sel else DIM)
        sw_c = c(*THEMES[i][2])
        display.rect_filled(W - SR - 50, y + 8, 34, 14, sw_c)

    y = oy + NT * rh
    is_sl = sel == NT
    if is_sl:
        display.rect_filled(SL + 2, y + 1, W - SL - SR - 4, rh - 2, BDR)
        display.rect_filled(SL + 2, y + 1, 4, rh - 2, ACC)
    sl_txt = 'Scanlines: ' + ('ON' if scanlines else 'OFF')
    display.text(SL + 12, y + 10, sl_txt, 1, FG if is_sl else DIM)

    y = oy + (NT + 1) * rh
    is_wf = sel == NT + 1
    if is_wf:
        display.rect_filled(SL + 2, y + 1, W - SL - SR - 4, rh - 2, BDR)
        display.rect_filled(SL + 2, y + 1, 4, rh - 2, ACC)
    display.text(SL + 12, y + 10, 'Change WiFi', 1, FG if is_wf else DIM)

# ── State machine ──
# States: 0=FACE, 1=GRID, 2=SETTINGS, 3=CONNECTION_NEEDED (QR), 4=REPROVISION (C screen)
state = 0
connection_needed = False
_qr_url = 'https://opengotchi.pet/connect?deviceHash=' + mqtt.hash()
sel = 0
set_sel = 0
prev_g = 'none'
_state_t = 0

load_eye(0)  # Load neutral eyes at startup
nbl = time.ticks_ms() + 2500

# Wait for all buttons released and drain touch events
for _drain in range(30):
    _g = touch.gesture()
    if not buttons.any():
        break
    time.sleep_ms(30)

_bp = [False, False, False, False]
_startup = 5
_lr_hold_start = 0

def btn_edge(n):
    cur = buttons.pressed(n)
    was = _bp[n - 1]
    _bp[n - 1] = cur
    return cur and not was

gc.collect()

# ── Main loop ──
while True:
    now = time.ticks_ms()
    g = touch.gesture()
    b1 = btn_edge(1); b2 = btn_edge(2); b3 = btn_edge(3); b4 = btn_edge(4)

    if _startup > 0:
        _startup -= 1
        g = 'none'
        b1 = b2 = b3 = b4 = False

    # L+R hold 10s = forget WiFi (hardware escape hatch)
    if buttons.pressed(1) and buttons.pressed(4):
        if _lr_hold_start == 0:
            _lr_hold_start = now
        elif time.ticks_diff(now, _lr_hold_start) > 10000:
            display.clear(BG)
            display.text(SL + 8, GRID_TOP + 40, 'Forgetting WiFi...', 1, ACC)
            display.text(SL + 8, GRID_TOP + 60, 'Restarting...', 1, FG)
            display.flush()
            wifi.forget()
    else:
        _lr_hold_start = 0

    # Pet system runs every frame (even in GRID/SETTINGS)
    pet_update()
    update_eyes()

    # Gesture handling (600ms cooldown after state change)
    # State 3/4 (connection needed / reprovision) blocks all input
    if state >= 3:
        pass
    elif g != 'none' and time.ticks_diff(now, _state_t) > 600:
        if state == 0:  # FACE
            if g == 'swipe_down':
                state = 1; sel = 0; _state_t = now
                buzzer.click()
            elif g == 'swipe_up' or g == 'long_press':
                state = 2; set_sel = 0; _state_t = now
                buzzer.click()
        elif state == 1:  # GRID
            if g == 'swipe_up':
                state = 0; _state_t = now
                buzzer.click()
            elif g == 'swipe_left' and grid_page < ((len(apps) + PER_PAGE - 1) // PER_PAGE) - 1:
                grid_page += 1; sel = grid_page * PER_PAGE
                buzzer.click()
            elif g == 'swipe_left':
                state = 0; _state_t = now
                buzzer.click()
            elif g == 'swipe_right' and grid_page > 0:
                grid_page -= 1; sel = grid_page * PER_PAGE
                buzzer.click()
            elif g == 'press':
                tp = touch.pos()
                if tp:
                    tc = (tp[0] - SL) // CELL_W
                    tr = (tp[1] - GRID_TOP) // CELL_H
                    if 0 <= tc < GCOLS and 0 <= tr < GROWS:
                        idx = grid_page * PER_PAGE + tr * GCOLS + tc
                        if idx < len(apps):
                            buzzer.click()
                            save_pet_stats()
                            system.launch(apps[idx][1])
        elif state == 2:  # SETTINGS
            if g == 'swipe_up' or g == 'swipe_left':
                state = 0; _state_t = now
                buzzer.click()
            elif g == 'swipe_down':
                if set_sel < N_SET - 1:
                    set_sel += 1
                    buzzer.click()
            elif g == 'press':
                if set_sel < NT:
                    apply_theme(set_sel)
                    save_config()
                elif set_sel == NT:
                    scanlines = 1 - scanlines
                    save_config()
                else:
                    display.clear(BG)
                    display.text(SL + 8, GRID_TOP + 40, 'Forgetting WiFi...', 1, ACC)
                    display.text(SL + 8, GRID_TOP + 60, 'Restarting...', 1, FG)
                    display.flush()
                    wifi.forget()
                buzzer.click()
    prev_g = g

    # Button handling (state 3/4 blocks all input)
    if state >= 3:
        pass
    elif state == 0:  # FACE — pet commands
        if b1:
            pet_cmd('feed'); buzzer.click()
        if b2:
            pet_cmd('sleep'); buzzer.click()
        if b3:
            pet_cmd('pet'); buzzer.click()
        if b4:
            pet_cmd('clean'); buzzer.click()
    elif state == 1:  # GRID
        na = len(apps)
        n_pages = (na + PER_PAGE - 1) // PER_PAGE if na > 0 else 1
        if b1 and grid_page > 0:
            grid_page -= 1
            sel = grid_page * PER_PAGE
            buzzer.click()
        elif b4 and grid_page < n_pages - 1:
            grid_page += 1
            sel = grid_page * PER_PAGE
            buzzer.click()
        elif b2:
            if sel > grid_page * PER_PAGE:
                sel -= 1
                buzzer.click()
            elif grid_page > 0:
                grid_page -= 1
                sel = min((grid_page + 1) * PER_PAGE - 1, na - 1)
                buzzer.click()
        elif b3:
            if sel + 1 < min((grid_page + 1) * PER_PAGE, na):
                sel += 1
                buzzer.click()
            elif grid_page < n_pages - 1:
                grid_page += 1
                sel = grid_page * PER_PAGE
                buzzer.click()
    elif state == 2:  # SETTINGS
        if b4:
            state = 0; _state_t = now
            buzzer.click()
        if b2 and set_sel > 0:
            set_sel -= 1
            buzzer.click()
        if b3 and set_sel < N_SET - 1:
            set_sel += 1
            buzzer.click()
        if b1:
            if set_sel < NT:
                apply_theme(set_sel)
                save_config()
            elif set_sel == NT:
                scanlines = 1 - scanlines
                save_config()
            else:
                display.clear(BG)
                display.text(SL + 8, GRID_TOP + 40, 'Forgetting WiFi...', 1, ACC)
                display.text(SL + 8, GRID_TOP + 60, 'Restarting...', 1, FG)
                display.flush()
                wifi.forget()
            buzzer.click()

    # ── Draw ──
    if state == 4:
        # Reprovision needed — draw error screen, skip all normal UI
        # Scale 0 = 6px/char, scale 1 = 12px/char. Screen = 280px.
        display.clear(0x0000)
        display.text(10, 30, 'Reprovision', 2, c(255, 60, 60))
        display.text(10, 58, 'Device', 2, c(255, 60, 60))
        display.text(10, 100, 'If you own this', 0, c(200, 200, 200))
        display.text(10, 114, 'device, open your', 0, c(200, 200, 200))
        display.text(10, 128, 'dashboard and click', 0, c(200, 200, 200))
        display.text(10, 142, 'Re-provision button.', 0, c(200, 200, 200))
        display.text(10, 170, 'Retrying every 5 min...', 0, c(80, 80, 100))
        display.text(10, 220, 'gotchiOS', 0, c(60, 60, 75))
        display.flush()
        time.sleep_ms(500)
    elif state == 3:
        # Connection needed — show QR code on white bg, skip all other UI
        display.clear(0x0000)
        display.text((W - 15 * 12) // 2, 2, 'Scan to Connect', 1, ACC)
        _qr_s = 4
        _qr_mods = 33
        _qr_px = _qr_mods * _qr_s
        _qz = _qr_s * 2
        _qr_total = _qr_px + _qz * 2
        _qr_x = (W - _qr_px) // 2
        _qr_y = (H - _qr_total) // 2 + 10
        display.rect_filled(_qr_x - _qz, _qr_y - _qz,
                            _qr_total, _qr_total, 0xFFFF)
        display.qr(_qr_x, _qr_y, _qr_url, _qr_s, 0x0000, 0xFFFF)
        _by = _qr_y + _qr_px + _qz + 2
        display.text((W - 20 * 6) // 2, _by, 'opengotchi.pet/connect', 0, DIM)
        display.flush()
    else:
        # Normal states (0-2) — clear + bezel + content
        display.clear(BG)
        draw_bezel()
        draw_status()
        if state == 0:
            draw_eyes()
            draw_pet_stats()
            wst = wifi.status()
            if wst == 'ap_portal':
                display.text(SL + 10, H - CR - 38, 'Connect to WiFi:', 0, ACC)
                display.text(SL + 10, H - CR - 26, 'gotchiOS hotspot', 0, FG)
                display.text(SL + 10, H - CR - 14, '192.168.4.1', 0, DIM)
        elif state == 1:
            draw_grid(sel)
        elif state == 2:
            draw_settings(set_sel)

        if state == 0:
            draw_scanlines()
        draw_corners()
        display.flush()

    fr += 1
    if fr % 60 == 0:
        gc.collect()

    time.sleep_ms(33)
