import os
import json
import yaml

def parse_markdown_with_front_matter(path):
    """
    Încărcă un fișier .md și extrage:
    - front matter YAML (dacă există)
    - contentul markdown
    """

    with open(path, "r", encoding="utf8") as f:
        raw = f.read().lstrip("\ufeff")  # elimină BOM

    front = {}
    content = raw

    # detectare front matter
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


def load_lessons_from_md(lessondir="lessons"):
    lessons = {}

    if not os.path.isdir(lessondir):
        return lessons

    for filename in sorted(os.listdir(lessondir)):
        if not filename.endswith(".md"):
            continue

        slug = filename[:-3]
        path = os.path.join(lessondir, filename)
        
        front, md = parse_markdown_with_front_matter(path)

         # titlu fallback
        title = front.get("title")

        if not title:
            # dacă nu e în YAML → caută primul heading
            lines = md.splitlines()
            if lines and lines[0].startswith("# "):
                title = lines[0][2:].strip()
            else:
                title = slug.replace("-", " ").title()

        # metadata completă
        lessons[slug] = {
            "slug": slug,
            "title": title,
            "md": md,
            "meta": front,    # păstrăm TOT YAML-ul
            "path": path
        }

    return lessons


def load_lessons_json(path="generated_lessons.json"):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)
    
def load_lessons_live(lessondir="lessons"):
    lessons = {}
    if not os.path.isdir(lessondir):
        return lessons

    for filename in sorted(os.listdir(lessondir)):
        if not filename.endswith(".md"):
            continue

        slug = filename[:-3]
        path = os.path.join(lessondir, filename)

        with open(path, "r", encoding="utf8") as f:
            content = f.read().lstrip("\ufeff")

        lines = content.splitlines()
        if lines and lines[0].startswith("# "):
            title = lines[0][2:].strip()
        else:
            title = slug.replace("-", " ").title()

        lessons[slug] = {
            "title": title,
            "md": content,
            "path": path,
        }

    return lessons

def save_lessons_json(lessons, output="generated_lessons.json"):
    with open(output, "w", encoding="utf8") as f:
        json.dump(lessons, f, indent=2, ensure_ascii=False)