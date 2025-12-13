import os
import time
import threading
from flask import Response, stream_with_context, Flask, render_template, abort, url_for
import markdown2
import json


# Adaugare monitor global
LESSONS_DIR = "lessons"
_last_mtime = 0
_reload_flag = False

from lesson_loader import load_lessons_live, generate_summary
from ai_utils import generate_summary_ai
from api_bp import bp as api_bp


def get_lessons():
    return load_lessons_live("lessons")


app = Flask(__name__)
app.register_blueprint(api_bp)


def watch_lessons_folder():
    global _last_mtime, _reload_flag

    while True:
        latest = 0
        for root, dirs, files in os.walk(LESSONS_DIR):
            for f in files:
                if f.endswith(".md"):
                    path = os.path.join(root, f)
                    m = os.path.getmtime(path)
                    if m > latest:
                        latest = m

        if latest > _last_mtime:
            _reload_flag = True
            _last_mtime = latest

        time.sleep(0.5)


threading.Thread(target=watch_lessons_folder, daemon=True).start()

# Încarcă lecțiile generate din JSON 
# Reîncărcare automată făra restart în Flask
LESSONS = {}
LESSONS_MTIME = 0   # timestamp last load


def load_lessons_dynamic(path="generated_lessons.json"):
    global LESSONS, LESSONS_MTIME

    try:
        mtime = os.path.getmtime(path)
    except FileNotFoundError:
        LESSONS = {}
        LESSONS_MTIME = 0
        return LESSONS

    # dacă fișierul nu s-a modificat → folosește cache
    if mtime == LESSONS_MTIME:
        return LESSONS

    # dacă fișierul S-A modificat → reîncarcă
    LESSONS = load_lessons_json(path)
    LESSONS_MTIME = mtime
    print(f"[INFO] Reloaded lessons ({len(LESSONS)})")
    return LESSONS


@app.route('/')
def index():
    LESSONS = get_lessons()
    items = [(slug, data['title']) for slug, data in LESSONS.items()]
    items.sort()
    list_html = ['<div class="lesson-list">']
    for slug, title in items:
        href = url_for('lesson', slug=slug)
        list_html.append(f'<a class="lesson-item" href="{href}"><strong>{title}</strong></a>')
    list_html.append('</div>')
    content = '<h2>Lecții</h2>' + ' '.join(list_html)
    return render_template("index.html", title="Home", lessons=items, content=content)


@app.route('/lesson/<slug>')
def lesson(slug):
    LESSONS = get_lessons()
    data = LESSONS.get(slug)
    if not data:
        abort(404)
    html = markdown2.markdown(data['md'], extras=["fenced-code-blocks", "tables"])
    summary = generate_summary(data['text'])
    summary_ai = generate_summary_ai(data['text'])
    return render_template(
        "lesson.html", 
        title=data["title"],
        summary=summary,
        summary_ai=summary_ai,
        html=html)


@app.route("/livereload")
def livereload():
    @stream_with_context
    def event_stream():
        global _reload_flag
        while True:
            if _reload_flag:
                _reload_flag = False
                yield "data: reload\n\n"
            else:
                yield "data: ping\n\n"
            time.sleep(1)
    return Response(event_stream(), mimetype="text/event-stream")


@app.route('/about')
def about():
    return render_template(
        "pages/about.html",
        title="About"
    )
    
    
@app.route('/blog')
def blog():
    return render_template(
        "pages/blog.html",
        title="Blog"
    )
    
    
@app.route('/faq')
def faq():
    return render_template(
        "pages/faq.html",
        title="FAQ"
    )

@app.route('/contact')
def contact():
    return render_template(
        "pages/contact.html",
        title="Contact"
    )


@app.route('/services')
def services():
    return render_template(
        "pages/services.html",
        title="Services"
    )

if __name__ == '__main__':
    app.run(debug=True)