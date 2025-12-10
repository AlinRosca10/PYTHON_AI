import os
import json
import re


def md_to_text(md):
    # elimină titlurile markdown
    text = re.sub(r'#.*', '', md)
    # elimină bold, italic etc.
    text = re.sub(r'[*_`]', '', text)
    # elimină linkuri [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # elimina spații multiple
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def load_lessons_from_md(lessondir="lessons"):
    lessons = {}

    if not os.path.isdir(lessondir):
        return lessons

    for filename in sorted(os.listdir(lessondir)):
        if not filename.endswith(".md"):
            continue

        slug = filename[:-3]
        path = os.path.join(lessondir, filename)

        if not os.path.isfile(path):
            continue

        with open(path, "r", encoding="utf8") as f:
            content = f.read().lstrip("\ufeff")

        lines = content.splitlines()
        if not lines:
            title = slug
        else:
            first = lines[0].strip()
            if first.startswith("# "):
                title = first[2:].strip()
            else:
                title = slug.replace("-", " ").title()

        lessons[slug] = {"title": title, 
                         "md": content,
                         "text": md_to_text(content),
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
            "text": md_to_text(content),
            "path": path,
        }

    return lessons


def generate_summary(text, max_len=200):
    sentences = text.split(". ")
    first = sentences[0].strip()
    if len(first) > max_len:
        return first[:max_len] + "..."
    return first + "."

