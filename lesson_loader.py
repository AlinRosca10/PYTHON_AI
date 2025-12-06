import os
import json

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

        lessons[slug] = {"title": title, "md": content}

    return lessons


def load_lessons_json(path="generated_lessons.json"):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)