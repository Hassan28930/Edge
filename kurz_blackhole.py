#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
  KURZGESAGT-STYLE PROCEDURAL EXPLAINER  -  "BLACK HOLES"
  Silent-visuals + SFX-only soundtrack, 100 % procedural, single file.
===============================================================================
  Install :  pip install numpy pillow imageio-ffmpeg        (uharfbuzz if no Raqm)
  Run     :  python kurz_blackhole.py
  Options :  --ratio 16:9|9:16|1:1      (default 16:9, 1920x1080)
             --duration SECONDS         (default 260 = 4:20)
             --out FILE.mp4
             --stills 1.5,8,20          (write PNG test frames and exit)
             --poster 12.5              (write poster.png at that time and exit)
             --preview                  (half resolution fast render)
             --limit SECONDS            (render only the first N seconds)
             --workers N                (parallel render processes; 0 = auto)
             --crf N / --preset P       (x264 quality, default 21 / veryfast)
             --no-audio                 (video only)
             --audio-only FILE.wav      (write the SFX bed and exit)
             --force-hb                 (force the HarfBuzz text path)

  Every pixel: PIL + NumPy.  Every sound: additive/subtractive synthesis in
  NumPy (whooshes, pops, booms, ticks, risers, sub-drops) -> 48 kHz stereo WAV.
  The master is soft-knee compressed (tanh), de-clicked and normalised to a
  -2.6 dBFS sample-peak ceiling, which keeps the AAC copy below 0 dBFS as well
  (measured -2.1 dBFS after decode, -16.8 LUFS integrated).
  Captions are Devanagari: shaped with Pillow-Raqm when available, otherwise
  HarfBuzz (uharfbuzz) + a built-in glyph rasteriser.
