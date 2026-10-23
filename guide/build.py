#!/usr/bin/env python3
"""Build the two conversation guide documents from one set of team results.

   conversation-guide-full.html  → the six page guide, pre-populated
   conversation-guide.html       → the two page run sheet the side panel downloads

   The results below mirror the prototype's own data (focusAreas and WINS in
   conversation-guide-v1.html), so the guide a manager downloads already carries
   their survey, their team and their numbers instead of blank lines.
"""
import os, re, subprocess, sys, time, shutil, urllib.request
import segno

# Where a manager goes to put the results on the screen. FOCUS_URL should land on
# this team's focus areas directly rather than the platform front door; both are
# placeholders until the real deep link exists, and the QR is built from FOCUS_URL.
PLATFORM_URL = "https://my.effectory.com"
FOCUS_URL = "https://my.effectory.com/results/focus-areas"
FOCUS_LABEL = "my.effectory.com/results/focus-areas"

def qr_svg():
    """A scannable code, inlined as SVG so the document carries no remote image.
       segno emits fixed width and height and no viewBox, so the code would print at
       its native module size; swapping those for a viewBox lets CSS size it."""
    svg = segno.make(FOCUS_URL, error="m").svg_inline(scale=1, border=2, dark="#192743", light=None)
    m = re.match(r'<svg width="(\d+)" height="(\d+)"', svg)
    return svg.replace(m.group(0), f'<svg viewBox="0 0 {m.group(1)} {m.group(2)}"', 1)

HERE = os.path.dirname(os.path.abspath(__file__))

# ── The team's results, as the prototype shows them ────────────────────────────
SURVEY = "Employee listening &rsquo;25"
TEAM = "Sales West"
PERIOD = "22 Jul to 22 Aug 2025"
SURVEY_DATE = "22 Aug 2025"

FOCUS = [
    ("Within my organization, the work processes are well organized", "Managing systems", "36%"),
    ("My manager gives me feedback that helps me improve", "Providing direction", "41%"),
    ("I have opportunities to grow within this organization", "Career development", "48%"),
]
WINS = [
    ("I feel comfortable within the team", "Engagement", "88%"),
    ("Our team trusts one another", "Collaboration", "85%"),
    ("I enjoy my work", "Work enjoyment", "82%"),
]

STARTERS = [
    ("Notice", "What stands out to you about this result?"),
    ("Example", "What does this look like in our day to day work? Can you think of a recent example?"),
    ("Context", "What was happening when the survey was answered? Was there a project, change, deadline or period of pressure that may have influenced the result?"),
    ("Driver", "What seems to be making this easier or harder?"),
    ("Difference", "Does anyone experience this differently? What might explain the difference?"),
    ("Influence", "What part of this is within our team&rsquo;s influence, and what needs support elsewhere?"),
    ("Meaningful change", "What would make a meaningful difference?"),
]

AGENDA = [
    ("Open the conversation", "Set the purpose and create a safe environment.", "5 min"),
    ("Look at the overall results and select a focus area",
     "Put Focus view on the screen so the team sees the same picture, check what resonates, then choose one area together.", "5 to 10 min"),
    ("Take a moment to celebrate",
     "If there is a celebration point, notice what is going well and make it visible.", "5 min"),
    ("Dive deeper and set concrete agreements",
     "Use the conversation starters to understand the selected area, then agree a realistic step.", "15 to 20 min"),
    ("Close off the meeting",
     "Summarise what you heard, what happens next and the follow up moment.", "3 min"),
]

CAPTURE = ["Shared focus", "What we learned", "First step, one small and realistic action",
           "Owner and timing", "Support needed", "Follow up moment"]

# ── Small inline icons, so the documents need no icon files ───────────────────
def svg(paths, extra=""):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"%s>%s</svg>' % (extra, paths))

