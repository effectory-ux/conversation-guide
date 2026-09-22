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
I_PEN    = svg('<path d="M4 20h4L20 8a2.8 2.8 0 0 0-4-4L4 16z"/>')
I_ARROW  = svg('<path d="M12 4v15M6.5 13.5L12 19.5l5.5-6"/>')
I_CHECK  = svg('<path d="M20 6.5L9.5 17 4 11.5"/>')
I_FLAG   = svg('<path d="M5 21V4M5 4h13l-2.5 4L18 12H5"/>')
I_SCREEN = svg('<rect x="2.5" y="4" width="19" height="13" rx="2"/><path d="M9 21h6M12 17v4"/>')
I_LINK   = svg('<path d="M10 13.5a4 4 0 0 0 6 .5l2.5-2.5a4 4 0 0 0-5.7-5.7L11.5 7"/><path d="M14 10.5a4 4 0 0 0-6-.5L5.5 12.5a4 4 0 0 0 5.7 5.7L12.5 17"/>')
I_PPT    = svg('<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h5a2.5 2.5 0 0 1 0 5H8zM8 13v4"/>')
I_IMG    = svg('<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="8.5" cy="10" r="1.6"/><path d="M4 17l4.5-4.5 3 3L15 12l5 5"/>')

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="guide.css">
</head>
<body>
"""

def res_card(kind, n, item):
    text, theme, score = item
    label = "scored" if kind == "focus" else "scored"
    return f"""      <div class="res is-{kind}">
        <span class="res-n">{n}</span>
        <div class="res-b"><h3>{text}</h3><span class="res-tag">{theme}</span></div>
        <div class="res-score"><b>{score}</b><span>{label}</span></div>
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
    focus = "\n".join(res_card("focus", i + 1, f) for i, f in enumerate(FOCUS))
    wins = "\n".join(res_card("win", i + 1, w) for i, w in enumerate(WINS))
    note = ('<p class="note-line">Present all three, check what resonates, then choose one together. '
            'You guide the choice, the team makes it with you.</p>')
    win_note = '<p class="note-line">Notice what is working well, and how the team can protect or build on it.</p>'
    return f"""    <h2 class="sub">{I_TARGET} Three focus areas from your team results</h2>
    <div class="results">
{focus}
    </div>
    {note}
    <h2 class="sub" style="margin-top:7mm">{I_STAR} Celebration points from your team results</h2>
    <div class="results">
{wins}
    </div>
    {win_note}"""

def present_block():
    """How to actually get the results in front of the team. The guide sends a
       manager to the platform first, because the live view is the only version
       that is current, and gives fallbacks for the day the screen share fails."""
    alts = [
        (I_PPT, "Export to PowerPoint from the same page and present from the deck"),
        (I_IMG, "Or screenshot Focus view beforehand, so nothing depends on signing in"),
    ]
    items = "".join(f'<li>{ic}<span>{tx}</span></li>' for ic, tx in alts)
    return f"""    <div class="present">
      <div class="present-main">
        <h2 class="sub" style="margin-bottom:2mm">{I_SCREEN} Showing the results to your team</h2>
        <p class="present-lede">Put the results on the screen so everyone sees the same picture you do.
          This link opens your focus areas straight away, and the code does the same on your phone.</p>
        <p class="present-link">{I_LINK}<a href="{FOCUS_URL}">{FOCUS_LABEL}</a></p>
        <ul class="alts">{items}</ul>
      </div>
      <div class="qr">{qr_svg()}<span>Scan to open<br>your focus areas</span></div>
    </div>"""

def starters_table():
    rows = "\n".join(f'    <div class="st-r"><div class="st-k">{k}</div><div class="st-v">{v}</div></div>'
                     for k, v in STARTERS)
    return f"""  <div class="starters">
    <div class="st-h"><span>Starter</span><span>Use it to explore</span></div>
{rows}
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

    return HEAD % "Understanding what drives results &mdash; Conversation guide" + cover(
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
      Create safety by agreeing to listen to understand, making room for different experiences,
      and discussing patterns rather than individual responses.</p>
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
def build_condensed():
    """Two pages: the results and the agenda on one, the starters and what you
       agree on the other. Everything a manager needs in the room, nothing to read
       beforehand."""
    agenda = "\n".join(
        f"""      <div class="ag"><span class="ag-n">{i+1}</span>
        <div class="ag-b"><h3>{t}</h3></div><span class="ag-t">{m}</span></div>"""
        for i, (t, d, m) in enumerate(AGENDA))
    starters = starters_table()
    triage = (f'<span class="triage is-improve">{I_TARGET} improve</span>, '
              f'<span class="triage is-monitor">{I_SEARCH} monitor</span> or '
              f'<span class="triage is-support">{I_FLAG} need support</span>')
    pr = (f'<span class="principle is-curious">{I_SEARCH} Be curious</span>'
          f'<span class="principle is-listen">{I_MSG} Listen before deciding</span>'
          f'<span class="principle is-share">{I_GROUP} Share ownership</span>')

    return HEAD % "Conversation run sheet &mdash; Sales West" + f"""
