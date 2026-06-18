#!/usr/bin/env python3
"""Generate adaptive launcher icons (Android 8+) so no launcher pads the icon
with white. Per app: background = solid dominant-bg colour; foreground = the
existing full-bleed icon art centred in the safe zone on a transparent canvas.
Writes mipmap-*/ic_launcher_foreground.png, values/ic_launcher_colors.xml,
and mipmap-anydpi-v26/ic_launcher{,_round}.xml."""
import os, sys
from collections import Counter
from PIL import Image

REPO = "/home/user/Documents/Gs"
DENS = {"mdpi":1,"hdpi":1.5,"xhdpi":2,"xxhdpi":3,"xxxhdpi":4}
FG_FRAC = 1.0    # full-bleed: art fills the masked shape edge-to-edge (no bg-colour margin)

ADAPT = ('<?xml version="1.0" encoding="utf-8"?>\n'
 '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
 '    <background android:drawable="@color/ic_launcher_background"/>\n'
 '    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n'
 '</adaptive-icon>\n')


def dominant_bg(im):
    w,h=im.size; px=im.load(); c=Counter()
    for y in range(0,h,2):
        for x in range(0,w,2):
            p=px[x,y]
            if p[3]<200: continue
            if p[0]>=249 and p[1]>=249 and p[2]>=249: continue
            c[(p[0]//8*8,p[1]//8*8,p[2]//8*8)]+=1
    if not c: return (20,25,40)
    return c.most_common(1)[0][0]


def src_icon(app):
    for p in [f"{REPO}/{app}/store/icon_512_playstore.png",
              f"{REPO}/{app}/android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png"]:
        if os.path.isfile(p): return p
    return None


def gen(app):
    sp=src_icon(app)
    if not sp: return None
    src=Image.open(sp).convert("RGBA")
    bg=dominant_bg(src)
    res=f"{REPO}/{app}/android/app/src/main/res"
    for d,scale in DENS.items():
        canvas=round(108*scale); art=round(108*scale*FG_FRAC)
        fg=Image.new("RGBA",(canvas,canvas),(0,0,0,0))
        a=src.resize((art,art),Image.LANCZOS)
        off=(canvas-art)//2
        fg.paste(a,(off,off),a)
        outdir=f"{res}/mipmap-{d}"; os.makedirs(outdir,exist_ok=True)
        fg.save(f"{outdir}/ic_launcher_foreground.png")
    vdir=f"{res}/values"; os.makedirs(vdir,exist_ok=True)
    open(f"{vdir}/ic_launcher_colors.xml","w").write(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        f'    <color name="ic_launcher_background">#{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}</color>\n'
        '</resources>\n')
    adir=f"{res}/mipmap-anydpi-v26"; os.makedirs(adir,exist_ok=True)
    open(f"{adir}/ic_launcher.xml","w").write(ADAPT)
    open(f"{adir}/ic_launcher_round.xml","w").write(ADAPT)
    return f"#{bg[0]:02X}{bg[1]:02X}{bg[2]:02X}"


if __name__=="__main__":
    for app in sys.argv[1:]:
        print(f"{app}: bg={gen(app)}")