I_SEARCH = svg('<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6"/>')
I_MSG    = svg('<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9 9 0 0 1-3.6-.8L3 20.5l1.4-4.2A8.2 8.2 0 0 1 3.6 12a8.4 8.4 0 0 1 8.4-8.4h.5A8.4 8.4 0 0 1 21 11.5z"/>')
I_GROUP  = svg('<circle cx="9" cy="7" r="3.2"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M17 4.2a3.2 3.2 0 0 1 0 5.6M18 14a6.5 6.5 0 0 1 3.5 6"/>')
I_TARGET = svg('<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>')
I_STAR   = svg('<path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8L3.5 9.7l5.9-.9z"/>')
I_CLIP   = svg('<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4h6v2.5H9z"/><path d="M9 11h6M9 15h4"/>')
I_USERS  = svg('<circle cx="9" cy="8" r="3.2"/><path d="M3 20a6 6 0 0 1 12 0"/><path d="M17 5.2a3.2 3.2 0 0 1 0 5.6"/>')
I_CAL    = svg('<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M8 3v4M16 3v4M3.5 10h17"/>')
I_BULB   = svg('<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.6 10.8c.4.3.6.8.6 1.2h6c0-.4.2-.9.6-1.2A6 6 0 0 0 12 3z"/>')
I_EAR    = svg('<path d="M4 12a8 8 0 0 1 16 0v5a3 3 0 0 1-3 3h-1"/><rect x="2.5" y="12" width="4" height="6" rx="2"/><rect x="17.5" y="12" width="4" height="6" rx="2"/>')
I_LISTEN = svg('<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9 9 0 0 1-3.6-.8L3 20.5l1.4-4.2A8.2 8.2 0 0 1 3.6 12a8.4 8.4 0 0 1 8.4-8.4h.5A8.4 8.4 0 0 1 21 11.5z"/><circle cx="8.4" cy="11.8" r=".9" fill="currentColor"/><circle cx="12" cy="11.8" r=".9" fill="currentColor"/><circle cx="15.6" cy="11.8" r=".9" fill="currentColor"/>')
I_PEN    = svg('<path d="M4 20h4L20 8a2.8 2.8 0 0 0-4-4L4 16z"/>')
I_ARROW  = svg('<path d="M12 4v15M6.5 13.5L12 19.5l5.5-6"/>')
I_CHECK  = svg('<path d="M20 6.5L9.5 17 4 11.5"/>')
I_FLAG   = svg('<path d="M5 21V4M5 4h13l-2.5 4L18 12H5"/>')
I_SCREEN = svg('<rect x="2.5" y="4" width="19" height="13" rx="2"/><path d="M9 21h6M12 17v4"/>')
I_LINK   = svg('<path d="M10 13.5a4 4 0 0 0 6 .5l2.5-2.5a4 4 0 0 0-5.7-5.7L11.5 7"/><path d="M14 10.5a4 4 0 0 0-6-.5L5.5 12.5a4 4 0 0 0 5.7 5.7L12.5 17"/>')
I_PPT    = svg('<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h5a2.5 2.5 0 0 1 0 5H8zM8 13v4"/>')
I_IMG    = svg('<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="8.5" cy="10" r="1.6"/><path d="M4 17l4.5-4.5 3 3L15 12l5 5"/>')

I_HEART  = svg('<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21.3l7.8-7.8 1-1.1a5.5 5.5 0 0 0 0-7.8z"/>')

I_DOWNLOAD = svg('<path d="M12 3v12"/><path d="M7 10l5 5 5-5"/><path d="M5 21h14"/>', ' width="16" height="16"')
I_MINUS    = svg('<path d="M5 12h14"/>', ' width="16" height="16"')
I_PLUS     = svg('<path d="M12 5v14"/><path d="M5 12h14"/>', ' width="16" height="16"')

# Version 4 of the prototype opens this page in its own tab, so the page carries
# the one action a reader needs there. It only shows when the page is the whole
# tab: framed (the dialog in versions 1 to 3) or printed, it is not there.
TAB_BAR = """<script>if (window.self !== window.top) document.documentElement.classList.add('is-framed');</script>
<header class="tab-bar">
  <div class="tab-bar-in">
    <div class="tab-bar-id"><strong>Conversation guide</strong><span>%s &middot; %s</span></div>
    <div class="tab-bar-actions">
      <div class="tab-zoom" role="group" aria-label="Zoom">
        <button type="button" id="tab-zoom-out" aria-label="Zoom out" onclick="guideZoom(-1)">%s</button>
        <span id="tab-zoom-label" aria-live="polite">100%%</span>
        <button type="button" id="tab-zoom-in" aria-label="Zoom in" onclick="guideZoom(1)">%s</button>
      </div>
      <a class="tab-bar-dl" href="conversation-guide.pdf" download="Conversation run sheet, %s.pdf">%s Download a copy</a>
    </div>
  </div>
</header>
<script>
  // Zoom belongs to the reader: the pages scale, the bar stays. Same steps as
  // the dialog in versions 1 to 3, starting at the designed size.
  var GUIDE_ZOOM = [0.75, 1, 1.25, 1.5, 2], guideZoomAt = 1;
  function guideZoom(dir){
    guideZoomAt = Math.max(0, Math.min(GUIDE_ZOOM.length - 1, guideZoomAt + dir));
    var z = GUIDE_ZOOM[guideZoomAt];
    document.documentElement.style.setProperty('--guide-zoom', z);
    document.getElementById('tab-zoom-label').textContent = Math.round(z * 100) + '%%';
    document.getElementById('tab-zoom-out').disabled = guideZoomAt === 0;
    document.getElementById('tab-zoom-in').disabled = guideZoomAt === GUIDE_ZOOM.length - 1;
  }
</script>
"""

