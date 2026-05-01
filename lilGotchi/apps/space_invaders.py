import display,touch,buttons,buzzer,system,time,gc,imu
W=display.WIDTH;H=display.HEIGHT;c=display.color
BK=c(0,0,0);WH=c(255,255,255);GR=c(50,50,60)
GN=c(0,230,80);RD=c(255,50,50);YL=c(255,220,0);CY=c(0,200,255)
MG=c(255,0,255);OR=c(255,160,0);AC=[CY,GN,YL,c(255,100,180)]
_rs=time.ticks_us()
def _rn():
 global _rs;_rs=(_rs*1103515245+12345)&0x7FFFFFFF;return _rs
def ri(a,b):return a+_rn()%(b-a+1)
PW=14;PY=H-18;px=W//2-7
AW=12;AH=8;AG=4;NC=8;NR=4
bl=[];ab=[];ex=[];pups=[]
ao=10;ayo=28;ad=1;adr=0
al=[];sc=0;bs=0;lv=3;ok=True;wv=1
si=400;st=0;bcd=0;at=0
pr=0;ps=0;pt=0;ptx='';ptt=0
s=system.readfile('/littlefs/config/inv_best.txt')
if s:
 try:bs=int(s.strip())
 except:pass
def ia():
 global al,ao,ayo,ad,adr;al=[];ao=10;ayo=28;ad=1;adr=0
 for r in range(NR):
  for cl in range(NC):al.append([cl,r,True])
def xy(a):return ao+a[0]*(AW+AG),ayo+a[1]*(AH+AG)+adr
def rst():
 global sc,lv,ok,wv,si,bl,ab,ex,st,pups,pr,ps,pt
 sc=0;lv=3;ok=True;wv=1;si=400;bl=[];ab=[];ex=[];pups=[]
 pr=0;ps=0;pt=0;st=time.ticks_ms();ia()
ia();st=time.ticks_ms()
bp=[False]*4
def be(n):
 cu=buttons.pressed(n);h=cu and not bp[n-1];bp[n-1]=cu;return h