<section class="sheet is-runsheet">
  <div class="intro">
    <div class="intro-cut"></div>
    <img class="intro-art" src="../assets/illustrations/follow-up-guide.svg" alt="">
    <div class="intro-body">
      <p class="eyebrow-light">Conversation guide for managers</p>
      <h1 class="intro-title">Understanding what drives results</h1>
      <p class="intro-lede">You are a facilitator and listener. Open with the team&rsquo;s overall
        results and create a shared picture before you discuss the focus areas.</p>
      <div class="intro-meta">
        <div class="im"><i class="im-rule is-a"></i><span>Survey</span><strong>{SURVEY}</strong></div>
        <div class="im"><i class="im-rule is-b"></i><span>Team</span><strong>{TEAM}</strong></div>
        <div class="im"><i class="im-rule is-c"></i><span>Results period</span><strong>{PERIOD}</strong></div>
      </div>
      <div class="principles is-onnavy">{pr}</div>
    </div>
  </div>
{results_block(compact=True)}
{present_block()}
  <span class="pageno">1</span>
</section>

<section class="sheet is-compact">
  <h2 class="sub">{I_CLIP} The conversation, about 35 to 45 minutes</h2>
  <div class="agenda is-rows" style="margin-bottom:6mm">
{agenda}
  </div>

  <div class="step">
    <div class="step-head"><span class="step-n">1</span><h3>Open the conversation</h3></div>
    <p>Set the purpose: understand the experience behind the results before deciding what to do.
      Agree to listen to understand, make room for different experiences, and discuss patterns
      rather than individual responses.</p>
    <div class="starter-box"><div class="lbl">{I_MSG} Say something like</div>
      <p>&ldquo;These results tell us where to look, not why they are what they are. I would like us
        to understand the experience behind them together.&rdquo;</p></div>
  </div>

  <div class="step">
    <div class="step-head"><span class="step-n">2</span><h3>Look at the results and select a focus area</h3></div>
    <div class="pair">
      <div class="pair-box"><span class="tag">Open the picture</span><p>What do you recognise in this picture?</p></div>
      <div class="pair-box"><span class="tag">Check resonance</span><p>What feels incomplete or surprising?
        Which focus area is most useful for us to explore?</p></div>
    </div>
  </div>

  <div class="step" style="margin-bottom:0">
    <div class="step-head"><span class="step-n">3</span><h3>Take a moment to celebrate</h3></div>
    <div class="pair">
      <div class="pair-box"><span class="tag" style="color:var(--green)">Notice</span><p>What is helping this work well?
        When have you experienced this at its best?</p></div>
      <div class="pair-box"><span class="tag" style="color:var(--green)">Build</span><p>What should we protect,
        repeat or build on?</p></div>
    </div>
  </div>
  <span class="pageno">2</span>
</section>

<section class="sheet is-compact">
  <div class="step-head" style="margin-bottom:3mm"><span class="step-n">4</span><h3>Dive deeper, then agree a step</h3></div>
  <p class="note-line" style="margin:0 0 4mm">Choose two or three starters, listen, ask a follow up where
    useful, check whether others recognise the pattern, and summarise what you hear.</p>
{starters}

  <p class="note-line" style="display:flex;gap:2mm;align-items:flex-start">{I_EAR}
    <span><b>Keep listening</b> &ldquo;Can you say a little more?&rdquo; &middot;
    &ldquo;What else is important here?&rdquo; &middot;
    &ldquo;I am hearing &hellip; Did I capture that accurately?&rdquo;</span></p>

  <h2 class="sub" style="margin-top:6mm">{I_CHECK} What you agree together</h2>
  <p class="note-line" style="margin:0 0 4mm">Decide whether to {triage}, then set one small, realistic step and
    name who owns it.</p>
  <div class="grid3" style="margin-bottom:3mm">
    <div class="write"><div class="lbl">{I_PEN} Shared focus</div></div>
    <div class="write"><div class="lbl">{I_PEN} What we learned</div></div>
    <div class="write"><div class="lbl">{I_PEN} First step</div></div>
  </div>
  <div class="grid3" style="margin-bottom:6mm">
    <div class="write"><div class="lbl">{I_PEN} Owner and timing</div></div>
    <div class="write"><div class="lbl">{I_PEN} Support needed</div></div>
    <div class="write"><div class="lbl">{I_PEN} Follow up moment</div></div>
  </div>

  <div class="step" style="margin-bottom:0">
    <div class="step-head"><span class="step-n">5</span><h3>Close off the meeting</h3></div>
    <div class="starter-box"><div class="lbl">{I_MSG} Summarise and close</div>
      <p>&ldquo;Today we heard &hellip; We agreed to &hellip; The first step is &hellip;
        [name] will &hellip; by &hellip;&rdquo;</p>
      <p>&ldquo;What is the most important thing we should take forward?&rdquo;</p></div>
    <p class="note-line" style="margin-top:3mm">Thank everyone for participating and being open. Make sure the
      agreement and the follow up moment are visible to the team afterwards.</p>
  </div>
  """ + DOC_FOOT % (TEAM, PERIOD, "3") + """
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
    open(os.path.join(HERE, "conversation-guide.html"), "w", encoding="utf-8").write(build_condensed())
    print("wrote conversation-guide-full.html and conversation-guide.html")