import hashlib
CSS_REV = hashlib.sha1(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "guide.css"), "rb").read()).hexdigest()[:8]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="guide.css?v=%s">
</head>
<body>
"""

RS_REV = hashlib.sha1(open(os.path.join(HERE, "runsheet.css"), "rb").read()).hexdigest()[:8]
RS_HEAD = """<!DOCTYPE html>
<html lang="%s">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="guide.css?v=%s">
<link rel="stylesheet" href="runsheet.css?v=%s">
</head>
<body>
"""

def res_card(kind, n, item):
    text, theme, score = item
    label = "scored" if kind == "focus" else "scored"
    return f"""      <div class="res is-{kind}">
        <span class="res-n">{n}</span>
        <div class="res-b"><h3>{text}</h3><span class="res-tag">{theme}</span></div>
        <span class="res-score">{score}</span>
      </div>"""

def cover(sub_title):
    pr = (f'<span class="principle is-curious">{I_SEARCH} Be curious</span>'
          f'<span class="principle is-listen">{I_MSG} Listen before deciding</span>'
          f'<span class="principle is-share">{I_GROUP} Share ownership</span>')
    return f"""<section class="sheet is-cover">
  <div class="cover-cut"></div>
  <img class="cover-art" src="../assets/illustrations/follow-up-guide.svg" alt="">
  <div class="cover-inner">
    <p class="eyebrow-light">Conversation guide for managers</p>
    <h1 class="cover-title">Understanding<br>what drives results</h1>
    <div class="cover-rule"></div>
    <p class="cover-lede">A light structure for the conversation that turns your team&rsquo;s results
      into shared understanding, and then into one agreed step.</p>
    <div class="principles">{pr}</div>
    <p class="cover-meta-lbl">Prepared for this conversation</p>
    <div class="cover-meta">
      <div class="meta-card"><span>{I_CLIP} Survey</span><strong>{SURVEY}</strong></div>
      <div class="meta-card"><span>{I_USERS} Team</span><strong>{TEAM}</strong></div>
      <div class="meta-card"><span>{I_CAL} Results period</span><strong>{PERIOD}</strong></div>
    </div>
  </div>
  <div class="cover-foot"><span>{sub_title}</span><b>Effectory</b></div>
