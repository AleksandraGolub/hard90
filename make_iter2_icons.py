from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import math, os

S=1024
OUT='icons'
os.makedirs(OUT,exist_ok=True)

paper=(247,244,238); dark=(33,30,25)
green=(74,124,89); deep=(44,79,58); light=(123,178,133); cream=(246,241,229)

def mask(): return Image.new('L',(S,S),0)
def rounded(box,r):
    m=mask(); ImageDraw.Draw(m).rounded_rectangle(box,r,fill=255); return m
def ellipse(box):
    m=mask(); ImageDraw.Draw(m).ellipse(box,fill=255); return m
def poly(points):
    m=mask(); ImageDraw.Draw(m).polygon(points,fill=255); return m
def line(points,width):
    m=mask(); d=ImageDraw.Draw(m); d.line(points,fill=255,width=width,joint='curve')
    for p in (points[0],points[-1]): d.ellipse((p[0]-width//2,p[1]-width//2,p[0]+width//2,p[1]+width//2),fill=255)
    return m
def union(*ms):
    x=mask()
    for m in ms:x=ImageChops.lighter(x,m)
    return x
def subtract(a,b): return ImageChops.subtract(a,b)
def shifted(m,x,y): return ImageChops.offset(m,x,y)
_BG=None
def bg():
    global _BG
    if _BG is None:
      im=Image.new('RGB',(S,S),paper); px=im.load()
      for y in range(S):
        for x in range(S):
          # ivory light pool, deliberately quiet
          d=((x-365)**2+(y-265)**2)**.5/S
          v=max(0,min(10,int(10-14*d)))
          px[x,y]=(min(255,paper[0]+v),min(255,paper[1]+v),min(255,paper[2]+v))
      _BG=im
    return _BG.copy()
def grad(c1,c2, vertical=True, offset=0):
    im=Image.new('RGB',(S,S)); p=im.load()
    for y in range(S):
      for x in range(S):
        t=(y/S if vertical else x/S)
        # light source upper left, a broad surface falloff
        t=max(0,min(1,t+offset - .12*(1-x/S)))
        p[x,y]=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))
    return im
def color_layer(im,m,top,bottom,shadow=(49,91,65), elev=22, rim=True):
    # long colored cast and tight contact
    cast=shifted(m,18,30).filter(ImageFilter.GaussianBlur(32))
    sh=Image.new('RGBA',(S,S),shadow+(0,)); sh.putalpha(cast.point(lambda a:int(a*.23))); im.alpha_composite(sh)
    contact=shifted(m,5,11).filter(ImageFilter.GaussianBlur(10))
    sh=Image.new('RGBA',(S,S),shadow+(0,)); sh.putalpha(contact.point(lambda a:int(a*.30))); im.alpha_composite(sh)
    # dark lower material thickness
    thick=shifted(m,0,elev); im.paste(grad(tuple(max(0,v-24) for v in top),bottom),mask=thick)
    im.paste(grad(top,bottom),mask=m)
    # rim light: upper-left exterior crescent
    if rim:
      expanded=m.filter(ImageFilter.MaxFilter(17)); outer=subtract(expanded,m)
      rim_mask=ImageChops.multiply(outer, grad((255,255,255),(15,15,15),True).convert('L'))
      hl=Image.new('RGBA',(S,S),(255,253,244,0)); hl.putalpha(rim_mask.point(lambda a:int(a*.48))); im.alpha_composite(hl)
    # wide diffused reflection within top left
    glow=Image.new('L',(S,S),0); gd=ImageDraw.Draw(glow); gd.ellipse((120,70,650,340),fill=105)
    glow=ImageChops.multiply(glow.filter(ImageFilter.GaussianBlur(56)),m)
    hi=Image.new('RGBA',(S,S),(255,255,242,0)); hi.putalpha(glow); im.alpha_composite(hi)
    return im
def spec(im,xy,r=14):
    m=ellipse((xy[0]-r,xy[1]-r,xy[0]+r,xy[1]+r)).filter(ImageFilter.GaussianBlur(3))
    q=Image.new('RGBA',(S,S),(255,255,248,0));q.putalpha(m.point(lambda a:int(a*.9)));im.alpha_composite(q)
def save(im,n): im.convert('RGB').save(f'{OUT}/iter2_v{n}.png',quality=95)

def v1(): # puffy check, a decisive tactile control
 im=bg().convert('RGBA'); tile=rounded((145,145,879,879),190); color_layer(im,tile,(239,235,222),(207,220,199),(81,113,84),24)
 # recessed well and raised check
 well=rounded((247,270,777,750),130); inn=Image.new('RGBA',(S,S),(60,102,74,0)); inn.putalpha(well.filter(ImageFilter.GaussianBlur(5)).point(lambda a:int(a*.37)));im.alpha_composite(inn)
 ck=line([(330,520),(465,657),(690,388)],105); color_layer(im,ck,(124,190,134),(51,111,72),(37,76,52),18)
 spec(im,(395,452),12); save(im,1)
