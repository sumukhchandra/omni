#!/usr/bin/env python3
"""
Everything-In-Screen: cross-platform automation server.

Drop this file as everything_server.py in the project root.

Security note: This server executes OS inputs; run locally and only on machines you control.
"""
import os, sys, time, json, traceback, subprocess, platform
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import pytesseract

# Optional automation libs
try:
    import pyautogui
except Exception:
    pyautogui = None

ROOT = Path(__file__).resolve().parent
SS = ROOT / "screenshots"
ANN = SS / "annotated"
SS.mkdir(exist_ok=True)
ANN.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=str(ROOT / "ui"))
CORS(app)

# Config
EXECUTE = os.environ.get("EXECUTE", "0") == "1"    # only perform clicks/typing if set
DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"
TESSERACT_CMD = os.environ.get("TESSERACT_CMD", "tesseract")  # allow overriding
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def ts(prefix):
    return f"{prefix}_{int(time.time()*1000)}.png"

def capture():
    # Use platform-specific screenshot if mss missing
    try:
        import mss
        with mss.mss() as s:
            m = s.monitors[1]
            g = s.grab(m)
            return Image.frombytes("RGB", g.size, g.rgb)
    except Exception:
        # fallback: pyautogui.screenshot (works on all OS if pyautogui installed)
        if pyautogui:
            return Image.fromarray(np.array(pyautogui.screenshot()))
        raise

def save(img: Image.Image, name: str):
    p = SS / name
    img.save(str(p))
    return p

def ocr(img: Image.Image):
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    out = []
    for i in range(len(data["text"])):
        t = data["text"][i].strip()
        if not t: continue
        conf_text = data["conf"][i]
        try:
            conf = int(float(conf_text))
        except Exception:
            conf = 0
        out.append({
            "text": t,
            "conf": conf,
            "left": data["left"][i],
            "top": data["top"][i],
            "width": data["width"][i],
            "height": data["height"][i]
        })
    return out

def annotate(img: Image.Image, boxes):
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
    for t, (x, y, w, h) in boxes:
        d.rectangle([x, y, x+w, y+h], outline="red", width=2)
        # measure
        try:
            tx1, ty1, tx2, ty2 = font.getbbox(t)
            tw, th = tx2-tx1, ty2-ty1
        except Exception:
            tw, th = font.getsize(t)
        lx, ly = x, max(0, y-th)
        d.rectangle([lx, ly, lx+tw, ly+th], fill="red")
        d.text((lx, ly), t, fill="white", font=font)
    return img

def platform_open_app(app_name: str):
    plat = platform.system().lower()
    if plat == "darwin":
        # macOS: try open -a "Spotify" or use Spotlight via AppleScript
        try:
            subprocess.run(["open", "-a", app_name], check=False)
            return True
        except Exception:
            return False
    elif plat == "windows":
        # Windows: try start "" "spotify:"
        try:
            # Windows: try shell start to open app by name or protocol
            subprocess.run(["cmd", "/c", "start", "", app_name], shell=False)
            return True
        except Exception:
            return False
    else:
        # linux: try xdg-open or run the app directly
        try:
            subprocess.run(["/usr/bin/xdg-open", app_name], check=False)
            return True
        except Exception:
            try:
                subprocess.Popen([app_name])
                return True
            except Exception:
                return False

def do_click(x, y):
    if DRY_RUN:
        return {"ok": True, "dry": True, "action": "click", "x": x, "y": y}
    if not pyautogui:
        return {"ok": False, "error": "pyautogui not installed"}
    pyautogui.click(x, y)
    return {"ok": True}

def do_type(text):
    if DRY_RUN:
        return {"ok": True, "dry": True, "action": "type", "text": text}
    if not pyautogui:
        return {"ok": False, "error": "pyautogui not installed"}
    pyautogui.write(text, interval=0.05)
    return {"ok": True}