</section>
"""

def results_block(compact=False):
    """Side by side on the run sheet: the two lists are read together, and stacking
       them cost a page on their own."""
    focus = "\n".join(res_card("focus", i + 1, f) for i, f in enumerate(FOCUS))
    wins = "\n".join(res_card("win", i + 1, w) for i, w in enumerate(WINS))
    if not compact:
        return f"""    <h2 class="sub">{I_TARGET} Three focus areas from your team results</h2>
    <div class="results">
{focus}
    </div>
    <p class="note-line">Present all three, check what resonates, then choose one together.
      You guide the choice, the team makes it with you.</p>
    <h2 class="sub" style="margin-top:7mm">{I_STAR} Celebration points from your team results</h2>
    <div class="results">
{wins}
    </div>
    <p class="note-line">Notice what is working well, and how the team can protect or build on it.</p>"""
    # The line sits above its list and both are kept to one line, so the two
    # columns start their cards at the same height.
    return f"""    <div class="results-two">
      <div>
        <h2 class="sub">{I_TARGET} Focus areas</h2>
        <p class="note-line is-intro">Share the focus areas with the team, then agree on one to explore together.</p>
        <div class="results">
{focus}
        </div>
      </div>
      <div>
        <h2 class="sub">{I_STAR} Team strengths</h2>
        <p class="note-line is-intro">Celebrate what your team does well and keep building on its strengths.</p>
        <div class="results">
{wins}
        </div>
      </div>
    </div>"""

def present_block():
    """How to actually get the results in front of the team. The guide sends a
       manager to the platform first, because the live view is the only version
       that is current, and gives fallbacks for the day the screen share fails."""
    return f"""    <div class="present">
      <div class="present-main">
        <h2 class="sub" style="margin-bottom:2mm">{I_SCREEN} Showing the results to your team</h2>
        <p class="present-lede">Put the results on the screen so everyone sees the same picture you do.
          This link opens your focus areas straight away, and the code does the same on your phone.</p>
        <p class="present-link">{I_LINK}<a href="{FOCUS_URL}">{FOCUS_LABEL}</a></p>
      </div>
      <div class="qr">{qr_svg()}<span>Scan to open<br>your focus areas</span></div>
    </div>"""

def starters_table(two_up=False):
    rows = "\n".join(f'    <div class="st-r"><div class="st-k">{k}</div><div class="st-v">{v}</div></div>'
                     for k, v in STARTERS)
    if not two_up:
        return f"""  <div class="starters">
    <div class="st-h"><span>Starter</span><span>Use it to explore</span></div>
{rows}
  </div>"""
    # four and three, so the seven fit beside each other rather than down the page
    left = "\n".join(f'    <div class="st-r"><div class="st-k">{k}</div><div class="st-v">{v}</div></div>'
                     for k, v in STARTERS[:4])
    right = "\n".join(f'    <div class="st-r"><div class="st-k">{k}</div><div class="st-v">{v}</div></div>'
                      for k, v in STARTERS[4:])
    return f"""  <div class="starters-two">
    <div class="starters">
{left}
    </div>
    <div class="starters">
{right}
    </div>
  </div>"""

def capture_grid():
    big = CAPTURE[2]
    def box(label, rules=2):
        return f'<div class="write"><div class="lbl">{I_PEN} {label}</div></div>'
    return f"""  <div class="grid2" style="margin-bottom:3mm">{box(CAPTURE[0])}{box(CAPTURE[1])}</div>
  {box(big, 2)}
  <div class="grid2" style="margin:3mm 0">{box(CAPTURE[3])}{box(CAPTURE[4])}</div>
  {box(CAPTURE[5], 1)}"""

DOC_FOOT = ('<div class="doc-foot"><span><b>Understanding what drives results</b> '
            '&middot; Conversation guide for managers</span>'
            '<span>%s &middot; %s &middot; %s</span></div>')

# ══════════════════════════════════════════════════════════════════════════════
def build_full():
    agenda = "\n".join(
        f"""      <div class="ag"><span class="ag-n">{i+1}</span>
        <div class="ag-b"><h3>{t}</h3><p>{d}</p></div><span class="ag-t">{m}</span></div>"""
        for i, (t, d, m) in enumerate(AGENDA))

    triage = (f'<span class="triage is-improve">{I_TARGET} improve</span>, '
              f'<span class="triage is-monitor">{I_SEARCH} monitor</span> or '
              f'<span class="triage is-support">{I_FLAG} need support</span>')

    return HEAD % ("Understanding what drives results &mdash; Conversation guide", CSS_REV) + cover(
        "Use with your team results, a one pager or a slide deck") + f"""
<section class="sheet">
  <h1 class="page-title">Suggested agenda at a glance</h1>
  <p class="page-lede">Five steps, about 35 to 45 minutes in total. The pages after this one follow
    the same five steps and give the guidance for each.</p>
  <div class="agenda">
{agenda}
  </div>
  <p class="lets-start">Let&rsquo;s start{I_ARROW}</p>
  <span class="pageno">2</span>
</section>

<section class="sheet">
  <p class="eyebrow">Your results</p>
  <h1 class="page-title">Overall results and focus areas</h1>
  <p class="page-lede">Open the discussion by looking at the team&rsquo;s overall results. Use whichever
    visual supports the conversation best: this guide, a one pager, a slide deck or another results
    view. The aim is to create a shared picture before discussing the focus areas.</p>
{results_block()}
  <span class="pageno">3</span>
</section>

