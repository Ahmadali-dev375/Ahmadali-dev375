from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path
import math, os

PHOTO = Path("assets/ahmad-photo.png")
OUTPUT = Path("assets/ahmad-profile-animation.gif")

W, H = 900, 320
FPS = 12
SECONDS = 6
N = FPS * SECONDS

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()

def ease_in_out(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))

def fit_height(img, height):
    w, h = img.size
    return img.resize((int(w * height / h), height), Image.Resampling.LANCZOS)

def add_glow(base, cx, cy, radius, alpha, rgb):
    glow = Image.new("RGBA", base.size, (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    for r, a in [(radius, int(alpha*.22)), (int(radius*.72), int(alpha*.38)), (int(radius*.45), int(alpha*.62))]:
        gd.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(*rgb, a))
    glow = glow.filter(ImageFilter.GaussianBlur(radius//3))
    return Image.alpha_composite(base, glow)

src = Image.open(PHOTO).convert("RGB")
portrait = src.crop((245, 35, 1085, 1260))
portrait = fit_height(portrait, 345)
portrait = ImageEnhance.Contrast(portrait).enhance(1.08)
portrait = ImageEnhance.Sharpness(portrait).enhance(1.08)
portrait = portrait.convert("RGBA")

pw, ph = portrait.size
mask = Image.new("L", (pw, ph), 0)
md = ImageDraw.Draw(mask)
md.rounded_rectangle((8,5,pw-8,ph-5), radius=60, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(18))
portrait.putalpha(mask)

F_BIG = font(47, True)
F_MED = font(25, True)
F_SMALL = font(17)
F_TINY = font(14)

roles = [
    "Flutter Developer",
    "Firebase & Cloud Builder",
    "AI Automation Developer",
    "AI Agent Builder",
    "Full-Stack App Developer",
]

frames = []
for i in range(N):
    t = i / N
    frame = Image.new("RGBA", (W,H), (4,7,12,255))
    draw = ImageDraw.Draw(frame)

    for y in range(H):
        v = int(6 + 10*y/H)
        draw.line((0,y,W,y), fill=(v,v+2,v+7,255))
    for x in range(0,W,45):
        draw.line((x,0,x,H), fill=(16,21,30,255))
    for y in range(0,H,40):
        draw.line((0,y,W,y), fill=(14,19,27,255))

    scan_x = int((t*1.25 % 1.0)*(W+180))-90
    scan = Image.new("RGBA",(W,H),(0,0,0,0))
    sd = ImageDraw.Draw(scan)
    sd.rectangle((scan_x-18,0,scan_x+18,H), fill=(38,208,255,16))
    scan = scan.filter(ImageFilter.GaussianBlur(18))
    frame = Image.alpha_composite(frame, scan)

    pulse = .5 + .5*math.sin(2*math.pi*t)
    frame = add_glow(frame,720,163,165,100+int(50*pulse),(0,190,255))
    frame = add_glow(frame,730,162,128,75+int(35*(1-pulse)),(139,92,246))

    ghost_phase = (t*2)%1
    if .46 < ghost_phase < .82:
        q=(ghost_phase-.46)/.36
        alpha=int(75*math.sin(math.pi*q))
        shift=int(-155+135*ease_in_out(q))
        ghost=portrait.copy()
        ghost.putalpha(ghost.getchannel("A").point(lambda p: p*alpha//255))
        ghost=ghost.filter(ImageFilter.GaussianBlur(1.2))
        frame.alpha_composite(ghost,(555+shift,-10))

    scale=.985+.018*(.5+.5*math.sin(2*math.pi*t))
    nw,nh=int(portrait.width*scale),int(portrait.height*scale)
    person=portrait.resize((nw,nh),Image.Resampling.LANCZOS)
    frame.alpha_composite(person,(555-(nw-portrait.width)//2,-9-(nh-portrait.height)//2))

    draw=ImageDraw.Draw(frame)
    draw.text((52,50),"AHMAD ALI",font=F_BIG,fill=(245,248,255,255))
    draw.rounded_rectangle((52,111,318,115),radius=2,fill=(55,205,255,255))
    draw.rounded_rectangle((319,111,403,115),radius=2,fill=(168,85,247,255))
    draw.text((52,132),"Flutter • Firebase • AI Automation",font=F_SMALL,fill=(184,194,211,255))

    role_index=int(t*len(roles))%len(roles)
    role=roles[role_index]
    local=(t*len(roles))%1
    if local<.68:
        chars=max(1,int(len(role)*(local/.68)))
    elif local<.86:
        chars=len(role)
    else:
        chars=max(0,int(len(role)*(1-(local-.86)/.14)))
    typed=role[:chars]

    draw.text((52,181),"> building:",font=F_TINY,fill=(87,209,255,255))
    draw.text((52,204),typed,font=F_MED,fill=(247,249,255,255))
    if int(i/(FPS/2))%2==0:
        bbox=draw.textbbox((52,204),typed,font=F_MED)
        draw.rectangle((bbox[2]+4,207,bbox[2]+7,231),fill=(80,220,255,255))

    for label,x in [("FLUTTER",52),("FIREBASE",143),("N8N",252),("REACT",315)]:
        tw=draw.textbbox((0,0),label,font=F_TINY)[2]
        draw.rounded_rectangle((x,262,x+tw+22,290),radius=14,outline=(94,111,135,170),width=1)
        draw.text((x+11,268),label,font=F_TINY,fill=(205,213,226,255))

    dot_alpha=150+int(105*(.5+.5*math.sin(4*math.pi*t)))
    draw.ellipse((52,18,62,28),fill=(61,226,139,dot_alpha))
    draw.text((69,16),"OPEN TO REMOTE / FREELANCE",font=F_TINY,fill=(144,154,171,255))
    frames.append(frame.convert("RGB"))

pal=[f.quantize(colors=128,method=Image.Quantize.MEDIANCUT) for f in frames]
pal[0].save(OUTPUT,save_all=True,append_images=pal[1:],duration=int(1000/FPS),loop=0,optimize=True,disposal=2)
print(f"Created: {OUTPUT}")
