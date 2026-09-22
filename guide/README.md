# The conversation guide documents

Both are built from one set of team results, so a manager downloads a guide that
already carries their survey, their team and their numbers instead of blank lines.

| File | What it is |
|---|---|
| `conversation-guide.pdf` | **The run sheet, 2 pages.** What *Download a copy* hands over: the results and the principles on page one, the agenda, the starters and what you agree on page two |
| `conversation-guide-full.pdf` | **The full guide, 7 pages.** The same content with the guidance for each agenda step written out. Not linked from the prototype, kept as the long form reference |
| `build.py` | Builds both documents, and holds the team results they are populated with |
| `guide.css` | The shared print stylesheet |
| `conversation-guide.html` | The build output, and what the prototype's **View the guide** dialog shows in an iframe. Do not edit by hand, it is overwritten |
| `conversation-guide-source.docx` | The original content brief, before the design pass |

## The platform link and the QR code

`build.py` holds `PLATFORM_URL`, which is where a manager goes to put the results
on the screen. The QR code on the run sheet is generated from it at build time
with `segno` and inlined as SVG, so the document carries no remote image. It
currently points at `my.effectory.com`; swap it for the real Focus view deep link
once that exists and the code regenerates itself.

## Changing the results

The team's focus areas, celebration points, survey and period live at the top of
`build.py` as `FOCUS`, `WINS`, `SURVEY`, `TEAM` and `PERIOD`. They mirror
`focusAreas` and `WINS` in `conversation-guide-v1.html`, so if the prototype's
results change, change them here too.

## Rebuilding

```
python3 -m http.server 8000
python3 guide/build.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \
  --print-to-pdf=guide/conversation-guide.pdf --no-pdf-header-footer \
  http://localhost:8000/guide/conversation-guide.html
```

Repeat the last command for `conversation-guide-full`. Two things to keep in
mind: `print-color-adjust: exact` is what stops the brand colours being dropped,
and each `.sheet` is one A4 page, so check the page count after any edit rather
than trusting it.

## How the prototype uses these

**View the guide** in the side panel opens `conversation-guide.html` in a dialog,
so a manager reads the guide in the platform; **Download a copy** inside that
dialog serves the PDF. The HTML is used rather than the PDF because a PDF in an
iframe is unreliable on mobile, and the two are built from the same source.

The `.sheet` is a fixed 210mm so the print stays exact, which is wider than a
narrow dialog, so a screen-only `zoom` scales the page down. Print is untouched.

## Keeping the side panel honest

The panel is a trailer for the run sheet. When the guide changes, re-check
`guideStepsHTML()` and `guideTakeawaysHTML()` in both prototype files.