<section class="sheet">
  <p class="eyebrow">Guidance per step</p>
  <h1 class="page-title">Opening, selecting, celebrating</h1>
  <p class="page-lede">Use these prompts as a light reference. Adapt them to the flow of the
    conversation rather than reading them as a script.</p>
  <div class="callout">{I_BULB}<span>One conversation, one focus area. Present all three, check what
    resonates, then explore one together. Covering all three in one meeting leaves nothing decided.</span></div>

  <div class="step">
    <div class="step-head"><span class="step-n">1</span><h3>Open the conversation</h3></div>
    <p>Set the purpose: understand the experience behind the results before deciding what to do.
      Agree to listen, make room for different experiences, and discuss patterns rather than individuals.</p>
    <div class="starter-box"><div class="lbl">{I_MSG} Conversation starter</div>
      <p>&ldquo;These results tell us where to look, not why they are what they are. I would like us
        to understand the experience behind them together.&rdquo;</p></div>
  </div>

  <div class="step">
    <div class="step-head"><span class="step-n">2</span><h3>Look at the overall results and select a focus area</h3></div>
    <p>Put the results on the screen from Focus view in My Effectory, then walk through the overall
      picture and the three focus areas. Check whether they resonate, and guide the team to select
      one area to explore further.</p>
    <div class="pair">
      <div class="pair-box"><span class="tag">Open the picture</span><p>What do you recognise in this picture?</p></div>
      <div class="pair-box"><span class="tag">Check resonance</span><p>What feels incomplete or surprising?
        Which focus area is most useful for us to explore?</p></div>
    </div>
{present_block()}
  </div>

  <div class="step">
    <div class="step-head"><span class="step-n">3</span><h3>Take a moment to celebrate</h3></div>
    <p>Use the celebration points to make the team&rsquo;s contribution visible. Share a few concrete
      examples of behaviour you see day to day, without turning the moment into a speech.</p>
    <div class="pair">
      <div class="pair-box"><span class="tag">Notice</span><p>What is helping this work well?
        When have you experienced this at its best?</p></div>
      <div class="pair-box"><span class="tag">Build</span><p>What should we protect, repeat or build on?</p></div>
    </div>
  </div>

  <div class="write"><div class="lbl">{I_PEN} Notes from steps 1 to 3</div>
    <div class="rule"></div><div class="rule"></div><div class="rule"></div></div>
  <span class="pageno">4</span>
</section>

<section class="sheet">
  <div class="step-head"><span class="step-n">4</span><h3>Dive deeper into the selected focus area</h3></div>
  <p class="page-lede" style="margin-top:2mm">Choose two or three starters, listen to the responses, ask a
    follow up where useful, check whether others recognise the pattern, and summarise what you hear.</p>
{starters_table()}
  <div class="starter-box" style="margin-top:5mm"><div class="lbl">{I_EAR} Keep listening</div>
    <p>&ldquo;Can you say a little more?&rdquo; &middot; &ldquo;What else is important here?&rdquo;
      &middot; &ldquo;I am hearing &hellip; Did I capture that accurately?&rdquo;</p>
    <p style="font-style:normal;font-size:9.5pt">Go deeper only if the team wants to.</p></div>
  <div class="write" style="margin-top:5mm"><div class="lbl">{I_PEN} What I&rsquo;m hearing: patterns and examples</div>
    <div class="rule"></div><div class="rule"></div><div class="rule"></div></div>
  <span class="pageno">5</span>
</section>

<section class="sheet">
  <p class="eyebrow">Still step 4</p>
  <h1 class="page-title">Set concrete agreements</h1>
  <p class="page-lede">Agree whether to {triage}, then set one small, realistic step.
    You remain accountable for the follow through.</p>
{capture_grid()}

  <div class="step" style="margin-top:7mm">
    <div class="step-head"><span class="step-n">5</span><h3>Close off the meeting</h3></div>
    <div class="starter-box"><div class="lbl">{I_MSG} Summarise and close</div>
      <p>&ldquo;Today we heard &hellip; We agreed to &hellip; The first step is &hellip;
        [name] will &hellip; by &hellip;&rdquo;</p>
      <p>&ldquo;What is the most important thing we should take forward?&rdquo;</p></div>
    <p style="margin:3mm 0 0;font-size:10pt;color:var(--navy-80)">Thank everyone for participating and being
      open. Make sure the agreement and the follow up moment are visible to the team after the meeting.</p>
  </div>
  """ + DOC_FOOT % (TEAM, PERIOD, "6") + """