@app.route("/command", methods=["POST"])
def command():
    try:
        j = request.get_json(force=True)
        cmd = (j.get("text","") or "").strip()
        if not cmd:
            return jsonify({"ok": False, "error": "empty command"})

        # Basic commands
        if cmd.lower() == "inspect":
            img = capture()
            raw = ts("raw")
            save(img, raw)
            boxes = ocr(img)
            ann = ts("ann")
            annotate(img.copy(), [(b["text"], (b["left"], b["top"], b["width"], b["height"])) for b in boxes]).save(str(ANN / ann))
            return jsonify({"ok": True, "raw": f"/screenshots/{raw}", "annotated": f"/screenshots/annotated/{ann}", "boxes": boxes})

        if cmd.lower().startswith("click"):
            # expected: click x y
            parts = cmd.split()
            if len(parts) >= 3:
                x = int(parts[1]); y = int(parts[2])
                return jsonify(do_click(x,y))
            return jsonify({"ok": False, "error": "click requires x y"})

        if cmd.lower().startswith("type"):
            # type <value>
            val = cmd.partition(" ")[2]
            return jsonify(do_type(val))

        if cmd.lower().startswith("open "):
            # open <app>
            appname = cmd.partition(" ")[2].strip()
            ok = platform_open_app(appname)
            return jsonify({"ok": True, "action": "open", "app": appname, "executed": ok, "steps": ["platform_open_app"]})

        # example: play_spotify: expect 'play hanuman song in spotify'
        if cmd.lower().startswith("play "):
            # This is a best-effort sequence: open spotify, find search, type, click first result.
            # Very environment dependent. Use EXECUTE=1 only when tested in dry-run.
            result = {"ok": False}
            # open spotify first
            platform_open_app("Spotify")
            time.sleep(1.5)
            try:
                img = capture()
                raw = ts("raw")
                save(img, raw)
                boxes = ocr(img)
                # quick heuristic: find word 'search' or 'Search' bounding box
                search_coords = None
                for b in boxes:
                    if b["text"].lower().startswith("search") or b["text"].lower() == "search":
                        search_coords = (b["left"] + b["width"]//2, b["top"] + b["height"]//2)
                        break
                # fallback center-top click
                if search_coords is None:
                    w,h = img.size
                    search_coords = (w//2, 80)
                if EXECUTE and pyautogui:
                    pyautogui.click(search_coords[0], search_coords[1])
                    time.sleep(0.3)
                    # type the query
                    query = cmd.partition("play ")[2]
                    pyautogui.write(query, interval=0.05)
                    time.sleep(0.2)
                    pyautogui.press("enter")
                    time.sleep(1.0)
                    # screenshot and ocr to find first song line (heuristic)
                    img2 = capture()
                    boxes2 = ocr(img2)
                    # choose a text with confidence and click its center (heuristic: top-most near results area)
                    candidate = None
                    for b in boxes2:
                        t = b["text"].lower()
                        if len(t) > 2 and not t.startswith("http"):
                            candidate = b
                            break
                    if candidate:
                        cx = candidate["left"] + candidate["width"]//2
                        cy = candidate["top"] + candidate["height"]//2
                        pyautogui.click(cx, cy)
                        result = {"ok": True, "action": "play_spotify", "song": query, "final_ocr": boxes2}
                    else:
                        result = {"ok": False, "error": "couldn't find candidate song after search", "ocr": boxes2}
                else:
                    result = {"ok": True, "dry": True, "search_coords": search_coords}
            except Exception as e:
                result = {"ok": False, "error": str(e), "trace": traceback.format_exc()}
            return jsonify(result)

        # fallback unknown
        return jsonify({"ok": False, "error": "unknown command"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "trace": traceback.format_exc()})

@app.route("/screenshots/<path:p>")
def scr(p):
    if p.startswith("annotated/"):
        return send_from_directory(str(ANN), p.split("/",1)[1])
    return send_from_directory(str(SS), p)

@app.route("/ui/<path:f>")
def ui(f):
    return send_from_directory(app.static_folder, f)

@app.route("/ui/")
def ui_root():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    print("SERVER STARTED → http://127.0.0.1:5005 (DRY_RUN=%s EXECUTE=%s)" % (DRY_RUN, EXECUTE))
    app.run(host="0.0.0.0", port=5005, debug=False)