fr=0
while True:
 g=touch.gesture()
 if g=='swipe_left'or g=='long_press':system.exit()
 nw=time.ticks_ms()
 if not ok:
  display.clear(BK)
  display.text(W//2-50,50,"GAME OVER",2,RD)
  display.text(W//2-40,90,"score:"+str(sc),1,WH)
  display.text(W//2-35,115,"best:"+str(bs),1,YL)
  display.text(W//2-30,140,"wave:"+str(wv),1,CY)
  display.text(W//2-45,180,"tap to retry",1,GR)
  display.flush()
  if touch.touching()or buttons.any():time.sleep_ms(200);rst()
  time.sleep_ms(33);continue
 try:
  ax,_,_=imu.accel()
 except:
  ax=0.0
 px+=int(ax*8)
 if buttons.pressed(1):px-=5
 if buttons.pressed(4):px+=5
 px=max(0,min(W-PW,px))
 fcd=90 if nw<pr else 180
 if(be(2)or be(3))and time.ticks_diff(nw,bcd)>fcd:
  bcd=nw
  if nw<pt:bl.append([px+2,PY-2]);bl.append([px+7,PY-2]);bl.append([px+12,PY-2]);buzzer.tone(900,15)
  else:bl.append([px+7,PY-2]);buzzer.tone(800,15)
 bl[:]=[[b[0],b[1]-6]for b in bl if b[1]>0]
 ab[:]=[[b[0],b[1]+3]for b in ab if b[1]<H]
 if time.ticks_diff(nw,st)>=si:
  st=nw;mn=999;mx=0
  for a in al:
   if not a[2]:continue
   x,_=xy(a)
   if x<mn:mn=x
   if x+AW>mx:mx=x+AW
  if mx+ad>W-2 or mn+ad<2:ad=-ad;adr+=AH
  else:ao+=ad
  if time.ticks_diff(nw,at)>max(400,1400-wv*100):
   cs={}
   for a in al:
    if not a[2]:continue
    if a[0]not in cs or a[1]>cs[a[0]][1]:cs[a[0]]=a
   if cs:
    ks=list(cs.keys());a=cs[ks[ri(0,len(ks)-1)]]
    x,y=xy(a);ab.append([x+6,y+AH]);at=nw
 for b in bl[:]:
  ht=False
  for a in al:
   if not a[2]:continue
   x,y=xy(a)
   if x<=b[0]<=x+AW and y<=b[1]<=y+AH:
    a[2]=False;sc+=(NR-a[1])*10;ex.append([x+6,y+4,0])
    buzzer.tone(300,10);ht=True
    if ri(0,99)<15:pups.append([x+4,y+4,ri(0,3)])
    break
  if ht and b in bl:bl.remove(b)
 for b in ab[:]:
  if px<=b[0]<=px+PW and PY<=b[1]<=PY+8:
   ab.remove(b)
   if nw<ps:ptx='BLOCKED!';ptt=nw;buzzer.tone(600,30)
   else:
    lv-=1;buzzer.tone(150,60)
    if lv<=0:
     ok=False
     if sc>bs:bs=sc;system.writefile('/littlefs/config/inv_best.txt',str(bs))
 for a in al:
  if a[2]:
   _,y=xy(a)
   if y+AH>=PY:
    ok=False
    if sc>bs:bs=sc;system.writefile('/littlefs/config/inv_best.txt',str(bs))
    break
 np=[]
 for p in pups:
  p[1]+=2
  if p[1]>H:continue
  if px-2<=p[0]<=px+PW+2 and PY-4<=p[1]<=PY+8:
   if p[2]==0:pr=nw+8000;ptx='RAPID!';ptt=nw
   elif p[2]==1:ps=nw+10000;ptx='SHIELD!';ptt=nw
   elif p[2]==2:pt=nw+6000;ptx='TRIPLE!';ptt=nw
   elif p[2]==3:
    ptx='NUKE!';ptt=nw
    for a in al:
     if a[2]:a[2]=False;sc+=5;ex.append([xy(a)[0]+6,xy(a)[1]+4,0])
    buzzer.tone(200,150)
   buzzer.tone(500,40);sc+=25;continue
  np.append(p)
 pups=np
 clr=True
 for a in al:
  if a[2]:clr=False;break
 if clr:wv+=1;si=max(80,400-wv*40);ia()
 ex[:]=[[e[0],e[1],e[2]+1]for e in ex if e[2]<4]
 display.clear(BK)
 display.rect_filled(0,0,W,16,c(20,20,30))
 display.text(4,2,str(sc),1,WH)
 display.text(W//2-12,2,"W"+str(wv),0,CY)
 for i in range(lv):display.rect_filled(W-14-i*16,4,10,8,GN)
 if nw<pr:display.text(60,2,"R",0,OR)
 if nw<ps:display.text(72,2,"S",0,CY)
 if nw<pt:display.text(84,2,"3",0,MG)
 for a in al:
  if not a[2]:continue
  x,y=xy(a);display.rect_filled(x,y,AW,AH,AC[a[1]%4])
  display.pixel(x+3,y+3,BK);display.pixel(x+AW-4,y+3,BK)
 pc=CY if nw<ps else GN
 display.rect_filled(px,PY,PW,8,pc)
 display.rect_filled(px+6,PY-3,3,3,pc)
 if nw<ps:display.rect(px-1,PY-1,PW+2,10,CY)
 for b in bl:display.rect_filled(b[0],b[1],1,4,YL)
 for b in ab:display.rect_filled(b[0],b[1],1,4,RD)
 PC=[OR,CY,MG,RD];PS=["R","S","3","X"]
 for p in pups:
  display.rect_filled(p[0],p[1],8,8,PC[p[2]])
  display.text(p[0]+1,p[1],PS[p[2]],0,BK)
 for e in ex:display.circle(e[0],e[1],3+e[2]*2,YL)
 if ptx and time.ticks_diff(nw,ptt)<1500:
  display.text(W//2-len(ptx)*5,PY-20,ptx,1,YL)
 else:ptx=''
 display.flush()
 fr+=1
 if fr%60==0:gc.collect()
 time.sleep_ms(16)
