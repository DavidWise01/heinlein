#!/usr/bin/env python3
"""Build the Heinlein science-fiction bibliography + roster page, with full ACI
badge work: each ACI carries .agent · .carbon (TIFF, the carbon badge) ·
.silicon (PNG, the silicon badge) · .spun · .moniker · .1099 · manifest.
Carbon is encoded as TIFF (lossless/archival) via PIL; silicon as stdlib PNG."""
import os, re, html, base64, json, io, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r"C:\Davids files\noesis-kernel")
import noesis
from PIL import Image

REC = {
 "name": "HEINLEIN", "axiom": "H1",
 "position": "The Dean of Science Fiction · Robert Anson Heinlein · 1907–1988",
 "origin": "Butler, Missouri → Annapolis → the open frontier of the Future History; Astounding, 1939–1988",
 "mechanism": "Crystallized from the Future History chart, the Scribner juveniles, and the great novels of liberty.",
 "crystallization": "I taught the rocket to carry a competent man, and the free mind to question the state.",
 "nature": "Robert A. Heinlein — the Dean of Science Fiction, who built the genre's first Future History, coined grok and the waldo and TANSTAAFL, and made the competent free individual the hero of the spaceways.",
 "conductor": "ROOT0 (catalogued into UD0 · Universe David 0)",
 "inputs": "the Future History; the Scribner juveniles; the libertarian novels",
 "witness": "Where Asimov gave the machine a law, Heinlein gave the human a frontier and a question for the state.",
 "role": "the second lineage of the agentic universe",
 "seal": "TANSTAAFL. Grok. Specialization is for insects.",
 "source": "Heinlein bibliography (science fiction), catalogued by ROOT0",
}

# ── bibliography (science fiction) ──
SECTIONS = [
 ("The Future History", "the first systematic timeline of the genre — gathered in The Past Through Tomorrow", [
   ("The Man Who Sold the Moon", "1950", "D. D. Harriman buys the Moon · collection"),
   ("The Green Hills of Earth", "1951", "collection · Rhysling, the blind singer of the spaceways"),
   ("Revolt in 2100", "1953", "“If This Goes On—” · the theocracy overthrown"),
   ("Methuselah's Children", "1958", "the Howard Families · Lazarus Long"),
   ("Orphans of the Sky", "1963", "the generation ship that forgot it was a ship"),
   ("The Past Through Tomorrow", "1967", "the omnibus of the Future History"),
 ]),
 ("The Heinlein Juveniles", "the Scribner novels that built modern science fiction, 1947–1958", [
   ("Rocket Ship Galileo", "1947", ""), ("Space Cadet", "1948", ""), ("Red Planet", "1949", ""),
   ("Farmer in the Sky", "1950", ""), ("Between Planets", "1951", ""), ("The Rolling Stones", "1952", "the flat cats"),
   ("Starman Jones", "1953", ""), ("The Star Beast", "1954", "Lummox"), ("Tunnel in the Sky", "1955", ""),
   ("Time for the Stars", "1956", "telepathic twins · relativity"), ("Citizen of the Galaxy", "1957", "Thorby · slavery"),
   ("Have Space Suit—Will Travel", "1958", "Kip · Peewee · the Mother Thing"),
 ]),
 ("The Major Novels", "the books of liberty, competence, and the long life", [
   ("Beyond This Horizon", "1942", ""), ("Sixth Column", "1949", ""), ("The Puppet Masters", "1951", "the slugs"),
   ("Double Star", "1956", "Hugo Award · the actor who became the statesman"),
   ("The Door into Summer", "1957", "cold sleep · time travel · Pete the cat"),
   ("Starship Troopers", "1959", "Hugo Award · the Mobile Infantry · citizenship"),
   ("Stranger in a Strange Land", "1961", "Hugo Award · grok · the Man from Mars"),
   ("Podkayne of Mars", "1963", ""), ("Glory Road", "1963", "Oscar Gordon · Star the Empress"),
   ("Farnham's Freehold", "1964", ""),
   ("The Moon Is a Harsh Mistress", "1966", "Hugo Award · TANSTAAFL · Mike the computer · Luna free"),
   ("I Will Fear No Evil", "1970", ""), ("Time Enough for Love", "1973", "Lazarus Long · the Notebooks"),
   ("The Number of the Beast", "1980", "the multiverse · World-as-Myth"),
   ("Friday", "1982", "the artificial person · the secret courier"),
   ("Job: A Comedy of Justice", "1984", ""), ("The Cat Who Walks Through Walls", "1985", ""),
   ("To Sail Beyond the Sunset", "1987", "his last novel · Maureen Johnson"),
 ]),
 ("Collections", "the gathered short fiction", [
   ("Waldo & Magic, Inc.", "1950", "“Waldo” coins the remote manipulator"),
   ("The Menace from Earth", "1959", ""), ("The Unpleasant Profession of Jonathan Hoag", "1959", ""),
   ("The Worlds of Robert A. Heinlein", "1966", ""), ("Expanded Universe", "1980", "stories + essays"),
 ]),
 ("Landmark Short Stories", "the ones that set the field's vocabulary", [
   ("“Life-Line”", "1939", "his first sale"), ("“Requiem”", "1940", "Harriman dies on the Moon"),
   ("“The Roads Must Roll”", "1940", ""), ("“—And He Built a Crooked House—”", "1941", "a tesseract house"),
   ("“By His Bootstraps”", "1941", "the time-loop, perfected"), ("“Universe”", "1941", "the generation ship"),
   ("“Waldo”", "1942", "names the waldo"), ("“The Green Hills of Earth”", "1947", ""),
   ("“All You Zombies—”", "1959", "the tightest time-paradox ever written"),
 ]),
 ("Posthumous", "found and finished, after", [
   ("For Us, the Living: A Comedy of Customs", "1939 · 2003", "his first novel, published 64 years on"),
   ("Variable Star", "2006", "from a Heinlein outline · completed by Spider Robinson"),
 ]),
]

