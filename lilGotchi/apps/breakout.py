import display, touch, buttons, buzzer, system, time, gc, imu

W = display.WIDTH
H = display.HEIGHT
c = display.color
BK=c(0,0,0); WH=c(255,255,255); GR=c(50,50,60); DG=c(25,25,35)
YL=c(255,220,0); RD=c(255,50,50); GN=c(0,230,80); CY=c(0,200,255)
MG=c(255,0,255); OR=c(255,160,0); BL=c(80,80,255)

_rs=time.ticks_us()
def _rn():
    global _rs
    _rs=(_rs*1103515245+12345)&0x7FFFFFFF
    return _rs
def ri(a,b): return a+_rn()%(b-a+1)

def hue(n):
    h=(n*47)%360
    hi=int(h/60)%6; f=h/60-int(h/60)
    v=0.9; s=0.85
    p=v*(1-s);q=v*(1-f*s);t=v*(1-(1-f)*s)
    r,g,b=[(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)][hi]
    return c(int(r*255),int(g*255),int(b*255))

# paddle
PW=50; PH=6; PY=H-20
pw=PW  # current paddle width (changes with powerup)
px=W//2-PW//2

# ball(s): [x, y, vx, vy]
balls=[]
BR=4

# bricks: [x, y, w, h, alive, color, hits]
BC=10; BR_ROWS=5; BW=W//BC; BHT=10; BY_OFF=24
bricks=[]

def init_bricks():
    global bricks
    bricks=[]
    for r in range(BR_ROWS):
        hp = 2 if r == 0 else 1  # top row = 2 hits
        for col in range(BC):
            bricks.append([col*BW, BY_OFF+r*(BHT+2), BW-2, BHT, True, hue(r*3+col), hp])

init_bricks()

score=0; best=0; lives=3; alive=True
level=1; combo=0

s=system.readfile('/littlefs/config/break_best.txt')
if s:
    try: best=int(s.strip())
    except: pass

# power-ups: [x, y, type, active]
# types: 0=wide, 1=multi, 2=slow, 3=life, 4=laser
pups=[]
PU_COLS=[GN, MG, CY, RD, OR]
PU_SYMS=['W','M','S','+','L']

# active effects
wide_t=0; slow_t=0; laser_t=0
lasers=[]  # [x, y]