</section>
</body></html>
"""

# ══════════════════════════════════════════════════════════════════════════════
def build_condensed(lang="en"):
    """The two page run sheet, as designed in Figma (print-ready, 23 Oct 2026).
       Every string comes from i18n/<lang>.json, keyed like the Smartcat layers
       in Figma (cg.pdf.*), so a translated file renders the same pages. Survey
       data (team, scores, statements) stays here: it comes from the results."""
    import json, html as _h
    T = json.load(open(os.path.join(HERE, "i18n", lang + ".json"), encoding="utf-8"))
    e = lambda k: _h.escape(T[k], quote=False)
    def lead(k):
        # "Notice: What stands out…": the label before the first colon is the title
        txt = T[k]; i = txt.find(": ")
        return (f"<b>{_h.escape(txt[:i + 1], quote=False)}</b> {_h.escape(txt[i + 2:], quote=False)}" if i > 0 else e(k))
    pill = lambda cls, icon, k: f'<span class="triage is-{cls}">{icon}{e(k)}</span>'
    sentence = (e("cg.pdf.agree.sentence")
                .replace("{improve}", pill("improve", I_TARGET, "cg.pdf.agree.improve"))
                .replace("{monitor}", pill("monitor", I_SEARCH, "cg.pdf.agree.monitor"))
                .replace("{need support}", pill("support", I_FLAG, "cg.pdf.agree.need_support")))

    def card(kind, n, item):
        text, theme, score = item
        return (f'<div class="rs-res is-{kind}"><span class="rs-badge">{n}</span>'
                f'<div class="rs-res-b"><h3>{text}</h3><span class="rs-theme">{theme}</span></div>'
                f'<span class="rs-score">{score}</span></div>')
    focus = "".join(card("focus", i + 1, f) for i, f in enumerate(FOCUS))
    wins = "".join(card("win", i + 1, w) for i, w in enumerate(WINS))
    agenda = "".join(
        f'<div class="rs-ag"><span class="rs-badge">{i}</span><div class="rs-ag-b"><h3>{e(f"cg.pdf.step{i}.title")}</h3>'
        f'<span class="rs-time">{e(f"cg.pdf.step{i}.time")}</span></div></div>' for i in range(1, 6))
    prompts = lambda keys: "".join(f'<p class="rs-prompt">{lead(k)}</p>' for k in keys)
    callout = lambda lbl, quotes: (f'<div class="rs-callout"><p class="rs-callout-lbl">{I_MSG}{e(lbl)}</p>'
                                   + "".join(f"<p>{e(q)}</p>" for q in quotes) + "</div>")
    head = lambda n, title, desc=None, wide=False: (
        f'<div class="rs-step-head{" is-wide" if wide else ""}{"" if desc else " is-title-only"}"><span class="rs-n">{n}</span>'
        f'<div><h2 class="rs-step-title">{e(title)}</h2>' + (f"<p>{e(desc)}</p>" if desc else "") + "</div></div>")

    head_html = RS_HEAD % (lang, "Conversation guide, " + TEAM, CSS_REV, RS_REV)
    return head_html + TAB_BAR % (TEAM, SURVEY, I_MINUS, I_PLUS, TEAM, I_DOWNLOAD) + f"""