def v2(): # ceramic leaf, discipline/growth
 im=bg().convert('RGBA'); leaf=ellipse((220,166,785,842)); # pointed leaf by adding tip, cutting right side character
 leaf=union(leaf,poly([(440,165),(676,287),(540,715),(295,792)]))
 color_layer(im,leaf,(126,190,135),(49,112,72),(55,88,62),30)
 # central embossed vein
 vein=line([(390,694),(493,495),(602,304)],35); color_layer(im,vein,(179,221,169),(89,147,94),(42,83,56),7,True)
 # side cut veins tasteful low detail
 for a,b in [((484,510),(350,458)),((510,458),(651,435)),((455,566),(343,541))]:
  vm=line([a,b],18); x=Image.new('RGBA',(S,S),(205,230,190,0));x.putalpha(vm.point(lambda z:int(z*.55)));im.alpha_composite(x)
 spec(im,(415,290),17);save(im,2)
def v3(): # stacked habit tiles; stack literally conveys daily accumulation
 im=bg().convert('RGBA')
 for b,c,e in [((238,400,760,775),(100,154,106),18),((275,300,797,675),(80,135,91),18)]: color_layer(im,rounded(b,106),tuple(min(255,x+55) for x in c),c,(61,91,61),e)
 top=rounded((314,205,836,580),106);color_layer(im,top,(156,207,151),(64,130,82),(47,83,57),22)
 # stamped check on top only
 ck=line([(425,390),(521,477),(696,300)],72);color_layer(im,ck,(244,241,225),(201,224,192),(66,103,68),10)
 spec(im,(442,281),10);save(im,3)
def v4(): # thick silicone ring with inset check token
 im=bg().convert('RGBA'); outer=ellipse((161,161,863,863)); inner=ellipse((314,314,710,710)); ring=subtract(outer,inner)
 color_layer(im,ring,(132,194,139),(45,103,68),(48,85,60),29)
 # bottom-right inset token (positive completion)
 token=ellipse((483,483,779,779));color_layer(im,token,(245,239,222),(209,227,200),(56,96,64),16)
 ck=line([(552,628),(606,681),(711,562)],49);color_layer(im,ck,(99,170,104),(42,103,65),(37,75,50),8)
 spec(im,(333,306),16);save(im,4)
def v5(): # rounded notebook, no literal calendar number
 im=bg().convert('RGBA'); note=rounded((218,142,806,878),150);color_layer(im,note,(137,192,137),(56,111,72),(50,84,59),31)
 # page inset: lightly frosted tactile panel
 page=rounded((286,272,738,763),95);color_layer(im,page,(250,246,232),(220,233,210),(66,104,69),9)
 # spine tabs
 for y in (315,435,555):
  tab=rounded((193,y,272,y+63),28);color_layer(im,tab,(164,205,150),(79,132,84),(45,76,53),7)
 ck=line([(388,516),(476,603),(650,415)],63);color_layer(im,ck,(112,181,112),(47,112,70),(51,83,55),9)
 spec(im,(329,337),11);save(im,5)
def v6(): # chunky checklist puck: recessed lines not a flat glyph
 im=bg().convert('RGBA'); puck=rounded((146,170,878,850),210);color_layer(im,puck,(119,180,127),(52,110,71),(50,83,58),28)
 # inset rounded checklist plate
 plate=rounded((250,267,774,750),126); # ambient occlusion recess
 ao=shifted(plate,0,12).filter(ImageFilter.GaussianBlur(10));q=Image.new('RGBA',(S,S),(30,75,48,0));q.putalpha(ao.point(lambda a:int(a*.34)));im.alpha_composite(q)
 color_layer(im,plate,(230,239,217),(182,211,176),(57,95,63),7)
 # one large affirmative check + 2 tactile rows
 ck=line([(334,470),(409,546),(535,388)],55);color_layer(im,ck,(78,151,88),(36,96,61),(34,71,47),7)
 for y,w in [(575,157),(649,113)]:
  row=rounded((527,y,527+w,y+28),14);color_layer(im,row,(147,190,138),(92,145,94),(59,97,63),3,False)
 spec(im,(336,314),12);save(im,6)

for i,f in enumerate((v1,v2,v3,v4,v5,v6),1):f()

# Contact sheet: icon previews have actual 40px radius at this preview scale as requested.
sheet=Image.new('RGB',(3*300,2*270),(239,235,226));d=ImageDraw.Draw(sheet)
font=ImageFont.load_default()
names=['Puffy check','Ceramic leaf','Habit stack','Completion ring','Soft notebook','Checklist puck']
for i in range(6):
 im=Image.open(f'{OUT}/iter2_v{i+1}.png').resize((180,180),Image.Resampling.LANCZOS)
 # rounded clip preview 40px
 m=Image.new('L',(180,180),0);ImageDraw.Draw(m).rounded_rectangle((0,0,179,179),40,fill=255)
 x=(i%3)*300+60;y=(i//3)*270+25;sheet.paste(im,(x,y),m);d.text((x,y+197),f'v{i+1}  {names[i]}',fill=dark,font=font)
sheet.save(f'{OUT}/iter2_sheet.png')

# size proof strip, preserving pixel rendering at each supplied size.
# Each row is 210px high, so the 180px rendition cannot overlap its neighbours.
strip=Image.new('RGB',(410,6*210),(239,235,226));d=ImageDraw.Draw(strip)
for i in range(6):
 src=Image.open(f'{OUT}/iter2_v{i+1}.png'); y=i*210;d.text((10,y+96),f'v{i+1}',fill=dark,font=font)
 x=40
 for size in (180,80,40):
  im=src.resize((size,size),Image.Resampling.LANCZOS); strip.paste(im,(x,y+(190-size)//2));d.text((x,y+193),str(size),fill=dark,font=font);x+=size+22
strip.save(f'{OUT}/iter2_small.png')
