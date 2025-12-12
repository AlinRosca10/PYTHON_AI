import os
import json
import time
import re
import hashlib
import random
from pathlib import Path
from colorsys import hsv_to_rgb
from openai import OpenAI


# ------------------------------
# INIT CLIENT
# ------------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
assert client, "Nu s-a putut inițializa clientul OpenAI"


# ------------------------------
# SUMMARY AI
# ------------------------------
def generate_summary_ai(text: str, max_len=120):
    prompt = f"""
    Rezumă următorul text în maximum {max_len} de caractere.
    Stil calm, clar, concis. Fără markdown, fără listă.

    Text:
    {text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("[WARN] AI summary failed:", e)
        return fallback_summary(text, max_len)


def fallback_summary(text, max_len=120):
    clean = text.replace("\n", " ").strip()
    return clean[:max_len].rsplit(" ", 1)[0] + "..." if len(clean) > max_len else clean


# ------------------------------
# PALETTE AI
# ------------------------------
CACHE_PATH = Path("ai_palette_cache.json")

try:
    _CACHE = json.loads(CACHE_PATH.read_text(encoding="utf8"))
except:
    _CACHE = {}


def _save_cache():
    try:
        CACHE_PATH.write_text(json.dumps(_CACHE, ensure_ascii=False, indent=2), encoding="utf8")
    except Exception as e:
        print("[WARN] Cannot write cache:", e)


def _format_colors_from_model(content: str):
    # încearcă json direct
    try:
        j = json.loads(content)
        if isinstance(j, dict) and "colors" in j:
            return j["colors"]
        if isinstance(j, list) and len(j) >= 4:
            return j[:4]
    except:
        pass

    # regex HEX
    hexes = re.findall(r'#(?:[0-9a-fA-F]{6})', content)
    if len(hexes) >= 4:
        return hexes[:4]

    return None


def generate_palette_ai(prompt: str, style_hint: str = "", max_tokens: int = 200):
    """
    generator AI cu cache 24h
    """
    key = f"{prompt}|{style_hint}"
    if key in _CACHE and (time.time() - _CACHE[key]["_ts"] < 86400):
        return _CACHE[key]["data"]

    system = (
        "You are a helpful design assistant. "
        "Return ONLY JSON with: "
        "{\"colors\": [\"#xxxxxx\", ... x4], \"caption\": \"...\"}"
    )

    user = (
        f"Generate a UI color palette.\n\n"
        f"Description: {prompt}\n"
    )
    if style_hint:
        user += f"Style hint: {style_hint}\n"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=0.45,
        )

        content = response.choices[0].message.content.strip()

        colors = _format_colors_from_model(content)
        if not colors:
            colors = _fallback_palette(prompt)

        # caption
        caption = None
        try:
            j = json.loads(content)
            caption = j.get("caption")
        except:
            pass

        data = {
            "colors": colors[:4],
            "caption": caption or "AI generated palette",
            "raw": content,
            "source": "openai"
        }

        _CACHE[key] = {"_ts": time.time(), "data": data}
        _save_cache()

        return data

    except Exception as e:
        print("[ERROR] Palette AI failed:", e)
        data = {
            "colors": _fallback_palette(prompt),
            "caption": "Generated locally (fallback)",
            "raw": str(e),
            "source": "fallback"
        }
        _CACHE[key] = {"_ts": time.time(), "data": data}
        _save_cache()
        return data


# ------------------------------
# FALLBACK LOCAL PALETTE
# ------------------------------
def _fallback_palette(seed: str):
    h = hashlib.sha1(seed.encode("utf8")).hexdigest()
    rnd = random.Random(int(h[:8], 16))

    def rnd_color():
        h = rnd.randint(0, 360)
        s = rnd.uniform(0.45, 0.85)
        v = rnd.uniform(0.55, 0.95)
        r, g, b = hsv_to_rgb(h/360, s, v)
        return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

    return [rnd_color() for _ in range(4)]