import os
import time
from flask import Flask, render_template_string, abort, url_for
import markdown2
import json

from lesson_loader import load_lessons_json

app = Flask(__name__)

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

BASE_TEMPLATE = """
<!Doctype html>
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
      <div class="logo">C</div>
      <div>
        <h1>Calm-style Lessons</h1>
        <div class="meta">Lecții scurte. Clar. Calm.</div>
      </div>
      <nav style="margin-left:auto">
        <a href="{{ url_for('index') }}">Home</a>
        <a href="{{ url_for('about') }}">About</a>
      </nav>
    </header>

    <main>
      {{ content|safe }}
    </main>

    <footer>
      © Exemple — stil inspirat de calmcode.io
    </footer>
  </div>
</body>
</html>
"""

@app.route('/')
def index():
    LESSONS = load_lessons_dynamic()
    items = [(slug, data['title']) for slug, data in LESSONS.items()]
    items.sort()
    list_html = ['<div class="lesson-list">']
    for slug, title in items:
        href = url_for('lesson', slug=slug)
        list_html.append(f'<a class="lesson-item" href="{href}"><strong>{title}</strong></a>')
    list_html.append('</div>')
    content = '<h2>Lecții</h2>' + ' '.join(list_html)
    return render_template_string(BASE_TEMPLATE, title="Home", content=content)

@app.route('/lesson/<slug>')
def lesson(slug):
    LESSONS = load_lessons_dynamic()
    data = LESSONS.get(slug)
    if not data:
        abort(404)
    html = markdown2.markdown(data['md'], extras=["fenced-code-blocks", "tables"])
    content = f"""
    <article>
        <h2>{data['title']}</h2>
        <div class="meta">Lecție scurtă</div>
        <div>{html}</div>
        <p><a href="{url_for('index')}" class="button">Înapoi</a></p>
    </article>"""
    return render_template_string(BASE_TEMPLATE, title=data["title"], content=content)

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
""")

if __name__ == '__main__':
    app.run(debug=True)