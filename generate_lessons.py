import json
from lesson_loader import load_lessons_from_md

OUTPUT = "generated_lessons.json"

if __name__ == "__main__":
    lessons = load_lessons_from_md("lessons")
    with open(OUTPUT, "w", encoding="utf8") as f:
        json.dump(lessons, f, indent=2, ensure_ascii=False)
    print(f"Generat {OUTPUT} cu {len(lessons)} lecții.")