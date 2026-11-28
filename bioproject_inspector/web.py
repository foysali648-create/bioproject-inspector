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
#intro{position:fixed;inset:0;z-index:99;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;background:var(--bg);cursor:pointer;transition:opacity .5s;text-align:center;padding:16px}
#intro.hide{opacity:0;pointer-events:none}
#intro h2{margin:0;font-size:1.6rem}
#intro p{margin:0;color:var(--muted)}
.stage{display:flex;gap:28px;align-items:flex-end;justify-content:center;flex-wrap:wrap;margin:18px 0 8px}
.mate{display:flex;flex-direction:column;align-items:center;animation:bob 2.4s ease-in-out infinite}
.mate.b{animation-delay:-1.1s}
.bubble{background:var(--card);border:2px solid var(--line);border-radius:14px;padding:6px 12px;font-size:.9rem;margin-bottom:8px;animation:pop .5s ease-out both}
.mate.b .bubble{animation-delay:.9s}
.wag{transform-box:fill-box;transform-origin:right center;animation:wag .6s ease-in-out infinite}
.spin{transform-box:fill-box;transform-origin:center;animation:spin 10s linear infinite}
.pupil{transform-box:fill-box;transform-origin:center;animation:blink 3s infinite}
.skip{font-size:.8rem;color:var(--muted)}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}
@keyframes wag{0%,100%{transform:rotate(-16deg)}50%{transform:rotate(16deg)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes blink{0%,92%,100%{transform:scaleY(1)}96%{transform:scaleY(.1)}}
@keyframes pop{0%{opacity:0;transform:scale(.6)}100%{opacity:1;transform:scale(1)}}
@media (prefers-reduced-motion:reduce){#intro *{animation:none!important}}
.sig{margin-top:8px;font-size:1.05rem;font-style:italic;opacity:.9;font-family:"Brush Script MT","Segoe Script",cursive}
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
<div id="intro"><h2>BioProject Inspector</h2><p>Meet the microbes who check your metadata first!</p><div class="stage"><div class="mate"><div class="bubble">Check my metadata first!</div><svg viewBox="-8 0 210 120" width="210" height="120" aria-hidden="true"><g class="wag"><path d="M32 60 C20 42 10 78 -2 58" fill="none" stroke="#1f7a4d" stroke-width="4" stroke-linecap="round"/></g><rect x="30" y="28" width="130" height="64" rx="32" fill="#7ee8a6" stroke="#1f7a4d" stroke-width="4"/><circle cx="62" cy="76" r="5" fill="#a8f3c4"/><circle cx="138" cy="44" r="5" fill="#a8f3c4"/><circle cx="125" cy="78" r="4" fill="#a8f3c4"/><circle cx="82" cy="56" r="11" fill="#fff" stroke="#1f7a4d" stroke-width="2"/><circle cx="112" cy="56" r="11" fill="#fff" stroke="#1f7a4d" stroke-width="2"/><circle class="pupil" cx="84" cy="58" r="5" fill="#173b2a"/><circle class="pupil" cx="114" cy="58" r="5" fill="#173b2a"/><path d="M84 74 Q97 88 110 74" fill="none" stroke="#173b2a" stroke-width="3.5" stroke-linecap="round"/></svg></div><div class="mate b"><div class="bubble">Do not download me blindly!</div><svg viewBox="0 0 140 140" width="140" height="140" aria-hidden="true"><g class="spin" stroke="#5b3fb3" stroke-width="4" fill="#c4b5fd"><line x1="100.0" y1="70.0" x2="120.0" y2="70.0"/><circle cx="120.0" cy="70.0" r="6"/><line x1="91.2" y1="91.2" x2="105.4" y2="105.4"/><circle cx="105.4" cy="105.4" r="6"/><line x1="70.0" y1="100.0" x2="70.0" y2="120.0"/><circle cx="70.0" cy="120.0" r="6"/><line x1="48.8" y1="91.2" x2="34.6" y2="105.4"/><circle cx="34.6" cy="105.4" r="6"/><line x1="40.0" y1="70.0" x2="20.0" y2="70.0"/><circle cx="20.0" cy="70.0" r="6"/><line x1="48.8" y1="48.8" x2="34.6" y2="34.6"/><circle cx="34.6" cy="34.6" r="6"/><line x1="70.0" y1="40.0" x2="70.0" y2="20.0"/><circle cx="70.0" cy="20.0" r="6"/><line x1="91.2" y1="48.8" x2="105.4" y2="34.6"/><circle cx="105.4" cy="34.6" r="6"/></g><circle cx="70" cy="70" r="32" fill="#c4b5fd" stroke="#5b3fb3" stroke-width="4"/><circle cx="59" cy="64" r="9" fill="#fff" stroke="#5b3fb3" stroke-width="2"/><circle cx="82" cy="64" r="9" fill="#fff" stroke="#5b3fb3" stroke-width="2"/><circle class="pupil" cx="61" cy="66" r="4" fill="#2b1b5e"/><circle class="pupil" cx="84" cy="66" r="4" fill="#2b1b5e"/><path d="M58 80 Q70 92 82 80" fill="none" stroke="#2b1b5e" stroke-width="3.5" stroke-linecap="round"/></svg></div></div><span class="skip">Click anywhere to skip</span></div>
<script>(function(){var o=document.getElementById("intro");if(!o)return;var seen=false;try{seen=sessionStorage.getItem("introSeen")==="1";}catch(e){}if(seen){o.remove();return;}function close(){o.classList.add("hide");setTimeout(function(){if(o.parentNode)o.remove();},500);try{sessionStorage.setItem("introSeen","1");}catch(e){}}o.addEventListener("click",close);setTimeout(close,4500);})();</script>
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
  <div class="sig">Foysal &amp; Mumu</div>
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