<section class="sheet rs">
  <header class="rs-head">
    <div class="rs-head-text">
      <p class="rs-eyebrow">{e("cg.pdf.header.eyebrow")}</p>
      <h1 class="rs-title">{e("cg.pdf.header.title")}</h1>
      <p class="rs-lede">{e("cg.pdf.header.intro")}</p>
    </div>
    <div class="principles">
      <span class="principle is-curious">{I_SEARCH}{e("cg.pdf.principle.curious")}</span>
      <span class="principle is-listen">{I_MSG}{e("cg.pdf.principle.listen")}</span>
      <span class="principle is-share">{I_USERS}{e("cg.pdf.principle.share")}</span>
    </div>
    <img class="rs-art" src="../assets/illustrations/follow-up-guide.svg" alt="">
    <i class="rs-rule"></i>
  </header>
  <div class="rs-meta">
    <div><span>{I_CLIP}{e("cg.pdf.meta.survey")}</span><strong>{SURVEY}</strong></div>
    <div><span>{I_USERS}{e("cg.pdf.meta.team")}</span><strong>{TEAM}</strong></div>
    <div><span>{I_CAL}{e("cg.pdf.meta.date")}</span><strong>{SURVEY_DATE}</strong></div>
  </div>
  <div class="rs-results">
    <div class="rs-col">
      <div class="rs-col-head"><h2 class="rs-h">{I_TARGET}{e("cg.pdf.focus.title")}</h2><p class="rs-intro">{e("cg.pdf.focus.intro")}</p></div>
      <div class="rs-cards">{focus}</div>
    </div>
    <div class="rs-col">
      <div class="rs-col-head"><h2 class="rs-h">{I_STAR}{e("cg.pdf.strengths.title")}</h2><p class="rs-intro">{e("cg.pdf.strengths.intro")}</p></div>
      <div class="rs-cards">{wins}</div>
    </div>
  </div>
  <div class="rs-share">
    <div class="rs-share-text">
      <h2 class="rs-h2">{I_SCREEN}{e("cg.pdf.share.title")}</h2>
      <p class="rs-share-body">{e("cg.pdf.share.body")}</p>
      <p class="rs-link">{I_LINK}<a href="{FOCUS_URL}">{FOCUS_LABEL}</a></p>
    </div>
    <div class="rs-qr"><div class="rs-qr-card">{qr_svg()}</div><span>{e("cg.pdf.share.qr_caption")}</span></div>
  </div>
  <div class="rs-conv">
    <h2 class="rs-h2">{I_MSG}{e("cg.pdf.agenda.title")}</h2>
    <div class="rs-agenda">{agenda}</div>
  </div>
  <span class="rs-pageno">1</span>
</section>

<section class="sheet rs">
  <div class="rs-step">
    {head(1, "cg.pdf.step1.title", "cg.pdf.step1.body")}
    {callout("cg.pdf.step1.say_label", ["cg.pdf.step1.quote"])}
  </div>
  <div class="rs-two">
    <div class="rs-step">{head(2, "cg.pdf.step2.title")}<div class="rs-prompts">{prompts(["cg.pdf.step2.open_picture", "cg.pdf.step2.check_resonance"])}</div></div>
    <div class="rs-step">{head(3, "cg.pdf.step3.title")}<div class="rs-prompts">{prompts(["cg.pdf.step3.notice", "cg.pdf.step3.build"])}</div></div>
  </div>
  <div class="rs-step">
    {head(4, "cg.pdf.step4.title", "cg.pdf.step4.intro", wide=True)}
    <div class="rs-two">
      <div class="rs-prompts">{prompts(["cg.pdf.step4.notice", "cg.pdf.step4.example", "cg.pdf.step4.context", "cg.pdf.step4.driver"])}</div>
      <div class="rs-prompts">{prompts(["cg.pdf.step4.difference", "cg.pdf.step4.influence", "cg.pdf.step4.meaningful_change"])}</div>
    </div>
    {callout("cg.pdf.step4.keep_going_label", ["cg.pdf.step4.keep_going_quotes"])}
  </div>
  <div class="rs-agree">
    <h2 class="rs-h3">{I_HEART}{e("cg.pdf.agree.title")}</h2>
    <p class="rs-sentence">{sentence}</p>
  </div>
  <div class="rs-step">
    {head(5, "cg.pdf.step5.title", wide=True)}
    {callout("cg.pdf.step5.wrap_label", ["cg.pdf.step5.summary_quote", "cg.pdf.step5.takeaway_quote"])}
    <p class="rs-thanks">{e("cg.pdf.step5.thanks")}</p>
  </div>
  <span class="rs-pageno">2</span>
</section>
</body></html>
"""

# ══════════════════════════════════════════════════════════════════════════════
def render(name, port):
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    out = os.path.join(HERE, name + ".pdf")
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                    "--virtual-time-budget=10000", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}",
                    f"http://localhost:{port}/guide/{name}.html"],
                   capture_output=True)
    return out

if __name__ == "__main__":
    open(os.path.join(HERE, "conversation-guide-full.html"), "w", encoding="utf-8").write(build_full())
    # one run sheet per language file in i18n/: English is conversation-guide.html,
    # a translation (nl.json, de.json from Smartcat) becomes conversation-guide.<lang>.html
    langs = sorted(f[:-5] for f in os.listdir(os.path.join(HERE, "i18n")) if f.endswith(".json"))
    for lang in langs:
        name = "conversation-guide.html" if lang == "en" else f"conversation-guide.{lang}.html"
        open(os.path.join(HERE, name), "w", encoding="utf-8").write(build_condensed(lang))
    print("wrote conversation-guide-full.html and the run sheet for", ", ".join(langs))