def reset_ball():
    global balls
    sp=2.5+level*0.3
    balls=[[float(px+pw//2), float(PY-10), sp*(1 if ri(0,1) else -1), -sp]]

def check_clear():
    for b in bricks:
        if b[4]: return False
    return True

def next_level():
    global level
    level+=1
    init_bricks()
    reset_ball()

reset_ball()
fr=0

while True:
    g=touch.gesture()
    if g=='swipe_left' or g=='long_press': system.exit()
    now=time.ticks_ms()

    if not alive:
        display.clear(BK)
        display.text(W//2-50,50,"GAME OVER",2,RD)
        display.text(W//2-40,90,"score: "+str(score),1,WH)
        display.text(W//2-35,115,"best: "+str(best),1,YL)
        display.text(W//2-30,140,"lvl: "+str(level),1,CY)
        display.text(W//2-45,180,"tap to retry",1,GR)
        display.flush()
        if touch.touching() or buttons.any():
            time.sleep_ms(200)
            score=0;lives=3;level=1;alive=True;combo=0
            pw=PW;wide_t=0;slow_t=0;laser_t=0
            pups=[];lasers=[]
            init_bricks(); reset_ball()
        time.sleep_ms(33); continue

    # --- expire powerups ---
    if wide_t and now>wide_t:
        wide_t=0; pw=PW
    if slow_t and now>slow_t:
        slow_t=0
    if laser_t and now>laser_t:
        laser_t=0

    # paddle control: IMU tilt + touch + buttons
    try:
        ax,_,_=imu.accel()
        if abs(ax)>0.15: px+=int((ax-0.1)*14)
    except: pass
    if touch.touching():
        tx,_=touch.pos()
        px=tx-pw//2
    if buttons.pressed(1): px-=5
    if buttons.pressed(4): px+=5
    px=max(0,min(W-pw,px))

    # laser fire
    if laser_t and now<laser_t:
        if buttons.pressed(2) or buttons.pressed(3):
            if len(lasers)<4:
                lasers.append([px+pw//2, PY-4])
                buzzer.tone(600,10)

    # update lasers
    nl=[]
    for ls in lasers:
        ls[1]-=6
        if ls[1]>0:
            hit=False
            for b in bricks:
                if not b[4]: continue
                if b[0]<=ls[0]<=b[0]+b[2] and b[1]<=ls[1]<=b[1]+b[3]:
                    b[6]-=1
                    if b[6]<=0:
                        b[4]=False
                        combo+=1; score+=combo*2
                        if ri(0,99)<20:
                            pups.append([b[0]+4,b[1]+4,ri(0,4)])
                    else:
                        b[5]=GR  # dim on damage
                    buzzer.tone(500,15); hit=True; break
            if not hit:
                nl.append(ls)
    lasers=nl

    # ball speed factor
    spf=0.6 if slow_t and now<slow_t else 1.0

    # update balls
    nb=[]
    for bl in balls:
        bl[0]+=bl[2]*spf; bl[1]+=bl[3]*spf

        # walls
        if bl[0]<=BR or bl[0]>=W-BR:
            bl[2]=-bl[2]; bl[0]=max(BR,min(W-BR,bl[0]))
        if bl[1]<=BR+20:
            bl[3]=abs(bl[3]); bl[1]=BR+20

        # paddle
        if bl[3]>0 and PY-2<=bl[1]+BR<=PY+PH and px-2<=bl[0]<=px+pw+2:
            bl[3]=-abs(bl[3])
            hit=(bl[0]-px)/pw
            bl[2]=(hit-0.5)*6
            bl[1]=PY-BR-1
            buzzer.click()
            combo=0

        # brick collision
        for b in bricks:
            if not b[4]: continue
            if b[0]<=bl[0]<=b[0]+b[2] and b[1]<=bl[1]-BR<=b[1]+b[3]+BR:
                b[6]-=1
                if b[6]<=0:
                    b[4]=False
                    combo+=1; score+=combo
                    buzzer.tone(400+combo*30,30)
                    if ri(0,99)<18:
                        pups.append([b[0]+4,b[1]+4,ri(0,4)])
                else:
                    b[5]=GR
                    buzzer.tone(300,20)
                bl[3]=-bl[3]
                break

        # floor
        if bl[1]>H:
            continue  # ball lost
        nb.append(bl)

    balls=nb
    if len(balls)==0:
        lives-=1; combo=0
        if lives<=0:
            alive=False
            if score>best:
                best=score
                system.writefile('/littlefs/config/break_best.txt',str(best))
            buzzer.tone(150,200)
        else:
            pw=PW;wide_t=0;slow_t=0;laser_t=0
            reset_ball()
            buzzer.tone(200,100)

    if alive and check_clear(): next_level()

    # update powerups
    np=[]
    for p in pups:
        p[1]+=2
        if p[1]>H: continue
        if px-2<=p[0]<=px+pw+2 and PY-4<=p[1]<=PY+8:
            pt=p[2]
            if pt==0:  # wide paddle
                pw=PW+30; wide_t=now+8000
                buzzer.tone(500,40)
            elif pt==1:  # multi-ball
                extra=[]
                for bl in balls[:2]:
                    extra.append([bl[0],bl[1],bl[2]+1.5,-abs(bl[3])])
                    extra.append([bl[0],bl[1],bl[2]-1.5,-abs(bl[3])])
                balls+=extra
                buzzer.tone(700,40)
            elif pt==2:  # slow
                slow_t=now+6000
                buzzer.tone(400,40)
            elif pt==3:  # extra life
                lives=min(lives+1,5)
                buzzer.tone(800,60)
            elif pt==4:  # laser
                laser_t=now+8000
                buzzer.tone(600,40)
            score+=25
            continue
        np.append(p)
    pups=np

    # --- draw ---
    display.clear(BK)

    # HUD
    display.rect_filled(0,0,W,18,DG)
    display.text(4,2,str(score),1,WH)
    display.text(W//2-10,2,"L"+str(level),0,CY)
    for i in range(lives):
        display.circle_filled(W-10-i*12,9,4,RD)
    if combo>1:
        display.text(60,2,str(combo)+"x",1,YL)

    # active powerup indicators
    ix=90
    if wide_t and now<wide_t:
        display.text(ix,2,"W",0,GN); ix+=10
    if slow_t and now<slow_t:
        display.text(ix,2,"S",0,CY); ix+=10
    if laser_t and now<laser_t:
        display.text(ix,2,"L",0,OR); ix+=10

    # bricks
    for b in bricks:
        if b[4]:
            display.rect_filled(b[0],b[1],b[2],b[3],b[5])
            if b[6]>1:  # multi-hit indicator
                display.rect(b[0]+1,b[1]+1,b[2]-2,b[3]-2,WH)

    # powerup drops
    for p in pups:
        display.rect_filled(p[0],p[1],8,8,PU_COLS[p[2]])
        display.text(p[0]+1,p[1],PU_SYMS[p[2]],0,BK)

    # lasers
    for ls in lasers:
        display.rect_filled(ls[0],ls[1],2,6,OR)

    # paddle
    pc=GN if wide_t and now<wide_t else (OR if laser_t and now<laser_t else WH)
    display.rect_filled(px,PY,pw,PH,pc)
    if laser_t and now<laser_t:
        display.rect_filled(px+2,PY-3,3,3,OR)
        display.rect_filled(px+pw-5,PY-3,3,3,OR)

    # balls
    for bl in balls:
        bc=CY if slow_t and now<slow_t else YL
        display.circle_filled(int(bl[0]),int(bl[1]),BR,bc)

    display.flush()
    fr+=1
    if fr%10==0: gc.collect()
    time.sleep_ms(16)