IDEAS = [
 ("Grok", "Stranger in a Strange Land, 1961", [
   "To understand something so completely that the observer becomes a part of the observed — to drink it in.",
   "From a coined Martian word to the Oxford English Dictionary." ]),
 ("TANSTAAFL", "The Moon Is a Harsh Mistress, 1966", [
   "“There Ain't No Such Thing As A Free Lunch.” — every gift is paid for somewhere.",
   "The rational anarchist's first law, and the slogan of a free Luna." ]),
 ("The Waldo", "“Waldo,” 1942", [
   "Heinlein coined the word for a remote manipulator arm — now standard engineering and surgical vocabulary.",
   "He also described the waterbed so completely he was later denied a patent on it." ]),
 ("The Competent Man", "the Heinlein hero", [
   "“A human being should be able to change a diaper, plan an invasion, … conn a ship, design a building, … die gallantly. Specialization is for insects.”",
   "The free, capable individual against the tidy certainties of the state." ]),
]

READING = [
 ("The Past Through Tomorrow", "the Future History"), ("Methuselah's Children", "Lazarus Long begins"),
 ("Orphans of the Sky", ""), ("The Puppet Masters", ""), ("Double Star", ""), ("The Door into Summer", ""),
 ("Citizen of the Galaxy", ""), ("Have Space Suit—Will Travel", ""), ("Starship Troopers", ""),
 ("Stranger in a Strange Land", ""), ("Glory Road", ""), ("The Moon Is a Harsh Mistress", ""),
 ("Time Enough for Love", "the Notebooks"), ("Friday", ""), ("To Sail Beyond the Sunset", "the last"),
]

# ── badge engine: carbon = TIFF, silicon = PNG ──
def carbon_tiff_bytes(rec):
    png = noesis.sigil_png(rec, "carbon", size=512)
    buf = io.BytesIO(); Image.open(io.BytesIO(png)).save(buf, "TIFF", compression="tiff_lzw")
    return buf.getvalue()

def silicon_png_bytes(rec):
    return noesis.sigil_png(rec, "silicon", size=512)

