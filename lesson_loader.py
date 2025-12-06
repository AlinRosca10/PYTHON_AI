
import os
import json

def load_lessons_from_md(lessondir="lessons"):
    lessons = {}
    for filename in os.listdir(lessondir):
        if filename.endswith(".md"):
            slug = filename[:-3]
            path = os.path.join(lessondir, filename)
            with open(path, "r", encoding="utf8") as f:
                content = f.read()

            # Prima linie este titlul (# titlu)
            first_line = content.splitlines()[0]
            title = first_line.replace("#", "").strip()

            lessons[slug] = {"title": title, "md": content}
    return lessons

def load_lessons_json(path="generated_lessons.json"):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)