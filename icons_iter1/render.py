"""Иконка «75 дней». Рисуем в координатах 1024, суперсэмплинг x2, экспорт через LANCZOS.
Запуск: python3 icons/render.py [N]  (N = номер варианта для боевого экспорта в корень репо)"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
ROOT = OUT.parent
K = 2  # суперсэмплинг
PAPER='#f7f4ee'; INK='#211e19'; DARK='#2c4f3a'; MID='#3d6a4e'; GREEN='#4a7c59'
WHITE='#fffdf9'; LINE='#d6d1c7'

class C:
    def __init__(s, bg=PAPER):
        s.im = Image.new('RGB', (1024*K,)*2, bg); s.d = ImageDraw.Draw(s.im)
    def p(s, v): return [(x*K, y*K) for x, y in v]
    def circle(s, cx, cy, r, fill=None, outline=None, w=0):
        s.d.ellipse((( cx-r)*K,(cy-r)*K,(cx+r)*K,(cy+r)*K), fill=fill, outline=outline, width=w*K)
    def rr(s, box, r, fill=None, outline=None, w=0):
        s.d.rounded_rectangle([c*K for c in box], r*K, fill=fill, outline=outline, width=w*K)
    def stroke(s, pts, w, col):
        s.d.line(s.p(pts), fill=col, width=w*K, joint='curve')
        for x, y in pts: s.circle(x, y, w/2, col)
    def done(s): return s.im.resize((1024,1024), Image.Resampling.LANCZOS)

CHECK = ((0,0),(1,0),(2,0))
def chk(cx, cy, size, w, col, c, outline=None):
    """галочка с центром ограничивающей рамки в (cx,cy); size — ширина"""
    pts=[(cx-size*.5, cy+size*.02), (cx-size*.14, cy+size*.38), (cx+size*.5, cy-size*.36)]
    if outline: c.stroke(pts, w+outline*2, PAPER)
    c.stroke(pts, w, col)

def v1():  # диск с жёсткой тенью
    c=C(); c.circle(540,540,330,DARK); c.circle(500,500,330,GREEN)
    chk(500,505,350,92,WHITE,c); return c.done()
def v2():  # кольцо, галочка вырывается наружу
    c=C(); c.circle(512,520,320,None,DARK,80)
    pts=[(290,540),(440,690),(790,310)]
    c.stroke(pts,96+44,PAPER); c.stroke(pts,96,GREEN); return c.done()
def v3():  # стопка карточек
    c=C()
    c.rr((300,170,800,750),60,'#cfdacf'); c.rr((250,230,750,810),60,'#a3bda9')
    c.rr((200,290,700,870),60,WHITE,INK,26)
    chk(450,585,270,88,GREEN,c); return c.done()
def v4():  # росчерк: гигантская двухтонная галочка
    c=C(); c.stroke([(270,560),(430,740)],176,GREEN)
    c.stroke([(430,740),(790,290)],176,DARK)
    c.circle(430,740,88,DARK); return c.done()
def v5():  # три строки на тёмно-зелёной плитке
    c=C(DARK); c.rr((140,140,884,884),90,WHITE)
    for i,y in enumerate((330,512,694)):
        if i<2:
            c.rr((215,y-75,375,y+75),38,GREEN); chk(295,y,100,32,WHITE,c)
        else:
            c.rr((215,y-75,375,y+75),38,None,LINE,24)
        c.rr((430,y-36,800 if i<2 else 700,y+36),36,'#cfc9bb' if i<2 else '#e8e4da')
    return c.done()
def v6():  # страница отрывного календаря без числа
    c=C(); c.rr((190,225,860,885),70,DARK)
    c.rr((160,195,830,855),70,WHITE,INK,26)
    c.d.rounded_rectangle([x*K for x in (173,208,817,380)],57*K,fill=GREEN)
    c.d.rectangle([x*K for x in (173,300,817,380)],fill=GREEN)
    c.d.line([(173*K,380*K),(817*K,380*K)],fill=INK,width=26*K)
    for x in (340,650): c.stroke([(x,140),(x,260)],46,INK)
    chk(495,625,290,90,GREEN,c); return c.done()

VARS=[("Диск + галочка",v1),("Кольцо, галочка наружу",v2),("Стопка карточек",v3),
      ("Росчерк",v4),("Чек-лист на тёмном",v5),("Лист календаря",v6)]

def font(sz):
    for f in ('/System/Library/Fonts/Supplemental/Arial.ttf','/System/Library/Fonts/Helvetica.ttc'):
        try: return ImageFont.truetype(f,sz)
        except Exception: pass
    return ImageFont.load_default()

def rounded(im, size, r):
    im=im.resize((size,size),Image.Resampling.LANCZOS).convert('RGBA')
    m=Image.new('L',(size*4,)*2,0); ImageDraw.Draw(m).rounded_rectangle((0,0,size*4-1,size*4-1),r*4,fill=255)
    im.putalpha(m.resize((size,size),Image.Resampling.LANCZOS)); return im

def main():
    ims=[]
    for i,(n,f) in enumerate(VARS,1):
        im=f(); ims.append(im); im.resize((512,512),Image.Resampling.LANCZOS).save(OUT/f'var{i}.png')
    # контактный лист 3x2
    W,H=900,640; sh=Image.new('RGB',(W,H),'#ebe7de'); d=ImageDraw.Draw(sh); ft=font(20)
    for i,(im,(n,_)) in enumerate(zip(ims,VARS)):
        x=60+(i%3)*280; y=40+(i//3)*290
        sh.paste(rounded(im,180,40),(x,y),rounded(im,180,40))
        t=f'{i+1} · {n}'; w=d.textlength(t,font=ft); d.text((x+90-w/2,y+198),t,fill=INK,font=ft)
    sh.save(OUT/'sheet.png')
    # проверка уменьшением: 180 и 40 (40 увеличен x4 nearest для просмотра)
    ck=Image.new('RGB',(6*200+20,180+160+60),'#ebe7de')
    for i,im in enumerate(ims):
        ck.paste(rounded(im,180,40),(20+i*200,20),rounded(im,180,40))
        s=rounded(im,40,9); big=s.resize((160,160),Image.Resampling.NEAREST)
        ck.paste(big,(20+i*200,220),big); ck.paste(s,(20+i*200,400),s)
    ck.save(OUT/'check40.png')
    if len(sys.argv)>1:
        im=ims[int(sys.argv[1])-1]
        im.resize((180,180),Image.Resampling.LANCZOS).save(ROOT/'apple-touch-icon.png')
        im.resize((192,192),Image.Resampling.LANCZOS).save(ROOT/'icon-192.png')
        im.resize((512,512),Image.Resampling.LANCZOS).save(ROOT/'icon-512.png')
        im.save(ROOT/'favicon.ico',sizes=[(16,16),(32,32),(48,48)])
main()