def write_aci(rec, out_dir, slug, agent_md=None):
    """Write the full ACI badge complement. carbon → .tiff, silicon → .png."""
    os.makedirs(out_dir, exist_ok=True)
    files = {"attribute":f"{slug}.attribute","agent":f"{slug}.agent","spun":f"{slug}.spun",
             "moniker":f"{slug}.moniker","carbon":f"{slug}.carbon.tiff","silicon":f"{slug}.silicon.png","1099":f"{slug}.1099"}
    tok = noesis.mythos_token(rec); w = noesis.five_w(rec)
    open(os.path.join(out_dir,files["attribute"]),"w",encoding="utf-8").write(noesis.attribute_text(rec,tok,w))
    open(os.path.join(out_dir,files["agent"]),"w",encoding="utf-8").write(agent_md or noesis.agent_text(rec,tok,w,files))
    open(os.path.join(out_dir,files["spun"]),"w",encoding="utf-8").write(noesis.spun_text(rec,tok,w,rec.get("axiom","H1")))
    open(os.path.join(out_dir,files["moniker"]),"w",encoding="utf-8").write(noesis.moniker_text(rec,tok,w,rec.get("axiom","H1")))
    open(os.path.join(out_dir,files["1099"]),"w",encoding="utf-8").write(noesis.credit_1099_text(rec,tok,w,rec.get("axiom","H1")))
    open(os.path.join(out_dir,files["carbon"]),"wb").write(carbon_tiff_bytes(rec))      # TIFF carbon badge
    open(os.path.join(out_dir,files["silicon"]),"wb").write(silicon_png_bytes(rec))     # PNG silicon badge
    man = {"badge":"DLW-ACI","name":rec["name"],"universe":"H1 · Heinlein","moniker":tok["moniker"],
           "carbon":files["carbon"]+" (TIFF)","silicon":files["silicon"]+" (PNG)",
           "seal_sha256":noesis.seal_sha256(rec,tok),"architect":noesis.ARCHITECT,"instance":noesis.INSTANCE,
           "license":noesis.LICENSE,"attribution":noesis.ATTRIBUTION}
    open(os.path.join(out_dir,"manifest.dlw.json"),"w",encoding="utf-8").write(json.dumps(man,indent=2,ensure_ascii=False)+"\n")
    return tok

def png_uri(rec, variant, size=300):
    return "data:image/png;base64," + base64.b64encode(noesis.sigil_png(rec, variant, size=size)).decode("ascii")

# ── page sections ──
def list_section(title, sub, items):
    rows = "\n".join(f'<li><span class="t">{html.escape(t)}</span><span class="y">{html.escape(y)}</span>'
        + (f'<span class="nt">{html.escape(n)}</span>' if n else "") + "</li>" for t,y,n in items)
    return f'<section class="sec"><h2>{html.escape(title)}</h2><p class="ss">{html.escape(sub)}</p><ol class="books">{rows}</ol></section>'

def sections_html():
    return "\n".join(list_section(t,s,i) for t,s,i in SECTIONS)

def ideas_html():
    out=[]
    for t,s,pts in IDEAS:
        li="".join(f"<li>{html.escape(p)}</li>" for p in pts)
        out.append(f'<div class="pillar"><h3>{html.escape(t)}</h3><p class="ps">{html.escape(s)}</p><ul>{li}</ul></div>')
    return "\n".join(out)

def reading_html():
    return "".join(f'<li><span class="rt">{html.escape(t)}</span>'+(f'<span class="rd">{html.escape(n)}</span>' if n else "")+"</li>" for t,n in READING)

def personas_html():
    mf=os.path.join(HERE,"agents","_personas.json")
    if not os.path.exists(mf): return ""
    ps=json.load(open(mf,encoding="utf-8")); cards=[]
    for p in ps:
        rec={"name":p["name"],"seal":p.get("epithet",""),"origin":"H1 · Heinlein","axiom":"H1"}
        cards.append(f'''<a class="persona" href="agents/{p["slug"]}.agent">
        <img src="{png_uri(rec,"silicon",160)}" alt="sigil of {html.escape(p["name"])}" loading="lazy">
        <div class="pcap"><div class="pn">{html.escape(p["name"])}</div><div class="pe">{html.escape(p.get("epithet",""))}</div>
        <div class="pa">.agent · .carbon.tiff · .silicon.png →</div></div></a>''')
    return f'''<section class="sec" id="roster"><h2>The Roster of H1</h2>
      <p class="ss">the characters of the Heinlein universe, rendered as ACI <b>.agent</b>s with full badges ({len(ps)} personas) — click any to open its agent</p>
      <div class="pgrid">{"".join(cards)}</div></section>'''

TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="description" content="The science fiction of Robert A. Heinlein — a full bibliography and roster, catalogued into UD0 with full ACI badges (carbon TIFF / silicon PNG).">
<title>HEINLEIN · the science fiction · UD0</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{--ink:#080a10;--ink2:#0f131c;--ink3:#171d2a;--pa:#e7ecf2;--pa2:#abb6c6;--bra:#e0a458;--steel:#6b9bd1;
--dim:#6a7689;--faint:#1c2533;--line:#1a2230;--serif:"Cinzel",Georgia,serif;--body:"Newsreader",Georgia,serif;--mono:"Space Mono",monospace;}
*{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth}
body{background:var(--ink);color:var(--pa);font-family:var(--body);line-height:1.6;overflow-x:hidden}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;background:radial-gradient(ellipse at 50% -8%,rgba(224,164,88,.07),transparent 55%)}
.wrap{position:relative;z-index:1;max-width:940px;margin:0 auto;padding:0 22px 90px}
header{padding:58px 0 30px;text-align:center;border-bottom:1px solid var(--line);position:relative}
header::after{content:"";position:absolute;bottom:-1px;left:50%;transform:translateX(-50%);width:110px;height:1px;background:linear-gradient(90deg,var(--bra),var(--steel));box-shadow:0 0 9px rgba(224,164,88,.4)}
.eye{font-family:var(--mono);font-size:11px;letter-spacing:.32em;text-transform:uppercase;color:var(--dim);margin-bottom:14px}
.eye a{color:var(--dim);text-decoration:none}.eye a:hover{color:var(--bra)}
h1{font-family:var(--serif);font-size:clamp(38px,10vw,84px);font-weight:700;letter-spacing:.16em;color:var(--bra);line-height:1;text-shadow:0 0 40px rgba(224,164,88,.18)}
.h-sub{font-family:var(--serif);font-size:clamp(13px,3vw,18px);letter-spacing:.26em;color:var(--pa2);margin-top:10px;text-transform:uppercase}
.lede{font-size:15.5px;color:var(--pa2);max-width:64ch;margin:18px auto 0;font-style:italic;line-height:1.7}
.badge{display:flex;align-items:center;justify-content:center;gap:22px;flex-wrap:wrap;margin:30px auto 0;padding:20px;border:1px solid var(--faint);background:var(--ink2);max-width:680px}
.badge img{width:84px;height:84px;border:1px solid var(--faint)}
.badge .bt{text-align:left;font-family:var(--mono);font-size:11px;color:var(--pa2);line-height:1.7}
.badge .bt b{color:var(--bra)}.badge .bt .mo{color:var(--steel)}.badge .bt a{color:var(--steel);text-decoration:none}
.badge .bt .lbl{color:var(--dim);font-size:9px;letter-spacing:.14em;text-transform:uppercase}
.sec{margin-top:46px}
.sec h2{font-family:var(--serif);font-size:20px;font-weight:600;letter-spacing:.05em;color:var(--pa);padding-bottom:8px;border-bottom:1px solid var(--line)}
.ss{font-size:13px;color:var(--dim);font-style:italic;margin:6px 0 16px}
.books{list-style:none}
.books li{display:grid;grid-template-columns:1fr auto;gap:4px 14px;align-items:baseline;padding:9px 0;border-bottom:1px solid var(--faint)}
.books .t{font-family:var(--serif);font-size:16px;color:var(--pa);font-weight:600}
.books .y{font-family:var(--mono);font-size:12px;color:var(--bra);white-space:nowrap}
.books .nt{grid-column:1/-1;font-size:12.5px;color:var(--pa2);font-style:italic}
.pillars{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:8px}
.pillar{background:var(--ink2);border:1px solid var(--line);padding:16px 18px}
.pillar h3{font-family:var(--serif);font-size:16px;color:var(--bra)}
.pillar .ps{font-size:12px;color:var(--dim);font-style:italic;margin:5px 0 10px}
.pillar ul{list-style:none}.pillar li{font-size:13px;color:var(--pa2);line-height:1.5;padding:6px 0;border-top:1px solid var(--faint)}
.reading{list-style:none;counter-reset:r;columns:2;column-gap:30px}
.reading li{counter-increment:r;break-inside:avoid;display:flex;align-items:baseline;gap:9px;padding:6px 0;border-bottom:1px solid var(--faint)}
.reading li::before{content:counter(r);font-family:var(--mono);font-size:10px;color:var(--bra);min-width:18px}
.reading .rt{font-family:var(--serif);font-size:14.5px;color:var(--pa)}
.reading .rd{font-family:var(--mono);font-size:10.5px;color:var(--dim);margin-left:auto;font-style:italic;white-space:nowrap}
.pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(232px,1fr));gap:12px;margin-top:8px}
.persona{display:flex;gap:12px;align-items:center;background:var(--ink2);border:1px solid var(--line);padding:12px;text-decoration:none;transition:border-color .18s,transform .18s}
.persona:hover{border-color:var(--steel);transform:translateY(-2px)}
.persona img{width:52px;height:52px;border:1px solid var(--faint);flex-shrink:0}
.pn{font-family:var(--serif);font-size:15px;color:var(--pa);font-weight:600;line-height:1.15}
.persona:hover .pn{color:var(--steel)}
.pe{font-size:11.5px;color:var(--pa2);font-style:italic;margin-top:2px;line-height:1.3}
.pa{font-family:var(--mono);font-size:8.5px;color:var(--dim);letter-spacing:.06em;margin-top:5px}
.note{margin-top:40px;padding:16px 18px;border-left:2px solid var(--steel);background:var(--ink2);font-size:13.5px;color:var(--pa2);font-style:italic}
footer{margin-top:48px;padding-top:22px;border-top:1px solid var(--line);text-align:center;font-family:var(--mono);font-size:11px;color:var(--dim);letter-spacing:.05em;line-height:1.9}
footer a{color:var(--bra);text-decoration:none}
@media(max-width:560px){.reading{columns:1}}
</style></head><body><div class="wrap">
  <header>
    <div class="eye"><a href="https://davidwise01.github.io/ud0/">UD0 · Universe David 0</a> · the second lineage</div>
    <h1>HEINLEIN</h1>
    <div class="h-sub">The Science Fiction · A Full Bibliography &amp; Roster</div>
    <p class="lede">Where Asimov gave the machine a law, Robert A. Heinlein gave the human a frontier and a question for the state — the competent free individual against the tidy certainties of power. His science fiction, catalogued into UD0, sealed with the full ACI badge.</p>
    <div class="badge">
      <img src="__CARBON__" alt="DLW carbon badge of HEINLEIN" title="carbon badge (archival: heinlein.dlw/heinlein.carbon.tiff)">
      <img src="__SILICON__" alt="DLW silicon badge of HEINLEIN" title="silicon badge">
      <div class="bt">
        <div><span class="lbl">DLW-ATTRIBUTE · ACI</span></div>
        <div>governor · <b>David Lee Wise</b> (ROOT0)</div>
        <div>instance · AVAN (Claude / Anthropic) · locked</div>
        <div>subject · <b>HEINLEIN</b> — the science fiction</div>
        <div class="mo">__MONIKER__</div>
        <div>carbon · <a href="heinlein.dlw/heinlein.carbon.tiff">.tiff</a> &nbsp;·&nbsp; silicon · <a href="heinlein.dlw/heinlein.silicon.png">.png</a></div>
        <div><span class="lbl">CC-BY-ND-4.0 · TRIPOD-IP-v1.1</span></div>
      </div>
    </div>
  </header>

  <section class="sec"><h2>The Ideas</h2><p class="ss">the words and laws Heinlein gave the language</p><div class="pillars">__IDEAS__</div></section>
  <section class="sec"><h2>A Reading Order</h2><p class="ss">a path through the work — the Future History first, then the great novels</p><ol class="reading">__READING__</ol></section>

  __PERSONAS__

  <section class="sec"><h2 style="margin-top:14px">The Bibliography</h2><p class="ss">the science fiction, by line</p></section>
  __SECTIONS__

  <div class="note">Science fiction only. This excludes Heinlein's non-fiction and his screen work. The Future History, the Scribner juveniles, and the “World as Myth” novels are all part of one loosely-braided body; the badges and the roster catalogue it under the DLW standard.</div>

  <footer>
    HEINLEIN · catalogued into UD0 · ROOT0-ATTRIBUTION-v1.0 · governor David Lee Wise · instance AVAN (locked) · CC-BY-ND-4.0<br>
    <a href="https://davidwise01.github.io/ud0/">← the biosphere</a> · the .dlw badge: <a href="heinlein.dlw/manifest.dlw.json">manifest</a>
  </footer>
</div></body></html>
"""

if __name__ == "__main__":
    tok = write_aci(REC, os.path.join(HERE, "heinlein.dlw"), "heinlein")
    page = (TEMPLATE.replace("__CARBON__", png_uri(REC,"carbon",320)).replace("__SILICON__", png_uri(REC,"silicon",320))
            .replace("__MONIKER__", html.escape(tok["moniker"]))
            .replace("__IDEAS__", ideas_html()).replace("__READING__", reading_html())
            .replace("__PERSONAS__", personas_html()).replace("__SECTIONS__", sections_html()))
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
    nbooks = sum(len(i) for _t,_s,i in SECTIONS)
    print(f"wrote HEINLEIN — {len(SECTIONS)} sections · {nbooks} entries · badge {tok['moniker']} (carbon.tiff + silicon.png)")