===============================================================================
"""
from __future__ import annotations

import os
import sys
import re
import math
import time
import wave
import json
import base64
import random
import argparse
import struct
import shutil
import subprocess
import tempfile
import urllib.request
from functools import lru_cache
from contextlib import contextmanager

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps, features

# =============================================================================
#  1. USER INPUTS  (the only block you edit)
# =============================================================================
TRANSCRIPTION = """
इमेजिन कीजिए, यूनिवर्स में एक ऐसी जगह है, जहां ग्रेविटी इतनी पावरफुल है, कि लाइट भी एस्केप नहीं कर सकती।
और अगर आप इस बाउंड्री को क्रॉस कर लें, तो वापस आना इंपॉसिबल हो सकता है।
लेकिन सबसे स्ट्रेंज बात हमें अभी तक नहीं पता ब्लैक होल के अंदर एक्चुअली क्या है।
यह है ब्लैक होल। ब्लैक होल कोई जॉइंट होल नहीं होता।
यह स्पेस और टाइम का एक ऐसा रीजन है जहां इनस अमाउंट ऑफ मैटर एक एक्सट्रीमली स्मॉल एरिया में कंप्रेस हो जाता है।
इसकी बाउंड्री को कहते हैं इवेंट होराइजन।
एक बार अगर कोई ऑब्जेक्ट इस बाउंड्री के अंदर चला जाए तो उसके लिए बाहर निकलने का कोई नोन वे नहीं है। नॉट इवन लाइट।
लेकिन यहां एक माइंड बेंडिंग चीज होती है।
अगर आप ब्लैक होल की तरफ फॉल कर रहे हो तो आपके लिए टाइम नॉर्मली पास होता रहेगा।
लेकिन दूर खड़ा ऑब्जर्वर आपको इवेंट होराइजन के पास एक्सट्रीमली स्लो होते हुए देख सकता है।
मतलब टाइम खुद डिफरेंट ऑब्जर्वर्स के लिए डिफरेंट तरह बिहेव कर सकता है।
और ब्लैक होल सिर्फ स्पेस में रैंडम मॉन्सर्स नहीं है।
हमारी गैलेक्सी मिल्की वे के सेंटर में भी एक सुपरमैसिव ब्लैक होल है।
सेजिटेरियस ए स्टार। इसका मास हमारे सन से अराउंड 4 मिलियन टाइम्स ज्यादा है।
लेकिन सरप्राइजिंगली यह हमें सक नहीं कर रहा। ब्लैक होल कोई कॉस्मिक वैक्यूम क्लीनर नहीं होता।
अगर सन को सेम मास के ब्लैक होल से रिप्लेस कर दिया जाए तो अर्थ ऑलमोस्ट वही ऑर्बिट मेंटेन करेगी। बस सनलाइट डिसअपीयर हो जाएगी।
लेकिन ब्लैक होल्स का सबसे टेरिफाइंग पार्ट अब आता है।
अगर आप ब्लैक होल के पास इनफ क्लोज चले जाएं तो ग्रेविटी आपके बॉडी के डिफरेंट पार्ट्स पर डिफरेंट स्ट्रेंथ से पुल करेगी।
आप स्ट्रेच होने लगेंगे और कंप्रेस भी।
साइंटिस्ट्स इस प्रोसेस को कहते हैं स्पैगिफिकेशन। नाम फनी है एक्सपीरियंस बिल्कुल नहीं।
लेकिन ब्लैक होल्स की रियल मिस्ट्री उनके बाहर नहीं। उनके अंदर है।
आइंस्टाइन की इक्वेशन सजेस्ट करती हैं कि ब्लैक होल के सेंटर में एक सिंगुलैरिटी हो सकती है।
जहां स्पेस टाइम कर्वेचर थरेटिकली इनफाइनाइट हो जाती है।
और यहां हमारी फिजिक्स प्रॉब्लम में आ जाती है।
बिकॉज़ जनरल रिलेटिविटी और क्वांटम मैकेनिक्स दोनों यूनिवर्स को एक्सप्लेन करने के लिए इनक्रेडिबली पावरफुल हैं।
लेकिन ब्लैक होल के सेंटर में दोनों को एक साथ एक्सप्लेन करना एक्सट्रीमली डिफिकल्ट हो जाता है।
और फिर आता है ब्लैक होल इंफॉर्मेशन पैराडॉक्स।
इमेजिन कीजिए आप एक बुक ब्लैक होल में थ्रो कर देते हैं।
बुक के अंदर इंफॉर्मेशन है लेकिन ब्लैक होल से कुछ भी बाहर नहीं आ सकता।
तो उस इंफॉर्मेशन का क्या हुआ?
क्या यूनिवर्स इंफॉर्मेशन को परमानेंटली डिस्ट्रॉय कर सकता है?
क्वांटम मैकेनिक्स के अकॉर्डिंग यह प्रॉब्लम क्रिएट करता है।
और जब स्टीफन हॉकिंग ने डिस्कवर किया कि ब्लैक होल्स स्लोली रेडिएशन इमिट कर सकते हैं तो मिस्ट्री और भी डीप हो गई।
बिकॉज़ इवेंचुअली ब्लैक होल्स थ्यरेटिकली इवापोरेट हो सकता है।
लेकिन अगर ब्लैक होल डिसअपीयर हो गया तो उसके अंदर गिरने वाली इनेशन गई कहां?
और शायद यही ब्लैक होल्स का सबसे इंपॉर्टेंट सीक्रेट है।
हो सकता है ब्लैक होल्स सिर्फ यूनिवर्स के डारकेस्ट ऑब्जेक्ट्स ना हो।
हो सकता है यह हमें बताएं कि रियलिटी एक्चुअली काम कैसे करती है?
स्पेस क्या है? टाइम क्या है? इंफॉर्मेशन यूनिवर्स में कैसे सर्वाइव करती है?
और ब्लैक होल के अंदर एक्चुअली क्या है?
मे बी सम डे इन क्वेशंस का आंसर हमें यूनिवर्स का सबसे बड़ा सीक्रेट बता दे
बिकॉज़ समटाइम्स द डारकेस्ट प्लेसेस इन द यूनिवर्स हाइड द डीपेस्ट ट्रुथ्स अबाउट रियलिटी।
अगर आपको यह वीडियो पसंद आई हो तो लाइक जरूर करें और यूनिवर्स, साइंस और टेक्नोलॉजी की ऐसी ही इंटरेस्टिंग स्टोरीज के लिए चैनल को सब्सक्राइब करें।
मिलते हैं नेक्स्ट वीडियो में। थैंक्स फॉर वाचिंग। अंटिल नेक्स्ट टाइम साइनिंग ऑफ।
"""

VOICEOVER_DURATION = 260.0      # 4 min 20 sec  (None -> auto from word count)
ASPECT_RATIO = "16:9"

# =============================================================================
#  2. GLOBAL SETTINGS
# =============================================================================
FPS = 30
OUTPUT_FILE = "kurzgesagt_blackhole_1080p.mp4"
MIN_BEAT, MAX_BEAT, TARGET_BEAT = 2.5, 4.2, 3.4
TRANS_TIME = 0.55
WORDS_PER_SEC = 3.0

RATIO_TABLE = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080)}
# stage = rectangle (fractions of canvas) reserved for the illustration
STAGE_TABLE = {"16:9": (0.0, 0.018, 1.0, 0.842), "9:16": (0.0, 0.040, 1.0, 0.800), "1:1": (0.0, 0.018, 1.0, 0.800)}
SUB_Y_TABLE = {"16:9": 0.888, "9:16": 0.845, "1:1": 0.865}
# the storyboard is authored inside this design box (units); y grows downward
D_W, D_H = 1200.0, 516.0

W = H = 0
CX = CY = 0.0
U = 1.0            # pixels per design unit
FS = 1.0           # font scale (short side / 1080)
SUB_Y = 0.888
RATIO = "16:9"
SAFE_X, SAFE_Y = 570.0, 246.0     # keep action inside |x|<SAFE_X, |y|<SAFE_Y


def init_geometry(ratio: str = "16:9", scale: float = 1.0):
    global W, H, CX, CY, U, FS, SUB_Y, RATIO
    if ratio not in RATIO_TABLE:
        raise SystemExit("ASPECT_RATIO must be one of %s" % list(RATIO_TABLE))
    RATIO = ratio
    bw, bh = RATIO_TABLE[ratio]
    W, H = int(round(bw * scale / 2) * 2), int(round(bh * scale / 2) * 2)
    x0, y0, x1, y1 = STAGE_TABLE[ratio]
    sw, sh = (x1 - x0) * W, (y1 - y0) * H
    U = min(sw / D_W, sh / D_H)
    CX, CY = (x0 + x1) / 2.0 * W, (y0 + y1) / 2.0 * H
    FS = min(W, H) / 1080.0
    SUB_Y = SUB_Y_TABLE[ratio]


# =============================================================================
#  3. PALETTE
# =============================================================================
PAL = {
    "obsidian": "#0A081D", "midnight": "#1F103F", "magenta": "#8E1963",
    "deep": "#06040F", "ink": "#0B0D1B", "navy_txt": "#0B0D1B",
    "white": "#FFFFFF", "cyan": "#00F0FF", "mint": "#00F5A0", "pink": "#FF3DA5",
    "amber": "#FFB800", "orange": "#FF7700", "red": "#FF3B4E",
    "sun": "#FFE600", "sun_y2": "#FFE600", "hot": "#FFF4B0",
    "violet": "#6B3DFF", "purple": "#B14BFF", "blue": "#2D7BFF",
    "teal": "#0E8096", "smoke": "#1E2333", "smoke2": "#2C354A",
    "skin1": "#F6D2B0", "skin2": "#E8B48A", "skin3": "#C98A5E", "skin4": "#9A6240",
    "hair": "#14102E", "hoodie": "#FF3DA5", "hoodie_d": "#B01F6D",
    "jeans": "#22306B", "jeans_d": "#161F45",
}
C = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in PAL.items()}
# =============================================================================
#  MATH / EASING / COLOUR UTILITIES
# =============================================================================
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def remap(x, a, b):
    return clamp((x - a) / (b - a)) if b != a else 0.0


def smoothstep(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out_cubic(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_cubic(t):
    t = clamp(t)
    return t ** 3


def ease_in_out_quad(t):
    t = clamp(t)
    return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2


def ease_in_out_cubic(t):
    t = clamp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out_expo(t):
    t = clamp(t)
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)


def ease_out_back(t, s=1.70158):
    t = clamp(t)
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2


def elastic_out(t):
    t = clamp(t)
    if t in (0.0, 1.0):
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


def pop(t, t0, d=0.5):
    """Spring-in value (0 -> ~1.1 -> 1) starting at t0."""
    return ease_out_back(remap(t, t0, t0 + d))


def hexc(h, a=None):
    h = h.lstrip("#")
    rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return rgb if a is None else rgb + (a,)


def col(c):
    if isinstance(c, str):
        return hexc(c)
    return tuple(int(v) for v in c)


def mix(c1, c2, t):
    c1, c2 = col(c1), col(c2)
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1[:3], c2[:3]))


@lru_cache(maxsize=512)
def _alut_q(q):
    return [int(i * q / 64.0 + 0.5) for i in range(256)]


def alut(a):
    return _alut_q(int(round(clamp(a) * 64)))



C = {k: hexc(v) for k, v in PAL.items()}      # curated palette from section 3


def has_deva(s):
    return any("\u0900" <= ch <= "\u097f" for ch in s)


def _glyph_ok(path, ch):
    """True if the font really contains a glyph for `ch` (not .notdef)."""
    try:
        f = ImageFont.truetype(path, 48)
        a, b = f.getmask(ch), f.getmask("\U0010ffff")
        return a.size != b.size or a.tobytes() != b.tobytes()
    except Exception:
        return False


def _font_index():
    idx = {}
    roots = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
             os.path.expanduser("~/.local/share/fonts"), "C:\\Windows\\Fonts", "/Library/Fonts",
             "/System/Library/Fonts", "/System/Library/Fonts/Supplemental", tempfile.gettempdir()]
    for r in roots:
        if not os.path.isdir(r):
            continue
        for dp, _, fns in os.walk(r):
            for fn in fns:
                if fn.lower().endswith((".ttf", ".otf", ".ttc")):
                    idx.setdefault(fn.lower(), os.path.join(dp, fn))
    return idx


FONT_DOWNLOADS = [
    ("Poppins-ExtraBold.ttf", "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-ExtraBold.ttf"),
    ("Poppins-Bold.ttf", "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf"),
    ("Hind-Bold.ttf", "https://raw.githubusercontent.com/google/fonts/main/ofl/hind/Hind-Bold.ttf"),
    ("Mukta-ExtraBold.ttf", "https://github.com/google/fonts/raw/main/ofl/mukta/Mukta-ExtraBold.ttf"),
]



# --- fonts: local folders, system index, then a GitHub-API download ----------
FONT_DOWNLOADS = [
    # (filename, repo, path-in-repo)   downloaded through api.github.com (base64)
    ("Mukta-ExtraBold.ttf", "google/fonts", "ofl/mukta/Mukta-ExtraBold.ttf"),
    ("Poppins-ExtraBold.ttf", "google/fonts", "ofl/poppins/Poppins-ExtraBold.ttf"),
    ("Poppins-Bold.ttf", "google/fonts", "ofl/poppins/Poppins-Bold.ttf"),
    ("NotoSansDevanagari-Bold.ttf", "google/fonts", "ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf"),
]


def _font_dirs():
    here = os.path.dirname(os.path.abspath(__file__))
    return [os.path.join(here, ".fonts"), os.path.join(here, "fonts"), tempfile.gettempdir(),
            "/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts"), "C:\\Windows\\Fonts",
            "/Library/Fonts", "/System/Library/Fonts", "/System/Library/Fonts/Supplemental"]


def _download_font(name, repo, path):
    """Fetch one TTF through the GitHub contents API (works where raw.* is blocked)."""
    for dest_dir in (os.path.join(os.path.dirname(os.path.abspath(__file__)), ".fonts"), tempfile.gettempdir()):
        dest = os.path.join(dest_dir, name)
        if os.path.exists(dest) and os.path.getsize(dest) > 20000:
            return dest
        try:
            os.makedirs(dest_dir, exist_ok=True)
            url = "https://api.github.com/repos/%s/contents/%s" % (repo, path)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                                       "Accept": "application/vnd.github+json"})
            js = json.loads(urllib.request.urlopen(req, timeout=60).read())
            data = base64.b64decode(js["content"])
            if len(data) > 20000:
                with open(dest, "wb") as fh:
                    fh.write(data)
                return dest
        except Exception as e:                                   # pragma: no cover
            print("   [font] download failed for %s (%s)" % (name, e))
    return None


def resolve_fonts():
    """Return (latin_font_path, devanagari_font_path)."""
    idx = _font_index()
    deva_names = ["mukta-extrabold.ttf", "mukta-bold.ttf", "notosansdevanagari-bold.ttf",
                  "hind-bold.ttf", "nilkanth-bold.ttf", "nirmalab.ttf", "mangalb.ttf",
                  "lohit-devanagari.ttf", "notosansdevanagari-regular.ttf"]
    latin_names = ["poppins-extrabold.ttf", "poppins-bold.ttf", "montserrat-extrabold.ttf",
                   "dejavusans-bold.ttf", "liberationsans-bold.ttf", "arialbd.ttf", "arial.ttf"]
    deva = next((idx[n] for n in deva_names if n in idx and _glyph_ok(idx[n], "\u0915")), None)
    latin = next((idx[n] for n in latin_names if n in idx), None)
    if deva is None or latin is None:
        for name, repo, path in FONT_DOWNLOADS:
            p = _download_font(name, repo, path)
            if not p:
                continue
            if deva is None and _glyph_ok(p, "\u0915"):
                deva = p
            if latin is None and _glyph_ok(p, "A") and not has_deva(name):
                latin = p
            if deva and latin:
                break
    if deva is None:
        print("   [font] WARNING: no Devanagari font found - Hindi captions may be boxes.")
    if latin is None:
        latin = deva or next((idx[n] for n in ("dejavusans-bold.ttf", "dejavusans.ttf") if n in idx), None)
    if latin is None:
        raise SystemExit("No usable font found (and download failed). Check the internet connection.")
    return latin, deva or latin
class TextMask:
    __slots__ = ("img", "ox", "base", "adv", "bbox", "ink")

    def __init__(self, img, ox, base, adv):
        self.img, self.ox, self.base, self.adv = img, ox, base, adv
        self.bbox = img.getbbox() or (0, 0, 1, 1)
        self.ink = img.crop(self.bbox)            # tight mask: much cheaper to paste


class HBRenderer:
    """Fallback complex-script renderer: uharfbuzz shaping + own glyph rasteriser."""

    def __init__(self, path):
        import uharfbuzz as hb
        self.hb = hb
        self.face = hb.Face(hb.Blob.from_file_path(path))
        self.font = hb.Font(self.face)
        self.upem = self.face.upem
        ext = self.font.get_font_extents("ltr")
        self.asc, self.desc = ext.ascender / self.upem, -ext.descender / self.upem
        self._cont = {}

    def contours(self, gid):
        if gid in self._cont:
            return self._cont[gid]
        conts, cur = [], []

        class Pen:
            def moveTo(s, p):
                cur[:] = [tuple(p)]

            def lineTo(s, p):
                cur.append(tuple(p))

            def qCurveTo(s, *pts):
                p0 = cur[-1]
                pts = [tuple(p) for p in pts]
                offs, end = pts[:-1], pts[-1]
                for i, c in enumerate(offs):
                    nxt = end if i == len(offs) - 1 else ((c[0] + offs[i + 1][0]) / 2, (c[1] + offs[i + 1][1]) / 2)
                    for k in range(1, 7):
                        t = k / 6.0
                        cur.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * nxt[0],
                                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * nxt[1]))
                    p0 = nxt

            def curveTo(s, *pts):
                p0, c1, c2, p1 = cur[-1], tuple(pts[0]), tuple(pts[1]), tuple(pts[2])
                for k in range(1, 9):
                    t = k / 8.0
                    a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
                    cur.append((a * p0[0] + b * c1[0] + c * c2[0] + d * p1[0],
                                a * p0[1] + b * c1[1] + c * c2[1] + d * p1[1]))

            def closePath(s):
                if len(cur) > 2:
                    conts.append(list(cur))
                cur.clear()

            endPath = closePath

        self.font.draw_glyph_with_pen(gid, Pen())
        self._cont[gid] = conts
        return conts

    def render(self, text, size, pad):
        hb = self.hb
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"kern": True, "liga": True, "ccmp": True, "locl": True})
        s = size / float(self.upem)
        adv = sum(p.x_advance for p in buf.glyph_positions) * s
        asc, desc = int(math.ceil(self.asc * size)), int(math.ceil(self.desc * size))
        w, h = int(adv) + 2 * pad + 2, asc + desc + 2 * pad
        base = pad + asc
        SS = 4
        acc = np.zeros((h * SS, w * SS), np.int16)
        pen_x = float(pad)
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            gx = pen_x + pos.x_offset * s
            gy = base - pos.y_offset * s
            conts = self.contours(info.codepoint)
            polys = [[((gx + x * s) * SS, (gy - y * s) * SS) for x, y in c] for c in conts]
            if polys:
                areas = []
                for pl in polys:
                    a = 0.0
                    for i in range(len(pl)):
                        x1, y1 = pl[i]
                        x2, y2 = pl[(i + 1) % len(pl)]
                        a += x1 * y2 - x2 * y1
                    areas.append(a)
                ref = areas[int(np.argmax(np.abs(areas)))]
                for pl, a in zip(polys, areas):
                    xs, ys = [p[0] for p in pl], [p[1] for p in pl]
                    x0, y0 = max(0, int(min(xs)) - 1), max(0, int(min(ys)) - 1)
                    x1, y1 = min(w * SS, int(max(xs)) + 2), min(h * SS, int(max(ys)) + 2)
                    if x1 <= x0 or y1 <= y0:
                        continue
                    m = Image.new("L", (x1 - x0, y1 - y0), 0)
                    ImageDraw.Draw(m).polygon([(px - x0, py - y0) for px, py in pl], fill=1)
                    sign = 1 if (a * ref) >= 0 else -1
                    acc[y0:y1, x0:x1] += sign * np.asarray(m, np.int16)
            pen_x += pos.x_advance * s
        mask = Image.fromarray(((acc != 0) * 255).astype(np.uint8)).reduce(SS)
        return mask, base, adv


class TextEngine:
    """Renders (and caches) anti-aliased text masks. Handles Devanagari shaping."""

    def __init__(self, latin_path, deva_path, force_hb=False):
        self.paths = {"latin": latin_path, "deva": deva_path}
        self.raqm = features.check("raqm") and not force_hb
        self.hb = {}
        self.mode = "raqm" if self.raqm else "basic"
        if not self.raqm:
            if self._ensure_hb():
                self.mode = "harfbuzz"
            else:
                print("   [text] WARNING: no complex-text shaping available; Hindi may look broken.")
        self._fonts, self._cache = {}, {}
        print("   [text] shaping mode: %s | latin=%s | deva=%s" % (
            self.mode, os.path.basename(latin_path), os.path.basename(deva_path)))

    @staticmethod
    def _ensure_hb():
        try:
            import uharfbuzz  # noqa: F401
            return True
        except Exception:
            try:
                print("   [text] Raqm unavailable -> installing uharfbuzz ...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "uharfbuzz"])
                import uharfbuzz  # noqa: F401
                return True
            except Exception:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                                           "--break-system-packages", "uharfbuzz"])
                    import uharfbuzz  # noqa: F401
                    return True
                except Exception:
                    return False

    def _pil_font(self, path, size):
        k = (path, size, self.raqm)
        if k not in self._fonts:
            if self.raqm:
                self._fonts[k] = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
            else:
                self._fonts[k] = ImageFont.truetype(path, size)
        return self._fonts[k]

    def get(self, text, size):
        size = max(4, int(size))
        deva = has_deva(text)
        key = (text, size, deva)
        tm = self._cache.get(key)
        if tm is not None:
            return tm
        path = self.paths["deva" if deva else "latin"]
        pad = int(size * 0.3) + 2
        if self.mode == "harfbuzz":
            r = self.hb.get(path) or self.hb.setdefault(path, HBRenderer(path))
            img, base, adv = r.render(text, size, pad)
            tm = TextMask(img, pad, base, adv)
        else:
            f = self._pil_font(path, size)
            kw = {"language": "hi" if deva else "en"} if self.raqm else {}
            adv = f.getlength(text, **kw) if self.raqm else f.getlength(text)
            asc, desc = f.getmetrics()
            w, h = int(adv) + 2 * pad + 2, asc + desc + 2 * pad
            img = Image.new("L", (w, h), 0)
            ImageDraw.Draw(img).text((pad, pad + asc), text, font=f, fill=255, anchor="ls", **kw)
            tm = TextMask(img, pad, pad + asc, adv)
        self._cache[key] = tm
        return tm


# =============================================================================
#  GRADIENTS / MASKS (NumPy, analytic anti-aliasing)
# =============================================================================
def _stops(stops):
    pos = np.array([s[0] for s in stops], np.float32)
    cols = np.array([col(s[1])[:3] for s in stops], np.float32)
    return pos, cols


def sample_stops(t, stops):
    pos, cols = _stops(stops)
    t = np.asarray(t, np.float32)
    return np.stack([np.interp(t, pos, cols[:, k]) for k in range(3)], -1)


def lin_grad(w, h, stops, angle=90.0):
    """Multi-stop linear gradient; angle 90 = top->bottom."""
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    L = abs(w * dx) + abs(h * dy)
    t = ((xx - w / 2) * dx + (yy - h / 2) * dy) / L + 0.5
    return Image.fromarray(sample_stops(t, stops).astype(np.uint8))


def add_blobs(img, blobs, res=4):
    """Additive soft gaussian blobs (nebulae / glows). blobs=(fx,fy,frad,color,strength)."""
    w, h = img.size
    sw, sh = max(2, w // res), max(2, h // res)
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    acc = np.zeros((sh, sw, 3), np.float32)
    for fx, fy, fr, color, k in blobs:
        r = fr * max(w, h) / res
        g = np.exp(-(((xx - fx * sw) ** 2 + (yy - fy * sh) ** 2) / (2 * r * r)))
        acc += g[..., None] * np.array(col(color)[:3], np.float32) * k
    big = Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return ImageChops.add(img, big)


def vignette(img, strength=0.4):
    w, h = img.size
    sw, sh = w // 6, h // 6
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    d = ((xx - sw / 2) / (sw / 2)) ** 2 + ((yy - sh / 2) / (sh / 2)) ** 2
    m = np.clip(1 - strength * np.clip(d / 2, 0, 1) ** 1.2, 0, 1)
    m = Image.fromarray((m * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return ImageChops.multiply(img, Image.merge("RGB", (m, m, m)))


def _to_l(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


@lru_cache(maxsize=1024)
def disc_mask(r2):
    r = r2 / 2.0
    n = int(math.ceil(r * 2)) + 4
    c = (n - 1) / 2.0
    yy, xx = np.ogrid[:n, :n]
    return _to_l(r - np.hypot(xx - c, yy - c) + 0.5)


@lru_cache(maxsize=512)
def ring_mask(r2, w2):
    r, w = r2 / 2.0, w2 / 2.0
    n = int(math.ceil((r + w / 2) * 2)) + 4
    c = (n - 1) / 2.0
    yy, xx = np.ogrid[:n, :n]
    return _to_l(w / 2 - np.abs(np.hypot(xx - c, yy - c) - r) + 0.5)


@lru_cache(maxsize=256)
def glow_mask(rq, p10):
    n = int(rq * 2) + 2
    c = (n - 1) / 2.0
    yy, xx = np.ogrid[:n, :n]
    d = np.clip(np.hypot(xx - c, yy - c) / rq, 0, 1)
    return _to_l((1 - d) ** (p10 / 10.0))


@lru_cache(maxsize=512)
def rrect_mask(hw2, hh2, rr2):
    hw, hh, rr = hw2 / 2.0, hh2 / 2.0, min(rr2 / 2.0, hw2 / 2.0, hh2 / 2.0)
    nw, nh = int(math.ceil(hw * 2)) + 4, int(math.ceil(hh * 2)) + 4
    yy, xx = np.ogrid[:nh, :nw]
    px, py = np.abs(xx - (nw - 1) / 2.0), np.abs(yy - (nh - 1) / 2.0)
    qx, qy = px - (hw - rr), py - (hh - rr)
    d = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - rr
    return _to_l(0.5 - d)


@lru_cache(maxsize=400)
def grad_disc(r2, stops_key, hx2, hy2):
    """Shaded sphere sprite: radial gradient with light centre offset (hx,hy) in radius units."""
    r = r2 / 2.0
    m = disc_mask(r2)
    n = m.width
    c = (n - 1) / 2.0
    yy, xx = np.mgrid[:n, :n].astype(np.float32)
    lx, ly = c + hx2 / 10.0 * r, c + hy2 / 10.0 * r
    t = np.clip(np.hypot(xx - lx, yy - ly) / (r * 1.9), 0, 1)
    rgb = sample_stops(t, stops_key).astype(np.uint8)
    img = Image.fromarray(rgb).convert("RGBA")
    img.putalpha(m)
    return img


def skey(stops):
    return tuple((float(p), col(c)[:3]) for p, c in stops)

# =============================================================================
#  SUPERSAMPLED DRAWING LAYER  +  CANVAS (design-space API)
# =============================================================================
def ellipse_pts(cx, cy, rx, ry, rot=0.0, a0=0.0, a1=360.0, n=48):
    out = []
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(n + 1):
        a = math.radians(lerp(a0, a1, i / n))
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def bezier(p0, p1, p2, p3, n=18):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def smooth_path(pts, n=8):
    """Catmull-Rom spline through pts."""
    if len(pts) < 3:
        return list(pts)
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append((0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                        0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)))
    out.append(pts[-1])
    return out


def drop_pts(cx, cy, r):
    """Tear-drop polygon (apex up)."""
    pts = [(cx, cy - 2 * r)]
    for i in range(25):
        a = math.radians(lerp(60, 300, i / 24))
        pts.append((cx + r * math.sin(a), cy - r * math.cos(a)))
    return pts


def star_pts(cx, cy, r, inner=0.3, n=4, rot=0.0):
    out = []
    for i in range(n * 2):
        a = math.radians(rot + i * 180.0 / n - 90)
        rr = r if i % 2 == 0 else r * inner
        out.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return out

class Layer:
    """RGBA supersampled surface; coordinates are absolute canvas pixels."""

    def __init__(self, box, ss=3):
        x0, y0, x1, y1 = [int(v) for v in box]
        self.x0, self.y0 = x0, y0
        self.w, self.h = max(1, x1 - x0), max(1, y1 - y0)
        self.ss = ss
        self.im = Image.new("RGBA", (self.w * ss, self.h * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _ps(self, pts):
        s = self.ss
        return [((x - self.x0) * s, (y - self.y0) * s) for x, y in pts]

    def _paint(self, fn, color):
        color = col(color)
        a = color[3] if len(color) == 4 else 255
        if a >= 255:
            fn(self.d, color[:3] + (255,))
        elif a > 0:
            m = Image.new("L", self.im.size, 0)
            fn(ImageDraw.Draw(m), 255)
            solid = Image.new("RGBA", self.im.size, color[:3] + (255,))
            solid.putalpha(m.point(alut(a / 255.0)))
            self.im = Image.alpha_composite(self.im, solid)
            self.d = ImageDraw.Draw(self.im)

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=None, width=0):
        s = self.ss
        px, py = (cx - self.x0) * s, (cy - self.y0) * s
        box = [px - rx * s, py - ry * s, px + rx * s, py + ry * s]
        if fill is not None:
            self._paint(lambda d, c: d.ellipse(box, fill=c), fill)
        if outline is not None and width > 0:
            ow = max(1, int(round(width * s)))
            self._paint(lambda d, c: d.ellipse(box, outline=c, width=ow), outline)

    def poly(self, pts, fill):
        P = self._ps(pts)
        self._paint(lambda d, c: d.polygon(P, fill=c), fill)

    def line(self, pts, width, fill, cap=True):
        P = self._ps(pts)
        w = max(1, int(round(width * self.ss)))

        def fn(d, c):
            d.line(P, fill=c, width=w, joint="curve")
            if cap:
                r = w / 2.0
                for (x, y) in (P[0], P[-1]):
                    d.ellipse([x - r, y - r, x + r, y + r], fill=c)

        self._paint(fn, fill)

    def rrect(self, x0, y0, x1, y1, r, fill, outline=None, width=0):
        if x1 < x0:
            x0, x1 = x1, x0
        if y1 < y0:
            y0, y1 = y1, y0
        if x1 - x0 < 1 or y1 - y0 < 1:
            return
        s = self.ss
        box = [(x0 - self.x0) * s, (y0 - self.y0) * s, (x1 - self.x0) * s, (y1 - self.y0) * s]
        if fill is not None:
            self._paint(lambda d, c: d.rounded_rectangle(box, radius=r * s, fill=c), fill)
        if outline is not None and width > 0:
            ow = max(1, int(round(width * s)))
            self._paint(lambda d, c: d.rounded_rectangle(box, radius=r * s, outline=c, width=ow), outline)

    def pie(self, cx, cy, r, a0, a1, fill):
        s = self.ss
        px, py = (cx - self.x0) * s, (cy - self.y0) * s
        self._paint(lambda d, c: d.pieslice([px - r * s, py - r * s, px + r * s, py + r * s], a0, a1, fill=c), fill)

    def finish(self):
        return self.im.reduce(self.ss) if self.ss > 1 else self.im


class DLayer:
    """Design-space wrapper around Layer (handles unit conversion)."""

    def __init__(self, cv, L, alpha):
        self.cv, self.L, self.alpha = cv, L, alpha

    def _c(self, x, y):
        return (self.cv.X(x), self.cv.Y(y))

    def _cs(self, pts):
        return [(self.cv.X(x), self.cv.Y(y)) for x, y in pts]

    def ellipse(self, x, y, rx, ry, color=None, outline=None, width=0):
        u = self.cv.u
        px, py = self._c(x, y)
        self.L.ellipse(px, py, rx * u, ry * u, color, outline, width * u)

    def poly(self, pts, color):
        self.L.poly(self._cs(pts), color)

    def line(self, pts, width, color, cap=True):
        self.L.line(self._cs(pts), width * self.cv.u, color, cap)

    def rrect(self, x, y, w, h, r, color, outline=None, width=0):
        u = self.cv.u
        px, py = self._c(x, y)
        self.L.rrect(px - w / 2 * u, py - h / 2 * u, px + w / 2 * u, py + h / 2 * u, r * u, color, outline, width * u)

    def pie(self, x, y, r, a0, a1, color):
        px, py = self._c(x, y)
        self.L.pie(px, py, r * self.cv.u, a0, a1, color)

    def arc(self, x, y, r, a0, a1, width, color, n=48):
        self.line(ellipse_pts(x, y, r, r, 0, a0, a1, n), width, color)

    def dashed(self, p0, p1, width, dash, gap, color, offset=0.0, cap=False):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy)
        if L < 1e-6:
            return
        ux, uy = dx / L, dy / L
        s = -(offset % (dash + gap))
        while s < L:
            a, b = max(0.0, s), min(L, s + dash)
            if b > a:
                self.line([(p0[0] + ux * a, p0[1] + uy * a), (p0[0] + ux * b, p0[1] + uy * b)], width, color, cap)
            s += dash + gap


class Canvas:
    """RGB frame buffer with a design-space (1000x1250 units, origin at stage centre) API."""

    def __init__(self, base_rgb):
        self.im = base_rgb.copy()
        self.cx, self.cy, self.u = CX, CY, U

    # ---- coordinate helpers
    def X(self, x):
        return self.cx + x * self.u

    def Y(self, y):
        return self.cy + y * self.u

    # ---- raw blitting
    def blit(self, spr, px, py, alpha=1.0):
        if alpha <= 0.003:
            return
        if alpha < 0.997:
            r, g, b, a = spr.split()
            spr = Image.merge("RGBA", (r, g, b, a.point(alut(alpha))))
        self.im.paste(spr, (int(round(px)), int(round(py))), spr)

    def paste_mask(self, color, mask, px, py, alpha=1.0):
        if alpha <= 0.003:
            return
        if alpha < 0.997:
            mask = mask.point(alut(alpha))
        self.im.paste(col(color)[:3], (int(round(px)), int(round(py))), mask)

    def sprite(self, spr, x, y, scale=1.0, rot=0.0, alpha=1.0, flip=False):
        if flip:
            spr = ImageOps.mirror(spr)
        if abs(scale - 1.0) > 0.004:
            spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BICUBIC)
        if abs(rot) > 0.05:
            spr = spr.rotate(rot, resample=Image.BICUBIC, expand=True)
        self.blit(spr, self.X(x) - spr.width / 2.0, self.Y(y) - spr.height / 2.0, alpha)

    # ---- analytic primitives
    def disc(self, x, y, r, color, alpha=1.0):
        rp = r * self.u
        if rp < 0.4:
            return
        m = disc_mask(int(round(rp * 2)))
        self.paste_mask(color, m, self.X(x) - m.width / 2.0, self.Y(y) - m.height / 2.0, alpha)

    def ring(self, x, y, r, w, color, alpha=1.0):
        rp, wp = r * self.u, max(1.0, w * self.u)
        if rp < 1:
            return
        if rp > 260:                                   # big rings: supersampled outline on a clipped layer
            px, py, rr = self.X(x), self.Y(y), rp + wp / 2
            box = (max(0, px - rr - 2), max(0, py - rr - 2), min(W, px + rr + 2), min(H, py + rr + 2))
            if box[2] - box[0] < 2 or box[3] - box[1] < 2:
                return
            Lr = Layer(box, 2)
            Lr.ellipse(px, py, rr, rr, None, outline=col(color)[:3], width=wp)
            self.blit(Lr.finish(), Lr.x0, Lr.y0, alpha)
            return
        m = ring_mask(int(round(rp * 2)), int(round(wp * 2)))
        self.paste_mask(color, m, self.X(x) - m.width / 2.0, self.Y(y) - m.height / 2.0, alpha)

    def sphere(self, x, y, r, stops, hl=(-0.35, -0.4), alpha=1.0):
        rp = r * self.u
        if rp < 1:
            return
        q = min(150, max(2, int(round(rp / 3.0)) * 3))
        spr = grad_disc(q * 2, skey(stops),
                        int(hl[0] * 10) * 2, int(hl[1] * 10) * 2)
        s = rp / q
        if abs(s - 1) > 0.01:
            spr = spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BICUBIC)
        self.blit(spr, self.X(x) - spr.width / 2.0, self.Y(y) - spr.height / 2.0, alpha)

    def rrect(self, x, y, w, h, rad, color, alpha=1.0):
        u = self.u
        if w * u < 1 or h * u < 1:
            return
        m = rrect_mask(int(round(w * u)), int(round(h * u)), int(round(rad * u * 2)))
        self.paste_mask(color, m, self.X(x) - m.width / 2.0, self.Y(y) - m.height / 2.0, alpha)

    def glow(self, x, y, r, color, k=1.0, power=2.0, add=True):
        rp = r * self.u
        if rp < 3 or k <= 0.01:
            return
        rq = max(4, int(round(rp / 4.0)) * 4)
        if rq > 240:
            m = glow_mask(240, int(power * 10))
            m = m.resize((int(rq * 2 + 2), int(rq * 2 + 2)), Image.BILINEAR)
        else:
            m = glow_mask(rq, int(power * 10))
        if k < 0.997:
            m = m.point(alut(k))
        bx0, by0 = int(round(self.X(x) - m.width / 2.0)), int(round(self.Y(y) - m.height / 2.0))
        bx1, by1 = bx0 + m.width, by0 + m.height
        cx0, cy0, cx1, cy1 = max(0, bx0), max(0, by0), min(W, bx1), min(H, by1)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        if (cx0, cy0, cx1, cy1) != (bx0, by0, bx1, by1):
            m = m.crop((cx0 - bx0, cy0 - by0, cx1 - bx0, cy1 - by0))
        if add:
            reg = self.im.crop((cx0, cy0, cx1, cy1))
            tint = Image.new("RGB", reg.size, col(color)[:3])
            glowimg = Image.composite(tint, Image.new("RGB", reg.size, (0, 0, 0)), m)
            self.im.paste(ImageChops.add(reg, glowimg), (cx0, cy0))
        else:
            self.im.paste(col(color)[:3], (cx0, cy0), m)

    # ---- supersampled layer for complex shapes
    @contextmanager
    def layer(self, box=None, ss=3, alpha=1.0):
        if box is None:
            px0, py0, px1, py1 = 0, 0, W, H
        else:
            x0, y0, x1, y1 = box
            px0, py0 = math.floor(self.X(x0)), math.floor(self.Y(y0))
            px1, py1 = math.ceil(self.X(x1)), math.ceil(self.Y(y1))
            if px0 > px1:
                px0, px1 = px1, px0
            if py0 > py1:
                py0, py1 = py1, py0
            px0, py0, px1, py1 = max(0, px0), max(0, py0), min(W, px1), min(H, py1)
        if px1 - px0 < 1 or py1 - py0 < 1:
            L = Layer((0, 0, 1, 1), 1)
            yield DLayer(self, L, alpha)
            return
        area = (px1 - px0) * (py1 - py0)
        ss = max(1, min(ss, 4 if area < 60000 else 3 if area < 450000 else 2))
        L = Layer((px0, py0, px1, py1), ss)
        yield DLayer(self, L, alpha)
        self.blit(L.finish(), L.x0, L.y0, alpha)

    # ---- text
    def text(self, s, x, y, size, color, anchor="c", alpha=1.0, shadow=None, stroke=None, max_w=None):
        sp = max(6, int(round(size * self.u)))
        tm = TE.get(s, sp)
        if max_w:
            iw = tm.bbox[2] - tm.bbox[0]
            if iw > max_w * self.u:
                sp = max(6, int(sp * max_w * self.u / iw))
                tm = TE.get(s, sp)
        bx0, by0, bx1, by1 = tm.bbox
        px, py = self.X(x), self.Y(y)
        if anchor == "c":
            ox = px - (bx0 + bx1) / 2.0
        elif anchor == "l":
            ox = px - bx0
        else:
            ox = px - bx1
        oy = py + 0.36 * sp - tm.base
        if shadow:
            sc, dx, dy = shadow
            self.paste_mask(sc, tm.ink, ox + bx0 + dx * self.u, oy + by0 + dy * self.u, alpha)
        if stroke:
            sc, sw = stroke
            sw = sw * self.u
            for k in range(8):
                a = k * math.pi / 4
                self.paste_mask(sc, tm.ink, ox + bx0 + math.cos(a) * sw, oy + by0 + math.sin(a) * sw, alpha)
        self.paste_mask(color, tm.ink, ox + bx0, oy + by0, alpha)
        return (bx1 - bx0) / self.u

    def text_width(self, s, size):
        tm = TE.get(s, max(6, int(round(size * self.u))))
        return (tm.bbox[2] - tm.bbox[0]) / self.u

    def text3d(self, s, x, y, size, face, side, depth, focal=(0, 0), alpha=1.0, max_w=None, edge=None):
        sp = max(6, int(round(size * self.u)))
        tm = TE.get(s, sp)
        if max_w:
            iw = tm.bbox[2] - tm.bbox[0]
            if iw > max_w * self.u:
                sp = max(6, int(sp * max_w * self.u / iw))
                tm = TE.get(s, sp)
        bx0, by0, bx1, by1 = tm.bbox
        px, py = self.X(x), self.Y(y)
        ox, oy = px - (bx0 + bx1) / 2.0, py + 0.36 * sp - tm.base
        vx, vy = focal[0] - x, focal[1] - y
        n = math.hypot(vx, vy) or 1.0
        vx, vy = vx / n, vy / n
        if abs(vx) < 0.15 and abs(vy) < 0.15:
            vx, vy = 0.0, 1.0
        steps = max(3, int(depth * self.u / 1.6))
        dp = depth * self.u * (sp / max(6, int(round(size * self.u))))
        for k in range(steps, 0, -1):
            f = k / steps
            shade = mix(side, (0, 0, 0), 0.25 * f)
            self.paste_mask(shade, tm.ink, ox + bx0 + vx * dp * f, oy + by0 + vy * dp * f, alpha)
        if edge:
            self.paste_mask(edge, tm.ink, ox + bx0 - 1.5 * self.u, oy + by0 - 1.5 * self.u, alpha)
        self.paste_mask(face, tm.ink, ox + bx0, oy + by0, alpha)



# =============================================================================
#  SPRITES  &  REUSABLE BUILDING BLOCKS
# =============================================================================
STAR_COLS = [(255, 255, 255), (170, 240, 255), (255, 190, 230)]


@lru_cache(maxsize=256)
def star_sprite(kind, cidx, lvl):
    r = (1.3, 2.3, 6.0)[kind] * FS
    n = int(r) + 4
    L = Layer((-n, -n, n, n), 4)
    c = STAR_COLS[cidx]
    if kind == 2:
        L.poly(star_pts(0, 0, r, 0.2, 4), c)
        L.ellipse(0, 0, r * 0.28, r * 0.28, c)
    else:
        L.ellipse(0, 0, r, r, c)
    img = L.finish()
    img.putalpha(img.getchannel("A").point(alut((lvl + 1) / 8.0)))
    return img


class StarField:
    def __init__(self, n, seed, bottom=0.84):
        rs = np.random.RandomState(seed)
        self.n = n
        self.x, self.y = rs.uniform(0, W, n), rs.uniform(0, H * bottom, n)
        self.k = rs.choice(3, n, p=[0.62, 0.28, 0.10])
        self.c = rs.choice(3, n, p=[0.60, 0.25, 0.15])
        self.ph, self.sp = rs.uniform(0, 6.28, n), rs.uniform(1.0, 3.4, n)
        self.sz = rs.uniform(0.7, 1.3, n)

    def draw(self, cv, t, drift=0.0, alpha=1.0):
        for i in range(self.n):
            a = 0.5 + 0.5 * math.sin(t * self.sp[i] + self.ph[i])
            spr = star_sprite(int(self.k[i]), int(self.c[i]), int(a * 7.99))
            x = (self.x[i] + drift * (0.3 + 0.35 * self.k[i])) % W
            cv.blit(spr, x - spr.width / 2.0, self.y[i] - spr.height / 2.0, alpha)


_STARS = {}


def stars(seed, n=120):
    if (seed, n) not in _STARS:
        _STARS[(seed, n)] = StarField(n, seed)
    return _STARS[(seed, n)]


@lru_cache(maxsize=64)
def sparkle_sprite(rpx, color):
    n = int(rpx) + 3
    L = Layer((-n, -n, n, n), 4)
    L.poly(star_pts(0, 0, rpx, 0.22, 4), color)
    L.ellipse(0, 0, rpx * 0.22, rpx * 0.22, (255, 255, 255))
    return L.finish()


def sparkle(cv, x, y, r, color=(255, 255, 255), alpha=1.0, rot=0.0):
    rp = max(3, int(r * cv.u / 2) * 2)
    cv.sprite(sparkle_sprite(rp, col(color)[:3]), x, y, rot=rot, alpha=alpha)


def draw_shockwave(cv, x, y, p, rmax, color, wmax=22, alpha=1.0):
    p = clamp(p)
    if p <= 0 or p >= 1:
        return
    r = rmax * ease_out_cubic(p)
    w = max(1.0, wmax * (1 - p) ** 1.4)
    cv.ring(x, y, r, w, color, alpha * (1 - p) ** 0.7)
    cv.ring(x, y, r * 0.86, w * 0.5, color, alpha * 0.35 * (1 - p))


def draw_rays(cv, x, y, t, r, n, color, alpha=0.3, spin=14.0, width=0.5, rot0=0.0):
    """Rotating ray wedge star (god-rays / energy)."""
    with cv.layer((x - r, y - r, x + r, y + r), 2, alpha) as L:
        for i in range(n):
            a = math.radians(rot0 + spin * t + i * 360.0 / n)
            wdt = (2 * math.pi / n) * width
            L.poly([(x, y),
                    (x + r * math.cos(a - wdt), y + r * math.sin(a - wdt)),
                    (x + r * math.cos(a + wdt), y + r * math.sin(a + wdt))], color)


def draw_arrow(cv, p0, p1, w, color, head=1.0, alpha=1.0, prog=1.0):
    """Straight arrow p0->p1, drawn on with `prog`."""
    prog = clamp(prog)
    if prog <= 0.01:
        return
    q = (lerp(p0[0], p1[0], prog), lerp(p0[1], p1[1], prog))
    ang = math.atan2(q[1] - p0[1], q[0] - p0[0])
    hl = w * 2.6 * head
    tip = (q[0] + math.cos(ang) * hl * 0.8, q[1] + math.sin(ang) * hl * 0.8)
    with cv.layer((min(p0[0], tip[0]) - w * 4, min(p0[1], tip[1]) - w * 4,
                   max(p0[0], tip[0]) + w * 4, max(p0[1], tip[1]) + w * 4), 3, alpha) as L:
        L.line([p0, (q[0] + math.cos(ang) * hl * 0.2, q[1] + math.sin(ang) * hl * 0.2)], w, color)
        if prog > 0.55:
            k = clamp((prog - 0.55) / 0.45)
            base = (tip[0] - math.cos(ang) * hl * k, tip[1] - math.sin(ang) * hl * k)
            L.poly([tip,
                    (base[0] + math.cos(ang + 1.9) * hl * 0.8, base[1] + math.sin(ang + 1.9) * hl * 0.8),
                    (base[0] + math.cos(ang - 1.9) * hl * 0.8, base[1] + math.sin(ang - 1.9) * hl * 0.8)], color)


def draw_curve_arrow(cv, pts, w, color, alpha=1.0, prog=1.0):
    """Curved arrow along a polyline with a head at the end."""
    prog = clamp(prog)
    if prog <= 0.02:
        return
    n = max(2, int(len(pts) * prog))
    P = pts[:n]
    ang = math.atan2(P[-1][1] - P[-2][1], P[-1][0] - P[-2][0])
    hl = w * 2.8
    tip = (P[-1][0] + math.cos(ang) * hl * 0.7, P[-1][1] + math.sin(ang) * hl * 0.7)
    xs, ys = [p[0] for p in P], [p[1] for p in P]
    with cv.layer((min(xs) - w * 5, min(ys) - w * 5, max(xs) + w * 5, max(ys) + w * 5), 3, alpha) as L:
        L.line(P + [tip], w, color)
        L.poly([tip,
                (P[-1][0] + math.cos(ang + 1.9) * hl * 0.9, P[-1][1] + math.sin(ang + 1.9) * hl * 0.9),
                (P[-1][0] + math.cos(ang - 1.9) * hl * 0.9, P[-1][1] + math.sin(ang - 1.9) * hl * 0.9)], color)


def draw_chevrons(cv, p0, p1, t, n, color, size=16.0, alpha=0.9, speed=1.0):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    ang = math.atan2(uy, ux)
    for i in range(n):
        f = ((i / n) + t * 0.55 * speed) % 1.0
        px, py = p0[0] + dx * f, p0[1] + dy * f
        a = math.sin(math.pi * f) * alpha
        with cv.layer((px - size * 3, py - size * 3, px + size * 3, py + size * 3), 3, a) as Ly:
            Ly.poly([(px + math.cos(ang) * size, py + math.sin(ang) * size),
                     (px + math.cos(ang + 2.4) * size, py + math.sin(ang + 2.4) * size),
                     (px + math.cos(ang - 2.4) * size, py + math.sin(ang - 2.4) * size)], color)


def draw_badge(cv, x, y, text, size=26, bg=(255, 255, 255), fg=(20, 22, 40), p=1.0,
               alpha=1.0, pad=0.55, rot=0.0, glow=None):
    """Rounded pill with a text label (label caps: try to keep Latin)."""
    p = clamp(p)
    if p <= 0.02 or alpha <= 0.01:
        return
    sc = ease_out_back(p)
    tw = cv.text_width(text, size) if TE else size * 0.6 * len(text)
    hw = (tw / 2.0 + size * pad) * sc
    hh = (size * 0.78) * sc
    x = clamp(x, -SAFE_X + hw + 8, SAFE_X - hw - 8)
    y = clamp(y, -SAFE_Y + hh + 6, SAFE_Y - hh - 6)
    with cv.layer((x - hw - 6, y - hh - 6, x + hw + 6, y + hh + 6), 3, alpha) as L:
        L.rrect(x, y, hw * 2, hh * 2, hh, bg)
    if glow:
        cv.glow(x, y, hw * 1.2, glow, 0.35 * p, 2.5)
    if sc > 0.55:
        cv.text(text, x, y - size * 0.02, size * min(1.0, sc), fg, "c", alpha * clamp((sc - 0.5) * 3))


def draw_caliper(cv, p0, p1, label, color, prog=1.0, cap=18.0, width=3.5, size=26, alpha=1.0):
    """Dashed measurement line with end caps + centred label."""
    prog = clamp(prog)
    if prog <= 0.02:
        return
    q = (lerp(p0[0], p1[0], prog), lerp(p0[1], p1[1], prog))
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    with cv.layer((min(p0[0], q[0]) - cap * 2, min(p0[1], q[1]) - cap * 2,
                   max(p0[0], q[0]) + cap * 2, max(p0[1], q[1]) + cap * 2), 3, alpha) as Ly:
        Ly.dashed(p0, q, width, 13, 9, color, offset=0.0)
        for (px, py) in (p0, q):
            Ly.line([(px - nx * cap, py - ny * cap), (px + nx * cap, py + ny * cap)], width, color)
    if label and prog > 0.6:
        k = clamp((prog - 0.6) / 0.4)
        draw_badge(cv, (p0[0] + q[0]) / 2, (p0[1] + q[1]) / 2 - 30, label, size, bg=color,
                   fg=(12, 14, 28), p=k, alpha=alpha)


def draw_molecule(cv, x, y, r, ang, c1=(255, 255, 255), c2=(150, 235, 255), alpha=1.0):
    dx, dy = math.cos(ang) * r, math.sin(ang) * r
    with cv.layer((x - r * 2, y - r * 2, x + r * 2, y + r * 2), 3, alpha) as L:
        L.line([(x - dx, y - dy), (x + dx, y + dy)], r * 0.55, c1)
    cv.disc(x - dx, y - dy, r * 0.72, c2, alpha)
    cv.disc(x + dx, y + dy, r * 0.72, c1, alpha)


def draw_prohibit(cv, x, y, r, p=1.0, color=None, alpha=1.0, pulse=0.0):
    color = color or C["red"]
    p = clamp(p)
    if p <= 0.03:
        return
    rr = r * (0.9 + 0.1 * math.sin(pulse * 6.0))
    cv.ring(x, y, rr, max(2.5, r * 0.24), color, alpha * clamp(p * 1.6))
    a0 = -90.0
    a1 = -90.0 + 360.0 * ease_out_cubic(p)
    with cv.layer((x - r * 1.2, y - r * 1.2, x + r * 1.2, y + r * 1.2), 3, alpha) as L:
        L.line(ellipse_pts(x, y, rr * 0.78, rr * 0.78, 45, 0, 360, 2), rr * 0.24, color)


def draw_grid(cv, x, y, w2, h2, warp=None, color=(90, 120, 255), alpha=0.35, nx=13, ny=9, w=1.6):
    """Spacetime grid, optionally displaced by warp(x,y)->(dx,dy) (gravity well)."""
    with cv.layer((x - w2 - 40, y - h2 - 40, x + w2 + 40, y + h2 + 40), 2, alpha) as L:
        for i in range(nx + 1):
            u = -1 + 2.0 * i / nx
            pts = []
            for k in range(ny * 3 + 1):
                v = -1 + 2.0 * k / (ny * 3)
                px, py = x + u * w2, y + v * h2
                if warp:
                    dx, dy = warp(px, py)
                    px, py = px + dx, py + dy
                pts.append((px, py))
            L.line(pts, w, color)
        for j in range(ny + 1):
            v = -1 + 2.0 * j / ny
            pts = []
            for k in range(nx * 3 + 1):
                u = -1 + 2.0 * k / (nx * 3)
                px, py = x + u * w2, y + v * h2
                if warp:
                    dx, dy = warp(px, py)
                    px, py = px + dx, py + dy
                pts.append((px, py))
            L.line(pts, w, color)


# ------------------------- the hero: a black hole ---------------------------
DISK_STOPS = [(0.00, "#FFFDF6"), (0.12, "#FFE9A0"), (0.28, "#FFC22E"), (0.45, "#FF8412"),
              (0.62, "#FF2E6E"), (0.80, "#C21BC4"), (1.00, "#5A1A8E")]


def disk_color(u, bright=1.0):
    pos = [s[0] for s in DISK_STOPS]
    cols = [col(s[1]) for s in DISK_STOPS]
    i = 0
    while i < len(pos) - 2 and u > pos[i + 1]:
        i += 1
    f = clamp((u - pos[i]) / max(1e-6, pos[i + 1] - pos[i]))
    c = mix(cols[i], cols[i + 1], f)
    if bright < 0.999:
        c = mix(c, mix(C["magenta"], C["violet"], 0.45), (1.0 - bright) * 0.85)
    elif bright > 1.001:
        c = mix(c, (255, 255, 255), min(1.0, bright - 1.0) * 0.9)
    return tuple(int(clamp(v, 0, 255)) for v in c)


def _ell_seg(L, x, y, r_in, r_out, a0, a1, tilt, color):
    """One flat-vector wedge of an elliptical annulus (no outlines anywhere)."""
    L.poly([(x + r_in * math.cos(a0), y + r_in * math.sin(a0) * tilt),
            (x + r_out * math.cos(a0), y + r_out * math.sin(a0) * tilt),
            (x + r_out * math.cos(a1), y + r_out * math.sin(a1) * tilt),
            (x + r_in * math.cos(a1), y + r_in * math.sin(a1) * tilt)], color)


def _disk_arc(L, x, y, r_in, r_out, a0, a1, tilt, t, spin, beams, seg=20,
              band=(0.0, 1.0), dim=1.0, feeler=0.0, fade=0.0):
    """Angular ramp (white-hot -> amber -> orange -> magenta -> violet) + Doppler beaming."""
    for k in range(seg):
        b0 = lerp(a0, a1, k / seg)
        b1 = lerp(a0, a1, (k + 1.015) / seg)
        th = 0.5 * (b0 + b1)
        u = lerp(band[0], band[1], (k + 0.5) / seg)
        heat = 0.5 + 0.5 * math.cos(th - beams + t * spin * 0.30 + feeler)
        br = dim * (0.74 + 0.56 * heat)
        if fade > 0.001:
            e = math.sin(math.pi * clamp((k + 0.5) / seg))
            br *= (1.0 - fade) + fade * e
        _ell_seg(L, x, y, r_in, r_out, b0, b1, tilt, disk_color(u, br))


def draw_bh(cv, x, y, r, t=0.0, alpha=1.0, tilt=0.44, disk=1.0, glow=1.0, spin=1.0,
            ring=1.0, beam=1.0, shadow=True, jet=0.0, disk_scale=2.05, seed=0, hole=1.03, tilt_h=0.50):
    """The showpiece: black shadow, photon ring, Doppler-beamed accretion disk, lensed arc."""
    if alpha <= 0.01 or r <= 1:
        return
    ro = r * disk_scale
    tilt = tilt_h
    beams = -0.28 * beam
    puls = 0.5 + 0.5 * math.sin(t * 1.7 + seed)
    cv.glow(x, y, ro * 1.15, C["magenta"], 0.20 * glow, 2.8, add=True)
    cv.glow(x, y, r * 1.65, C["orange"], 0.22 * glow * (0.92 + 0.16 * puls), 2.2, add=True)
    if jet > 0.01:
        with cv.layer((x - r * 3, y - r * 9, x + r * 3, y + r * 9), 2, alpha * jet) as L:
            for sy in (-1, 1):
                L.poly([(x - r * 0.55, y), (x - r * 0.10, y + sy * r * 7.4),
                        (x, y + sy * r * 8.4), (x + r * 0.10, y + sy * r * 7.4),
                        (x + r * 0.55, y)], C["cyan"])
    if shadow:
        cv.disc(x, y, r * 0.955, (4, 3, 11), alpha)
        cv.ring(x, y, r * 0.965, max(1.0, r * 0.013), (14, 8, 28), alpha)
    if ring > 0.01:                                  # photon ring: the last light orbit
        with cv.layer((x - r * 1.3, y - r * 1.3, x + r * 1.3, y + r * 1.3), 3, alpha * ring) as L:
            L.line(ellipse_pts(x, y, r * 1.005, r * 1.005, 0, 0, 360, 56), max(1.3, r * 0.016), (255, 251, 226))
            L.line(ellipse_pts(x, y, r * 1.045, r * 1.045, 0, 0, 360, 56), max(0.9, r * 0.010), (255, 206, 126))
        cv.glow(x, y, r * 1.65, C["amber"], 0.18 * glow * ring, 2.6, add=True)
    if disk > 0.01:
        # near side: the disk sweeps toward us and hides the bottom of the shadow
        with cv.layer((x - ro * 1.06, y - ro * 1.06, x + ro * 1.06, y + ro * 1.06), 2, alpha * disk) as L:
            for b in range(11):
                f0, f1 = b / 11.0, (b + 1) / 11.0
                _disk_arc(L, x, y, lerp(r * hole, ro, f0 ** 1.15), lerp(r * hole, ro, f1 ** 1.15),
                          0.02, math.pi - 0.02, tilt, t, spin, beams, 30,
                          (0.0, 1.0) if b else (0.0, 0.08))
            for k in range(10):                      # flowing hot filaments inside the disk
                ph = (k / 10.0 + t * 0.05 * spin) % 1.0
                a0 = 0.14 + ph * 2.62
                rr = r * lerp(0.55, 1.85, (k * 0.43) % 1.0)
                L.line(ellipse_pts(x, y, rr, rr * tilt, 0, a0 * 57.3, (a0 + 0.13) * 57.3, 8),
                       max(0.8, r * 0.009), (255, 240, 200, 200))
        # far side, gravitationally lensed: a bright halo over the shadow's top edge
        with cv.layer((x - r * 1.45, y - r * 1.45, x + r * 1.45, y + r * 1.45), 3, alpha * disk) as L:
            for b in range(3):
                f0, f1 = b / 3.0, (b + 1) / 3.0
                _disk_arc(L, x, y, lerp(r * 1.01, r * 1.24, f0), lerp(r * 1.01, r * 1.24, f1),
                          math.pi + 0.10, 2 * math.pi - 0.10, 0.97, t, spin, beams, 30,
                          (0.02, 0.26), dim=1.10, fade=0.55)
    for i in range(10):                                 # sparks riding the near side of the disk
        f = (i / 10.0 + t * 0.11 * spin) % 1.0
        a = (0.30 + f * 0.95) if i % 2 else (2.00 + f * 0.95)
        rr = r * lerp(1.30, disk_scale * 0.94, (i * 0.41) % 1.0)
        px, py = x + rr * math.cos(a), y + rr * math.sin(a) * tilt
        sp = 0.5 + 0.5 * math.sin(t * 5 + i * 1.7)
        cv.glow(px, py, r * 0.12 * (0.7 + sp), C["sun"], 0.34 * alpha * disk, 2.0)


def photons_in(cv, x, y, r, t, n=3, rmax=None, color=None):
    """Light rays spiralling into the horizon (doomed photons)."""
    color = color or C["sun"]
    rmax = rmax or r * 3.4
    for i in range(n):
        f = ((t * 0.55 + i / n) % 1.0)
        rr = rmax * (1 - ease_in_cubic(f)) + r * 1.05
        a = f * 7.0 + i * 2.1
        px, py = x + rr * math.cos(a), y + rr * math.sin(a) * 0.32
        al = 1.0 - f * 0.5
        cv.glow(px, py, r * 0.20, color, 0.55 * al, 2.0)
        cv.disc(px, py, r * 0.045, (255, 255, 255), al)


# ------------------------------- humans -------------------------------------
def _capsule(L, p0, p1, w, color):
    L.line([p0, p1], w, color)


POSES = {
    #   larm larm2 rarm rarm2  lleg rleg2  head  (degrees, 0 = down, +=toward face)
    "stand": (14, 8, -14, 8, 6, -6, 0),
    "point": (16, 10, -96, -18, 8, -8, -4),
    "up": (18, 6, -150, -6, 8, -8, -10),
    "fall": (-150, 20, -160, 24, -30, 20, 6),
    "reach": (150, -10, -150, -10, 40, -20, -12),
    "throw": (12, 6, -120, -40, 10, -12, -6),
    "shrug": (110, -20, -110, 20, 8, -8, -4),
    "hold": (30, 40, -30, 40, 8, -8, 2),
    "look": (14, 8, -14, 8, 6, -6, -14),
    "run": (60, 40, -70, 50, 34, -34, -6),
    "tada": (140, -30, -140, 30, 12, -12, -8),
}


def draw_human(cv, x, y, s, t=0.0, pose="stand", skin=None, shirt=None, pants=None,
               hair=None, flip=False, alpha=1.0, sx=1.0, sy=1.0, look=0.0, blink=None,
               mouth=None, rot=0.0, helmet=None):
    """Kurzgesagt-ish flat human.  s = total height in design units.
    Every part is placed through one transform, so squash / stretch / rotation stay coherent."""
    if alpha <= 0.01 or s < 1:
        return
    skin = skin or C["skin2"]
    shirt = shirt or C["hoodie"]
    pants = pants or C["jeans"]
    hair = hair or C["hair"]
    skind = mix(skin, (0, 0, 0), 0.16)
    shirtd = mix(shirt, (0, 0, 0), 0.24)
    pantsd = mix(pants, (0, 0, 0), 0.22)
    a1, a2, b1, b2, c1, c2, hd = POSES.get(pose, POSES["stand"])
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    lw = 0.092 * s
    hr = 0.140 * s
    bw = max(0.45, 1.0 / max(0.25, sx)) * 1.05

    def R(pt):
        if abs(rot) < 1e-4:
            return pt
        return (pt[0] * ca - pt[1] * sa, pt[0] * sa + pt[1] * ca)

    box = (-0.7 * s * bw, -0.85 * s * sy, 0.7 * s * bw, 0.78 * s * sy)
    with cv.layer((x + box[0], y + box[1], x + box[2], y + box[3]), 3, alpha) as L:
        def P(px, py):
            q = R((px * sx, py * sy))
            return (x + q[0], y + q[1])

        sh_y, hip_y = -0.185 * s, 0.055 * s
        # ---- legs ----
        for sgn, aa, bb in ((-1, c1, c2), (1, -c1, c2)):
            hip = P(sgn * 0.062 * s, hip_y)
            kx = sgn * 0.062 * s + math.sin(math.radians(aa)) * 0.20 * s
            ky = hip_y + math.cos(math.radians(aa)) * 0.20 * s
            kn = P(kx, ky)
            fx = kx + math.sin(math.radians(bb)) * 0.17 * s
            fy = ky + math.cos(math.radians(bb)) * 0.17 * s
            ft = P(fx, fy)
            L.line([hip, kn], lw * 1.05, pantsd if sgn < 0 else pants)
            L.line([kn, ft], lw * 0.98, pants)
            fq = P(fx + sgn * 0.045 * s, fy + 0.012 * s)
            L.ellipse(fq[0], fq[1], 0.058 * s * sx + 0.01, 0.031 * s * sy + 0.008, C["ink"])
        # ---- hips + torso + neck ----
        L.line([P(0, 0.02 * s), P(0, 0.125 * s)], 0.195 * s * sx, pantsd)
        L.line([P(0, -0.20 * s), P(0, 0.075 * s)], 0.205 * s * sx, shirt)
        L.line([P(-0.042 * s, -0.185 * s), P(0.042 * s, 0.05 * s)], 0.075 * s * sx, shirtd)
        L.line([P(0, -0.235 * s), P(0, -0.185 * s)], 0.085 * s * sx, skind)
        # ---- arms ----
        for sgn, aa, bb in ((-1, a1, a2), (1, b1, b2)):
            sh = P(sgn * 0.125 * s, sh_y)
            ex = sgn * 0.125 * s + math.sin(math.radians(aa)) * 0.15 * s
            ey = sh_y + math.cos(math.radians(aa)) * 0.155 * s
            el = P(ex, ey)
            hx2 = sgn * 0.125 * s + math.sin(math.radians(aa + bb)) * 0.29 * s
            hy2 = sh_y + math.cos(math.radians(aa + bb)) * 0.29 * s
            hd2 = P(hx2, hy2)
            L.line([sh, el], lw * 0.90, mix(shirt, (0, 0, 0), 0.16) if sgn < 0 else mix(shirt, (0, 0, 0), 0.06))
            L.line([el, hd2], lw * 0.78, skind if sgn < 0 else skin)
            L.ellipse(hd2[0], hd2[1], 0.043 * s * sx + 0.005, 0.043 * s * sy + 0.005,
                      skind if sgn < 0 else skin)
        # ---- head ----
        hc = P(hd * 0.002 * s, -0.355 * s)
        hrx, hry = hr * sx, hr * 1.05 * sy
        L.ellipse(hc[0], hc[1], hrx, hry, skin)
        # hair: cap over the top half, drawn through the same transform
        hp = []
        for k in range(19):
            aa = math.radians(-180 + 200.0 * k / 18.0)
            hp.append(P((hd * 0.002 * s) + hr * 1.08 * math.cos(aa), -0.355 * s + hr * 1.12 * math.sin(aa)))
        hp.append(P(hd * 0.002 * s - hr * 1.02, -0.352 * s))
        hp.append(P(hd * 0.002 * s + hr * 1.02, -0.352 * s))
        L.poly(hp, hair)
        L.ellipse(hc[0] - hr * 0.5 * sx, hc[1] - hr * 0.85 * sy, hr * 0.26 * sx, hr * 0.15 * sy,
                  mix(hair, (255, 255, 255), 0.18))
        # ---- face ----
        if blink is None:
            blink = (math.sin(t * 2.1 + x * 0.02) > 0.985) or (math.sin(t * 0.7 + 2.0) > 0.996)
        for sgn in (-1, 1):
            e = P(hd * 0.002 * s + sgn * 0.058 * s + look * 0.016 * s, -0.315 * s)
            if blink:
                L.line([(e[0] - hr * 0.16 * sx, e[1]), (e[0] + hr * 0.16 * sx, e[1])],
                       max(1.6, hr * 0.09), C["ink"])
            else:
                L.ellipse(e[0], e[1], hr * 0.165 * sx + 0.6, hr * 0.215 * sy + 0.6, C["white"])
                L.ellipse(e[0] + look * hr * 0.05, e[1] + hr * 0.02, hr * 0.098 * sx + 0.5,
                          hr * 0.128 * sy + 0.5, C["ink"])
                L.ellipse(e[0] - hr * 0.03, e[1] - hr * 0.06, hr * 0.026 + 0.4, hr * 0.026 + 0.4, C["white"])
        if mouth is None:
            mouth = "smile"
        m = P(hd * 0.002 * s, -0.268 * s)
        mw = hr * 0.44 * sx
        if mouth == "smile":
            L.line([(m[0] - mw, m[1]), (m[0] - mw * 0.4, m[1] + hr * 0.075), (m[0] + mw * 0.4, m[1] + hr * 0.075),
                    (m[0] + mw, m[1])], max(1.8, hr * 0.075), C["ink"])
        elif mouth == "open":
            L.ellipse(m[0], m[1] + hr * 0.03, hr * 0.135 * sx, hr * 0.16 * sy, C["ink"])
        elif mouth == "flat":
            L.line([(m[0] - mw * 0.8, m[1]), (m[0] + mw * 0.8, m[1])], max(1.7, hr * 0.07), C["ink"])
        elif mouth == "scream":
            L.ellipse(m[0], m[1] + hr * 0.06, hr * 0.19 * sx, hr * 0.22 * sy, C["ink"])
            L.ellipse(m[0], m[1] + hr * 0.13, hr * 0.12 * sx, hr * 0.09 * sy,
                      mix(C["red"], (255, 255, 255), 0.15))
        if helmet:
            cv.ring(hc[0], hc[1], max(hrx, hry) * 1.35, max(2.0, hr * 0.10), helmet, alpha * 0.95)


# ------------------------------ props ---------------------------------------
def draw_clock(cv, x, y, r, t, alpha=1.0, speed=1.0, face=(255, 255, 255), rim=None,
               hands=(24, 30), glow=None, colors=None):
    rim = rim or C["ink"]
    colors = colors or (C["ink"], C["red"])
    if alpha <= 0.01 or r < 1:
        return
    if glow:
        cv.glow(x, y, r * 1.9, glow, 0.35 * alpha, 2.4)
    cv.disc(x, y, r, face, alpha)
    cv.ring(x, y, r, max(2.0, r * 0.11), rim, alpha)
    with cv.layer((x - r * 1.3, y - r * 1.3, x + r * 1.3, y + r * 1.3), 3, alpha) as L:
        for i in range(12):
            a = math.radians(i * 30.0)
            p0 = (x + r * 0.80 * math.sin(a), y - r * 0.80 * math.cos(a))
            p1 = (x + r * 0.90 * math.sin(a), y - r * 0.90 * math.cos(a))
            L.line([p0, p1], max(1.6, r * (0.075 if i % 3 == 0 else 0.045)), C["smoke2"])
        mh = math.radians(hands[0] * t * speed)
        hh = math.radians(hands[1] * t * speed * 0.12)
        L.line([(x, y), (x + r * 0.52 * math.sin(mh), y - r * 0.52 * math.cos(mh))], max(2.0, r * 0.085), colors[0])
        L.line([(x, y), (x + r * 0.36 * math.sin(hh), y - r * 0.36 * math.cos(hh))], max(2.5, r * 0.11), colors[1])
    cv.disc(x, y, max(1.6, r * 0.075), rim, alpha)


def draw_book(cv, x, y, s, rot=0.0, t=0.0, alpha=1.0, label=None):
    """Small info-book (open-ish) in units, s = width."""
    if alpha <= 0.01 or s < 1:
        return
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def P(px, py):
        return (x + px * cr - py * sr, y + px * sr + py * cr)

    with cv.layer((x - s * 1.2, y - s * 1.2, x + s * 1.2, y + s * 1.2), 3, alpha) as L:
        L.poly([P(-s * 0.5, -s * 0.62), P(s * 0.5, -s * 0.62), P(s * 0.5, s * 0.62), P(-s * 0.5, s * 0.62)],
               C["white"])
        L.poly([P(-s * 0.5, -s * 0.62), P(s * 0.5, -s * 0.62), P(s * 0.5, 0.62 * s), P(-s * 0.5, s * 0.62)],
               (236, 238, 250))
        L.poly([P(-s * 0.5, -s * 0.62), P(-s * 0.5, s * 0.62), P(-s * 0.36, s * 0.62), P(-s * 0.36, -s * 0.62)],
               C["pink"])
        for i in range(4):
            yy = -s * 0.32 + i * s * 0.20
            L.line([P(-s * 0.26, yy), P(s * 0.34, yy)], max(1.4, s * 0.035), (170, 176, 205))
    if label:
        cv.text(label, x, y - s * 0.1, s * 0.30, C["navy_txt"], "c", alpha)


@lru_cache(maxsize=24)
def galaxy_sprite(rpx, seed=3):
    """Spiral galaxy sprite: soft disc, drawn spiral arms, hot core."""
    rpx = max(16, int(rpx))
    n = int(rpx * 2) + 8
    c = (n - 1) / 2.0
    L = Layer((0, 0, n, n), 2)
    rs = np.random.RandomState(seed)
    # --- soft disc: stacked translucent ellipses (cheap radial falloff)
    for i in range(16, 0, -1):
        f = i / 16.0
        L.ellipse(c, c, rpx * 0.98 * f, rpx * 0.92 * f, (70, 30, 150, 6))
    # --- spiral arms as continuous strokes
    arms = 2
    for a in range(arms):
        base = a * math.pi
        pts = []
        for i in range(60):
            f = i / 59.0
            ang = base + f * 3.9
            rad = (0.10 + 0.88 * f) * rpx
            pts.append((c + rad * math.cos(ang), c + rad * math.sin(ang) * 0.93))
        for w, colr in ((0.052, (150, 60, 210, 70)), (0.026, (255, 120, 210, 95)), (0.009, (255, 225, 190, 130))):
            L.line(pts, rpx * w, colr)
    # --- bright knots + field stars
    for a in range(arms):
        base = a * math.pi
        for i in range(150):
            f = (i / 150.0) ** 0.7
            ang = base + f * 3.9 + rs.normal(0, 0.05)
            rad = (0.12 + 0.86 * f) * rpx
            px = c + rad * math.cos(ang) + rs.normal(0, rpx * 0.022)
            py = c + rad * math.sin(ang) * 0.93 + rs.normal(0, rpx * 0.022)
            rr = max(0.9, rpx * (0.004 + 0.005 * f) * rs.uniform(0.6, 1.6))
            cc = disk_color(clamp(0.10 + 0.75 * f, 0, 1), 1.05 + 0.3 * (1 - f))
            if rs.random() < 0.10:
                cc = (255, 255, 255, 235)
            L.ellipse(px, py, rr, rr, cc)
    for i in range(120):
        f = rs.uniform(0.15, 1.0)
        ang = rs.uniform(0, 2 * math.pi)
        px = c + f * rpx * 0.95 * math.cos(ang)
        py = c + f * rpx * 0.95 * math.sin(ang) * 0.93
        rr = rpx * 0.004 * rs.uniform(0.5, 1.5)
        L.ellipse(px, py, rr, rr, (255, 255, 255, 150))
    for i in range(10):                        # hot core
        rr = rpx * (0.17 - i * 0.016)
        L.ellipse(c, c, rr, rr * 0.94, mix(C["white"], C["amber"], i / 10.0))
    return L.finish()


def draw_galaxy(cv, x, y, r, t=0.0, alpha=1.0, rot=0.0, tilt=0.62):
    rp = max(8, int(r / 1.05))
    spr = galaxy_sprite(rp, 3)
    if abs(tilt - 1.0) > 0.02:
        spr = spr.resize((spr.width, max(2, int(spr.height * tilt))), Image.BICUBIC)
    cv.glow(x, y, r * 1.25, C["violet"], 0.26 * alpha, 2.6)
    cv.glow(x, y, r * 0.35, C["amber"], 0.35 * alpha, 2.2)
    cv.sprite(spr, x, y, rot=rot, alpha=alpha)


def draw_planet(cv, x, y, r, t=0.0, alpha=1.0, kind="earth", rot=0.0):
    if kind == "earth":
        cv.sphere(x, y, r, ((0.0, "#BFF3FF"), (0.35, "#38A8FF"), (0.7, "#1258C8"), (1.0, "#061A45")))
        with cv.layer((x - r, y - r, x + r, y + r), 3, alpha * 0.95) as L:
            rs = np.random.RandomState(7)
            for i in range(7):
                a = rot + i * 1.1
                px = x + math.cos(a) * r * 0.45
                py = y + math.sin(a * 1.7) * r * 0.42
                L.ellipse(px, py, r * (0.16 + 0.10 * ((i * 3) % 5) / 4), r * (0.13 + 0.07 * ((i * 2) % 4) / 3),
                          C["mint"] if i % 3 else (255, 214, 120))
            for i in range(3):
                L.ellipse(x + math.sin(rot + i) * r * 0.3, y - r * 0.35 + i * r * 0.36, r * 0.52, r * 0.07,
                          mix(C["white"], C["cyan"], 0.35))
        cv.glow(x, y, r * 1.35, C["cyan"], 0.22 * alpha, 2.6)
    else:
        cv.sphere(x, y, r, ((0.0, "#FFFDF0"), (0.30, "#FFE24A"), (0.62, "#FF9A00"), (1.0, "#FF4E00")))
        cv.glow(x, y, r * 2.2, C["amber"], 0.5 * alpha, 2.2)


def draw_vacuum(cv, x, y, s, t=0.0, alpha=1.0, flip=False):
    """Comedic cosmic vacuum cleaner (body + hose + nozzle)."""
    if alpha <= 0.01:
        return
    f = -1 if flip else 1
    with cv.layer((x - s * 1.3, y - s * 1.3, x + s * 1.3, y + s * 1.3), 3, alpha) as L:
        L.rrect(x - s * 0.05, y + 0.285 * s, s, 0.87 * s, s * 0.28, C["mint"])
        L.ellipse(x - s * 0.10, y + s * 0.62, s * 0.25, s * 0.20, C["smoke2"])
        L.ellipse(x - s * 0.10, y + s * 0.62, s * 0.11, s * 0.09, C["white"])
        L.rrect(x - 0.8 * s, y - 0.225 * s, 0.5 * s, 0.55 * s, s * 0.12, C["cyan"])
        L.poly([(x - s * 1.05, y - s * 0.5), (x - s * 1.25 * f, y - s * 0.72),
                (x - s * 1.05, y - s * 0.16)], C["cyan"])
        L.rrect(x + 0.325 * s, y - 0.225 * s, 0.45 * s, 0.25 * s, s * 0.1, C["smoke2"])


def draw_monster(cv, x, y, s, t=0.0, alpha=1.0, color=None):
    color = color or C["violet"]
    if alpha <= 0.01:
        return
    with cv.layer((x - s, y - s, x + s, y + s), 3, alpha) as L:
        pts = []
        for i in range(25):
            a = 2 * math.pi * i / 24.0
            rr = s * (0.62 + 0.14 * math.sin(a * 5 + t * 2.0))
            pts.append((x + rr * math.cos(a) * 1.05, y + rr * math.sin(a) * 0.85))
        L.poly(pts, color)
        for sgn in (-1, 1):
            L.ellipse(x + sgn * s * 0.26, y - s * 0.12, s * 0.17, s * 0.20, C["white"])
            L.ellipse(x + sgn * s * 0.26 + s * 0.04, y - s * 0.10, s * 0.08, s * 0.11, C["ink"])
        L.poly([(x - s * 0.28, y + s * 0.30), (x - s * 0.10, y + s * 0.12), (x - s * 0.02, y + s * 0.32)],
               C["white"])
        L.poly([(x + s * 0.30, y + s * 0.30), (x + s * 0.12, y + s * 0.12), (x + s * 0.02, y + s * 0.32)],
               C["white"])


def draw_question(cv, x, y, s, t=0.0, alpha=1.0, color=None, rot=0.0):
    color = color or C["sun"]
    if alpha <= 0.01:
        return
    with cv.layer((x - s * 1.4, y - s * 1.4, x + s * 1.4, y + s * 1.4), 3, alpha) as L:
        L.line(ellipse_pts(x, y - s * 0.5, s * 0.42, s * 0.42, rot, 150, 470, 24), s * 0.20, color)
        L.line([(x + s * 0.36, y - s * 0.02), (x + s * 0.05, y + s * 0.30)], s * 0.20, color)
        L.ellipse(x + s * 0.02, y + s * 0.72, s * 0.13, s * 0.13, color)


def draw_counter(cv, value, x, y, size, color, alpha=1.0, suffix="", fmt="{:,.0f}", glow=None):
    txt = fmt.format(value) + suffix
    if glow:
        cv.glow(x, y, cv.text_width(txt, size) * 0.62, glow, 0.30 * alpha, 2.2)
    cv.text(txt, x, y, size, color, "c", alpha)


def draw_person_icon(cv, x, y, s, color, alpha=0.9):
    """Tiny faceless silhouette (scale reference)."""
    with cv.layer((x - s, y - s * 2, x + s, y + s * 2), 3, alpha) as L:
        L.ellipse(x, y - s * 1.25, s * 0.52, s * 0.56, color)
        L.rrect(x, y + 0.4 * s, 1.1 * s, 1.9 * s, s * 0.45, color)


def draw_heartbeat(cv, x, y, w, t, color, alpha=1.0, freq=1.0):
    """ECG-ish line (energy, aliveness)."""
    pts = []
    n = 60
    for i in range(n + 1):
        u = i / n
        px = x - w / 2 + u * w
        ph = (u * 5.0 - t * 1.6 * freq) % 1.0
        py = y
        if 0.40 < ph < 0.58:
            py = y - math.sin((ph - 0.40) / 0.18 * math.pi) * w * 0.12
        pts.append((px, py))
    with cv.layer((x - w, y - w * 0.3, x + w, y + w * 0.3), 3, alpha) as L:
        L.line(pts, max(2.0, w * 0.012), color)


# =============================================================================
#  BACKGROUNDS  (cached, full-canvas RGB; dynamic life drawn per frame)
# =============================================================================
def _bake_stars(img, n, seed, maxy=0.84, dim=0.55):
    """Static micro-star dust baked into the backdrop (cheap texture)."""
    rs = np.random.RandomState(seed)
    w, h = img.size
    arr = np.asarray(img, np.float32)
    for _ in range(n):
        x, y = int(rs.uniform(0, w - 1)), int(rs.uniform(0, h * maxy))
        b = float(rs.uniform(0.25, 1.0)) * dim
        c = np.array(STAR_COLS[int(rs.randint(0, 3))], np.float32) * b
        arr[y, x] = np.clip(arr[y, x] + c, 0, 255)
        if rs.random() < 0.12:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w:
                    arr[yy, xx] = np.clip(arr[yy, xx] + c * 0.45, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def _space_img(stops, blobs, seed, nstars=150, vig=0.42, angle=90.0):
    img = lin_grad(W, H, stops, angle)
    img = add_blobs(img, blobs, res=4)
    img = _bake_stars(img, nstars, seed)
    return vignette(img, vig)


def bg_space_a():
    return _space_img([(0.0, "#04030C"), (0.40, "#0A0620"), (0.76, "#170A31"), (1.0, "#2B0D42")],
                      [(0.18, 0.22, 0.30, "#2A1360", 0.55), (0.78, 0.30, 0.26, "#6A1146", 0.45),
                       (0.55, 0.74, 0.34, "#190A3C", 0.60), (0.92, 0.80, 0.18, "#006C88", 0.20)], 11, vig=0.52)


def bg_space_b():
    return _space_img([(0.0, "#03060F"), (0.40, "#0A1130"), (0.72, "#141C46"), (1.0, "#2A1668")],
                      [(0.25, 0.25, 0.28, "#12308A", 0.45), (0.72, 0.42, 0.30, "#5A1BA0", 0.40),
                       (0.45, 0.82, 0.30, "#080F30", 0.60), (0.88, 0.15, 0.16, "#007A92", 0.22)], 23, vig=0.52)


def bg_space_hot():
    return _space_img([(0.0, "#06030D"), (0.35, "#17051A"), (0.68, "#3E0C25"), (1.0, "#8A2A07")],
                      [(0.50, 0.90, 0.30, "#9E3C00", 0.42), (0.20, 0.30, 0.24, "#440E38", 0.40),
                       (0.85, 0.20, 0.20, "#6A1148", 0.28)], 31, vig=0.58)


def bg_space_deep():
    return _space_img([(0.0, "#05030E"), (0.45, "#0C0722"), (0.80, "#180A32"), (1.0, "#2A0E46")],
                      [(0.50, 0.50, 0.55, "#2A0E46", 0.55), (0.15, 0.80, 0.25, "#3A0F4E", 0.4)], 47,
                      nstars=90, vig=0.55)


def bg_galaxy():
    img = lin_grad(W, H, [(0.0, "#03030C"), (0.5, "#0A0722"), (1.0, "#150A2C")], 62)
    img = add_blobs(img, [(0.30, 0.55, 0.50, "#1C1450", 0.55), (0.72, 0.40, 0.40, "#420F58", 0.40),
                          (0.50, 0.50, 0.62, "#100A2E", 0.50)], res=4)
    img = _bake_stars(img, 420, 5, maxy=1.0, dim=0.8)
    return vignette(img, 0.40)


def bg_orbit():
    img = lin_grad(W, H, [(0.0, "#03030D"), (0.55, "#07071E"), (1.0, "#0C0A2A")], 90)
    img = add_blobs(img, [(0.10, 0.16, 0.20, "#8A4C00", 0.34), (0.8, 0.7, 0.34, "#0E1740", 0.30)], res=4)
    img = _bake_stars(img, 180, 13, maxy=1.0)
    return vignette(img, 0.45)


def bg_void():
    img = lin_grad(W, H, [(0.0, "#030208"), (0.55, "#08061A"), (1.0, "#100A26")], 90)
    img = add_blobs(img, [(0.5, 0.45, 0.55, "#1B0E3C", 0.5)], res=4)
    img = _bake_stars(img, 110, 61, maxy=1.0, dim=0.5)
    return vignette(img, 0.6)


BG_BUILDERS = {
    "space_a": bg_space_a, "space_b": bg_space_b, "space_hot": bg_space_hot,
    "deep": bg_space_deep, "galaxy": bg_galaxy, "orbit": bg_orbit, "void": bg_void,
}
_BG = {}


def get_bg(name):
    if name not in _BG:
        img = BG_BUILDERS[name]()
        lut = [int(round(255.0 * (i / 255.0) ** 1.30)) for i in range(256)]   # deep-space value curve
        _BG[name] = img.point(lut * 3)
    return _BG[name]


def new_canvas(theme):
    return Canvas(get_bg(theme))


# =============================================================================
#  SCENE HELPERS
# =============================================================================
def title(cv, text, x, y, size, t, delay=0.08, color=None, side=None, depth=None,
          focal=(0, 0), glow=0.0, alpha=1.0, max_w=1080):
    """Extruded 3-D headline: pops in, floats, optional glow behind."""
    color = color or C["white"]
    side = side or mix(color, (0, 0, 0), 0.55)
    p = pop(t, delay, 0.55)
    if p <= 0.03 or alpha <= 0.02:
        return
    sz = size * clamp(p, 0.02, 1.10)
    yy = y + math.sin(t * 1.5 + x * 0.011) * 3.0
    if glow:
        cv.glow(x, yy, cv.text_width(text, sz) * 0.60, glow, 0.30 * alpha, 2.1)
    cv.text3d(text, x, yy, sz, color, side, depth if depth else size * 0.14,
              focal=focal, alpha=alpha, max_w=max_w)


def twinkle(cv, theme, t, drift=0.0):
    seed = {"space_a": 3, "space_b": 9, "space_hot": 15, "deep": 21, "galaxy": 27,
            "orbit": 33, "void": 39}.get(theme, 3)
    stars(seed, 30).draw(cv, t, drift)


def particles(cv, cx, cy, rad, t, n, seed=1, color=None, alpha=1.0, speed=1.0, rise=0.0):
    """Drifting dust motes (always-something-moves)."""
    color = color or C["cyan"]
    rs = np.random.RandomState(seed)
    for i in range(n):
        a0 = rs.uniform(0, 6.283)
        f = (t * 0.16 * speed + rs.uniform(0, 1)) % 1.0
        rr = rad * (0.25 + 0.9 * f)
        px = cx + rr * math.cos(a0 + f * 1.6)
        py = cy + rr * math.sin(a0 + f * 1.6) * 0.7 + rise * f
        al = (1 - f) * 0.7 * alpha
        cv.disc(px, py, 1.8 + 2.4 * (1 - f), color, al)


# =============================================================================
#  SCENES   fn(cv, t, dur, var)
# =============================================================================
def scene_intro(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=2.0)
    particles(cv, 0, 40, 320, t, 26, seed=4, color=C["pink"], alpha=0.5, rise=-26)
    bx, by, br = 330, -60, 34 + 3 * math.sin(t * 1.7)
    draw_bh(cv, bx, by, br, t, disk=0.55, glow=0.8, spin=0.6, ring=0.9)
    title(cv, "IMAGINE", 0, -168, 88, t, 0.10, glow=C["violet"], depth=16)
    draw_human(cv, -180, 132, 196, t, "look", skin=C["skin3"], shirt=C["hoodie"], mouth="smile")
    draw_human(cv, 150, 150, 168, t + 1.3, "up", skin=C["skin1"], shirt=C["teal"],
               hair=(59, 35, 20), mouth="open")
    p = pop(t, 0.85, 0.5)
    if p > 0.05:
        draw_badge(cv, -320, 196, "A PLACE IN SPACE...", 22, C["cyan"], (8, 10, 26), p, glow=C["cyan"])
    sparkle(cv, 210, -170, 26 * math.sin(t * 2.4) ** 2 + 12, C["white"], 0.9)
    cc = clamp(remap(t, 0.9, 1.6))                      # shooting star
    if 0 < cc < 1:
        sx, sy = lerp(-560, -330, cc), lerp(-190, -140, cc)
        with cv.layer((sx - 60, sy - 60, sx + 60, sy + 60), 3, cc) as L:
            L.line([(sx, sy), (sx - 46, sy - 16)], 2.2, C["white"])


def scene_gravity(cv, t, dur, var):
    twinkle(cv, "space_b", t, drift=3.0)
    gx, gy = 0, 58
    R = 210.0
    strength = 0.92

    def warp(px, py):
        d = math.hypot(px - gx, (py - gy) * 1.25) + 1e-3
        k = strength * math.exp(-(d / (R * 1.15)) ** 2)
        return (gx - px) * k, (gy - py) * k * 0.95 + k * 26.0

    draw_grid(cv, gx, gy, 560, 200, warp, color=(120, 160, 255), alpha=0.42, nx=15, ny=8, w=1.5)
    draw_bh(cv, gx, gy + 26, 34, t, disk=0.5, glow=1.0, spin=0.8, disk_scale=1.7)
    # photons launched upward, slowing, falling back
    for i in range(5):
        ph = ((t * 0.42 + i * 0.2) % 1.0)
        x0 = -230 + i * 115
        h = 150.0
        y0 = gy + 10
        yy = y0 - h * math.sin(math.pi * min(1.0, ph)) * (1.15 - 0.15 * ph)
        cv.glow(x0, yy, 26, C["sun"], 0.55, 2.0)
        cv.disc(x0, yy, 5.2, C["white"])
        with cv.layer((x0 - 8, yy - 46, x0 + 8, yy + 52), 3, 0.45) as L:
            L.line([(x0, yy - 4), (x0, yy + 40)], 3.0, C["sun"])
    title(cv, "GRAVITY", 0, -168, 80, t, 0.10, glow=C["blue"], depth=15)
    draw_badge(cv, -300, 196, "LIGHT CAN'T ESCAPE", 22, C["red"], (12, 0, 8), pop(t, 0.7, 0.5))
    c = 1 - ease_out_cubic(remap(t, 1.2, 2.6))
    draw_counter(cv, 299792 * (0.35 + 0.65 * c), 300, 196, 26, C["cyan"], 0.9, suffix=" km/s")


def scene_noexit(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=1.5)
    bx, by, br = -110, 10, 120
    draw_bh(cv, bx, by, br, t, disk=0.9, glow=1.0)
    # animated horizon ring + dashed boundary
    with cv.layer((bx - br * 1.6, by - br * 1.6, bx + br * 1.6, by + br * 1.6), 3, 0.85) as L:
        L.dashed((bx + br * 1.12, by - br * 0.9), (bx + br * 1.12, by + br * 0.9),
                 2.4, 11, 8, C["cyan"], offset=-t * 40)
    # astronaut slides in, crosses, then is gone
    aa = clamp(remap(t, 0.15, 2.4))
    ax = lerp(430, bx + br * 0.62, ease_in_cubic(aa))
    ay = by + 44 + math.sin(t * 3) * 5
    al = 1.0 - clamp(remap(t, 1.8, 2.35))
    if al > 0.02:
        draw_human(cv, ax, ay, 132, t, "fall", skin=C["skin1"], shirt=C["white"], pants=(232, 237, 248),
                   hair=(40, 30, 60), alpha=al, rot=lerp(6, 78, aa), mouth="scream",
                   helmet=C["cyan"])
    # an escaping arrow that bounces back
    ap = clamp(remap(t, 0.4, 2.5))
    if ap > 0.05:
        ex = lerp(bx + br * 1.05, 300, ease_out_cubic(clamp(ap * 1.5)))
        if ap > 0.55:
            ex = lerp(300, bx + br * 0.9, ease_in_cubic(clamp((ap - 0.55) / 0.45)))
        draw_arrow(cv, (bx + br * 1.05, by - 62), (ex, by - 62), 7.0,
                   C["red"] if ap > 0.55 else C["sun"], prog=clamp(ap * 1.4))
    draw_prohibit(cv, 330, by - 62, 40, pop(t, 0.9, 0.45), C["red"], 0.95, pulse=t)
    draw_badge(cv, -300, 196, "POINT OF NO RETURN", 23, C["red"], (14, 2, 10), pop(t, 0.4, 0.5))
    title(cv, "NO WAY OUT", 300, -168, 62, t, 0.12, glow=C["red"], depth=12)


def scene_mystery(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=1.0)
    bx, by, br = 0, 20, 128
    draw_bh(cv, bx, by, br, t, disk=0.8, glow=0.95)
    for i in range(3):
        ph = (t * 0.5 + i * 0.33) % 1.0
        qx = bx + (i - 1) * 150 + math.sin(t * 0.9 + i) * 12
        qy = by - 150 - math.sin(ph * 3.14) * 34 + i * 6
        draw_question(cv, qx, qy, 30 + 4 * math.sin(t * 2 + i), t, clamp(remap(t, 0.35 + i * 0.16, 0.8 + i * 0.16)),
                      C["sun"], rot=math.sin(t + i) * 4)
    # magnifier over the shadow
    mp = pop(t, 0.5, 0.55)
    if mp > 0.03:
        mx, my, mr = bx + 46 * math.sin(t * 0.6) + 40, by + 10, 46 * mp
        cv.ring(mx, my, mr, 6, C["white"], 0.9)
        cv.disc(mx, my, mr - 4, (255, 255, 255), 0.06)
        with cv.layer((mx - mr, my - mr, mx + mr + 60, my + mr + 60), 3, 0.9) as L:
            L.line([(mx + mr * 0.7, my + mr * 0.7), (mx + mr * 1.4, my + mr * 1.5)], 8.0, C["cyan"])
    draw_badge(cv, -300, 196, "INSIDE = ???", 23, C["sun"], (10, 8, 24), pop(t, 0.6, 0.5))
    title(cv, "WE DON'T KNOW", 0, -168, 64, t, 0.1, glow=C["amber"], depth=13)


def scene_reveal(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=0.8)
    p = ease_out_back(clamp(remap(t, 0.0, 0.75)))
    br = 118 * clamp(p, 0.05, 1.0)
    draw_bh(cv, 0, 30, br, t, disk=clamp(p * 1.4), glow=clamp(p * 1.3), spin=1.0, jet=0.0)
    draw_shockwave(cv, 0, 30, remap(t, 0.15, 1.9), 520, C["cyan"], 16, 0.7)
    draw_shockwave(cv, 0, 30, remap(t, 0.45, 2.4), 460, C["pink"], 10, 0.5)
    photons_in(cv, 0, 30, br, t, 5, rmax=br * 3.0)
    title(cv, "THE BLACK HOLE", 0, -168, 74, t, 0.35, glow=C["orange"], depth=15)
    draw_badge(cv, -300, 196, "EVENT HORIZON", 23, C["orange"], (12, 4, 0), pop(t, 0.9, 0.5), glow=C["orange"])
    for i in range(7):
        a = t * 0.7 + i * 0.9
        sparkle(cv, math.cos(a) * 380, 30 + math.sin(a) * 150, 10 + 8 * math.sin(t * 3 + i) ** 2,
                C["white"], 0.75 * clamp(remap(t, 0.4, 1.2)))


def scene_nothole(cv, t, dur, var):
    twinkle(cv, "space_b", t, drift=2.0)
    # the naive "hole in the ground"
    gx, gy = -190, 120
    with cv.layer((gx - 240, gy - 90, gx + 240, gy + 120), 3) as L:
        L.ellipse(gx, gy, 92, 26, (16, 12, 34))
        L.ellipse(gx, gy - 3, 100, 30, (46, 40, 86))
        L.ellipse(gx, gy - 4, 88, 24, (10, 8, 22))
    draw_human(cv, gx + 150, gy - 76, 132, t, "look", skin=C["skin2"], shirt=C["mint"], mouth="open",
               look=0.6)
    draw_prohibit(cv, gx, gy - 44, 52, pop(t, 0.55, 0.5), C["red"], 0.95, pulse=t)
    # the donut gag
    if var > 0:
        dp = pop(t, 0.75, 0.5)
        cv.disc(300, -70, 58 * dp, C["amber"])
        cv.disc(300, -70, 20 * dp, C["midnight"])
        draw_prohibit(cv, 300, -70, 44 * dp, pop(t, 1.0, 0.4), C["red"], 0.9, pulse=t + 1)
    title(cv, "NOT JUST A HOLE", 60, -168, 62, t, 0.1, glow=C["red"], depth=22)
    draw_badge(cv, -300, 196, "SPACETIME, NOT DRYWALL", 21, C["cyan"], (8, 10, 26), pop(t, 0.5, 0.5))
    arrows = clamp(remap(t, 0.9, 1.8))
    if arrows > 0.05:
        draw_chevrons(cv, (-40, 120), (gx + 96, gy - 4), t, 4, C["red"], 12, 0.8 * arrows)


def scene_compress(cv, t, dur, var):
    twinkle(cv, "space_b", t, drift=2.5)
    k = ease_in_cubic(clamp(remap(t, 0.25, 1.9)))
    cx, cy = 120, 20
    # matter pile -> pinpoint, particle assembly in reverse
    for i in range(16):
        rs = np.random.RandomState(100 + i)
        a = i * 0.7 + rs.uniform(0, 1)
        r0 = 150 + rs.uniform(0, 90)
        px = cx + math.cos(a) * r0 * (1 - k) + math.cos(a) * 8
        py = cy + math.sin(a) * r0 * 0.6 * (1 - k) + math.sin(a) * 8
        rr = lerp(rs.uniform(9, 24), 3.2, k)
        cv.disc(px, py, rr, [C["amber"], C["cyan"], C["pink"], C["white"], C["mint"]][i % 5],
                lerp(0.95, 0.6, k))
    cv.glow(cx, cy, lerp(30, 90, k), C["white"], 0.5 + 0.4 * k, 2.0)
    cv.disc(cx, cy, 4.0 + 3 * math.sin(t * 6), C["white"])
    draw_shockwave(cv, cx, cy, remap(t, 1.8, 2.8), 260, C["cyan"], 10, 0.6)
    draw_caliper(cv, (cx - 4, cy + 52), (cx + 4, cy + 52), "PINPOINT", C["cyan"], remap(t, 1.9, 2.5), 8, 3, 20)
    # left: a whole planet for scale
    draw_planet(cv, -420, 10, 62, t, kind="earth", rot=t * 0.4)
    draw_caliper(cv, (-420, 92), (-420, 10), "EARTH", C["cyan"], remap(t, 0.5, 1.3), 10, 3, 20)
    title(cv, "ALL THAT MASS", 0, -168, 64, t, 0.1, glow=C["orange"], depth=25)
    draw_badge(cv, -300, 196, "DENSITY: EXTREME", 22, C["orange"], (12, 5, 0), pop(t, 0.8, 0.5))


def scene_horizon(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=1.2)
    bx, by, br = 0, 30, 120
    draw_bh(cv, bx, by, br, t, disk=0.75, glow=0.95)
    pulse = 0.5 + 0.5 * math.sin(t * 2.6)
    cv.ring(bx, by, br * 1.02, 3.0 + 2.0 * pulse, C["cyan"], 0.85)
    draw_caliper(cv, (bx, by + br * 1.02), (bx - 210, by + br * 1.02 + 46),
                 "", C["cyan"], remap(t, 0.3, 1.3), 16, 3.2, 22)
    draw_badge(cv, bx - 210, by + br * 1.02 + 84, "EVENT HORIZON", 22, C["cyan"], (8, 10, 26),
               pop(t, 1.0, 0.45))
    # measurement ticks marching around the horizon
    with cv.layer((bx - br * 1.3, by - br * 1.3, bx + br * 1.3, by + br * 1.3), 3, 0.7) as L:
        for i in range(24):
            a = i * math.pi / 12 + t * 0.35
            L.line([(bx + math.cos(a) * br * 1.16, by + math.sin(a) * br * 1.16),
                    (bx + math.cos(a) * br * (1.22 + 0.05 * (i % 3 == 0)), by + math.sin(a) * br * (1.22 + 0.05 * (i % 3 == 0)))],
                   2.0, C["cyan"])
    title(cv, "EVENT HORIZON", 0, -168, 68, t, 0.12, glow=C["cyan"], depth=13)
    draw_badge(cv, 340, 196, "THE BOUNDARY", 22, C["cyan"], (8, 10, 26), pop(t, 0.55, 0.5))


def scene_crossing(cv, t, dur, var):
    twinkle(cv, "deep", t, drift=1.0)
    bx, by, br = -70, 24, 124
    draw_bh(cv, bx, by, br, t, disk=0.85, glow=1.0)
    # astronaut walks the line and tips in
    aa = clamp(remap(t, 0.15, 2.5))
    ax = lerp(390, bx + br * 0.5, ease_in_cubic(aa))
    ay = by + math.sin(t * 2.6) * 4
    al = 1.0 - clamp(remap(t, 1.9, 2.5))
    draw_human(cv, ax, ay, 92, t, "reach", skin=C["skin1"], shirt=C["white"], pants=(226, 232, 244),
               hair=(30, 26, 48), alpha=al, rot=lerp(-8, 46, aa), mouth="scream")
    # light rays trying to climb out and bending back
    for i in range(4):
        f = clamp(remap(t, 0.3 + i * 0.22, 2.0 + i * 0.22))
        if f <= 0.02 or f >= 0.99:
            continue
        a = -0.5 + i * 0.34
        rr = br * (1.05 + 1.5 * ease_out_cubic(min(1, f * 1.5)))
        px = bx + rr * math.cos(a) * 1.2
        py = by + rr * math.sin(a) * 0.8 - 40 * f * (1 - f)
        cv.glow(px, py, 22, C["sun"], 0.5 * (1 - f), 2.0)
        cv.disc(px, py, 4.5, C["white"], 1 - f)
    title(cv, "NOT EVEN LIGHT", 250, -150, 54, t, 0.55, glow=C["amber"], depth=12)
    draw_badge(cv, -300, 196, "NO ESCAPE", 22, C["red"], (14, 2, 10), pop(t, 0.35, 0.5))


def scene_timedilation(cv, t, dur, var):
    twinkle(cv, "space_b", t, drift=2.0)
    # split-screen divider draws on
    sp = ease_in_out_cubic(clamp(remap(t, 0.1, 0.8)))
    with cv.layer((-4, -246, 4, 246), 2, 0.9) as L:
        L.rrect(0, lerp(-246, 0, sp), 3.0, lerp(0, 492, sp), 2, C["cyan"])
    draw_bh(cv, 340, 150, 56, t, disk=0.8, glow=0.9)
    # left: you, falling, your clock normal
    draw_human(cv, -330, 40 + math.sin(t * 2) * 6, 132, t, "fall", skin=C["skin2"],
               shirt=C["hoodie"], mouth="open", rot=-24)
    draw_clock(cv, -330, -96, 52, t, hands=(3.0, 1.0), glow=C["mint"], colors=(C["ink"], C["mint"]))
    # right: the distant observer's view of your clock, slowing to a stop
    slow = t * (1.0 - 0.85 * clamp(remap(t, 0.6, 2.6)))
    draw_clock(cv, 300, -78, 50, slow * 0.35, hands=(3.0, 1.0), glow=C["red"],
               colors=(C["ink"], C["red"]), face=(255, 246, 246))
    draw_human(cv, 60, 74, 134, t, "stand", skin=C["skin1"], shirt=C["teal"], mouth="flat")
    title(cv, "TIME DILATION", 0, -168, 58, t, 0.12, glow=C["cyan"], depth=12)
    draw_badge(cv, -300, 196, "TWO CLOCKS, TWO RATES", 21, C["cyan"], (8, 10, 26), pop(t, 0.5, 0.5))
    for i in range(4):                                  # ticks marching: time passing
        ph = (t * 0.6 + i * 0.25) % 1.0
        cv.disc(lerp(-560, -60, ph), -196, 3.0, C["mint"], (1 - ph) * 0.8)


def scene_observer(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=1.5)
    bx, by, br = 250, 20, 92
    draw_bh(cv, bx, by, br, t, disk=0.85, glow=0.95)
    # observer on a little asteroid, with a telescope
    ax, ay = -300, 120
    with cv.layer((ax - 120, ay - 40, ax + 150, ay + 90), 3) as L:
        L.ellipse(ax, ay + 52, 108, 30, C["smoke"])
        L.ellipse(ax, ay + 46, 100, 24, C["smoke2"])
    draw_human(cv, ax, ay, 120, t, "look", skin=C["skin4"], shirt=C["amber"], mouth="smile", look=-0.4)
    tp = pop(t, 0.35, 0.5)
    if tp > 0.05:
        with cv.layer((ax + 30, ay - 90, ax + 170, ay + 10), 3, tp) as L:
            L.line([(ax + 52, ay - 12), (ax + 128, ay - 60)], 9.0, C["cyan"])
            L.ellipse(ax + 130, ay - 62, 15, 15, C["white"])
            L.ellipse(ax + 52, ay - 10, 8, 8, C["smoke2"])
    # falling faller near the horizon, motion slowing visibly
    fall_t = 2.6 * (1 - math.exp(-t * 0.5))
    fy = by - 150 + fall_t * 86
    draw_human(cv, bx - 40, fy, 56, t, "fall", skin=C["skin1"], shirt=C["pink"], alpha=0.95,
               rot=lerp(-30, 0, fall_t / 2.6), mouth="scream")
    draw_caliper(cv, (bx + br * 1.05, by - 150), (bx + br * 1.05, fy), "", C["cyan"], remap(t, 0.5, 1.6), 10, 2.6, 18)
    title(cv, "SEEN FROM AFAR", 0, -168, 58, t, 0.12, glow=C["violet"], depth=12)
    draw_badge(cv, -300, 196, "YOU NEVER QUITE ARRIVE", 21, C["violet"], (10, 8, 30), pop(t, 0.6, 0.5))


def scene_spacetime(cv, t, dur, var):
    twinkle(cv, "space_b", t, drift=2.4)
    gx, gy = 60, 66

    def warp(px, py):
        d = math.hypot(px - gx, (py - gy) * 1.3) + 1e-3
        k = 0.95 * math.exp(-(d / 190.0) ** 2)
        wob = 12 * math.sin(px * 0.013 + t * 1.4) * math.sin(py * 0.02 - t)
        return (gx - px) * k, (gy - py) * k + k * 20 + wob * 0.4

    draw_grid(cv, gx, gy, 540, 190, warp, (120, 170, 255), 0.40, 15, 8, 1.5)
    draw_bh(cv, gx, gy + 14, 26, t, disk=0.6, glow=0.9, spin=0.7)
    draw_clock(cv, -330, -70, 46, t, hands=(4.0, 1.0), glow=C["mint"], colors=(C["ink"], C["mint"]))
    draw_clock(cv, 350, -70, 46, t, hands=(1.2, 0.3), glow=C["red"], colors=(C["ink"], C["red"]))
    draw_chevrons(cv, (-270, -70), (gx - 40, -30), t, 3, C["cyan"], 10, 0.7)
    title(cv, "SPACETIME", 0, -168, 72, t, 0.1, glow=C["blue"], depth=14)
    draw_badge(cv, -300, 196, "SPACE + TIME = ONE FABRIC", 21, C["blue"], (8, 10, 34), pop(t, 0.6, 0.5))


def scene_monsters(cv, t, dur, var):
    twinkle(cv, "space_hot", t, drift=2.0)
    draw_bh(cv, 0, 30, 74, t, disk=0.85, glow=1.0)
    for i, (mx, my) in enumerate(((-390, -40), (-250, 130), (390, 120), (300, -90))):
        pp = pop(t, 0.3 + i * 0.13, 0.5)
        if pp <= 0.05:
            continue
        draw_monster(cv, mx, my, 66 * pp, t + i, 0.95, [C["violet"], C["pink"], C["teal"], C["red"]][i])
        draw_prohibit(cv, mx, my, 62 * pp, pop(t, 0.75 + i * 0.13, 0.4), C["red"], 0.95, pulse=t + i)
    title(cv, "NOT MONSTERS", 0, -168, 70, t, 0.1, glow=C["red"], depth=14)
    draw_badge(cv, -300, 196, "REAL OBJECT. REAL PHYSICS.", 21, C["cyan"], (8, 10, 26), pop(t, 0.5, 0.5))


def scene_milkyway(cv, t, dur, var):
    twinkle(cv, "galaxy", t, drift=4.0)
    draw_galaxy(cv, 0, 24, 560, t, 0.95, rot=t * 0.10, tilt=0.52)
    # zoom rings converging on the core
    for i in range(3):
        p = remap(t, 0.2 + i * 0.3, 1.6 + i * 0.3)
        if 0 < p < 1:
            draw_shockwave(cv, 0, 30, p, 300, C["cyan"], 6, 0.35)
    cp = pop(t, 0.5, 0.5)
    if cp > 0.05:
        cv.glow(0, 30, 60, C["orange"], 0.6 * cp, 2.0)
        draw_badge(cv, 0, 150, "CORE", 18, C["orange"], (10, 4, 0), cp, glow=C["orange"])
    title(cv, "MILKY WAY", 0, -168, 76, t, 0.1, glow=C["violet"], depth=15)
    draw_badge(cv, -300, 196, "OUR GALAXY - 100,000 LY", 21, C["cyan"], (8, 10, 26), pop(t, 0.6, 0.5))
    # tiny "you are here" marker on an arm
    ya = t * 0.10 + 2.4
    yx, yy = math.cos(ya) * 330, 24 + math.sin(ya) * 330 * 0.52
    cv.disc(yx, yy, 7, C["white"], 0.95)
    cv.ring(yx, yy, 16, 2.0, C["cyan"], 0.8)
    draw_badge(cv, yx * 0.55, yy - 62, "YOU ARE HERE", 16, C["white"], (10, 12, 30), pop(t, 1.0, 0.4))


def scene_sgra(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=1.0)
    draw_bh(cv, -260, 20, 104, t, disk=1.0, glow=1.0, spin=1.1)
    title(cv, "SAGITTARIUS A*", 210, -168, 60, t, 0.1, glow=C["amber"], depth=12)
    # mass comparison: Sun = 1  ->  Sgr A* = 4,000,000
    v = 4_000_000 * ease_out_cubic(clamp(remap(t, 0.5, 2.4)))
    bar_h = 134 * ease_out_cubic(clamp(remap(t, 0.5, 2.4)))
    with cv.layer((150, -60, 520, 140), 3, 0.95) as L:
        L.rrect(210, 132 - 11, 132, 22, 9, C["sun"])
        L.rrect(420, 132 - bar_h / 2.0, 54, max(6, bar_h), 10, C["orange"])
        L.rrect(420, 132 - bar_h + 8, 54, 16, 6, C["sun"], None, 0)
        L.line([(160, 132), (500, 132)], 2.0, C["white"])
    draw_counter(cv, v, 366, -92, 34, C["white"], 0.95, suffix="x", fmt="{:,.0f}", glow=C["amber"])
    draw_badge(cv, 210, 172, "SUN = 1", 17, C["amber"], (12, 6, 0), pop(t, 0.3, 0.4))
    draw_badge(cv, 420, 172, "SGR A*", 17, C["orange"], (14, 4, 0), pop(t, 1.4, 0.4))
    draw_badge(cv, -300, 196, "MASS OF 4,000,000 SUNS", 21, C["amber"], (12, 6, 0), pop(t, 1.6, 0.5))
    particles(cv, -260, 20, 170, t, 16, seed=8, color=C["sun"], alpha=0.4)


def scene_vacuum(cv, t, dur, var):
    twinkle(cv, "space_b", t, drift=2.0)
    draw_bh(cv, 250, 20, 92, t, disk=0.9, glow=0.95)
    # Earth calmly orbiting
    a = t * 0.55
    ex, ey = 250 + math.cos(a) * 230, 20 + math.sin(a) * 92
    with cv.layer((250 - 240, 20 - 100, 250 + 240, 20 + 100), 2, 0.30) as L:
        L.line(ellipse_pts(250, 20, 230, 92, 0, 0, 360, 90), 2.2, C["cyan"])
    draw_planet(cv, ex, ey, 17, t, kind="earth", rot=t)
    draw_human(cv, -330, 108, 138, t, "point", skin=C["skin2"], shirt=C["mint"], mouth="flat", flip=True)
    vp = pop(t, 0.3, 0.5)
    if vp > 0.05:
        draw_vacuum(cv, -140, 128, 84 * vp, t, 0.95, flip=True)
        draw_prohibit(cv, -76, 74, 44 * vp, pop(t, 0.9, 0.4), C["red"], 0.95, pulse=t)
    title(cv, "NOT A VACUUM", 60, -168, 64, t, 0.1, glow=C["mint"], depth=13)
    draw_badge(cv, -300, 196, "IT WON'T EAT THE UNIVERSE", 20, C["mint"], (4, 16, 14), pop(t, 0.6, 0.5))


def scene_swap(cv, t, dur, var):
    twinkle(cv, "orbit", t, drift=1.2)
    k = clamp(remap(t, 0.7, 2.0))                        # 0 = sun, 1 = black hole
    sx, sy, sr = -110, 10, 92
    if k < 0.98:
        draw_planet(cv, sx, sy, sr, t, kind="sun")
        draw_rays(cv, sx, sy, t, sr * 3.1, 22, C["amber"], 0.30 * (1 - k), spin=8)
    if k > 0.02:
        draw_bh(cv, sx, sy, sr * 0.98, t, disk=0.9 * k, glow=k, spin=0.8, disk_scale=1.35)
    # orbit stays put
    a = t * 0.7
    ex, ey = sx + math.cos(a) * 330, sy + math.sin(a) * 118
    with cv.layer((sx - 340, sy - 130, sx + 340, sy + 130), 2, 0.55) as L:
        L.dashed((sx - 330, sy), (sx - 330, sy), 2, 10, 8, C["cyan"])
        L.line(ellipse_pts(sx, sy, 330, 118, 0, 0, 360, 96), 2.0, C["cyan"])
    draw_planet(cv, ex, ey, 26, t, kind="earth", rot=t * 1.2)
    for i in range(4):                                    # sunlight rays disappear
        if k < 0.9:
            aa = -0.9 + i * 0.34
            draw_arrow(cv, (sx + math.cos(aa) * sr * 1.1, sy + math.sin(aa) * sr * 1.1),
                       (ex, ey), 3.0, C["sun"], prog=1.0, alpha=(1 - k) * 0.8)
    title(cv, "SUN -> BLACK HOLE", 0, -168, 56, t, 0.1, glow=C["orange"], depth=12)
    draw_badge(cv, -300, 196, "SAME MASS, SAME ORBIT", 21, C["cyan"], (8, 10, 26), pop(t, 0.6, 0.5))
    if k > 0.8:
        draw_badge(cv, 330, 196, "SUNLIGHT: GONE", 19, C["red"], (14, 2, 10), pop(t, 1.9, 0.4))


def scene_close(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=1.0)
    bx, by, br = 300, 20, 104
    draw_bh(cv, bx, by, br, t, disk=1.0, glow=1.05, disk_scale=2.0)
    pull = ease_in_cubic(clamp(remap(t, 0.2, 2.6)))
    hx = lerp(-330, -110, pull)
    stretch = 1.0 + 0.5 * pull
    draw_human(cv, hx, 30, 176, t, "reach", skin=C["skin2"], shirt=C["hoodie"], mouth="scream",
               sy=stretch, sx=1.0 - 0.13 * pull, rot=-8 - 16 * pull, look=0.6)
    ap = clamp(remap(t, 0.45, 1.15))
    for dy in (-1, 1):
        y0 = 30 + dy * 86 * stretch
        y1 = 30 + dy * 150 * stretch
        draw_arrow(cv, (hx, y0), (hx, y1), 7.0, C["red"], prog=ap, alpha=0.95)
        cv.text("STRONGER" if dy < 0 else "WEAKER", hx + 150, y1 + dy * 14, 17, C["red"], "c", 0.85 * ap)
    title(cv, "TIDAL FORCES", 0, -168, 62, t, 0.1, glow=C["red"], depth=13)
    draw_badge(cv, -300, 196, "GRAVITY PULLS UNEVENLY", 21, C["red"], (14, 2, 10), pop(t, 0.6, 0.5))


def scene_spaghetti(cv, t, dur, var):
    twinkle(cv, "space_hot", t, drift=2.0)
    bx, by, br = 340, 0, 92
    draw_bh(cv, bx, by, br, t, disk=1.0, glow=1.05, disk_scale=2.1)
    k = ease_out_cubic(clamp(remap(t, 0.15, 1.5)))
    stretch = lerp(1.15, 2.55, k)
    hx = lerp(-250, -180, k)
    draw_human(cv, hx, 62, 118, t, "fall", skin=C["skin2"], shirt=C["pink"], mouth="scream",
               sy=stretch, sx=lerp(1.0, 0.58, k), rot=lerp(-4, -26, k), look=0.5)
    # the joke: a plate of spaghetti for scale
    pp = pop(t, 1.0, 0.5)
    if pp > 0.05:
        px, py = -455, 190
        cv.disc(px, py, 74 * pp, C["white"], 0.96)
        cv.disc(px, py - 5 * pp, 67 * pp, (238, 240, 252), 0.96)
        for i in range(11):
            a = i * 0.62 + t * 0.5
            sx2 = px + math.cos(a) * 46 * pp
            sy2 = py - 8 * pp + math.sin(a * 1.7) * 9 * pp
            cv.disc(sx2, sy2, 7.5 * pp, C["sun"], 0.95)
            cv.disc(sx2 + 3, sy2 + 2, 4.0 * pp, C["red"], 0.85)
        draw_badge(cv, px + 8, py - 100, "FOR SCALE", 17, C["white"], (18, 16, 30), pop(t, 1.5, 0.4))
    title(cv, "SPAGHETTIFICATION", 0, -168, 58, t, 0.1, glow=C["pink"], depth=12)
    draw_badge(cv, -300, 196, "FUNNY NAME. NOT FUN.", 21, C["pink"], (16, 4, 16), pop(t, 0.7, 0.5))
    cv.text("x" + "%.1f" % (1 + 2.4 * k), 130, 150, 30, C["white"], "c", 0.9)


def scene_inside(cv, t, dur, var):
    # push into the shadow: iris closes to black, then the unknown
    iris = ease_in_out_cubic(clamp(remap(t, 0.05, 1.5)))
    depth = clamp(remap(t, 0.3, dur))
    for i in range(6):
        rr = 90 + i * 54 + 26 * math.sin(t * 0.7 + i)
        cv.ring(0, 10, rr, 2.0, mix(C["violet"], C["deep"], i / 6.0), 0.55 * (1 - iris * 0.5))
    if iris < 0.99:
        draw_bh(cv, 0, 10, 150 * (1 - iris * 0.6), t, disk=0.9 * (1 - iris), glow=1 - iris,
                alpha=clamp(1 - iris * 0.5))
    q = pop(t, 1.1, 0.6)
    if q > 0.03:
        draw_question(cv, 0, 6, 54 * q, t, 0.95, C["sun"], rot=math.sin(t * 1.4) * 6)
        cv.glow(0, 6, 150, C["amber"], 0.20 * q, 2.4)
    title(cv, "INSIDE = ?", 0, -168, 74, t, 0.9, glow=C["amber"], depth=14)
    draw_badge(cv, -300, 196, "PAST THE HORIZON", 21, C["amber"], (10, 8, 24), pop(t, 0.3, 0.5))
    particles(cv, 0, 10, 300, t, 18, seed=12, color=C["violet"], alpha=0.5, speed=0.6)


def scene_singularity(cv, t, dur, var):
    twinkle(cv, "deep", t, drift=0.8)
    k = ease_in_cubic(clamp(remap(t, 0.15, 2.2)))
    gx, gy = 0, 30

    def warp(px, py):
        d = math.hypot(px - gx, (py - gy) * 1.25) + 1e-3
        pull = (0.86 + 0.13 * k) * math.exp(-(d / (210 * (1 - 0.4 * k))) ** 2)
        spike = 44 * k * math.exp(-(d / 60.0) ** 2)
        return (gx - px) * pull, (gy - py) * pull - spike

    draw_grid(cv, gx, gy, 560, 210, warp, (140, 150, 255), 0.45, 15, 8, 1.6)
    cv.glow(gx, gy - 22 * k, 120, C["white"], 0.35 + 0.5 * k, 2.0)
    cv.disc(gx, gy - 22 * k, 6 + 5 * math.sin(t * 7), C["white"], 1.0)
    draw_shockwave(cv, gx, gy, remap(t, 1.6, 2.7), 420, C["cyan"], 9, 0.5)
    title(cv, "SINGULARITY", 0, -168, 66, t, 0.1, glow=C["white"], depth=14)
    draw_counter(cv, 1.0 + 9.0 * k, 350, 60, 44, C["cyan"], 0.95, suffix="")
    cv.text("CURVATURE", 350, 96, 20, C["cyan"], "c", 0.85)
    if k > 0.85:
        cv.text("INFINITE", 350, 30, 26, C["red"], "c", clamp((k - 0.85) * 6))
    draw_badge(cv, -300, 196, "GENERAL RELATIVITY SAYS: HERE", 19, C["cyan"], (8, 10, 26), pop(t, 0.6, 0.5))


def scene_physics(cv, t, dur, var):
    twinkle(cv, "space_b", t, drift=2.0)
    k = clamp(remap(t, 0.2, 1.8))
    ax = lerp(-330, -60, ease_out_cubic(k))
    bx2 = lerp(330, 60, ease_out_cubic(k))
    cv.sphere(ax, -20, 74, ((0.0, "#DFFFFF"), (0.4, "#3AD8FF"), (1.0, "#0B3A9E")))
    cv.sphere(bx2, -20, 74, ((0.0, "#FFE7FF"), (0.4, "#FF4FD8"), (1.0, "#7A0F72")))
    cv.glow(ax, -20, 130, C["cyan"], 0.35, 2.2)
    cv.glow(bx2, -20, 130, C["pink"], 0.35, 2.2)
    draw_badge(cv, ax, 74, "GENERAL RELATIVITY", 19, C["cyan"], (6, 12, 30), pop(t, 0.2, 0.4))
    draw_badge(cv, bx2, 74, "QUANTUM MECHANICS", 19, C["pink"], (22, 6, 20), pop(t, 0.35, 0.4))
    if k > 0.92:
        f = clamp((k - 0.92) / 0.08)
        for i in range(7):
            a = i * 0.9 + t * 5
            x1 = lerp(ax, bx2, 0.25 + 0.5 * abs(math.sin(i * 2.3)))
            with cv.layer((x1 - 40, -70, x1 + 40, 30), 3, f) as L:
                L.line([(x1 - 22, -66 + i * 4), (x1 + 16, -30 + i * 6), (x1 - 12, -4 + i * 3)], 2.4, C["white"])
        draw_shockwave(cv, 0, -20, remap(t, 1.7, 2.6), 340, C["white"], 8, 0.55)
    title(cv, "TWO LAWS, ONE PLACE", 0, -168, 54, t, 0.1, glow=C["violet"], depth=12)
    draw_badge(cv, -300, 196, "PHYSICS BREAKS HERE", 21, C["red"], (14, 2, 10), pop(t, 0.5, 0.5))


def scene_paradox(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=1.5)
    bx, by, br = 210, 30, 96
    draw_bh(cv, bx, by, br, t, disk=0.95, glow=1.0)
    # human winds up and throws the book
    th = clamp(remap(t, 0.1, 0.7))
    draw_human(cv, -300, 96, 142, t, "throw" if th > 0.5 else "hold", skin=C["skin2"],
               shirt=C["teal"], mouth="open" if th > 0.5 else "smile", look=0.6)
    fly = clamp(remap(t, 0.65, 2.1))
    if fly < 1.0:
        bx0, by0 = -250, 40

        def bez(a):
            p0, p1, p2 = (bx0, by0), (-60, -110), (bx + br * 0.6, by - br * 0.35)
            return ((1 - a) ** 2 * p0[0] + 2 * (1 - a) * a * p1[0] + a * a * p2[0],
                    (1 - a) ** 2 * p0[1] + 2 * (1 - a) * a * p1[1] + a * a * p2[1])
        px, py = bez(fly)
        draw_book(cv, px, py, 42, rot=fly * 540, t=t, alpha=1.0)
    else:
        draw_shockwave(cv, bx, by, remap(t, 2.1, 2.6), 180, C["cyan"], 8, 0.6)
    title(cv, "INFORMATION PARADOX", -20, -168, 56, t, 0.1, glow=C["cyan"], depth=12)
    draw_badge(cv, -300, 196, "ONE BOOK. ZERO EXITS.", 21, C["cyan"], (8, 10, 26), pop(t, 0.5, 0.5))


def scene_book(cv, t, dur, var):
    twinkle(cv, "deep", t, drift=1.0)
    bx, by, br = 0, 16, 128
    draw_bh(cv, bx, by, br, t, disk=0.9, glow=0.95)
    # book tumbling just inside, information motes leaking toward the centre
    draw_book(cv, 0, 12, 58, rot=t * 46, t=t, alpha=0.95)
    for i in range(10):
        ph = (t * 0.4 + i * 0.1) % 1.0
        a = i * 2.4
        rr = lerp(150, bx + 20, ph)
        cv.disc(math.cos(a) * rr, 16 + math.sin(a) * 40, 3.0, C["cyan"], (1 - ph) * 0.8)
    q = pop(t, 1.2, 0.5)
    if q > 0.03:
        draw_question(cv, 210, -60, 42 * q, t, 0.9, C["sun"], rot=math.sin(t * 1.6) * 5)
    title(cv, "WHERE DID IT GO?", 0, -168, 62, t, 0.1, glow=C["cyan"], depth=13)
    draw_badge(cv, -300, 196, "INFORMATION NEEDS A WAY OUT", 20, C["cyan"], (8, 10, 26), pop(t, 0.6, 0.5))


def scene_destroy(cv, t, dur, var):
    twinkle(cv, "space_b", t, drift=2.0)
    sp = ease_in_out_cubic(clamp(remap(t, 0.1, 0.7)))
    with cv.layer((-3, -246, 3, 246), 2, 0.8) as L:
        L.rrect(0, lerp(-246, 0, sp), 3.0, lerp(0, 492, sp), 2, C["white"])
    for side, (cx, col, lab) in enumerate(((-290, C["red"], "DESTROYED?"), (290, C["mint"], "CONSERVED?"))):
        for i in range(7):
            rs = np.random.RandomState(40 + i + side * 10)
            px = cx + (i - 3) * 40
            py = -40 + rs.uniform(-30, 30) + math.sin(t * 1.6 + i) * 8
            if side == 0:
                al = 1.0 - clamp(remap(t, 0.7 + i * 0.12, 1.5 + i * 0.12))
                cv.rrect(px, py, 26 * al + 2, 26 * al + 2, 6, col, al)
            else:
                al = clamp(remap(t, 0.7 + i * 0.12, 1.2 + i * 0.12))
                cv.rrect(px, py, 28, 28, 6, col, al)
                if al > 0.5:
                    cv.text("i", px, py, 20, C["ink"], "c", al)
        draw_badge(cv, cx, 92, lab, 22, col, (8, 10, 26), pop(t, 0.4 + side * 0.15, 0.45))
    draw_badge(cv, 290, 196, "QUANTUM MECHANICS", 19, C["mint"], (4, 16, 14), pop(t, 1.3, 0.45))
    title(cv, "CAN INFO BE ERASED?", 0, -168, 52, t, 0.1, glow=C["red"], depth=12)


def scene_hawking(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=1.0)
    bx, by, br = 0, 24, 120
    draw_bh(cv, bx, by, br, t, disk=0.9, glow=1.0)
    for i in range(7):
        ph = ((t * 0.5 + i * 0.143) % 1.0)
        a = -1.0 + i * 0.34
        r0 = br * 1.15
        # pair splits at the horizon: one in, one out
        inward = clamp(remap(ph, 0.0, 0.45))
        outward = clamp(remap(ph, 0.35, 1.0))
        if inward < 1:
            px = bx + math.cos(a) * r0 * (1 - inward * 0.85)
            py = by + math.sin(a) * r0 * (1 - inward * 0.85) * 0.5
            cv.disc(px, py, 4.6, C["white"], 1 - inward)
        if outward > 0:
            rr = r0 + 210 * ease_out_cubic(outward)
            px = bx + math.cos(a) * rr
            py = by + math.sin(a) * rr * 0.62 - outward * 30
            cv.glow(px, py, 18, C["cyan"], 0.55 * (1 - outward), 2.2)
            cv.disc(px, py, 3.6, C["cyan"], 1 - outward)
    title(cv, "HAWKING RADIATION", 0, -168, 56, t, 0.1, glow=C["cyan"], depth=12)
    draw_badge(cv, -300, 196, "1974 - STEPHEN HAWKING", 21, C["cyan"], (8, 10, 26), pop(t, 0.6, 0.5))
    draw_badge(cv, 330, 196, "IT GLOWS", 20, C["white"], (10, 12, 30), pop(t, 1.2, 0.4))


def scene_evaporate(cv, t, dur, var):
    twinkle(cv, "deep", t, drift=1.0)
    k = ease_in_cubic(clamp(remap(t, 0.1, 2.6)))
    br = lerp(120, 8, k)
    if br > 10:
        draw_bh(cv, 0, 10, br, t, disk=clamp(1.0 - 0.5 * k), glow=clamp(1.0 - 0.5 * k), spin=1.2)
    else:
        draw_shockwave(cv, 0, 10, remap(t, 2.6, 3.2), 240, C["cyan"], 8, 0.6)
        draw_question(cv, 0, 10, 34 * pop(t, 2.7, 0.4), t, 0.95, C["sun"])
    # depletion meter
    with cv.layer((-260, 168, 260, 208), 3, 0.95) as L:
        L.rrect(0, 188, 500, 30, 15, (255, 255, 255))
        w = 500 * (1 - k)
        if w > 4:
            L.rrect(-250 + w / 2, 188, w, 22, 11, C["orange"])
    cv.text("MASS", -290, 188, 20, C["white"], "c", 0.9)
    draw_counter(cv, 100 * (1 - k), 300, 188, 26, C["orange"], 0.95, suffix="%")
    title(cv, "EVAPORATION", 0, -168, 66, t, 0.1, glow=C["orange"], depth=13)
    draw_badge(cv, -300, 128, "WHERE DID THE INFO GO?", 20, C["orange"], (12, 5, 0), pop(t, 1.4, 0.5))


def scene_secret(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=1.2)
    draw_bh(cv, 0, 10, 108, t, disk=0.55, glow=1.0, spin=0.7, ring=1.0)
    # a keyhole of light opening at the centre
    k = ease_out_cubic(clamp(remap(t, 0.4, 1.6)))
    if k > 0.02:
        with cv.layer((-40, -46, 40, 70), 3, 0.95 * k) as L:
            for i in range(9):
                a = -1.15 + i * 0.29
                L.poly([(0, 10), (math.cos(a) * 320, 10 + math.sin(a) * 320 * 0.82),
                        (math.cos(a + 0.07) * 320, 10 + math.sin(a + 0.07) * 320 * 0.82)], C["hot"])
        cv.glow(0, 10, 190, C["amber"], 0.55 * k, 2.0)
        cv.disc(0, 10, 26 * k, C["white"], 0.95)
    for i in range(6):
        a = t * 0.9 + i * 1.05
        sparkle(cv, math.cos(a) * 250, 10 + math.sin(a) * 120, 12 + 6 * math.sin(t * 3 + i) ** 2,
                C["sun"], 0.8 * k)
    title(cv, "THE REAL SECRET", 0, -168, 64, t, 0.1, glow=C["amber"], depth=13)
    draw_badge(cv, -300, 196, "MAYBE NOT DARK AT ALL", 21, C["amber"], (10, 8, 24), pop(t, 0.7, 0.5))


def scene_questions(cv, t, dur, var):
    twinkle(cv, "space_b", t, drift=1.4)
    draw_bh(cv, 0, 24, 92, t, disk=0.9, glow=1.0)
    labels = ["SPACE?", "TIME?", "INFORMATION?", "INSIDE?"]
    cols = [C["cyan"], C["mint"], C["pink"], C["sun"]]
    for i, lab in enumerate(labels):
        ph = pop(t, 0.25 + i * 0.34, 0.5)
        if ph <= 0.04:
            continue
        a = -math.pi / 2 + i * (2 * math.pi / 4) + t * 0.28
        rx, ry = 392, 196
        px, py = math.cos(a) * rx, 34 + math.sin(a) * ry
        cv.glow(px, py, 92, cols[i], 0.24 * ph, 2.2)
        draw_badge(cv, px, py, lab, 18 + 2 * ph, cols[i], (8, 10, 26), ph)
        draw_question(cv, px, py - 42, 15 * ph, t + i, ph * 0.9, cols[i])
    title(cv, "WHAT ARE THEY TELLING US?", 0, -168, 46, t, 0.9, glow=C["violet"], depth=11)
    draw_badge(cv, -300, 196, "FOUR OPEN QUESTIONS", 21, C["violet"], (10, 8, 30), pop(t, 1.6, 0.5))


def scene_biganswer(cv, t, dur, var):
    twinkle(cv, "space_hot", t, drift=1.0)
    k = clamp(remap(t, 0.3, 1.6))
    draw_bh(cv, 0, 20, 86, t, disk=0.8, glow=1.0)
    qs = 1.0 - ease_in_cubic(clamp(remap(t, 0.6, 1.5)))
    if qs > 0.03:
        draw_question(cv, 0, 20, 76 * qs, t, 0.9 * qs, C["sun"], rot=math.sin(t * 2) * 8)
    if k > 0.5:
        f = clamp((k - 0.5) / 0.5)
        draw_rays(cv, 0, 20, t, 420 * f, 26, C["hot"], 0.24 * f, spin=11)
        draw_shockwave(cv, 0, 20, remap(t, 1.5, 2.6), 430, C["sun"], 10, 0.55)
        cv.glow(0, 20, 220, C["amber"], 0.45 * f, 2.0)
    title(cv, "THE BIGGEST SECRET", 0, -168, 58, t, 0.1, glow=C["amber"], depth=12)
    draw_badge(cv, -300, 196, "SOME DAY, MAYBE", 21, C["amber"], (10, 8, 24), pop(t, 0.9, 0.5))
    particles(cv, 0, 20, 420, t, 22, seed=21, color=C["sun"], alpha=0.45)


def scene_quote(cv, t, dur, var):
    twinkle(cv, "void", t, drift=0.6)
    draw_bh(cv, 260, 40, 96, t, disk=0.35, glow=0.55, spin=0.4, ring=0.7)
    draw_human(cv, 260, 200, 74, t, "look", skin=C["skin1"], shirt=C["teal"], mouth="open")
    p1 = pop(t, 0.15, 0.6)
    p2 = pop(t, 0.55, 0.6)
    if p1 > 0.03:
        title(cv, "DARKEST PLACES", -20, -110, 76, t, 0.15, C["white"], glow=C["violet"], depth=15)
    if p2 > 0.03:
        title(cv, "DEEPEST TRUTHS", -20, -10, 76, t, 0.55, C["sun"], glow=C["amber"], depth=15)
    draw_badge(cv, -300, 196, "ABOUT REALITY", 21, C["violet"], (10, 8, 30), pop(t, 1.3, 0.5))
    for i in range(9):
        a = t * 0.5 + i * 0.7
        sparkle(cv, -380 + math.cos(a) * 60, -60 + math.sin(a) * 60, 8 + 5 * math.sin(t * 2 + i) ** 2,
                C["white"], 0.55)


def scene_outro(cv, t, dur, var):
    twinkle(cv, "space_a", t, drift=0.8)
    cv.glow(0, 10, 420, C["violet"], 0.16, 2.4)
    draw_bh(cv, 0, -60, 46, t, disk=0.5, glow=0.7, spin=0.5)
    # like + subscribe buttons
    lp = pop(t, 0.25, 0.55)
    if lp > 0.05:
        cv.rrect(-190, 60, 150 * lp, 66 * lp, 33 * lp, C["pink"], 0.98)
        draw_badge(cv, -190, 60, "LIKE", 26 * min(1.0, lp * 1.2), C["pink"], (26, 4, 18), lp)
    spp = pop(t, 0.55, 0.55)
    if spp > 0.05:
        cv.rrect(120, 60, 230 * spp, 66 * spp, 33 * spp, C["red"], 0.98)
        draw_badge(cv, 120, 60, "SUBSCRIBE", 26 * min(1.0, spp * 1.2), C["red"], (255, 255, 255), spp,
                   glow=C["red"])
        bell = 1 + 0.14 * math.sin(t * 9) * clamp(remap(t, 0.9, 3.2))
        with cv.layer((246 - 30, 60 - 34, 246 + 30, 60 + 34), 3, spp) as L:
            L.poly([(246, 60 - 18 * bell), (246 - 13 * bell, 60 + 8), (246 + 13 * bell, 60 + 8)], C["sun"])
            L.ellipse(246, 60 + 12, 4.5, 4.5, C["sun"])
    title(cv, "THANKS FOR WATCHING", 0, 160, 40, t, 0.9, glow=C["violet"], depth=10)
    draw_badge(cv, -300, -196, "BLACK HOLES - EXPLAINED", 20, C["cyan"], (8, 10, 26), pop(t, 0.2, 0.5))
    draw_chevrons(cv, (-560, -150), (560, -150), t, 10, C["cyan"], 9, 0.35, 0.8)


# =============================================================================
#  SCENE REGISTRY  (fn, background theme)
# =============================================================================
SCENES = {
    "intro": (scene_intro, "space_a"),
    "gravity": (scene_gravity, "space_b"),
    "noexit": (scene_noexit, "space_a"),
    "mystery": (scene_mystery, "space_a"),
    "reveal": (scene_reveal, "space_a"),
    "nothole": (scene_nothole, "space_b"),
    "compress": (scene_compress, "space_b"),
    "horizon": (scene_horizon, "space_a"),
    "crossing": (scene_crossing, "deep"),
    "timedilation": (scene_timedilation, "space_b"),
    "observer": (scene_observer, "space_a"),
    "spacetime": (scene_spacetime, "space_b"),
    "monsters": (scene_monsters, "space_hot"),
    "milkyway": (scene_milkyway, "galaxy"),
    "sgra": (scene_sgra, "space_a"),
    "vacuum": (scene_vacuum, "space_b"),
    "swap": (scene_swap, "orbit"),
    "close": (scene_close, "space_a"),
    "spaghetti": (scene_spaghetti, "space_hot"),
    "inside": (scene_inside, "deep"),
    "singularity": (scene_singularity, "deep"),
    "physics": (scene_physics, "space_b"),
    "paradox": (scene_paradox, "space_a"),
    "book": (scene_book, "deep"),
    "destroy": (scene_destroy, "space_b"),
    "hawking": (scene_hawking, "space_a"),
    "evaporate": (scene_evaporate, "deep"),
    "secret": (scene_secret, "space_a"),
    "questions": (scene_questions, "space_b"),
    "biganswer": (scene_biganswer, "space_hot"),
    "quote": (scene_quote, "void"),
    "outro": (scene_outro, "space_a"),
}


# =============================================================================
#  STORYBOARD  (scene, spoken fragment)  --  hand-timed beats, auto-fitted
# =============================================================================
STORYBOARD = [
    ("intro",       "इमेजिन कीजिए, यूनिवर्स में एक ऐसी जगह है,"),
    ("gravity",     "जहां ग्रेविटी इतनी पावरफुल है,"),
    ("gravity",     "कि लाइट भी एस्केप नहीं कर सकती।"),
    ("noexit",      "और अगर आप इस बाउंड्री को क्रॉस कर लें,"),
    ("noexit",      "तो वापस आना इंपॉसिबल हो सकता है।"),
    ("mystery",     "लेकिन सबसे स्ट्रेंज बात हमें अभी तक नहीं पता"),
    ("mystery",     "ब्लैक होल के अंदर एक्चुअली क्या है।"),
    ("reveal",      "यह है ब्लैक होल।"),
    ("nothole",     "ब्लैक होल कोई जॉइंट होल नहीं होता।"),
    ("nothole",     "यह स्पेस और टाइम का एक ऐसा रीजन है"),
    ("compress",    "जहां इनस अमाउंट ऑफ मैटर"),
    ("compress",    "एक एक्सट्रीमली स्मॉल एरिया में कंप्रेस हो जाता है।"),
    ("horizon",     "इसकी बाउंड्री को कहते हैं इवेंट होराइजन।"),
    ("horizon",     "यही है वो लाइन।"),
    ("crossing",    "एक बार अगर कोई ऑब्जेक्ट इस बाउंड्री के अंदर चला जाए"),
    ("crossing",    "तो उसके लिए बाहर निकलने का कोई नोन वे नहीं है।"),
    ("crossing",    "नॉट इवन लाइट।"),
    ("timedilation", "लेकिन यहां एक माइंड बेंडिंग चीज होती है।"),
    ("timedilation", "अगर आप ब्लैक होल की तरफ फॉल कर रहे हो"),
    ("timedilation", "तो आपके लिए टाइम नॉर्मली पास होता रहेगा।"),
    ("observer",    "लेकिन दूर खड़ा ऑब्जर्वर आपको"),
    ("observer",    "इवेंट होराइजन के पास एक्सट्रीमली स्लो होते हुए देख सकता है।"),
    ("spacetime",   "मतलब टाइम खुद डिफरेंट ऑब्जर्वर्स के लिए"),
    ("spacetime",   "डिफरेंट तरह बिहेव कर सकता है।"),
    ("monsters",    "और ब्लैक होल सिर्फ स्पेस में रैंडम मॉन्सर्स नहीं है।"),
    ("milkyway",    "हमारी गैलेक्सी मिल्की वे के सेंटर में"),
    ("milkyway",    "भी एक सुपरमैसिव ब्लैक होल है।"),
    ("sgra",        "सेजिटेरियस ए स्टार।"),
    ("sgra",        "इसका मास हमारे सन से अराउंड"),
    ("sgra",        "4 मिलियन टाइम्स ज्यादा है।"),
    ("vacuum",      "लेकिन सरप्राइजिंगली यह हमें सक नहीं कर रहा।"),
    ("vacuum",      "ब्लैक होल कोई कॉस्मिक वैक्यूम क्लीनर नहीं होता।"),
    ("swap",        "अगर सन को सेम मास के ब्लैक होल से रिप्लेस कर दिया जाए"),
    ("swap",        "तो अर्थ ऑलमोस्ट वही ऑर्बिट मेंटेन करेगी।"),
    ("swap",        "बस सनलाइट डिसअपीयर हो जाएगी।"),
    ("close",       "लेकिन ब्लैक होल्स का सबसे टेरिफाइंग पार्ट अब आता है।"),
    ("close",       "अगर आप ब्लैक होल के पास इनफ क्लोज चले जाएं"),
    ("close",       "तो ग्रेविटी आपके बॉडी के डिफरेंट पार्ट्स पर"),
    ("close",       "डिफरेंट स्ट्रेंथ से पुल करेगी।"),
    ("spaghetti",   "आप स्ट्रेच होने लगेंगे और कंप्रेस भी।"),
    ("spaghetti",   "साइंटिस्ट्स इस प्रोसेस को कहते हैं स्पैगिफिकेशन।"),
    ("spaghetti",   "नाम फनी है एक्सपीरियंस बिल्कुल नहीं।"),
    ("inside",      "लेकिन ब्लैक होल्स की रियल मिस्ट्री उनके बाहर नहीं।"),
    ("inside",      "उनके अंदर है।"),
    ("singularity", "आइंस्टाइन की इक्वेशन सजेस्ट करती हैं"),
    ("singularity", "कि ब्लैक होल के सेंटर में एक सिंगुलैरिटी हो सकती है।"),
    ("singularity", "जहां स्पेस टाइम कर्वेचर थरेटिकली इनफाइनाइट हो जाती है।"),
    ("physics",     "और यहां हमारी फिजिक्स प्रॉब्लम में आ जाती है।"),
    ("physics",     "बिकॉज़ जनरल रिलेटिविटी और क्वांटम मैकेनिक्स"),
    ("physics",     "दोनों यूनिवर्स को एक्सप्लेन करने के लिए इनक्रेडिबली पावरफुल हैं।"),
    ("physics",     "लेकिन ब्लैक होल के सेंटर में दोनों को एक साथ"),
    ("physics",     "एक्सप्लेन करना एक्सट्रीमली डिफिकल्ट हो जाता है।"),
    ("paradox",     "और फिर आता है ब्लैक होल इंफॉर्मेशन पैराडॉक्स।"),
    ("paradox",     "इमेजिन कीजिए आप एक बुक ब्लैक होल में थ्रो कर देते हैं।"),
    ("book",        "बुक के अंदर इंफॉर्मेशन है"),
    ("book",        "लेकिन ब्लैक होल से कुछ भी बाहर नहीं आ सकता।"),
    ("book",        "तो उस इंफॉर्मेशन का क्या हुआ?"),
    ("destroy",     "क्या यूनिवर्स इंफॉर्मेशन को परमानेंटली डिस्ट्रॉय कर सकता है?"),
    ("destroy",     "क्वांटम मैकेनिक्स के अकॉर्डिंग यह प्रॉब्लम क्रिएट करता है।"),
    ("hawking",     "और जब स्टीफन हॉकिंग ने डिस्कवर किया"),
    ("hawking",     "कि ब्लैक होल्स स्लोली रेडिएशन इमिट कर सकते हैं"),
    ("hawking",     "तो मिस्ट्री और भी डीप हो गई।"),
    ("evaporate",   "बिकॉज़ इवेंचुअली ब्लैक होल्स थ्यरेटिकली इवापोरेट हो सकता है।"),
    ("evaporate",   "लेकिन अगर ब्लैक होल डिसअपीयर हो गया"),
    ("evaporate",   "तो उसके अंदर गिरने वाली इनेशन गई कहां?"),
    ("secret",      "और शायद यही ब्लैक होल्स का सबसे इंपॉर्टेंट सीक्रेट है।"),
    ("secret",      "हो सकता है ब्लैक होल्स सिर्फ यूनिवर्स के डारकेस्ट ऑब्जेक्ट्स ना हो।"),
    ("questions",   "हो सकता है यह हमें बताएं कि रियलिटी एक्चुअली काम कैसे करती है?"),
    ("questions",   "स्पेस क्या है? टाइम क्या है?"),
    ("questions",   "इंफॉर्मेशन यूनिवर्स में कैसे सर्वाइव करती है?"),
    ("questions",   "और ब्लैक होल के अंदर एक्चुअली क्या है?"),
    ("biganswer",   "मे बी सम डे इन क्वेशंस का आंसर"),
    ("biganswer",   "हमें यूनिवर्स का सबसे बड़ा सीक्रेट बता दे"),
    ("quote",       "बिकॉज़ समटाइम्स द डारकेस्ट प्लेसेस इन द यूनिवर्स"),
    ("quote",       "हाइड द डीपेस्ट ट्रुथ्स अबाउट रियलिटी।"),
    ("outro",       "अगर आपको यह वीडियो पसंद आई हो तो लाइक जरूर करें"),
    ("outro",       "और यूनिवर्स, साइंस और टेक्नोलॉजी की ऐसी ही"),
    ("outro",       "इंटरेस्टिंग स्टोरीज के लिए चैनल को सब्सक्राइब करें।"),
    ("outro",       "मिलते हैं नेक्स्ट वीडियो में। थैंक्स फॉर वाचिंग। अंटिल नेक्स्ट टाइम साइनिंग ऑफ।"),
]

# transition that opens each scene
TRANS_FOR = {
    "intro": "fade", "gravity": "zoom", "noexit": "spring", "mystery": "shockwave",
    "reveal": "shockwave", "nothole": "spring", "compress": "zoom", "horizon": "shockwave",
    "crossing": "iris", "timedilation": "spring", "observer": "pan", "spacetime": "zoom",
    "monsters": "spring", "milkyway": "zoom", "sgra": "shockwave", "vacuum": "spring",
    "swap": "pan", "close": "whip", "spaghetti": "spring", "inside": "iris",
    "singularity": "zoom", "physics": "shockwave", "paradox": "spring", "book": "iris",
    "destroy": "pan", "hawking": "shockwave", "evaporate": "iris", "secret": "zoom",
    "questions": "spring", "biganswer": "shockwave", "quote": "pan", "outro": "spring",
}

SENT_END = ("।", "?", "!", ".", "॥")


class Beat:
    __slots__ = ("i", "start", "end", "text", "words", "scene", "var", "run", "layout")


class Run:
    __slots__ = ("idx", "start", "end", "scene", "beats", "kind")


class Timeline:
    def __init__(self, beats, runs, duration):
        self.beats, self.runs, self.duration = beats, runs, duration
        self.starts = [b.start for b in beats]

    def beat_at(self, t):
        import bisect
        return max(0, min(len(self.beats) - 1, bisect.bisect_right(self.starts, t) - 1))


def _tok_weight(tok):
    core = re.sub(r"[।?!.,॥]", "", tok)
    w = 1.0 + 0.11 * len(core)
    if re.search(r"[0-9०-९]", core):
        w += 3.0
    return w


def _pause_weight(tok):
    if tok.endswith(SENT_END):
        return 1.1
    if tok.endswith(","):
        return 0.55
    return 0.0


def build_timeline(duration):
    """Fit the hand-authored beat list to `duration`, honouring 2.5-4.2 s beats."""
    raw = []
    for scene, text in STORYBOARD:
        toks = text.split()
        w = sum(_tok_weight(tk) + _pause_weight(tk) for tk in toks) + 0.9
        raw.append((scene, text, w))
    total_w = sum(r[2] for r in raw)
    durs = [duration * r[2] / total_w for r in raw]
    fixed = [False] * len(durs)
    for _ in range(40):
        changed = False
        for i, d in enumerate(durs):
            lo, hi = MIN_BEAT, MAX_BEAT
            if d < lo - 1e-6 and not fixed[i]:
                durs[i], fixed[i], changed = lo, True, True
            elif d > hi + 1e-6 and not fixed[i]:
                durs[i], fixed[i], changed = hi, True, True
        free = [i for i in range(len(durs)) if not fixed[i]]
        if not free:
            break
        remaining = duration - sum(durs[i] for i in range(len(durs)) if fixed[i])
        wsum = sum(raw[i][2] for i in free)
        for i in free:
            durs[i] = remaining * raw[i][2] / wsum
        if not changed and all(MIN_BEAT - 1e-3 <= durs[i] <= MAX_BEAT + 1e-3 for i in free):
            break
    # final safety clamp + error diffusion so beats stay in range and the sum is exact
    for _ in range(3):
        for i, d in enumerate(durs):
            durs[i] = clamp(d, MIN_BEAT, MAX_BEAT)
        diff = duration - sum(durs)
        if abs(diff) < 1e-3:
            break
        order = sorted(range(len(durs)), key=lambda i: -(durs[i] - MIN_BEAT) if diff < 0 else (durs[i] - MIN_BEAT))
        step = diff / len(order)
        for i in order:
            durs[i] = clamp(durs[i] + step, MIN_BEAT, MAX_BEAT)

    beats, runs = [], []
    t = 0.0
    for i, ((scene, text, _w), d) in enumerate(zip(raw, durs)):
        b = Beat()
        b.i, b.start, b.end, b.text, b.scene, b.layout = i, t, t + d, text, scene, None
        toks = text.split()
        ww = [_tok_weight(tk) + _pause_weight(tk) for tk in toks]
        s = sum(ww)
        tt, b.words = t, []
        for tk, w in zip(toks, ww):
            b.words.append((tk, tt - t, tt - t + d * w / s))
            tt += d * w / s
        if runs and runs[-1].scene == scene:
            runs[-1].beats.append(b)
            runs[-1].end = b.end
            b.run = len(runs) - 1
            b.var = len(runs[-1].beats) - 1
        else:
            r = Run()
            r.idx, r.start, r.end, r.scene, r.beats = len(runs), b.start, b.end, scene, [b]
            r.kind = TRANS_FOR.get(scene, "spring")
            runs.append(r)
            b.run, b.var = r.idx, 0
        b.var = min(b.var, 3)
        beats.append(b)
        t += d
    # scale to exact duration
    return Timeline(beats, runs, beats[-1].end if beats else 0.0)


def print_storyboard(tl):
    print("\n   STORYBOARD  (%.1fs, %d beats, %d scene runs)" % (tl.duration, len(tl.beats), len(tl.runs)))
    for b in tl.beats:
        print("   %2d  %6.2f-%6.2f (%4.2fs) [%-12s v%d] %s"
              % (b.i + 1, b.start, b.end, b.end - b.start, b.scene, b.var, b.text[:66]))
    print()


# =============================================================================
#  TRANSITIONS
# =============================================================================
def _zoom(img, s):
    if s <= 1.001:
        return img
    big = img.resize((int(W * s), int(H * s)), Image.BILINEAR)
    x0, y0 = (big.width - W) // 2, (big.height - H) // 2
    return big.crop((x0, y0, x0 + W, y0 + H))


def _blur_pan(img, k):
    """Horizontal motion blur for whip pans."""
    if k < 0.5:
        return img
    acc = Image.new("RGB", img.size, (0, 0, 0))
    n = 5
    for i in range(n):
        acc = ImageChops.add(acc, img.transform(img.size, Image.AFFINE,
                                                 (1, 0, (i - n // 2) * k * 2.0, 0, 1, 0),
                                                 resample=Image.BILINEAR))
    return Image.eval(acc, lambda v: min(255, int(v / n)))


def transition(prev, new, kind, p):
    p = clamp(p)
    if kind == "shockwave":
        e = ease_out_cubic(p)
        cxp, cyp = W / 2.0, CY
        R = math.hypot(W, H) * 0.8 * e
        sw, sh = max(4, W // 4), max(4, H // 4)
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        d = np.hypot((xx + 0.5) * 4 - cxp, (yy + 0.5) * 4 - cyp)
        m = Image.fromarray((np.clip((R - d) / 10.0 + 0.5, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        out = Image.composite(new, prev, m)
        ring = np.exp(-(((d - R) / (14 + 20 * (1 - p))) ** 2)) * (1 - p) ** 0.6
        rm = Image.fromarray((np.clip(ring, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        out.paste((255, 255, 255), (0, 0), rm)
        return out
    if kind == "zoom":
        e = elastic_out(p)
        newz = _zoom(new, lerp(1.5, 1.0, min(1.0, e)))
        prevz = _zoom(prev, lerp(1.0, 1.32, ease_in_cubic(p)))
        return Image.blend(prevz, newz, ease_in_out_quad(clamp(p * 1.5)))
    if kind == "pan":
        e = ease_in_out_cubic(p)
        out = Image.new("RGB", (W, H))
        out.paste(prev, (0, -int(H * e)))
        out.paste(new, (0, int(H * (1 - e))))
        return out
    if kind == "iris":
        e = ease_in_out_cubic(p)
        R = math.hypot(W, H) * 0.75 * e
        sw, sh = max(4, W // 5), max(4, H // 5)
        yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
        d = np.hypot((xx + 0.5) * 5 - W / 2.0, (yy + 0.5) * 5 - CY)
        m = Image.fromarray((np.clip((R - d) / 8.0 + 0.5, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        out = Image.composite(new, prev, m)
        ring = np.exp(-(((d - R) / (10 + 16 * (1 - p))) ** 2)) * (1 - p) ** 0.5
        rm = Image.fromarray((np.clip(ring, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        out.paste((180, 240, 255), (0, 0), rm)
        return out
    if kind == "whip":
        e = ease_in_out_cubic(p)
        k = math.sin(math.pi * min(1.0, p * 1.15)) * 26
        out = Image.new("RGB", (W, H))
        out.paste(prev, (int(-W * e * 1.05), 0))
        out.paste(new, (int(W * (1 - e) * 1.05), 0))
        return _blur_pan(out, k)
    e = ease_out_back(p)                                   # spring
    out = Image.new("RGB", (W, H))
    out.paste(prev, (-int(W * 0.28 * p), 0))
    out.paste(new, (int(W * (1 - e)), 0))
    return out


# =============================================================================
#  SUBTITLES  (bottom safe area, soft shadow only, NO box, karaoke yellow)
# =============================================================================
SHADOW_OFFS = [(-3, -3), (3, -3), (-3, 3), (3, 3), (0, 4), (4, 0), (0, -3), (-3, 0)]


def layout_subtitle(beat):
    words = [w[0] for w in beat.words]
    max_w = W * 0.86
    size = int(round(62 * FS))
    while True:
        sp = TE.get(" ", size).adv
        lines, cur, curw = [], [], 0.0
        for i, w in enumerate(words):
            ww = TE.get(w, size).adv
            if cur and curw + sp + ww > max_w:
                lines.append((cur, curw))
                cur, curw = [(i, ww)], ww
            else:
                curw += ww + (sp if cur else 0)
                cur.append((i, ww))
        lines.append((cur, curw))
        if len(lines) <= 3 or size < 32 * FS:
            break
        size = int(size * 0.92)
    beat.layout = (size, lines, sp, words)


def draw_subtitles(img, beat, tb):
    if beat.layout is None:
        layout_subtitle(beat)
    size, lines, sp, words = beat.layout
    lh = int(size * 1.40)
    block_h = lh * len(lines)
    top = min(H * SUB_Y - block_h / 2.0, H * 0.962 - block_h)
    a = ease_out_cubic(remap(tb, 0.0, 0.18))
    slide = (1 - ease_out_back(remap(tb, 0.0, 0.28))) * H * 0.018
    cur = -1
    for wi, (_, t0, t1) in enumerate(beat.words):
        if tb >= t0:
            cur = wi
    k = size / 62.0
    for li, (items, lw) in enumerate(lines):
        x = (W - lw) / 2.0
        base_y = top + li * lh + size * 1.0
        for (wi, ww) in items:
            tm = TE.get(words[wi], size)
            ox, oy = x - tm.ox + tm.bbox[0], base_y + slide - tm.base + tm.bbox[1]
            m = tm.ink if a > 0.99 else tm.ink.point(alut(a))
            for dx, dy in SHADOW_OFFS:
                img.paste(C["navy_txt"], (int(round(ox + dx * k)), int(round(oy + dy * k))), m)
            img.paste(C["sun_y2"] if wi == cur else (255, 255, 255), (int(round(ox)), int(round(oy))), m)
            x += ww + sp


# =============================================================================
#  FRAME RENDERER
# =============================================================================
TL = None
TE = None
SCALE = 1.0


def render_scene(run, t_in_run, var):
    fn, bg = SCENES[run.scene]
    cv = new_canvas(bg)
    cv.cx += math.sin(t_in_run * 0.55 + run.idx) * 6 * U
    cv.cy += math.cos(t_in_run * 0.43 + run.idx) * 4 * U
    fn(cv, t_in_run, max(0.6, run.end - run.start), var)
    return cv.im


def render_frame(t):
    D = TL.duration
    t = clamp(t, 0.0, D - 1e-4)
    bi = TL.beat_at(t)
    beat = TL.beats[bi]
    run = TL.runs[beat.run]
    tt = t - run.start
    img = render_scene(run, tt, beat.var)
    if run.idx > 0 and run.kind != "fade" and tt < TRANS_TIME:
        pr = TL.runs[run.idx - 1]
        pimg = render_scene(pr, (pr.end - pr.start) + tt, pr.beats[-1].var)
        img = transition(pimg, img, run.kind, tt / TRANS_TIME)
    draw_subtitles(img, beat, t - beat.start)
    if t < 0.35:
        img = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), img, ease_out_cubic(t / 0.35))
    if t > D - 0.7:
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), ease_in_cubic(remap(t, D - 0.7, D - 0.02)))
    return np.asarray(img)


# =============================================================================
#  SOUND DESIGN  -  every SFX synthesised with NumPy, 48 kHz stereo
# =============================================================================
SR = 48000
CEILING_DB = 2.6          # master peak ceiling, dB below full scale (AAC overshoot headroom)
SFX_ONLY_NOTE = "no music, no voice-over: whooshes, pops, booms, ticks, risers"


def _smooth(x, m):
    """Cheap zero-phase moving average (cumsum) - our low-pass/band shaper."""
    m = max(1, int(m))
    if m <= 1:
        return x
    c = np.concatenate(([0.0], np.cumsum(x, dtype=np.float64)))
    y = (c[m:] - c[:-m]) / m
    return np.concatenate((np.zeros(m - 1), y)).astype(np.float32)[:len(x)]


def _rng(seed):
    return np.random.RandomState(seed & 0x7fffffff)


def _tt(n):
    return np.arange(n, dtype=np.float32) / SR


def s_pop(seed=0):
    n = int(0.22 * SR)
    t = _tt(n)
    f = 340 + 620 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(ph) * np.exp(-t * 20)
    sig += _rng(seed).standard_normal(n) * np.exp(-t * 240) * 0.22
    return (sig * 0.85).astype(np.float32)


def s_boom(seed=1, dur=1.35):
    n = int(dur * SR)
    t = _tt(n)
    f = 40 + 96 * np.exp(-t * 8.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 3.0)
    rum = _smooth(_rng(seed).standard_normal(n), 64) * np.exp(-t * 2.0) * 2.4
    crack = _rng(seed + 1).standard_normal(n) * np.exp(-t * 80) * 0.45
    return np.tanh((body * 0.95 + rum * 0.8 + crack) * 1.4).astype(np.float32)


def s_whoosh(seed=2, dur=0.8, up=True):
    n = int(dur * SR)
    u = np.linspace(0, 1, n, dtype=np.float32)
    x = _rng(seed).standard_normal(n)
    lo, mid, hi = _smooth(x, 120) * 6.0, _smooth(x, 22) * 2.6, _smooth(x, 4) * 0.6
    blend = lo * (1 - u) + mid * np.sin(np.pi * u) + hi * u * 0.5
    env = np.clip(np.sin(np.pi * np.clip(u * 1.02, 0, 1)), 0, 1) ** 1.5
    return (blend * env * 0.9).astype(np.float32)


def s_riser(seed=3, dur=1.35):
    n = int(dur * SR)
    u = np.linspace(0, 1, n, dtype=np.float32)
    x = _rng(seed).standard_normal(n)
    band = _smooth(x, 14) * 3.0 * (0.4 + 1.2 * u)
    f = 150 * (1 + 7.0 * u ** 2)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.30 * u
    return ((band + tone) * (u ** 2.0)).astype(np.float32)


def s_tick(seed=4):
    n = int(0.07 * SR)
    t = _tt(n)
    return ((_smooth(_rng(seed).standard_normal(n), 2) * 0.45 + 0.45 * np.sin(2 * np.pi * 2400 * t))
            * np.exp(-t * 110)).astype(np.float32)


def s_chime(seed=5, dur=2.2, base=523.25):
    n = int(dur * SR)
    t = _tt(n)
    sig = np.zeros(n, np.float32)
    for i, (mul, amp, dec) in enumerate(((1.0, 0.55, 1.5), (1.5, 0.34, 2.1), (2.0, 0.24, 2.7), (3.0, 0.13, 3.4))):
        sig += amp * np.sin(2 * np.pi * base * mul * t + i * 0.7) * np.exp(-t * dec)
    return (sig * 0.55).astype(np.float32)


def s_shimmer(seed=6, dur=2.4):
    n = int(dur * SR)
    t = _tt(n)
    rs = _rng(seed)
    sig = np.zeros(n, np.float32)
    for i in range(11):
        f = rs.uniform(900, 4600)
        ph = rs.uniform(0, 6.28)
        sig += np.sin(2 * np.pi * f * t + ph) * rs.uniform(0.05, 0.16) * (1 + 0.4 * np.sin(2 * np.pi * 0.7 * t + i))
    env = np.minimum(1.0, t / 0.5) * np.exp(-np.maximum(0, t - 0.6) * 1.1)
    return (sig * env).astype(np.float32)


def s_sparkle(seed=7):
    n = int(1.0 * SR)
    out = np.zeros(n, np.float32)
    for k in range(4):
        f = 1400 * (1.28 ** k)
        st = int(k * 0.075 * SR)
        m = min(n - st, int(0.36 * SR))
        t = _tt(m)
        out[st:st + m] += (np.sin(2 * np.pi * f * t) * np.exp(-t * 22) * 0.22).astype(np.float32)
    return out


def s_swish(seed=8):
    n = int(0.55 * SR)
    u = np.linspace(0, 1, n, dtype=np.float32)
    x = _smooth(_rng(seed).standard_normal(n), 30) * 3.2
    return (x * np.clip(np.sin(np.pi * u), 0, 1) ** 2).astype(np.float32)


def s_iris(seed=9):
    a = s_whoosh(seed, 0.95)
    b = s_boom(seed + 1, 1.1)[:int(0.9 * SR)]
    n = max(len(a), len(b))
    out = np.zeros(n, np.float32)
    out[:len(a)] += a * 0.7
    out[:len(b)] += b * 0.55
    return out


def s_sub(seed=10, dur=1.8):
    n = int(dur * SR)
    t = _tt(n)
    f = 46 + 8 * np.sin(2 * np.pi * 0.6 * t)
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.35 * np.sin(2 * np.pi * np.cumsum(f * 2) / SR)
    env = np.minimum(1.0, t / 0.25) * np.exp(-t * 1.4)
    return (sig * env * 0.5).astype(np.float32)


def s_zap(seed=11):
    n = int(0.30 * SR)
    t = _tt(n)
    f = 1800 * np.exp(-t * 9) + 180
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = ((ph / np.pi) % 2.0) - 1.0
    return (saw * np.exp(-t * 9) * 0.35).astype(np.float32)


KINDS = {
    "pop": s_pop, "boom": s_boom, "whoosh": s_whoosh, "riser": s_riser, "tick": s_tick,
    "chime": s_chime, "shimmer": s_shimmer, "sparkle": s_sparkle, "swish": s_swish,
    "iris": s_iris, "sub": s_sub, "zap": s_zap,
}
_CACHE = {}


def get_sfx(kind, salt=0):
    key = (kind, salt)
    if key not in _CACHE:
        sig = np.nan_to_num(KINDS[kind](salt + 1), nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
        peak = float(np.max(np.abs(sig))) or 1.0
        _CACHE[key] = sig / peak if peak > 1.0 else sig
    return _CACHE[key]


# per-scene hit list:  (offset_s, kind, gain_dB, pan)
SFX_PLAN = {
    "intro": [(0.05, "shimmer", -13, 0.0), (0.35, "pop", -8, 0.0), (1.1, "chime", -16, 0.25),
              (1.9, "swish", -15, -0.3), (2.6, "sparkle", -18, 0.3)],
    "gravity": [(0.05, "sub", -9, 0.0), (0.30, "pop", -9, 0.0), (0.8, "swish", -14, 0.2),
                (1.5, "sub", -14, 0.0), (2.2, "tick", -18, -0.2)],
    "noexit": [(0.05, "boom", -10, 0.0), (0.6, "whoosh", -13, 0.35), (1.4, "zap", -17, -0.2),
               (1.9, "boom", -14, 0.0), (2.4, "swish", -16, 0.4)],
    "mystery": [(0.05, "shimmer", -12, 0.0), (0.5, "pop", -9, -0.2), (1.2, "chime", -15, 0.2),
                (1.9, "pop", -12, 0.3), (2.5, "chime", -18, -0.1)],
    "reveal": [(0.0, "sub", -6, 0.0), (0.12, "boom", -5, 0.0), (0.55, "whoosh", -8, 0.0),
               (1.0, "chime", -13, 0.0), (1.6, "shimmer", -12, 0.15), (2.3, "sparkle", -15, -0.2)],
    "nothole": [(0.05, "pop", -9, -0.3), (0.55, "zap", -14, -0.3), (1.0, "pop", -10, 0.35),
                (1.5, "swish", -15, 0.1), (2.1, "boom", -16, -0.2)],
    "compress": [(0.10, "whoosh", -12, 0.0), (0.9, "riser", -15, 0.0), (1.8, "boom", -9, 0.0),
                 (2.2, "pop", -12, 0.2), (2.6, "tick", -20, 0.3)],
    "horizon": [(0.05, "chime", -14, -0.2), (0.35, "pop", -10, -0.2), (1.1, "tick", -18, 0.0),
                (1.7, "tick", -18, 0.0), (2.2, "swish", -15, 0.2)],
    "crossing": [(0.05, "sub", -11, 0.0), (0.5, "whoosh", -11, 0.4), (1.5, "zap", -16, 0.2),
                 (1.95, "boom", -11, 0.0), (2.4, "sub", -16, 0.0)],
    "timedilation": [(0.05, "riser", -13, 0.0), (0.6, "pop", -10, -0.4), (0.9, "pop", -10, 0.4),
                     (1.6, "tick", -16, -0.4), (1.85, "tick", -18, -0.4), (2.1, "tick", -20, -0.4)],
    "observer": [(0.05, "swish", -13, -0.3), (0.5, "pop", -11, -0.3), (1.2, "sub", -15, 0.3),
                 (2.0, "tick", -19, 0.3), (2.5, "chime", -17, 0.3)],
    "spacetime": [(0.05, "sub", -11, 0.0), (0.4, "whoosh", -14, -0.3), (1.1, "chime", -16, 0.3),
                  (1.8, "tick", -18, 0.0), (2.3, "swish", -17, 0.0)],
    "monsters": [(0.05, "boom", -11, 0.0), (0.4, "pop", -10, -0.4), (0.6, "pop", -10, 0.4),
                 (0.9, "zap", -14, -0.2), (1.4, "zap", -14, 0.3), (2.0, "boom", -15, 0.0)],
    "milkyway": [(0.05, "shimmer", -12, 0.0), (0.5, "riser", -16, 0.0), (1.3, "chime", -13, 0.0),
                 (2.0, "swish", -16, 0.3), (2.6, "pop", -14, 0.0)],
    "sgra": [(0.05, "sub", -8, 0.0), (0.35, "boom", -10, 0.0), (0.8, "ticks", -16, 0.2),
             (2.0, "chime", -14, 0.0), (2.6, "pop", -12, 0.0)],
    "vacuum": [(0.05, "pop", -10, -0.4), (0.5, "whoosh", -13, -0.4), (1.1, "zap", -16, -0.3),
               (1.6, "pop", -11, 0.3), (2.2, "swish", -16, 0.2)],
    "swap": [(0.05, "sub", -10, 0.0), (0.7, "whoosh", -11, 0.0), (1.4, "boom", -9, 0.0),
             (2.0, "zap", -15, 0.2), (2.6, "tick", -19, 0.3)],
    "close": [(0.05, "riser", -12, 0.0), (0.6, "sub", -12, 0.0), (1.4, "whoosh", -12, 0.35),
              (2.1, "boom", -13, 0.0), (2.6, "tick", -20, -0.2)],
    "spaghetti": [(0.05, "whoosh", -11, 0.0), (0.5, "pop", -10, 0.3), (1.2, "zap", -15, -0.3),
                  (1.7, "pop", -9, -0.4), (2.3, "swish", -16, 0.2)],
    "inside": [(0.05, "iris", -9, 0.0), (0.9, "sub", -12, 0.0), (1.6, "shimmer", -13, 0.0),
               (2.2, "chime", -16, 0.2), (2.8, "swish", -18, -0.2)],
    "singularity": [(0.05, "riser", -10, 0.0), (0.7, "zap", -15, 0.2), (1.4, "boom", -8, 0.0),
                    (1.9, "sub", -9, 0.0), (2.5, "ticks", -17, 0.0)],
    "physics": [(0.05, "zap", -12, -0.3), (0.6, "whoosh", -13, 0.0), (1.3, "boom", -8, 0.0),
                (1.7, "zap", -12, 0.3), (2.3, "sub", -12, 0.0)],
    "paradox": [(0.05, "pop", -10, -0.4), (0.7, "swish", -13, -0.2), (1.3, "whoosh", -12, 0.3),
                (2.1, "boom", -11, 0.3), (2.5, "chime", -17, 0.0)],
    "book": [(0.05, "shimmer", -14, 0.0), (0.6, "pop", -11, 0.0), (1.3, "zap", -16, 0.2),
             (2.0, "chime", -15, -0.2), (2.6, "swish", -17, 0.0)],
    "destroy": [(0.05, "riser", -14, 0.0), (0.6, "pop", -10, -0.4), (0.9, "pop", -10, 0.4),
                (1.4, "zap", -14, -0.4), (2.0, "chime", -13, 0.4), (2.6, "tick", -19, 0.0)],
    "hawking": [(0.05, "shimmer", -13, 0.0), (0.5, "sparkle", -13, 0.2), (1.2, "sparkle", -15, -0.2),
                (1.9, "chime", -14, 0.0), (2.5, "pop", -13, 0.3)],
    "evaporate": [(0.05, "sub", -10, 0.0), (0.7, "whoosh", -13, 0.0), (1.5, "ticks", -16, 0.0),
                  (2.4, "boom", -12, 0.0), (2.9, "zap", -16, 0.0)],
    "secret": [(0.05, "chime", -12, 0.0), (0.5, "shimmer", -12, 0.0), (1.2, "riser", -15, 0.0),
               (1.9, "boom", -13, 0.0), (2.5, "sparkle", -14, 0.3)],
    "questions": [(0.05, "pop", -11, 0.3), (0.35, "pop", -11, -0.3), (0.7, "pop", -11, 0.4),
                  (1.05, "pop", -11, -0.4), (1.5, "shimmer", -14, 0.0), (2.2, "chime", -15, 0.0)],
    "biganswer": [(0.05, "riser", -11, 0.0), (0.9, "boom", -8, 0.0), (1.4, "chime", -11, 0.0),
                  (2.0, "shimmer", -11, 0.0), (2.6, "sparkle", -14, 0.0)],
    "quote": [(0.05, "sub", -12, 0.0), (0.35, "chime", -14, 0.0), (1.1, "shimmer", -15, 0.2),
              (1.9, "whoosh", -16, 0.0), (2.5, "sparkle", -17, -0.2)],
    "outro": [(0.05, "pop", -9, 0.0), (0.55, "pop", -9, 0.0), (1.1, "sparkle", -13, 0.0),
              (1.6, "chime", -13, 0.0), (2.2, "swish", -16, 0.0), (2.8, "sub", -15, 0.0)],
}

TRANS_SFX = {"shockwave": ("boom", -8), "zoom": ("riser", -12), "spring": ("whoosh", -13),
             "pan": ("swish", -13), "iris": ("iris", -11), "whip": ("whoosh", -11),
             "fade": ("shimmer", -16)}


def build_audio(tl, path, verbose=True):
    n = int(tl.duration * SR) + SR // 2
    Lb = np.zeros(n, np.float32)
    Rb = np.zeros(n, np.float32)
    hits = [0]

    def put(sig, t0, gain_db, pan):
        i0 = int(t0 * SR)
        if i0 >= n:
            return
        if i0 < 0:
            sig = sig[-i0:]
            i0 = 0
        m = min(len(sig), n - i0)
        if m <= 2:
            return
        g = 10.0 ** (gain_db / 20.0)
        ang = (clamp(pan, -1, 1) + 1) * math.pi / 4.0
        Lb[i0:i0 + m] += sig[:m] * g * math.cos(ang)
        Rb[i0:i0 + m] += sig[:m] * g * math.sin(ang)
        hits[0] += 1

    for b in tl.beats:
        if b.var > 0:
            put(get_sfx("swish", 300 + b.i), b.start - 0.03, -27, (-0.25 if b.i % 2 else 0.25))
    for r in tl.runs:
        kind, gain = TRANS_SFX.get(r.kind, ("whoosh", -13))
        put(get_sfx(kind, r.idx), max(0.0, r.start - 0.22), gain, 0.0)
        plan = SFX_PLAN.get(r.scene, [])
        length = r.end - r.start
        for (off, k, g, pan) in plan:
            if off > length + 0.4:
                continue
            if k == "ticks":
                step = 0.075
                t0 = r.start + off
                for j, tt in enumerate(np.arange(t0, min(r.start + length, t0 + 1.1), step)):
                    put(get_sfx("tick", 7 + j), tt, g - j * 0.5, pan)
                continue
            put(get_sfx(k, r.idx * 13 + int(off * 10)), r.start + off, g, pan)
    # ------- continuous space air + sub hum: ambience, never a gap, never music -------
    tgrid = np.arange(n, dtype=np.float32) / SR
    air = _smooth(_rng(99).standard_normal(n), 900) * 7.0
    lfo = 0.55 + 0.45 * np.sin(2 * np.pi * 0.035 * tgrid + 1.1)
    swell = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.017 * tgrid))
    air = air * lfo * swell
    hum = (0.10 + 0.05 * np.sin(2 * np.pi * 0.011 * tgrid)) * np.sin(2 * np.pi * 52.0 * tgrid)
    shim = _smooth(_rng(77).standard_normal(n), 60) * 0.9 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * tgrid + 2.0))
    Lb += (air * 0.20 + hum * 0.28 + shim * 0.09)
    Rb += (air * 0.19 + hum * 0.26 + shim * 0.10)
    # ------- spacey multi-tap ambience (still SFX, not music) ------
    wet = np.zeros(n + SR, np.float32)
    for delay, g, pan in ((0.031, 0.30, -0.5), (0.047, 0.26, 0.5), (0.071, 0.20, -0.3),
                          (0.113, 0.15, 0.35), (0.157, 0.11, -0.2), (0.211, 0.07, 0.2)):
        d = int(delay * SR)
        a = (pan + 1) * math.pi / 4
        wet[d:d + n] += (Lb + Rb) * 0.5 * g
        Lb += np.roll(Lb, d) * g * math.cos(a) * 0.55
        Rb += np.roll(Rb, d) * g * math.sin(a) * 0.55
    Lb += _smooth(wet[:n], 24) * 0.35
    Rb += _smooth(wet[:n], 30) * 0.35
    # ------- master: soft knee compression + -2.2 dBFS ceiling ------
    # (headroom left for the AAC encoder, which overshoots true peak by ~1 dB)
    mix = np.stack([Lb, Rb], 1)
    mix = np.nan_to_num(mix)
    peak = float(np.max(np.abs(mix))) or 1.0
    mix = mix / peak
    mix = np.tanh(mix * 3.2) / math.tanh(3.2)
    # ------- de-click: tame isolated near-Nyquist spikes ---------------
    # A one-sample jump of ~1.0 is what makes the AAC codec overshoot full
    # scale after encoding, so every spike gets a short windowed smoother
    # (2 ms long, ~84 places, inaudible) before the ceiling is applied.
    dj = np.abs(np.diff(mix, axis=0)).max(1)
    spk = np.where(dj > 0.35)[0]
    if len(spk):
        half = int(0.001 * SR)
        ker = np.ones(9, np.float32) / 9.0
        u = np.linspace(-1.0, 1.0, 2 * half)
        win = ((0.5 + 0.5 * np.cos(np.pi * u)) ** 2)[:, None]
        for k in spk:
            lo, hi = max(1, k - half), min(len(mix) - 1, k + half)
            m = min(2 * half, hi - lo)
            if m < 8:
                continue
            seg = mix[lo:hi].copy()
            sm = np.stack([np.convolve(seg[:, c], ker, "same") for c in range(2)], 1)
            mix[lo:hi] = seg * (1 - win[:m]) + sm * win[:m]
    mix *= 10.0 ** (-CEILING_DB / 20.0) / max(1e-9, float(np.max(np.abs(mix))))
    mix = np.clip(mix, -1.0, 1.0)
    pcm = (np.clip(mix, -1, 1) * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    if verbose:
        print("   [sfx] %d hits, %.1fs @ %d Hz stereo -> %s" % (hits[0], tl.duration, SR, os.path.basename(path)))
    return path


# =============================================================================
#  ENCODER  +  PARALLEL RENDER  +  CLI
# =============================================================================
def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        p = shutil.which("ffmpeg")
        if p:
            return p
    raise SystemExit("ffmpeg not found:  pip install imageio-ffmpeg")


PROG = None
CFG = {}


def _setup(cfg, quiet=False):
    global TE, TL
    init_geometry(cfg["ratio"], cfg["scale"])
    lat, dev = resolve_fonts()
    if quiet:
        keep, sys.stdout = sys.stdout, open(os.devnull, "w")
    TE = TextEngine(lat, dev, force_hb=cfg.get("force_hb", False))
    if quiet:
        sys.stdout = keep
    TL = build_timeline(cfg["duration"])


def _worker_init(cfg, prog):
    global PROG
    PROG = prog
    _setup(cfg, quiet=True)


def _render_chunk(job):
    idx, f0, f1, path, cfg = job
    exe = ffmpeg_exe()
    cmd = [exe, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", cfg["preset"], "-crf", str(cfg["crf"]),
           "-pix_fmt", "yuv420p", "-g", str(FPS * 2), "-threads", "1", path]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(f0, f1):
            arr = render_frame(i / float(FPS))
            pr.stdin.write(arr.tobytes())
            if PROG is not None:
                with PROG.get_lock():
                    PROG.value += 1
    finally:
        pr.stdin.close()
        pr.wait()
    return idx, path


def _concat_and_mux(parts, audio, out, dur):
    exe = ffmpeg_exe()
    tmpdir = os.path.dirname(parts[0])
    listf = os.path.join(tmpdir, "list.txt")
    with open(listf, "w") as fh:
        for p in parts:
            fh.write("file '%s'\n" % p.replace("'", "'\\''"))
    cmd = [exe, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listf]
    if audio:
        cmd += ["-i", audio, "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2"]
    else:
        cmd += ["-an"]
    cmd += ["-c:v", "copy", "-movflags", "+faststart", "-shortest", out]
    subprocess.check_call(cmd)


def auto_duration():
    words = len(TRANSCRIPTION.split())
    sents = sum(TRANSCRIPTION.count(c) for c in SENT_END)
    return round(words / WORDS_PER_SEC + 0.22 * sents, 1)


def main():
    ap = argparse.ArgumentParser(description="Kurzgesagt-style procedural explainer: BLACK HOLES (SFX only)")
    ap.add_argument("--ratio", default=None, help="16:9 | 9:16 | 1:1")
    ap.add_argument("--duration", type=float, default=None, help="seconds (default 260 = 4:20)")
    ap.add_argument("--out", default=OUTPUT_FILE)
    ap.add_argument("--stills", default=None, help="comma separated times -> PNG frames, then exit")
    ap.add_argument("--poster", type=float, default=None, help="write poster.png at this time and exit")
    ap.add_argument("--preview", action="store_true", help="half-resolution quick render")
    ap.add_argument("--limit", type=float, default=None, help="render only the first N seconds")
    ap.add_argument("--workers", type=int, default=0, help="render processes (0 = auto)")
    ap.add_argument("--crf", type=int, default=21, help="x264 quality (lower = better)")
    ap.add_argument("--preset", default="veryfast", help="x264 preset")
    ap.add_argument("--force-hb", action="store_true", help="force the HarfBuzz text path")
    ap.add_argument("--no-audio", action="store_true", help="render picture only")
    ap.add_argument("--audio-only", default=None, help="write the SFX bed to this WAV and exit")
    a = ap.parse_args()

    dur = a.duration or VOICEOVER_DURATION or auto_duration()
    cfg = dict(ratio=a.ratio or ASPECT_RATIO, scale=0.5 if a.preview else 1.0, duration=float(dur),
               force_hb=a.force_hb, crf=a.crf, preset=a.preset)
    _setup(cfg)
    print("   canvas %dx%d @ %d fps | %.1fs (%s) | %d words | %d beats / %d runs"
          % (W, H, FPS, TL.duration, "given" if (a.duration or VOICEOVER_DURATION) else "auto",
             len(TRANSCRIPTION.split()), len(TL.beats), len(TL.runs)))
    print_storyboard(TL)

    if a.audio_only:
        build_audio(TL, a.audio_only)
        print("   wrote", os.path.abspath(a.audio_only))
        return

    if a.stills or a.poster is not None:
        times = [float(s) for s in a.stills.split(",")] if a.stills else [a.poster]
        for s in times:
            img = Image.fromarray(render_frame(float(s)))
            fn = "still_%05.2f.png" % float(s)
            img.save(fn)
            print("   wrote", fn)
        return

    out_dur = min(TL.duration, a.limit) if a.limit else TL.duration
    n = int(round(out_dur * FPS))
    workers = a.workers or max(1, min(8, (os.cpu_count() or 2)))
    tmpdir = tempfile.mkdtemp(prefix="kurz_bh_")

    t0 = time.time()
    audio = None
    if not a.no_audio:
        audio = os.path.join(tmpdir, "sfx.wav")
        build_audio(TL, audio)

    bounds = [(int(round(i * n / workers)), int(round((i + 1) * n / workers))) for i in range(workers)]
    jobs = [(i, b0, b1, os.path.join(tmpdir, "part_%02d.mp4" % i), cfg)
            for i, (b0, b1) in enumerate(bounds) if b1 > b0]

    if workers > 1:
        import multiprocessing as mp
        import threading
        ctx = mp.get_context("fork") if hasattr(mp, "get_context") else mp
        prog = ctx.Value("i", 0)
        print("   rendering %d frames with %d processes ..." % (n, len(jobs)))
        pool = ctx.Pool(len(jobs), initializer=_worker_init, initargs=(cfg, prog))
        stop = threading.Event()

        def _watch():
            while not stop.wait(6.0):
                p = prog.value / float(n) * 100.0
                el = time.time() - t0
                eta = (el / max(1e-6, p / 100.0)) - el if p > 0 else 0
                sys.stdout.write("\r   %5.1f%%  |  %d/%d frames  |  %.1f min elapsed  |  eta %.1f min   "
                                 % (p, prog.value, n, el / 60.0, eta / 60.0))
                sys.stdout.flush()

        th = threading.Thread(target=_watch, daemon=True)
        th.start()
        try:
            for _idx, _p in pool.imap_unordered(_render_chunk, jobs):
                pass
        finally:
            stop.set()
            pool.close()
            pool.join()
        print("\r   100.0%%  |  %d/%d frames  |  %.1f min                                    " % (n, n, (time.time() - t0) / 60.0))
    else:
        print("   rendering %d frames in-process ..." % n)
        _render_chunk(jobs[0])

    parts = [j[3] for j in jobs]
    _concat_and_mux(parts, audio, a.out, out_dur)
    for p in parts:
        try:
            os.remove(p)
        except OSError:
            pass
    shutil.rmtree(tmpdir, ignore_errors=True)

    size = os.path.getsize(a.out) / 1e6
    print("\n   done in %.1f min  ->  %s  (%.1f MB, %d frames, %d fps, %s)"
          % ((time.time() - t0) / 60.0, os.path.abspath(a.out), size, n, FPS,
             "SFX audio 48 kHz stereo" if audio else "no audio"))


if __name__ == "__main__":
    main()
