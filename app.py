import os
import time
import threading
from pathlib import Path

from flask import (
    Flask, Response, stream_with_context,
    render_template_string, abort, url_for
)
import markdown2

from lesson_loader import load_lessons_from_md, load_lessons_json

# ============================================================== #
# CONFIG
# ============================================================== #

LESSONS_DIR = Path("lessons")
GENERATED_JSON = Path("generated_lessons.json")

# Livereload state
_last_mtime = 0
_reload_flag = False

# JSON cache
LESSONS = {}
LESSONS_MTIME = 0

app = Flask(__name__)


# ============================================================== #
# DATA LOADING (OPTIMIZED)
# ============================================================== #

def load_lessons_dynamic(path=GENERATED_JSON):
    """Load lessons from JSON only when timestamp changes (cache)."""
    global LESSONS, LESSONS_MTIME

    try:
        mtime = os.path.getmtime(path)
    except FileNotFoundError:
        LESSONS = {}
        LESSONS_MTIME = 0
        return LESSONS

    if mtime == LESSONS_MTIME:
        return LESSONS  # return cached version

    # reload JSON
    LESSONS = load_lessons_json(path)
    LESSONS_MTIME = mtime
    print(f"[INFO] Reloaded JSON lessons ({len(LESSONS)})")

    return LESSONS


def get_lessons():
    """Unified entry point — use JSON if exists, fallback to direct MD parsing."""
    if GENERATED_JSON.exists():
        return load_lessons_dynamic(GENERATED_JSON)
    return load_lessons_from_md(LESSONS_DIR)


# ============================================================== #
# WATCH FOR CHANGES (OPTIMIZED)
# ============================================================== #

def watch_lessons_folder():
    """Monitor .md changes and trigger livereload."""
    global _last_mtime, _reload_flag

    debounce = 0.3
    last_trigger = 0

    while True:
        latest = 0

        for f in LESSONS_DIR.rglob("*.md"):
            m = f.stat().st_mtime
            if m > latest:
                latest = m

        if latest > _last_mtime:
            now = time.time()
            if now - last_trigger > debounce:
                _reload_flag = True
                last_trigger = now

            _last_mtime = latest

        time.sleep(0.3)


threading.Thread(target=watch_lessons_folder, daemon=True).start()


# ============================================================== #
# METADATA INDEXING
# ============================================================== #

def build_metadata_index(lessons):
    categories = {}
    tags = {}

    for slug, data in lessons.items():
        meta = data.get("meta", {})
        cat = meta.get("category")

        if cat:
            categories.setdefault(cat, []).append(slug)

        for tag in meta.get("tags", []):
            tags.setdefault(tag, []).append(slug)

    return categories, tags


