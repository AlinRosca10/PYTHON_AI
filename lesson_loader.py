import os
import json
import yaml


def parse_markdown_with_front_matter(path):
    """
    Încărcă un fișier .md și extrage:
    - front matter YAML (dacă există între blocuri ---)
    - conținutul markdown curat
    """

    with open(path, "r", encoding="utf8") as f:
        raw = f.read().lstrip("\ufeff")  # elimină BOM dacă apare

    front = {}
    content = raw

    # Detectare front-matter
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            _, yml, body = parts
            try:
                front = yaml.safe_load(yml) or {}
            except Exception:
                front = {}
            content = body.lstrip("\n")

    return front, content


def extract_title(front, md, fallback_slug):
    """
    Determină titlul lecției:
    1. din front-matter dacă există
    2. altfel din primul heading "# ..."
    3. altfel din numele fișierului
    """
    if "title" in front:
        return front["title"]

    lines = md.splitlines()
    if lines and lines[0].startswith("# "):
        return lines[0][2:].strip()

    return fallback_slug.replace("-", " ").title()


def load_lessons_from_md(lessondir="lessons"):
    """
    Încarcă toate lecțiile .md cu front-matter YAML.
    Returnează dict: {slug: {title, md, meta, path}}
    """
    lessons = {}

    if not os.path.isdir(lessondir):
        return lessons

    for filename in sorted(os.listdir(lessondir)):
        if not filename.endswith(".md"):
            continue

        slug = filename[:-3]
        path = os.path.join(lessondir, filename)

        front, md = parse_markdown_with_front_matter(path)
        title = extract_title(front, md, slug)

        lessons[slug] = {
            "slug": slug,
            "title": title,
            "md": md,
            "meta": front,
            "path": path,
        }

    return lessons


def save_lessons_json(lessons, output="generated_lessons.json"):
    """
    Salvează lecțiile într-un JSON frumos formatat.
    """
    with open(output, "w", encoding="utf8") as f:
        json.dump(lessons, f, indent=2, ensure_ascii=False)


def load_lessons_json(path="generated_lessons.json"):
    """
    Încarcă JSON-ul generat. Dacă nu există → întoarce dict gol.
    """
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)