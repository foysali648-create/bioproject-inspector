"""Small FastAPI web UI for bioproject-inspector (light/dark theme)."""
import html
import re

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from bioproject_inspector.report import build_report

app = FastAPI(title="BioProject Inspector")
ACCESSION = re.compile(r"^PRJ(NA|EB|DB)\d+$")

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BioProject Inspector</title>
<style>
:root { --bg:#f6f8fa; --fg:#1f2328; --card:#ffffff; --muted:#59636e; --line:#d1d9e0;
        --accent:#0969da; --warn:#9a6700; --warnbg:#fff8c5; --info:#0550ae; --infobg:#ddf4ff;
        --err:#cf222e; }
:root[data-theme="dark"] { --bg:#0d1117; --fg:#e6edf3; --card:#161b22; --muted:#8d96a0;
        --line:#30363d; --accent:#4493f8; --warn:#d29922; --warnbg:#3d2e00;
        --info:#79c0ff; --infobg:#0c2d6b; --err:#ff7b72; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg);
       font:16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 860px; margin: 0 auto; padding: 24px 16px 64px; }
header { display:flex; justify-content:space-between; align-items:center; gap:12px; }
h1 { font-size: 1.4rem; margin: 0; }
button, input { font: inherit; }
.toggle { background:var(--card); color:var(--fg); border:1px solid var(--line);
          border-radius:8px; padding:6px 12px; cursor:pointer; }
form { display:flex; gap:8px; margin:20px 0; flex-wrap:wrap; }
input[type=text] { flex:1; min-width:200px; padding:10px 12px; border-radius:8px;
          border:1px solid var(--line); background:var(--card); color:var(--fg); }
input[type=submit] { background:var(--accent); color:#fff; border:0; border-radius:8px;
          padding:10px 18px; cursor:pointer; }
.card { background:var(--card); border:1px solid var(--line); border-radius:12px;
        padding: 8px 20px 16px; overflow-x:auto; }
.card h1 { font-size:1.3rem; } .card h2 { font-size:1.1rem; margin-top:1.4em; }
.card h3 { font-size:1rem; color:var(--muted); }
ul { padding-left: 1.2em; } li { margin: 4px 0; }
.tag { font-size:.75rem; font-weight:600; padding:1px 8px; border-radius:99px; margin-right:6px; }
.warning { background:var(--warnbg); color:var(--warn); }
.info { background:var(--infobg); color:var(--info); }
.error { color:var(--err); font-weight:600; }
.hint { color:var(--muted); }
.brand{display:flex;align-items:center;gap:10px}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:12px 0 0;padding:0;list-style:none}
.steps li{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin:0}
.steps b{display:block}
.steps span{color:var(--muted);font-size:.9rem}
.examples{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.examples a{flex:1;min-width:220px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;color:var(--fg);text-decoration:none}
.examples a:hover{border-color:var(--accent)}
.examples small{display:block;color:var(--muted)}
.sec{font-size:1.1rem;margin:32px 0 0}
footer{margin-top:36px;color:var(--muted);font-size:.85rem}
footer a{color:var(--accent)}
</style>
<script>
(function () {
  var t = null;
  try { t = localStorage.getItem("theme"); } catch (e) {}
  if (!t) t = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", t);
})();
function toggleTheme() {
  var r = document.documentElement;
  var t = r.getAttribute("data-theme") === "dark" ? "light" : "dark";
  r.setAttribute("data-theme", t);
  try { localStorage.setItem("theme", t); } catch (e) {}
}
</script>
</head>
<body>
<main>
<header>
  <div class="brand"><svg width="34" height="34" viewBox="0 0 32 32" fill="none" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M9 3c0 8 14 8 14 13s-14 5-14 13" stroke="var(--accent)"/><path d="M23 3c0 8-14 8-14 13s14 5 14 13" stroke="var(--muted)"/><path d="M11 8h10M11 24h10M9.5 16h13" stroke="var(--line)"/></svg><h1>BioProject Inspector</h1></div>
  <button class="toggle" onclick="toggleTheme()" type="button">Light / Dark</button>
</header>
<form action="/report" method="get">
  <input type="text" name="accession" placeholder="PRJNA633959" value="__VALUE__"
         required pattern="PRJ(NA|EB|DB)[0-9]+" autocomplete="off" spellcheck="false">
  <input type="submit" value="Inspect">
</form>
__BODY__
<h2 class="sec">How it works</h2>
<ul class="steps">
  <li><b>&#128269; 1. Accession</b><span>Enter a BioProject ID such as PRJNA633959.</span></li>
  <li><b>&#128225; 2. ENA metadata</b><span>Run details are read from ENA. Nothing is downloaded.</span></li>
  <li><b>&#9989; 3. Checks</b><span>Data type, warnings and a QC checklist.</span></li>
  <li><b>&#128229; 4. Script</b><span>Use the CLI to get a disk-aware download script.</span></li>
</ul>
<h2 class="sec">Try an example</h2>
<div class="examples">
  <a href="/report?accession=PRJNA633959"><b>PRJNA633959</b><small>Amplicon (16S) example</small></a>
  <a href="/report?accession=PRJNA679346"><b>PRJNA679346</b><small>Shotgun metagenome example</small></a>
</div>
<footer>
  Unofficial community tool, not affiliated with NCBI or EMBL-EBI.
  <a href="https://github.com/foysali648-create/bioproject-inspector">GitHub</a> &middot;
  <a href="https://doi.org/10.5281/zenodo.24611635">DOI</a> &middot; MIT license
</footer>
</main>
</body>
</html>
"""


def _inline(text):
    text = html.escape(text)
    text = re.sub(r"\[(WARNING|INFO)\]",
                  lambda m: '<span class="tag %s">%s</span>' % (m.group(1).lower(), m.group(1)),
                  text)
    return text


def render_markdown(md):
    """Tiny renderer for the report's markdown (headings, bullets, paragraphs)."""
    out, in_list = [], False
    for line in md.splitlines():
        if line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>%s</li>" % _inline(line[2:]))
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        m = re.match(r"^(#{1,3}) (.*)$", line)
        if m:
            n = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (n, _inline(m.group(2)), n))
        elif line.strip():
            out.append("<p>%s</p>" % _inline(line))
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def _page(body, value=""):
    return PAGE.replace("__BODY__", body).replace("__VALUE__", html.escape(value, quote=True))


@app.get("/", response_class=HTMLResponse)
def home():
    return _page('<p class="hint">Enter a BioProject accession (PRJNA..., PRJEB..., PRJDB...). '
                 'This tool only reads metadata from ENA; it downloads nothing.</p>')


@app.get("/report", response_class=HTMLResponse)
def report(accession: str = ""):
    acc = accession.strip().upper()
    if not ACCESSION.match(acc):
        return HTMLResponse(_page('<p class="error">Please enter a valid accession such as PRJNA633959.</p>', acc),
                            status_code=400)
    try:
        md = build_report(acc)
    except Exception as exc:  # network error, unknown accession, ...
        return HTMLResponse(_page('<p class="error">Could not build report: %s</p>' % html.escape(str(exc)), acc),
                            status_code=502)
    return _page('<div class="card">%s</div>' % render_markdown(md), acc)


@app.get("/api/report/{accession}")
def api_report(accession: str):
    acc = accession.strip().upper()
    if not ACCESSION.match(acc):
        return JSONResponse({"error": "invalid accession"}, status_code=400)
    try:
        return {"accession": acc, "markdown": build_report(acc)}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=502)