# ============================================================== #
# HTML TEMPLATE
# ============================================================== #

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{{ title }}</title>
  <style>
    :root{--bg:#fbfcfd;--card:#ffffff;--muted:#6b7280;--accent:#2563eb}
    body{font-family: Inter, ui-sans-serif, system-ui; background:var(--bg); color:#0f172a;
    margin:0; padding:2rem}
    .container{max-width:880px;margin:0 auto}
    header{display:flex;align-items:center;gap:16px;margin-bottom:1.5rem}
    .logo{width:56px;height:56px;border-radius:8px;background:linear-gradient(135deg,var(--accent),#06b6d4);
    display:flex;align-items:center;justify-content:center;color:white;font-weight:700}
    h1{font-size:1.5rem;margin:0}
    nav a{color:var(--muted);text-decoration:none;margin-right:1rem}
    main{background:var(--card);padding:2rem;border-radius:12px;box-shadow:0 6px 18px rgba(2,6,23,0.06)}
    .meta{color:var(--muted);font-size:0.95rem;margin-bottom:1rem}
    pre{background:#0b1220;color:#e6eef8;padding:1rem;border-radius:8px;overflow:auto}
    code{font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New"}
    .lesson-list{display:flex;flex-direction:column;gap:0.6rem}
    .lesson-item{padding:0.8rem;border-radius:8px;border:1px solid #eef2ff}
    a.button{display:inline-block;padding:0.5rem 0.9rem;border-radius:8px;background:var(--accent);color:white;text-decoration:none}
    footer{margin-top:1.5rem;color:var(--muted);font-size:0.9rem}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo">CALM</div>
      <div>
        <h1>Calm-Style Lessons</h1>
        <div class="meta">Lecții scurte. Clar. Calm. Coerent. Corelat. Relaxat. Degajat</div>
      </div>
      <nav style="margin-left:auto">
        <a href="{{ url_for('index') }}">Home</a>
        <a href="{{ url_for('about') }}">About</a>
      </nav>
    </header>

    <div style="display:flex; gap:2rem;">
  
      <aside style="width:220px;">
        <h3>Categorii</h3>
        <ul>
          {% for cat in categories %}
            <li><a href="{{ url_for('category_page', category=cat) }}">{{ cat }}</a></li>
          {% endfor %}
        </ul>

        <h3>Tag-uri</h3>
        <ul>
          {% for tag in tags %}
            <li><a href="{{ url_for('tag_page', tag=tag) }}">#{{ tag }}</a></li>
          {% endfor %}
        </ul>
      </aside>

      <main style="flex:1; background:var(--card); padding:2rem; border-radius:12px;">
        {{ content|safe }}
      </main>

</div>

    <footer>
      <p>© 2025 — stil inspirat de 
        <a href="https://calmcode.io" target="_blank">calmcode.io</a>
      </p>
    </footer>
  </div>
  <script>
const evtSource = new EventSource("/livereload");
evtSource.onmessage = function(e) {
    if (e.data === "reload") {
        console.log("🔄 Live reload triggered");
        location.reload();
    }
};
</script>
</body>
</html>
"""

# ============================================================== #
# ROUTES
# ============================================================== #

@app.route('/')
def index():
    lessons = get_lessons()
    categories, tags = build_metadata_index(lessons)

    items = sorted((slug, d['title']) for slug, d in lessons.items())

    html = "<h2>Lecții</h2><div class='lesson-list'>"
    html += "".join(
        f'<a class="lesson-item" href="{url_for("lesson", slug=slug)}">'
        f'<strong>{title}</strong></a>'
        for slug, title in items
    )
    html += "</div>"

    return render_template_string(
        BASE_TEMPLATE,
        title="Home",
        content=html,
        categories=categories.keys(),
        tags=tags.keys()
    )


@app.route('/category/<category>')
def category_page(category):
    lessons = get_lessons()
    categories, tags = build_metadata_index(lessons)

    slugs = categories.get(category)
    if not slugs:
        abort(404)

    html = f"<h2>Categorie: {category}</h2><div class='lesson-list'>"
    html += "".join(
        f'<a class="lesson-item" href="{url_for("lesson", slug=s)}">'
        f'<strong>{lessons[s]["title"]}</strong></a>'
        for s in slugs
    )
    html += "</div>"

    return render_template_string(
        BASE_TEMPLATE,
        title=f"Categorie: {category}",
        content=html,
        categories=categories.keys(),
        tags=tags.keys()
    )


@app.route('/tag/<tag>')
def tag_page(tag):
    lessons = get_lessons()
    categories, tags = build_metadata_index(lessons)

    slugs = tags.get(tag)
    if not slugs:
        abort(404)

    html = f"<h2>Tag: #{tag}</h2><div class='lesson-list'>"
    html += "".join(
        f'<a class="lesson-item" href="{url_for("lesson", slug=s)}">'
        f'<strong>{lessons[s]["title"]}</strong></a>'
        for s in slugs
    )
    html += "</div>"

    return render_template_string(
        BASE_TEMPLATE,
        title=f"Tag: {tag}",
        content=html,
        categories=categories.keys(),
        tags=tags.keys()
    )


@app.route('/lesson/<slug>')
def lesson(slug):
    lessons = get_lessons()
    categories, tags = build_metadata_index(lessons)

    data = lessons.get(slug)
    if not data:
        abort(404)

    html = markdown2.markdown(
        data['md'],
        extras=["fenced-code-blocks", "tables"]
    )

    tag_buttons = " ".join(
        f'<a href="/tag/{t}" class="button">#{t}</a>'
        for t in data['meta'].get('tags', [])
    )

    content = f"""
    <article>
        <h2>{data['title']}</h2>
        <div class="meta">Categorie: {data['meta'].get('category', '—')}</div>
        <div>{html}</div>
        <p>{tag_buttons}</p>
        <p><a href="/" class="button">Înapoi</a></p>
    </article>
    """

    return render_template_string(
        BASE_TEMPLATE,
        title=data['title'],
        content=content,
        categories=categories.keys(),
        tags=tags.keys()
    )


# ============================================================== #
# LIVE RELOAD
# ============================================================== #

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


# ============================================================== #
# ABOUT
# ============================================================== #

@app.route('/about')
def about():
    return render_template_string(
        BASE_TEMPLATE,
        title="About",
        content="""
<h2>Despre</h2>
<p>Site minimal pentru lecții scurte, inspirat de calmcode.io.</p>
<h3>Cum contribui</h3>
<p>Adaugă fișiere markdown în directorul <code>lessons/</code>.</p>
"""
    )


# ============================================================== #
# MAIN
# ============================================================== #

if __name__ == '__main__':
    app.run(debug=True)