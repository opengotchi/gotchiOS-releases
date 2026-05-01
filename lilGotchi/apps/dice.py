import display, touch, buttons, system, time, gc, buzzer, imu, math

_rs=time.ticks_us()
def _rn():
    global _rs; _rs=(_rs*1103515245+12345)&0x7FFFFFFF; return _rs
def ri(a,b): return a+_rn()%(b-a+1)

W,H=280,240
BG=display.color(20,20,30)
WH=display.color(255,255,255)
RD=display.color(220,40,40)
GR=display.color(100,100,120)
GN=display.color(60,180,80)
YL=display.color(255,200,0)

modes=["1d6","2d6","1d20"]
mi=0
hist=[]
rolling=False
rtime=0
rval=[1]
fc=0

def pip(cx,cy,s,val):
    display.rect_filled(cx-s,cy-s,s*2,s*2,WH)
    display.rect(cx-s,cy-s,s*2,s*2,GR)
    r=max(3,s//6)
    m=s//2+2
    ps=[]
    if val==1: ps=[(0,0)]
    elif val==2: ps=[(-m,-m),(m,m)]
    elif val==3: ps=[(-m,-m),(0,0),(m,m)]
    elif val==4: ps=[(-m,-m),(m,-m),(-m,m),(m,m)]
    elif val==5: ps=[(-m,-m),(m,-m),(0,0),(-m,m),(m,m)]
    elif val==6: ps=[(-m,-m),(m,-m),(-m,0),(m,0),(-m,m),(m,m)]
    for dx,dy in ps:
        display.circle_filled(cx+dx,cy+dy,r,RD)

def d20face(cx,cy,s,val):
    display.rect_filled(cx-s,cy-s,s*2,s*2,WH)
    display.rect(cx-s,cy-s,s*2,s*2,GR)
    display.rect_filled(cx-s+4,cy-s+4,s*2-8,3,GR)
    display.rect_filled(cx-s+4,cy+s-7,s*2-8,3,GR)
    t=str(val)
    sz=3 if val<10 else 2
    tw=len(t)*sz*6
    display.text(cx-tw//2,cy-sz*4,t,sz,RD)

def draw():
    display.clear(BG)
    m=modes[mi]
    display.text(90,4,"DICE ROLLER",1,GR)
    display.text(10,22,"< "+m+" >",2,YL)
    if m=="1d6":
        pip(140,100,40,rval[0])
    elif m=="2d6":
        pip(90,100,32,rval[0])
        pip(190,100,32,rval[1] if len(rval)>1 else 1)
    elif m=="1d20":
        d20face(140,100,40,rval[0])
    if m=="2d6" and not rolling:
        t=sum(rval)
        display.text(120,148,"="+str(t),2,WH)
    if not rolling:
        display.text(70,168,"Shake or tap to roll",1,GR)
    else:
        display.text(100,168,"Rolling...",1,GN)
    if hist:
        display.rect_filled(0,190,W,2,GR)
        display.text(10,196,"Last:",1,GR)
        for i,h in enumerate(hist[-5:]):
            display.text(55+i*44,196,str(h),1,WH)
    display.flush()

def do_roll():
    global rolling, rtime
    rolling=True
    rtime=time.ticks_ms()
    buzzer.tone(800,30)

def finish_roll():
    global rolling
    rolling=False
    m=modes[mi]
    if m=="1d6":
        rval[0]=ri(1,6)
        hist.append(rval[0])
    elif m=="2d6":
        while len(rval)<2: rval.append(1)
        rval[0]=ri(1,6); rval[1]=ri(1,6)
        hist.append(rval[0]+rval[1])
    elif m=="1d20":
        rval[0]=ri(1,20)
        hist.append(rval[0])
    if len(hist)>5: hist.pop(0)
    buzzer.tone(400,80)

while True:
    g=touch.gesture()
    if g=="swipe_left" or g=="long_press":
        system.exit()
    bp1=buttons.pressed(1)
    bp2=buttons.pressed(2)
    bp3=buttons.pressed(3)
    if bp2:
        mi=(mi-1)%len(modes)
        while len(rval)<2: rval.append(1)
        buzzer.click()
    if bp3:
        mi=(mi+1)%len(modes)
        while len(rval)<2: rval.append(1)
        buzzer.click()
    shook=False
    try:
        ax,ay,az=imu.accel()
        mag=math.sqrt(ax*ax+ay*ay+az*az)
        if mag>1.8: shook=True
    except: pass
    if (bp1 or g=="tap" or shook) and not rolling:
        do_roll()
    if rolling:
        now=time.ticks_ms()
        dt=time.ticks_diff(now,rtime)
        m=modes[mi]
        if dt<900:
            if m=="1d6": rval[0]=ri(1,6)
            elif m=="2d6":
                rval[0]=ri(1,6)
                if len(rval)>1: rval[1]=ri(1,6)
            elif m=="1d20": rval[0]=ri(1,20)
            if dt%80<40: buzzer.tone(600,10)
        else:
            finish_roll()
    draw()
    fc+=1
    if fc%60==0: gc.collect()
    time.sleep_ms(33)
