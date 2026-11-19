"""Composes the photoreal Benny's Plumbing commercial from AI clips + ElevenLabs voiceover.

Usage: python3 compose_benny.py <workdir>
<workdir> must contain clips/c1.mp4 c2.mp4 c3.mp4, img/s3.png and vo/vo.mp3.
Scenes are AI-generated (FLUX.1-dev images -> LTX Video); music, captions and end card are made here.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

import render_benny as rb

W, H, FPS = 720, 1280, 24
BLUE = (28, 62, 170)
NAVY = (22, 44, 120)
ORANGE = (232, 120, 30)


def caption_png(path, text):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = rb.font(rb.FONT_XB, 66)
    for i, line in enumerate(text.split("\n")):
        d.text((W / 2, 250 + i * 84), line, font=f, fill="white", anchor="mm", stroke_width=7, stroke_fill=(15, 15, 20))
    im.save(path)


def endcard_frames(folder, icon):
    """Animated overlay for the last 5 s: band, logo oval, typed phone, CTA."""
    os.makedirs(folder, exist_ok=True)
    phone = "555.014.2200"
    band_y = 200
    for fi in range(5 * FPS):
        t = fi / FPS
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        a = rb.smooth(t / 0.35)
        d.rectangle([0, band_y - 42, W * a, band_y + 42], fill=BLUE)
        sc = rb.smooth((t - 0.2) / 0.3)
        if sc > 0:
            ow, oh = 300 * sc, 92 * sc
            d.ellipse([W / 2 - ow, band_y - oh, W / 2 + ow, band_y + oh], fill="white", outline=BLUE, width=7)
            if sc > 0.95:
                ic = icon.resize((150, 150))
                im.alpha_composite(ic, (int(W / 2 - 285), band_y - 78))
                d.text((W / 2 + 70, band_y - 14), "Benny's", font=rb.font(rb.FONT_XB, 84), fill=BLUE, anchor="mm")
                d.text((W / 2 + 70, band_y + 50), "PLUMBING", font=rb.font(rb.FONT_XB, 30), fill=ORANGE, anchor="mm")
        n = int(max(0, min(len(phone), (t - 1.0) / 1.2 * len(phone))))
        if n:
            d.text((W / 2, 365), phone[:n], font=rb.font(rb.FONT_B, 58), fill=NAVY, anchor="mm",
                   stroke_width=3, stroke_fill="white")
        if t >= 3.0:
            k = rb.smooth((t - 3.0) / 0.25)
            d.text((W / 2, 440), "Call Today", font=rb.font(rb.FONT_XB, int(54 * (0.6 + 0.4 * k))), fill=NAVY,
                   anchor="mm", stroke_width=3, stroke_fill="white")
        im.save(f"{folder}/{fi:04d}.png")


def logo_icon(s3_path):
    """Circular mascot-head icon cropped from the end-card image."""
    src = Image.open(s3_path).convert("RGB").crop((90, 50, 480, 440)).resize((300, 300))
    mask = Image.new("L", (300, 300), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 299, 299], fill=255)
    icon = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
    icon.paste(src, (0, 0), mask)
    ImageDraw.Draw(icon).ellipse([0, 0, 299, 299], outline=BLUE, width=10)
    return icon


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    wd = sys.argv[1]
    tmp = f"{wd}/compose"
    os.makedirs(tmp, exist_ok=True)

    # audio: same voiceover split/music/ducking as the 2D version, plus a "ding" when it's fixed
    rb.DRIP_TIMES = []
    rb.FIX_T = 5.15
    _, (l1_end, l2_mid, l2_end) = rb.build_audio(f"{wd}/vo/vo.mp3", tmp)

    caption_png(f"{tmp}/cap1.png", "LEAKY SINK?")
    caption_png(f"{tmp}/cap2.png", "FIXED FAST!")
    caption_png(f"{tmp}/cap3.png", "NO MESS.\nNO STRESS.")
    endcard_frames(f"{tmp}/end", logo_icon(f"{wd}/img/s3.png"))

    fit = f"scale=-2:{H}:flags=lanczos,crop={W}:{H},fps={FPS},setsar=1"
    # end card: mascot pushed down and enlarged so it fills the lower half, room blurred behind
    endbg = (f"[2:v]trim=0:5,setpts=PTS-STARTPTS,split[e1][e2];"
             f"[e1]crop=96:896:0:0,scale={W}:{H},boxblur=30:3,eq=brightness=0.06[eb];"
             f"[e2]scale=760:-2:flags=lanczos,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='clip(Y*255/60,0,255)'[ef];"
             f"[eb][ef]overlay=x=-20:y=470,crop={W}:{H}:0:0,fps={FPS},setsar=1[e3]")
    fc = (f"[0:v]trim=0:5,setpts=PTS-STARTPTS,{fit}[v1];"
          f"[1:v]trim=0:5,setpts=PTS-STARTPTS,{fit},eq=brightness=0.01[v2];"
          f"{endbg};"
          f"[v1][v2][e3]concat=n=3:v=1:a=0[base];"
          f"[base][3:v]overlay=enable='between(t,0.6,{l1_end + 0.5:.2f})'[o1];"
          f"[o1][4:v]overlay=enable='between(t,5.0,{l2_mid:.2f})'[o2];"
          f"[o2][5:v]overlay=enable='between(t,{l2_mid:.2f},{min(l2_end + 0.6, 9.95):.2f})'[o3];"
          f"[6:v]setpts=PTS-STARTPTS+10/TB[endov];"
          f"[o3][endov]overlay=eof_action=pass[vout]")
    run(["ffmpeg", "-y", "-v", "error",
         "-i", f"{wd}/clips/c1.mp4", "-i", f"{wd}/clips/c2.mp4", "-i", f"{wd}/clips/c3.mp4",
         "-loop", "1", "-i", f"{tmp}/cap1.png", "-loop", "1", "-i", f"{tmp}/cap2.png", "-loop", "1", "-i", f"{tmp}/cap3.png",
         "-framerate", str(FPS), "-i", f"{tmp}/end/%04d.png",
         "-i", f"{tmp}/mix.wav",
         "-filter_complex", fc, "-map", "[vout]", "-map", "7:a",
         "-t", "15", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
         f"{wd}/benny_photoreal.mp4"])
    print("ok", f"{wd}/benny_photoreal.mp4")


if __name__ == "__main__":
    main()
